"""
Configuration handling for Odoo MCP Server
"""

import json
import os

from ..client.odoo_client import OdooClient


def load_config():
    """
    Load Odoo configuration from environment variables or config file

    Returns:
        dict: Configuration dictionary with url, db, username, password, and optional parameters
    """
    # Initialize empty config
    config = {}
    
    # Check for config file path from environment or use defaults
    config_file = os.environ.get("ODOO_CONFIG_FILE")
    config_paths = []
    
    if config_file:
        config_paths.append(config_file)
    
    # Add default paths
    config_paths.extend([
        "./odoo_config.json",
        os.path.expanduser("~/.config/odoo/config.json"),
        os.path.expanduser("~/.odoo_config.json"),
    ])

    # Try to load from file first
    for path in config_paths:
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path):
            with open(expanded_path, "r") as f:
                config = json.load(f)
                break

    # Override with environment variables if present
    if "ODOO_URL" in os.environ:
        config["url"] = os.environ["ODOO_URL"]
    if "ODOO_DB" in os.environ:
        config["db"] = os.environ["ODOO_DB"]
    if "ODOO_USERNAME" in os.environ:
        config["username"] = os.environ["ODOO_USERNAME"]
    if "ODOO_PASSWORD" in os.environ:
        config["password"] = os.environ["ODOO_PASSWORD"]
    
    # Handle optional parameters
    if "ODOO_TIMEOUT" in os.environ:
        config["timeout"] = int(os.environ["ODOO_TIMEOUT"])
    elif "timeout" not in config:
        config["timeout"] = 30  # Default timeout
        
    if "ODOO_VERIFY_SSL" in os.environ:
        verify_value = os.environ["ODOO_VERIFY_SSL"].lower()
        config["verify_ssl"] = verify_value in ["1", "true", "yes"]
    elif "verify_ssl" not in config:
        config["verify_ssl"] = True  # Default verify_ssl
    
    if "HTTP_PROXY" in os.environ:
        config["proxy"] = os.environ["HTTP_PROXY"]
        
    # Add MCP prefix parameter - if not provided, db name will be used
    if "ODOO_MCP_PREFIX" in os.environ:
        config["mcp_prefix"] = os.environ["ODOO_MCP_PREFIX"]
    elif "mcp_prefix" not in config:
        config["mcp_prefix"] = ""  # Default is empty, will use db name
    
    # Validate required fields
    required_fields = ["url", "db", "username", "password"]
    if not all(field in config for field in required_fields):
        raise ValueError(f"Configuration is incomplete. Required fields: {required_fields}")
    
    return config


def get_odoo_client():
    """
    Get a configured Odoo client instance

    Returns:
        OdooClient: A configured Odoo client instance that is already logged in
    """
    config = load_config()

    # Print detailed configuration
    print("Odoo client configuration:", file=os.sys.stderr)
    print(f"  URL: {config['url']}", file=os.sys.stderr)
    print(f"  Database: {config['db']}", file=os.sys.stderr)
    print(f"  Username: {config['username']}", file=os.sys.stderr)
    print(f"  Timeout: {config.get('timeout', 30)}s", file=os.sys.stderr)
    print(f"  Verify SSL: {config.get('verify_ssl', True)}", file=os.sys.stderr)
    if "proxy" in config:
        print(f"  Proxy: {config['proxy']}", file=os.sys.stderr)
    print(f"  MCP Prefix: {config.get('mcp_prefix') or config.get('db', 'unknown')}", file=os.sys.stderr)

    # Filter out non-client parameters
    client_params = {
        k: v for k, v in config.items() 
        if k in ['url', 'db', 'username', 'password', 'timeout', 'verify_ssl', 'proxy']
    }
    
    # Create the client with filtered configuration
    client = OdooClient(**client_params)
    
    # Ensure client is logged in before returning
    client.login()
    
    return client
