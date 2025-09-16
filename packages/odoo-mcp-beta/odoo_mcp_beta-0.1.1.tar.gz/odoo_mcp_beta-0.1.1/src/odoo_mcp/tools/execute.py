"""
Tool for executing Odoo methods via MCP
"""

import json
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def execute_method(
    ctx: Context,
    model: str,
    method: str,
    args: List = None,
    kwargs: Optional[Dict[str, Any]] = None,
):
    """
    Execute a custom method on an Odoo model

    Parameters:
        model: The model name (e.g., 'res.partner')
        method: Method name to execute
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Dict with:
        - success: Boolean indicating success or failure
        - result: Result of the method (if success)
        - error: Error message (if failure)
    """
    # Get the Odoo client from the context
    odoo = get_odoo_client_from_context(ctx)

    if args is None:
        args = []

    if kwargs is None:
        kwargs = {}

    try:
        # Handle domain normalization for specific methods that require domains
        if method in ["search", "search_count", "search_read"]:
            # Check if we need to normalize domain (first arg is domain)
            if len(args) > 0:
                # Get the first argument (domain)
                domain_list = args[0]
                normalized_args = list(args)

                # Normalize string input to domain list
                if isinstance(domain_list, str):
                    try:
                        # Try to parse as JSON
                        domain_list = json.loads(domain_list)
                    except json.JSONDecodeError:
                        return {
                            "error": {
                                "code": "invalid_domain_format",
                                "message": f"Invalid domain format: {domain_list}"
                            }
                        }

                # Handle object format ({"conditions": [...]})
                if isinstance(domain_list, dict) and "conditions" in domain_list:
                    conditions_list = domain_list.get("conditions", [])
                    domain_list = []
                    
                    for cond in conditions_list:
                        if isinstance(cond, dict) and all(
                            k in cond for k in ["field", "operator", "value"]
                        ):
                            domain_list.append(
                                [cond["field"], cond["operator"], cond["value"]]
                            )

                # Validate list format and filter out invalid conditions
                if isinstance(domain_list, list):
                    valid_conditions = []
                    for cond in domain_list:
                        if isinstance(cond, str) and cond in ["&", "|", "!"]:
                            valid_conditions.append(cond)
                            continue

                        if (
                            isinstance(cond, list)
                            and len(cond) == 3
                            and isinstance(cond[0], str)
                            and isinstance(cond[1], str)
                        ):
                            valid_conditions.append(cond)

                    domain_list = valid_conditions

                # Update args with normalized domain
                normalized_args[0] = domain_list
                args = normalized_args

        # Report progress before executing the method
        report_progress(ctx, f"Executing {method} on {model}")
        
        # Execute the method on the Odoo model
        result = odoo.execute_method(model, method, *args, **kwargs)
        
        # Format result for JSON serialization if needed
        serializable_result = _make_serializable(result)
        
        # Return MCP-compliant response format
        return {
            "result": {
                "success": True,
                "data": serializable_result
            }
        }
    except Exception as e:
        # Return MCP-compliant error format
        return {
            "error": {
                "code": "method_execution_failed",
                "message": str(e)
            }
        }


def _make_serializable(value):
    """Helper function to convert non-serializable types to serializable ones"""
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    elif isinstance(value, (list, tuple)):
        return [_make_serializable(item) for item in value]
    elif isinstance(value, dict):
        return {k: _make_serializable(v) for k, v in value.items()}
    else:
        # Try to convert to string if not a basic type
        try:
            return str(value)
        except Exception:
            return "Unserializable value"
