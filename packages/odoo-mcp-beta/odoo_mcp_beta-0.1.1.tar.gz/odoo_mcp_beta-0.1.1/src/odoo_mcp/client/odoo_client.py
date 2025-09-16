"""
Odoo XML-RPC client for MCP server integration
"""

import os
import re
import socket
import urllib.parse
from datetime import datetime

import http.client
import xmlrpc.client


class OdooClient:
    """Client for interacting with Odoo via XML-RPC"""

    def __init__(
        self,
        url,
        db,
        username,
        password,
        timeout=10,
        verify_ssl=True,
    ):
        """
        Initialize the Odoo client with connection parameters

        Args:
            url: Odoo server URL (with or without protocol)
            db: Database name
            username: Login username
            password: Login password
            timeout: Connection timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        # Ensure URL has a protocol
        if not re.match(r"^https?://", url):
            url = f"http://{url}"

        # Remove trailing slash from URL if present
        url = url.rstrip("/")

        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None

        # Set timeout and SSL verification
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Setup connections
        self._common = None
        self._models = None

        # Parse hostname for logging
        parsed_url = urllib.parse.urlparse(self.url)
        self.hostname = parsed_url.netloc

        # Connect
        self._connect()

    def _connect(self):
        """Initialize the XML-RPC connection and authenticate"""
        # Create transport with appropriate timeout
        is_https = self.url.startswith("https://")
        transport = RedirectTransport(
            timeout=self.timeout, use_https=is_https, verify_ssl=self.verify_ssl
        )

        print(f"Connecting to Odoo at: {self.url}", file=os.sys.stderr)
        print(f"  Hostname: {self.hostname}", file=os.sys.stderr)
        print(
            f"  Timeout: {self.timeout}s, Verify SSL: {self.verify_ssl}",
            file=os.sys.stderr,
        )

        # Set up endpoints
        self._common = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/common", transport=transport,
            allow_none=True
        )
        self._models = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/object", transport=transport,
            allow_none=True
        )

        # Authenticate and get user ID
        print(
            f"Authenticating with database: {self.db}, username: {self.username}",
            file=os.sys.stderr,
        )
        try:
            print(
                f"Making request to {self.hostname}/xmlrpc/2/common (attempt 1)",
                file=os.sys.stderr,
            )
            self.uid = self._common.authenticate(
                self.db, self.username, self.password, {}
            )
            if not self.uid:
                raise ValueError("Authentication failed: Invalid username or password")
        except (socket.error, socket.timeout, ConnectionError, TimeoutError) as e:
            print(f"Connection error: {str(e)}", file=os.sys.stderr)
            raise ConnectionError(f"Failed to connect to Odoo server: {str(e)}")
        except Exception as e:
            print(f"Authentication error: {str(e)}", file=os.sys.stderr)
            raise ValueError(f"Failed to authenticate with Odoo: {str(e)}")
        
        return self.uid
        
    def login(self):
        """Authenticate with the Odoo server and return user ID
        
        This is an alias for _connect() added for test compatibility.
        
        Returns:
            int: The user ID if authentication is successful
        """
        return self._connect()

    def _execute(self, model, method, *args, **kwargs):
        """Execute a method on an Odoo model"""
        return self._models.execute_kw(
            self.db, self.uid, self.password, model, method, args, kwargs
        )

    def execute_method(self, model, method, *args, **kwargs):
        """
        Execute an arbitrary method on a model

        Args:
            model: The model name (e.g., 'res.partner')
            method: Method name to execute
            *args: Positional arguments to pass to the method
            **kwargs: Keyword arguments to pass to the method

        Returns:
            Result of the method execution
        """
        return self._execute(model, method, *args, **kwargs)

    def get_models(self):
        """
        Get a list of all available models in the system

        Returns:
            List of model names

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> models = client.get_models()
            >>> print(len(models))
            125
            >>> print(models[:5])
            ['res.partner', 'res.users', 'res.company', 'res.groups', 'ir.model']
        """
        try:
            # Try using ir.model to get all models
            ir_model = self._execute("ir.model", "search_read", [], ["model"])
            return sorted([record["model"] for record in ir_model])
        except Exception as e:
            print(f"Error getting models via ir.model: {str(e)}", file=os.sys.stderr)
            try:
                # Fallback to using the ORM's registry info
                # This returns a dict with model names as keys
                registry_info = self._execute(
                    "ir.model", "get_model_entries", ["not used"]
                )
                return sorted(list(registry_info.keys()))
            except Exception as e2:
                print(
                    f"Error getting models via registry: {str(e2)}", file=os.sys.stderr
                )
                try:
                    # Another fallback, just get the models the user has access to
                    # by listing database tables (only works if the user has sufficient privileges)
                    table_query = "SELECT model FROM ir_model"
                    result = self._execute("ir.model", "execute_query", table_query)
                    models = [row[0] for row in result]
                    return sorted(models)
                except Exception as e3:
                    print(
                        f"Final attempt to get models failed: {str(e3)}",
                        file=os.sys.stderr,
                    )
                    # Last resort, return a few common models
                    return [
                        "res.partner",
                        "res.users",
                        "res.company",
                        "product.template",
                        "sale.order",
                    ]

    def get_models_with_stats(self, limit=50, min_records=0):
        """
        Get models with additional information including record count and update/create dates
        
        This provides enhanced information about models to help identify relevant ones.
        
        Args:
            limit: Maximum number of models to return (default: 50)
            min_records: Minimum number of records a model must have to be included (default: 0)
            
        Returns:
            List of dictionaries with model information including:
            - name: Technical model name
            - display_name: User-friendly display name
            - record_count: Number of records in the model
            - latest_update: Date of most recent record update (if available)
            - latest_create: Date of most recent record creation (if available)
            - description: Model description if available
            
        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> model_stats = client.get_models_with_stats(limit=5)
            >>> print(model_stats[0]['name'], model_stats[0]['record_count'])
            'res.partner' 143
        """
        result = []
        try:
            # Get model metadata from ir.model
            ir_models = self._execute(
                "ir.model", 
                "search_read", 
                [], 
                ["model", "name", "description"]
            )
            
            # Create a mapping of model names to their metadata
            model_metadata = {}
            for model in ir_models:
                model_metadata[model["model"]] = {
                    "name": model["model"],
                    "display_name": model["name"],
                    "description": model.get("description", "")
                }
            
            # Get models, prioritizing the most commonly used ones
            models = self.get_models()
            
            # Process each model to get statistics
            for model_name in models[:100]:  # Limit initial processing to avoid timeouts
                try:
                    # Skip models that likely won't work with regular ORM methods
                    if model_name.startswith(('_', 'ir.', 'workflow.')) and model_name not in [
                        'ir.attachment', 'ir.ui.view', 'ir.model'
                    ]:
                        continue
                    
                    # Try to get record count
                    count = self._execute(model_name, "search_count", [])
                    
                    # Skip if below minimum record threshold
                    if count < min_records:
                        continue
                    
                    # Get latest dates (only for models with records)
                    latest_update = None
                    latest_create = None
                    
                    if count > 0:
                        # Check if model has these fields
                        fields_info = self.get_model_fields(model_name)
                        date_fields = []
                        
                        if 'write_date' in fields_info:
                            date_fields.append('write_date')
                        if 'create_date' in fields_info:
                            date_fields.append('create_date')
                            
                        if date_fields:
                            # Get the latest record by date fields
                            latest = self._execute(
                                model_name, 
                                "search_read", 
                                [], 
                                date_fields, 
                                0, 1, 
                                "write_date desc, create_date desc"
                            )
                            
                            if latest:
                                if 'write_date' in latest[0]:
                                    write_date = latest[0]['write_date']
                                    if write_date:
                                        # Convert string date to datetime
                                        latest_update = datetime.fromisoformat(write_date.replace('Z', '+00:00'))
                                
                                if 'create_date' in latest[0]:
                                    create_date = latest[0]['create_date']
                                    if create_date:
                                        # Convert string date to datetime
                                        latest_create = datetime.fromisoformat(create_date.replace('Z', '+00:00'))
                    
                    # Build the model info
                    model_info = {
                        "name": model_name,
                        "display_name": model_metadata.get(model_name, {}).get("display_name", model_name),
                        "description": model_metadata.get(model_name, {}).get("description", ""),
                        "record_count": count,
                        "latest_update": latest_update,
                        "latest_create": latest_create
                    }
                    
                    result.append(model_info)
                    
                    # Stop if we've reached the limit
                    if len(result) >= limit:
                        break
                        
                except Exception as model_error:
                    print(
                        f"Error getting stats for model {model_name}: {str(model_error)}",
                        file=os.sys.stderr
                    )
                    continue
            
            # Sort by record count (descending) for relevance
            result.sort(key=lambda x: x["record_count"], reverse=True)
            return result[:limit]
            
        except Exception as e:
            print(f"Error getting model stats: {str(e)}", file=os.sys.stderr)
            return []

    def get_model_info(self, model_name):
        """
        Get information about a specific model

        Args:
            model_name: Name of the model (e.g., 'res.partner')

        Returns:
            Dictionary with model information

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> info = client.get_model_info('res.partner')
            >>> print(info['name'])
            'Contact'
        """
        # Search for the model in ir.model
        model_search = self._execute(
            "ir.model", "search_read", [["model", "=", model_name]], ["name", "model"]
        )

        if not model_search:
            raise ValueError(f"Model not found: {model_name}")

        return model_search[0]

    def get_model_fields(self, model_name):
        """
        Get field definitions for a specific model

        Args:
            model_name: Name of the model (e.g., 'res.partner')

        Returns:
            Dictionary mapping field names to their definitions

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> fields = client.get_model_fields('res.partner')
            >>> print(fields['name']['type'])
            'char'
        """
        fields_info = self._execute(model_name, "fields_get", [])
        return fields_info

    def search_read(
        self, model_name, domain, fields=None, offset=None, limit=None, order=None
    ):
        """
        Search for records and read their data in a single call

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            domain: Search domain (e.g., [('is_company', '=', True)])
            fields: List of field names to return (None for all)
            offset: Number of records to skip
            limit: Maximum number of records to return
            order: Field to sort by (e.g., 'name ASC')

        Returns:
            List of dictionaries containing the record data

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> records = client.search_read('res.partner', [('is_company', '=', True)], limit=5)
            >>> print(len(records))
            5
        """
        kwargs = {}
        if fields is not None:
            kwargs["fields"] = fields
        if offset is not None:
            kwargs["offset"] = offset
        if limit is not None:
            kwargs["limit"] = limit
        if order is not None:
            kwargs["order"] = order

        return self._execute(model_name, "search_read", domain, **kwargs)

    def read_records(self, model_name, ids, fields=None):
        """
        Read data of records by IDs

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            ids: List of record IDs to read
            fields: List of field names to return (None for all)

        Returns:
            List of dictionaries containing the record data

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> records = client.read_records('res.partner', [1])
            >>> print(records[0]['name'])
            'YourCompany'
        """
        return self._execute(model_name, "read", ids, fields)


class RedirectTransport(xmlrpc.client.Transport):
    """Transport that adds timeout, SSL verification, and redirect handling"""

    def __init__(
        self, timeout=10, use_https=True, verify_ssl=True, max_redirects=5, proxy=None
    ):
        super().__init__()
        self.timeout = timeout
        self.use_https = use_https
        self.verify_ssl = verify_ssl
        self.max_redirects = max_redirects
        self.proxy = proxy
        self.proxy_url = proxy  # Add proxy_url alias for test compatibility

        # Create unverified SSL context if SSL verification is disabled
        if not verify_ssl and use_https:
            import ssl

            self.context = ssl._create_unverified_context()

    def make_connection(self, host):
        # Use proxy if specified
        if self.proxy:
            proxy_url = urllib.parse.urlparse(self.proxy)
            connection = http.client.HTTPConnection(
                proxy_url.hostname, proxy_url.port, timeout=self.timeout
            )
            connection.set_tunnel(host)
        else:
            if self.use_https and not self.verify_ssl:
                connection = http.client.HTTPSConnection(
                    host, timeout=self.timeout, context=self.context
                )
            else:
                if self.use_https:
                    connection = http.client.HTTPSConnection(host, timeout=self.timeout)
                else:
                    connection = http.client.HTTPConnection(host, timeout=self.timeout)

        return connection

    def request(self, host, handler, request_body, verbose):
        """Send HTTP request with retry for redirects"""
        redirects = 0
        while redirects < self.max_redirects:
            try:
                print(f"Making request to {host}{handler}", file=os.sys.stderr)
                return super().request(host, handler, request_body, verbose)
            except xmlrpc.client.ProtocolError as err:
                if err.errcode in (301, 302, 303, 307, 308) and err.headers.get(
                    "location"
                ):
                    redirects += 1
                    location = err.headers.get("location")
                    parsed = urllib.parse.urlparse(location)
                    if parsed.netloc:
                        host = parsed.netloc
                    handler = parsed.path
                    if parsed.query:
                        handler += "?" + parsed.query
                else:
                    raise
            except Exception as e:
                print(f"Error during request: {str(e)}", file=os.sys.stderr)
                raise

        raise xmlrpc.client.ProtocolError(host + handler, 310, "Too many redirects", {})
