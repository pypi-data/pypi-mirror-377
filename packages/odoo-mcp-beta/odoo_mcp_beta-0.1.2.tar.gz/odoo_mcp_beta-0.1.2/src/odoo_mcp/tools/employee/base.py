"""
Base employee tools for standard Odoo fields and functions
"""

import asyncio
from typing import Dict, Any, List, Optional

from mcp.server.fastmcp import Context
from ...utils.context_helpers import get_odoo_client_from_context, report_progress

from ...models.employee import EmployeeSearchResult, SearchEmployeeResponse
from ...config.config import get_odoo_client
from ...utils.db_helpers import get_formatted_db_name


# Standard HR fields that should exist in any Odoo installation with HR
STANDARD_EMPLOYEE_FIELDS = [
    "name", "work_email", "work_phone", "job_title", "department_id", 
    "job_id", "parent_id", "coach_id", "address_id", "work_location",
    "mobile_phone", "active", "company_id", "resource_calendar_id"
]


async def validate_field_exists(client, model, field_name) -> bool:
    """Check if a field exists in the model"""
    try:
        # Get all fields for the model
        fields = client.get_model_fields(model)
        return field_name in fields
    except Exception:
        return False


async def search_employee(
    ctx: Context,
    name: str,
    limit: int = 20,
):
    """
    Search for employees by name using Odoo's name_search method.

    Parameters:
        name: The name (or part of the name) to search for.
        limit: The maximum number of results to return (default 20).

    Returns:
        Object containing search results or error information.
    """
    response = SearchEmployeeResponse(success=False)
    
    try:
        # Report progress (if available)
        if hasattr(ctx, 'progress'):
            await ctx.progress(description=f"Searching for employees matching '{name}'", percent=10)
        
        # Get Odoo client from context
        odoo = get_odoo_client_from_context(ctx)
        model = "hr.employee"
        method = "name_search"

        args = []
        kwargs = {"name": name, "limit": limit}
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Executing search", percent=40)
        
        # Execute the search method
        result = odoo.execute_method(model, method, *args, **kwargs)
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Processing results", percent=70)
        
        # Convert result to appropriate format
        parsed_result = [
            EmployeeSearchResult(id=item[0], name=item[1]) 
            for item in result
        ]
        
        # Build response
        response.success = True
        response.result = parsed_result
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Complete", percent=100)
        
        return response.dict()
    except Exception as e:
        error_msg = f"Error searching employees: {str(e)}"
        response.success = False
        response.error = error_msg
        return response.dict()


async def get_employee_details(
    ctx: Context,
    employee_id: int,
    fields: Optional[List[str]] = None
):
    """
    Get detailed information about an employee.
    
    Parameters:
        employee_id: The ID of the employee to retrieve.
        fields: Optional list of fields to retrieve. If not provided,
               standard fields will be used.
               
    Returns:
        Object containing employee details or error information.
    """
    try:
        # Report progress (if available)
        if hasattr(ctx, 'progress'):
            await ctx.progress(description=f"Retrieving employee details for ID {employee_id}", percent=10)
        
        # Get Odoo client from context
        odoo = get_odoo_client_from_context(ctx)
        model = "hr.employee"
        
        # Use standard fields if none provided
        if not fields:
            # Validate fields exist
            existing_fields = []
            for field in STANDARD_EMPLOYEE_FIELDS:
                if await validate_field_exists(odoo, model, field):
                    existing_fields.append(field)
            
            fields = existing_fields
        else:
            # Validate provided fields exist
            existing_fields = []
            for field in fields:
                if await validate_field_exists(odoo, model, field):
                    existing_fields.append(field)
            
            fields = existing_fields
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Reading employee data", percent=40)
        
        # Execute the read method
        result = odoo.read_records(model, [employee_id], fields)
        
        if not result:
            return {
                "success": False,
                "error": f"Employee with ID {employee_id} not found"
            }
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Processing results", percent=90)
        
        return {
            "success": True,
            "data": result[0]
        }
    except Exception as e:
        error_msg = f"Error getting employee details: {str(e)}"
        return {
            "success": False,
            "error": error_msg
        }


def register_base_tools(mcp):
    """Register standard employee MCP tools"""
    
    db_prefix = get_formatted_db_name()
    
    # Get Odoo client to check fields
    client = get_odoo_client()
    
    # Register search_employee tool (always available)
    mcp.add_tool(
        f"{db_prefix}_search_employee",
        search_employee,
        "Search for employees by name"
    )
    
    # Only register get_employee_details if hr.employee model exists
    try:
        models = client.get_models()
        if "hr.employee" in models:
            mcp.add_tool(
                f"{db_prefix}_get_employee_details",
                get_employee_details,
                "Get detailed information about an employee"
            )
    except Exception as e:
        print(f"Warning: Could not register employee details tool: {str(e)}")
