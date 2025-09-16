"""
Resources for Odoo record operations
"""

import json

from ..config.config import get_odoo_client
from ..utils.db_helpers import get_formatted_db_name


def get_record(model_name: str, record_id: str):
    """
    Get a specific record by ID

    Parameters:
        model_name: Name of the Odoo model (e.g., 'res.partner')
        record_id: ID of the record
    """
    odoo_client = get_odoo_client()
    try:
        record_id_int = int(record_id)
        record = odoo_client.read_records(model_name, [record_id_int])
        if not record:
            return {
                "error": {
                    "code": "resource_not_found",
                    "message": f"Record not found: {model_name} ID {record_id}"
                }
            }
        
        # Get formatted database name
        db_name = get_formatted_db_name()
        
        # Return properly formatted MCP resource content with db_name in URI
        return {
            "contents": [
                {
                    "uri": f"odoo://{db_name}/record/{model_name}/{record_id}",
                    "mimeType": "application/json",
                    "content": json.dumps(record[0], indent=2)
                }
            ]
        }
    except ValueError:
        return {
            "error": {
                "code": "invalid_id_format",
                "message": f"Invalid record ID format: {record_id}"
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "resource_not_found",
                "message": str(e)
            }
        }


def search_records_resource(model_name: str, domain: str):
    """
    Search for records that match a domain

    Parameters:
        model_name: Name of the Odoo model (e.g., 'res.partner')
        domain: Search domain in JSON format (e.g., '[["name", "ilike", "test"]]')
    """
    odoo_client = get_odoo_client()
    try:
        # Parse domain from JSON string
        domain_list = json.loads(domain)

        # Set a reasonable default limit
        limit = 10

        # Perform search_read for efficiency
        results = odoo_client.search_read(model_name, domain_list, limit=limit)

        # Get formatted database name
        db_name = get_formatted_db_name()
        
        # Return properly formatted MCP resource content with db_name in URI
        return {
            "contents": [
                {
                    "uri": f"odoo://{db_name}/search/{model_name}/{domain}",
                    "mimeType": "application/json",
                    "content": json.dumps(results, indent=2)
                }
            ]
        }
    except json.JSONDecodeError as e:
        return {
            "error": {
                "code": "invalid_domain_format",
                "message": f"Invalid domain format: {str(e)}"
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "search_error",
                "message": str(e)
            }
        }
