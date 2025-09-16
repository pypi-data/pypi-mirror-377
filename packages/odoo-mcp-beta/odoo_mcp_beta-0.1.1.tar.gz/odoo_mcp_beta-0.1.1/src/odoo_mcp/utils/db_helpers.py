"""
Database utility functions for the Odoo MCP server
"""

from ..config.config import load_config


def get_formatted_db_name():
    """
    Get the formatted identifier for use in URIs and tool names
    
    Returns:
        str: The identifier (MCP prefix or database name) formatted for use in URIs and tool names
              with hyphens replaced by underscores
    """
    config = load_config()
    
    # First check if there's a specific MCP prefix set
    prefix = config.get('mcp_prefix', '')
    
    # If no prefix is set, fall back to using the database name
    if not prefix:
        prefix = config.get('db', 'odoo')
        
    # Format the prefix (replace hyphens with underscores)
    formatted_prefix = prefix.replace('-', '_')
    return formatted_prefix
