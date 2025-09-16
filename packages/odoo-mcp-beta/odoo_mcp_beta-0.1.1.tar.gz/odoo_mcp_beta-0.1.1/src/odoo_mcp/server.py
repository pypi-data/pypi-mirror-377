"""
MCP server for Odoo integration

Provides MCP tools and resources for interacting with Odoo ERP systems
"""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP

from .client.odoo_client import OdooClient
from .config.config import get_odoo_client
from .utils.db_helpers import get_formatted_db_name

from .resources.subscriptions import SubscriptionManager, subscribe_resource, unsubscribe_resource

@dataclass
class AppContext:
    """Application context for the MCP server"""

    odoo: OdooClient
    subscription_manager: SubscriptionManager


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Application lifespan for initialization and cleanup
    """
    # Initialize Odoo client on startup
    odoo_client = get_odoo_client()
    
    # Initialize subscription manager
    subscription_manager = SubscriptionManager(server)

    try:
        yield AppContext(odoo=odoo_client, subscription_manager=subscription_manager)
    finally:
        # No cleanup needed for Odoo client or subscription manager
        pass


# Create MCP server with database name in the title and description

# Get database name for inclusion in resource URIs and tool names
db_name = get_formatted_db_name()

mcp = FastMCP(
    f"Odoo MCP Server - {db_name}",
    dependencies=["requests"]
)

# Set lifespan separately
mcp.lifespan_context = app_lifespan


# ----- Import and register MCP Resources -----
from .resources.models import get_models, get_model_info
from .resources.records import get_record, search_records_resource

# Register the resources with the FastMCP instance - include db_name in URIs
mcp.resource(
    f"odoo://{db_name}/models", description=f"List all available models in the {db_name} Odoo system"
)(get_models)

mcp.resource(
    f"odoo://{db_name}/model/{{model_name}}",
    description=f"Get detailed information about a specific model in {db_name} including fields",
)(get_model_info)

mcp.resource(
    f"odoo://{db_name}/record/{{model_name}}/{{record_id}}",
    description=f"Get detailed information of a specific record by ID in {db_name}",
)(get_record)

mcp.resource(
    f"odoo://{db_name}/search/{{model_name}}/{{domain}}",
    description=f"Search for records matching the domain in {db_name}",
)(search_records_resource)

# Register subscription handlers with db_name
mcp.tool(
    f"{db_name}_resources_subscribe",
    description=f"Subscribe to changes in a specific resource in {db_name}"
)(subscribe_resource)

mcp.tool(
    f"{db_name}_resources_unsubscribe",
    description=f"Unsubscribe from changes in a specific resource in {db_name}"
)(unsubscribe_resource)


# ----- Register MCP tools using the modular registration system -----
from .tools.registration import register_all_tools

# Register all available tools using the modular registration system
register_all_tools(mcp)


# Make sure the mcp instance is accessible to other modules
__all__ = ["mcp", "AppContext"]
