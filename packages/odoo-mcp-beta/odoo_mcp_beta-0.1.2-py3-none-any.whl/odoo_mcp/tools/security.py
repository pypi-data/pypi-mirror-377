"""
Security and access control tools for Odoo MCP
"""

from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def get_user_info(
    ctx: Context,
    user_id: Optional[int] = None
):
    """
    Get information about a user
    
    Parameters:
        user_id: User ID (None for current user)
    
    Returns:
        User information
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Getting user information")
        
        # Get current user if not specified
        if user_id is None:
            user_id = odoo.uid
        
        # Get user data
        user_data = odoo.read_records(
            "res.users",
            [user_id],
            ["name", "login", "email", "groups_id", "company_id", 
             "company_ids", "lang", "tz", "active"]
        )
        
        if not user_data:
            return {
                "error": {
                    "code": "user_not_found",
                    "message": f"User {user_id} not found"
                }
            }
        
        user = user_data[0]
        
        # Get group names
        if user.get("groups_id"):
            groups = odoo.read_records(
                "res.groups",
                user["groups_id"],
                ["name", "category_id"]
            )
            user["groups"] = [
                {
                    "id": g["id"],
                    "name": g["name"],
                    "category": g["category_id"][1] if g.get("category_id") else None
                }
                for g in groups
            ]
        
        return {
            "result": {
                "success": True,
                "user": user
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "user_info_failed",
                "message": str(e)
            }
        }


def get_model_access_rights(
    ctx: Context,
    model: str,
    user_id: Optional[int] = None
):
    """
    Get access rights for a model
    
    Parameters:
        model: Model name
        user_id: User ID to check rights for (None for current user)
    
    Returns:
        Access rights information
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Getting access rights for {model}")
        
        # Check basic CRUD permissions
        access_rights = {}
        operations = ["create", "read", "write", "unlink"]
        
        for operation in operations:
            try:
                # Use check_access_rights method
                has_access = odoo.execute_method(
                    model, 
                    "check_access_rights", 
                    operation, 
                    raise_exception=False
                )
                access_rights[operation] = has_access
            except:
                access_rights[operation] = False
        
        # Get model access rules
        try:
            access_rules = odoo.search_read(
                "ir.model.access",
                [["model_id.model", "=", model]],
                ["name", "group_id", "perm_read", "perm_write", 
                 "perm_create", "perm_unlink"],
                limit=20
            )
            
            # Format access rules
            formatted_rules = []
            for rule in access_rules:
                formatted_rules.append({
                    "name": rule["name"],
                    "group": rule["group_id"][1] if rule.get("group_id") else "Global",
                    "permissions": {
                        "read": rule.get("perm_read", False),
                        "write": rule.get("perm_write", False),
                        "create": rule.get("perm_create", False),
                        "unlink": rule.get("perm_unlink", False),
                    }
                })
            
            access_rights["rules"] = formatted_rules
        except:
            access_rights["rules"] = []
        
        # Get record rules (domain-based access)
        try:
            record_rules = odoo.search_read(
                "ir.rule",
                [["model_id.model", "=", model]],
                ["name", "groups", "domain_force", "perm_read", 
                 "perm_write", "perm_create", "perm_unlink"],
                limit=10
            )
            access_rights["record_rules"] = record_rules
        except:
            access_rights["record_rules"] = []
        
        return {
            "result": {
                "success": True,
                "model": model,
                "access_rights": access_rights
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "access_rights_failed",
                "message": str(e)
            }
        }


def check_field_access(
    ctx: Context,
    model: str,
    fields: List[str],
    operation: str = "read"
):
    """
    Check field-level access rights
    
    Parameters:
        model: Model name
        fields: List of field names to check
        operation: Operation to check (read/write)
    
    Returns:
        Field access information
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Checking field access for {model}")
        
        # Get field metadata
        all_fields = odoo.get_model_fields(model)
        
        field_access = {}
        for field in fields:
            if field not in all_fields:
                field_access[field] = {
                    "exists": False,
                    "accessible": False,
                    "reason": "Field does not exist"
                }
                continue
            
            field_info = all_fields[field]
            
            # Check various access restrictions
            access_info = {
                "exists": True,
                "accessible": True,
                "readonly": field_info.get("readonly", False),
                "required": field_info.get("required", False),
                "groups": field_info.get("groups", []),
            }
            
            # Check if field is accessible based on operation
            if operation == "write":
                if field_info.get("readonly", False):
                    access_info["accessible"] = False
                    access_info["reason"] = "Field is readonly"
                elif not field_info.get("store", True):
                    access_info["accessible"] = False
                    access_info["reason"] = "Field is not stored"
                elif field_info.get("compute") and not field_info.get("inverse"):
                    access_info["accessible"] = False
                    access_info["reason"] = "Computed field without inverse method"
            
            # Check group restrictions
            if field_info.get("groups"):
                access_info["restricted"] = True
                access_info["restriction_groups"] = field_info["groups"]
            
            field_access[field] = access_info
        
        return {
            "result": {
                "success": True,
                "model": model,
                "operation": operation,
                "field_access": field_access
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "field_access_check_failed",
                "message": str(e)
            }
        }


def get_user_groups(
    ctx: Context,
    user_id: Optional[int] = None
):
    """
    Get groups for a user
    
    Parameters:
        user_id: User ID (None for current user)
    
    Returns:
        User groups
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Getting user groups")
        
        # Get current user if not specified
        if user_id is None:
            user_id = odoo.uid
        
        # Get user's groups
        user_data = odoo.read_records(
            "res.users",
            [user_id],
            ["groups_id"]
        )
        
        if not user_data or not user_data[0].get("groups_id"):
            return {
                "result": {
                    "success": True,
                    "groups": []
                }
            }
        
        group_ids = user_data[0]["groups_id"]
        
        # Get detailed group information
        groups = odoo.read_records(
            "res.groups",
            group_ids,
            ["name", "category_id", "implied_ids", "users", "model_access", "rule_groups"]
        )
        
        # Organize groups by category
        groups_by_category = {}
        for group in groups:
            category = group["category_id"][1] if group.get("category_id") else "Other"
            if category not in groups_by_category:
                groups_by_category[category] = []
            
            groups_by_category[category].append({
                "id": group["id"],
                "name": group["name"],
                "user_count": len(group.get("users", [])),
                "has_model_access": len(group.get("model_access", [])) > 0,
                "has_record_rules": len(group.get("rule_groups", [])) > 0,
            })
        
        return {
            "result": {
                "success": True,
                "user_id": user_id,
                "groups": groups_by_category,
                "total_groups": len(groups)
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "get_groups_failed",
                "message": str(e)
            }
        }


def sudo_execute(
    ctx: Context,
    model: str,
    method: str,
    args: List = None,
    kwargs: Dict[str, Any] = None,
    sudo_user_id: int = 1
):
    """
    Execute a method with elevated privileges (sudo)
    
    Parameters:
        model: Model name
        method: Method to execute
        args: Positional arguments
        kwargs: Keyword arguments
        sudo_user_id: User ID to execute as (1 = admin)
    
    Returns:
        Method execution result
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    
    try:
        report_progress(ctx, f"Executing {method} on {model} with sudo")
        
        # Note: This is a simplified version. Real sudo would require
        # server-side support or admin credentials
        # For now, we just execute with current user and note it was requested as sudo
        
        result = odoo.execute_method(model, method, *args, **kwargs)
        
        return {
            "result": {
                "success": True,
                "data": result,
                "executed_as": "current_user",
                "sudo_requested": True,
                "note": "Sudo execution requires server-side support"
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "sudo_execution_failed",
                "message": str(e)
            }
        }