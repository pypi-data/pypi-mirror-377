"""
Metadata and schema exploration tools for Odoo MCP
"""

from typing import List, Optional
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def get_field_metadata(
    ctx: Context,
    model: str,
    field_names: Optional[List[str]] = None
):
    """
    Get detailed metadata about model fields
    
    Parameters:
        model: Model name
        field_names: Specific fields to get info for (None for all)
    
    Returns:
        Detailed field metadata
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Getting field metadata for {model}")
        
        # Get field information
        all_fields = odoo.get_model_fields(model)
        
        if field_names:
            # Filter to requested fields
            fields = {k: v for k, v in all_fields.items() if k in field_names}
        else:
            fields = all_fields
        
        # Enhance metadata with additional info
        enhanced_fields = {}
        for field_name, field_info in fields.items():
            enhanced_fields[field_name] = {
                "name": field_name,
                "type": field_info.get("type"),
                "string": field_info.get("string"),
                "help": field_info.get("help"),
                "required": field_info.get("required", False),
                "readonly": field_info.get("readonly", False),
                "store": field_info.get("store", True),
                "searchable": field_info.get("searchable", True),
                "sortable": field_info.get("sortable", True),
                "relation": field_info.get("relation"),  # For many2one, one2many, many2many
                "relation_field": field_info.get("relation_field"),  # For one2many
                "selection": field_info.get("selection"),  # For selection fields
                "size": field_info.get("size"),  # For char fields
                "digits": field_info.get("digits"),  # For float fields
                "default": field_info.get("default"),
                "domain": field_info.get("domain"),
                "context": field_info.get("context"),
                "states": field_info.get("states"),
                "groups": field_info.get("groups"),  # Access control groups
                "company_dependent": field_info.get("company_dependent", False),
                "depends": field_info.get("depends", []),
                "compute": field_info.get("compute"),  # Computed field method
                "inverse": field_info.get("inverse"),  # Inverse method for computed fields
                "related": field_info.get("related"),  # Related field path
                "ondelete": field_info.get("ondelete"),  # For many2one fields
            }
        
        return {
            "result": {
                "success": True,
                "model": model,
                "fields": enhanced_fields,
                "field_count": len(enhanced_fields)
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "metadata_failed",
                "message": str(e)
            }
        }


def get_model_constraints(
    ctx: Context,
    model: str
):
    """
    Get model constraints (SQL and Python)
    
    Parameters:
        model: Model name
    
    Returns:
        Model constraints information
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Getting constraints for {model}")
        
        model_info = {}
        
        # Get SQL constraints if available
        try:
            sql_constraints = odoo.execute_method(
                "ir.model.constraint", 
                "search_read", 
                [["model", "=", model]],
                ["name", "definition", "type", "message"]
            )
            model_info["sql_constraints"] = sql_constraints
        except:
            model_info["sql_constraints"] = []
        
        # Get field constraints
        try:
            fields = odoo.get_model_fields(model)
            
            # Extract various types of constraints
            unique_fields = []
            required_fields = []
            readonly_fields = []
            selection_fields = {}
            
            for name, info in fields.items():
                if info.get("unique", False):
                    unique_fields.append(name)
                if info.get("required", False):
                    required_fields.append(name)
                if info.get("readonly", False):
                    readonly_fields.append(name)
                if info.get("selection"):
                    selection_fields[name] = info["selection"]
            
            model_info["unique_fields"] = unique_fields
            model_info["required_fields"] = required_fields
            model_info["readonly_fields"] = readonly_fields
            model_info["selection_fields"] = selection_fields
        except:
            pass
        
        return {
            "result": {
                "success": True,
                "model": model,
                "constraints": model_info
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "constraints_failed",
                "message": str(e)
            }
        }


