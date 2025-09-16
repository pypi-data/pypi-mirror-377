"""
MCP tool for getting model information with statistics
"""

import asyncio
from typing import Optional, Dict, Any

from mcp.server.fastmcp import Context

from ..config.config import get_odoo_client
from ..models.model_info import ModelInfoResponse
from ..utils.db_helpers import get_formatted_db_name


async def list_models_with_stats(
    ctx: Context,
    limit: int = 20,
    min_records: int = 0,
) -> Dict[str, Any]:
    """
    Get a list of Odoo models with record counts and update/create dates
    
    This helps identify which models have active data and when they were last updated.
    
    Args:
        limit: Maximum number of models to return (default: 20)
        min_records: Minimum number of records a model must have (default: 0)
    
    Returns:
        A dictionary with model information including record counts and dates
    """
    response = ModelInfoResponse(success=False)
    
    try:
        if hasattr(ctx, "progress"):
            await ctx.progress(description="Connecting to Odoo...", percent=10)
            
        # Get Odoo client
        client = get_odoo_client()
        
        if hasattr(ctx, "progress"):
            await ctx.progress(description="Fetching model statistics...", percent=30)
        
        # Call in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        model_stats = await loop.run_in_executor(
            None, 
            lambda: client.get_models_with_stats(limit=limit, min_records=min_records)
        )
        
        if hasattr(ctx, "progress"):
            await ctx.progress(description="Processing results...", percent=80)
        
        # Convert to Pydantic models
        response.success = True
        response.models = model_stats
        
        if hasattr(ctx, "progress"):
            await ctx.progress(description="Complete", percent=100)
        
        return response.dict()
    
    except Exception as e:
        error_msg = f"Error listing models: {str(e)}"
        response.success = False
        response.error = error_msg
        return response.dict()


def register_tools(mcp):
    """Register MCP tools"""
    
    db_prefix = get_formatted_db_name()
    
    mcp.add_tool(
        f"{db_prefix}_list_models",
        list_models_with_stats,
        "List Odoo models with record counts and last update/create dates"
    )
