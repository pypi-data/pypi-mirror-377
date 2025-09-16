"""
Resources for Odoo model operations
"""

import json

from ..config.config import get_odoo_client
from ..utils.db_helpers import get_formatted_db_name


def get_models():
    """Lists all available models in the Odoo system"""
    # Get formatted database name
    db_name = get_formatted_db_name()
    
    odoo_client = get_odoo_client()
    models = odoo_client.get_models()
    
    # Return a properly formatted MCP resource content with db_name in URI
    return {
        "contents": [
            {
                "uri": f"odoo://{db_name}/models",
                "mimeType": "application/json",
                "content": json.dumps(models, indent=2)
            }
        ]
    }


def get_model_info(model_name: str):
    """
    Get information about a specific model

    Parameters:
        model_name: Name of the Odoo model (e.g., 'res.partner')
    """
    odoo_client = get_odoo_client()
    try:
        # Get model info
        model_info = odoo_client.get_model_info(model_name)
        
        # Get model fields for detailed info
        fields = odoo_client.get_model_fields(model_name)
        model_info["fields"] = fields
        
        # Get formatted database name
        db_name = get_formatted_db_name()
        
        # Return properly formatted MCP resource content with db_name in URI
        return {
            "contents": [
                {
                    "uri": f"odoo://{db_name}/model/{model_name}",
                    "mimeType": "application/json",
                    "content": json.dumps(model_info, indent=2)
                }
            ]
        }
    except Exception as e:
        return {
            "error": {
                "code": "resource_not_found",
                "message": str(e)
            }
        }