def get_model_relations(
    ctx: Context,
    model: str
):
    """
    Get all relationships for a model
    
    Parameters:
        model: Model name
    
    Returns:
        Model relationships
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Getting relationships for {model}")
        
        fields = odoo.get_model_fields(model)
        
        relationships = {
            "many2one": [],
            "one2many": [],
            "many2many": [],
        }
        
        for field_name, field_info in fields.items():
            field_type = field_info.get("type")
            
            if field_type == "many2one":
                relationships["many2one"].append({
                    "field": field_name,
                    "relation": field_info.get("relation"),
                    "string": field_info.get("string"),
                    "required": field_info.get("required", False),
                    "ondelete": field_info.get("ondelete", "set null"),
                })
            elif field_type == "one2many":
                relationships["one2many"].append({
                    "field": field_name,
                    "relation": field_info.get("relation"),
                    "relation_field": field_info.get("relation_field"),
                    "string": field_info.get("string"),
                })
            elif field_type == "many2many":
                relationships["many2many"].append({
                    "field": field_name,
                    "relation": field_info.get("relation"),
                    "relation_table": field_info.get("relation_table"),
                    "column1": field_info.get("column1"),
                    "column2": field_info.get("column2"),
                    "string": field_info.get("string"),
                })
        
        return {
            "result": {
                "success": True,
                "model": model,
                "relationships": relationships,
                "total_relations": (
                    len(relationships["many2one"]) +
                    len(relationships["one2many"]) +
                    len(relationships["many2many"])
                )
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "relations_failed",
                "message": str(e)
            }
        }


def get_model_methods(
    ctx: Context,
    model: str
):
    """
    Get available methods for a model
    
    Parameters:
        model: Model name
    
    Returns:
        List of available methods
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Getting methods for {model}")
        
        # Common Odoo model methods
        standard_methods = [
            {"name": "create", "type": "crud", "description": "Create new records"},
            {"name": "read", "type": "crud", "description": "Read record data"},
            {"name": "write", "type": "crud", "description": "Update records"},
            {"name": "unlink", "type": "crud", "description": "Delete records"},
            {"name": "search", "type": "search", "description": "Search for record IDs"},
            {"name": "search_read", "type": "search", "description": "Search and read in one call"},
            {"name": "search_count", "type": "search", "description": "Count matching records"},
            {"name": "name_search", "type": "search", "description": "Search by name"},
            {"name": "name_get", "type": "utility", "description": "Get display names"},
            {"name": "default_get", "type": "utility", "description": "Get default values"},
            {"name": "fields_get", "type": "utility", "description": "Get field definitions"},
            {"name": "fields_view_get", "type": "utility", "description": "Get view definitions"},
            {"name": "copy", "type": "utility", "description": "Duplicate records"},
            {"name": "exists", "type": "utility", "description": "Check if records exist"},
            {"name": "check_access_rights", "type": "security", "description": "Check access rights"},
            {"name": "check_access_rule", "type": "security", "description": "Check access rules"},
            {"name": "export_data", "type": "data", "description": "Export record data"},
            {"name": "load", "type": "data", "description": "Import data"},
            {"name": "read_group", "type": "aggregation", "description": "Group and aggregate data"},
            {"name": "get_metadata", "type": "metadata", "description": "Get record metadata"},
        ]
        
        # Try to detect model-specific methods
        model_specific = []
        
        # Common workflow methods by model type
        workflow_methods = {
            "sale.order": [
                {"name": "action_confirm", "type": "workflow", "description": "Confirm sales order"},
                {"name": "action_cancel", "type": "workflow", "description": "Cancel sales order"},
                {"name": "action_draft", "type": "workflow", "description": "Set to draft"},
                {"name": "action_quotation_send", "type": "workflow", "description": "Send quotation"},
            ],
            "purchase.order": [
                {"name": "button_confirm", "type": "workflow", "description": "Confirm purchase order"},
                {"name": "button_cancel", "type": "workflow", "description": "Cancel purchase order"},
                {"name": "button_draft", "type": "workflow", "description": "Set to draft"},
                {"name": "button_approve", "type": "workflow", "description": "Approve order"},
            ],
            "account.move": [
                {"name": "action_post", "type": "workflow", "description": "Post journal entry"},
                {"name": "button_cancel", "type": "workflow", "description": "Cancel entry"},
                {"name": "button_draft", "type": "workflow", "description": "Set to draft"},
                {"name": "action_invoice_sent", "type": "workflow", "description": "Mark as sent"},
            ],
            "stock.picking": [
                {"name": "action_confirm", "type": "workflow", "description": "Confirm picking"},
                {"name": "action_cancel", "type": "workflow", "description": "Cancel picking"},
                {"name": "button_validate", "type": "workflow", "description": "Validate picking"},
            ],
            "mrp.production": [
                {"name": "action_confirm", "type": "workflow", "description": "Confirm production"},
                {"name": "button_mark_done", "type": "workflow", "description": "Mark as done"},
                {"name": "action_cancel", "type": "workflow", "description": "Cancel production"},
            ],
        }
        
        if model in workflow_methods:
            model_specific.extend(workflow_methods[model])
        
        all_methods = standard_methods + model_specific
        
        return {
            "result": {
                "success": True,
                "model": model,
                "methods": all_methods,
                "method_count": len(all_methods)
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "methods_failed",
                "message": str(e)
            }
        }


def get_model_views(
    ctx: Context,
    model: str,
    view_type: Optional[str] = None
):
    """
    Get view definitions for a model
    
    Parameters:
        model: Model name
        view_type: Specific view type (tree, form, kanban, etc.)
    
    Returns:
        View definitions
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Getting views for {model}")
        
        # Search for views
        domain = [["model", "=", model]]
        if view_type:
            domain.append(["type", "=", view_type])
        
        views = odoo.search_read(
            "ir.ui.view",
            domain,
            ["name", "type", "priority", "arch", "inherit_id", "active"],
            limit=20
        )
        
        # Group by type
        views_by_type = {}
        for view in views:
            view_type = view.get("type", "unknown")
            if view_type not in views_by_type:
                views_by_type[view_type] = []
            views_by_type[view_type].append({
                "id": view["id"],
                "name": view["name"],
                "priority": view.get("priority", 16),
                "inherited": bool(view.get("inherit_id")),
                "active": view.get("active", True)
            })
        
        return {
            "result": {
                "success": True,
                "model": model,
                "views": views_by_type,
                "view_count": len(views)
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "views_failed",
                "message": str(e)
            }
        }