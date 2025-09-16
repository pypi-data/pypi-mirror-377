"""
Batch operations tools for Odoo MCP
"""

from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def batch_execute(
    ctx: Context,
    operations: List[Dict[str, Any]]
):
    """
    Execute multiple operations in a single call (batch processing)
    
    Parameters:
        operations: List of operations, each containing:
            - model: Model name
            - method: Method to execute
            - args: Positional arguments
            - kwargs: Keyword arguments
    
    Returns:
        List of results for each operation
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    results = []
    errors = []
    
    try:
        report_progress(ctx, f"Executing {len(operations)} operations in batch")
        
        for i, operation in enumerate(operations):
            report_progress(ctx, f"Processing operation {i+1}/{len(operations)} ({int((i+1) * 100 / len(operations))}%)")
            
            try:
                model = operation.get("model")
                method = operation.get("method")
                args = operation.get("args", [])
                kwargs = operation.get("kwargs", {})
                
                result = odoo.execute_method(model, method, *args, **kwargs)
                results.append({
                    "index": i,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e)
                })
                errors.append({"operation": i, "error": str(e)})
        
        return {
            "result": {
                "success": len(errors) == 0,
                "results": results,
                "total": len(operations),
                "succeeded": len(operations) - len(errors),
                "failed": len(errors),
                "errors": errors
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "batch_execution_failed",
                "message": str(e)
            }
        }


def batch_create(
    ctx: Context,
    model: str,
    records: List[Dict[str, Any]]
):
    """
    Create multiple records at once
    
    Parameters:
        model: Model name
        records: List of dictionaries with field values
    
    Returns:
        List of created record IDs
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Creating {len(records)} records in {model}")
        
        created_ids = []
        for i, record_data in enumerate(records):
            report_progress(ctx, f"Creating record {i+1}/{len(records)} ({int((i+1) * 100 / len(records))}%)")
            
            record_id = odoo.execute_method(model, "create", record_data)
            created_ids.append(record_id)
        
        return {
            "result": {
                "success": True,
                "created_ids": created_ids,
                "count": len(created_ids)
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "batch_create_failed",
                "message": str(e)
            }
        }


def batch_update(
    ctx: Context,
    model: str,
    updates: List[Dict[str, Any]]
):
    """
    Update multiple records with different values
    
    Parameters:
        model: Model name
        updates: List of dicts with 'id' and 'values' keys
    
    Returns:
        Update results
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Updating {len(updates)} records in {model}")
        
        results = []
        for i, update in enumerate(updates):
            report_progress(ctx, f"Updating record {i+1}/{len(updates)} ({int((i+1) * 100 / len(updates))}%)")
            
            record_id = update.get("id")
            values = update.get("values", {})
            
            try:
                odoo.execute_method(model, "write", [record_id], values)
                results.append({"id": record_id, "success": True})
            except Exception as e:
                results.append({"id": record_id, "success": False, "error": str(e)})
        
        succeeded = sum(1 for r in results if r["success"])
        return {
            "result": {
                "success": succeeded == len(updates),
                "results": results,
                "updated": succeeded,
                "failed": len(updates) - succeeded
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "batch_update_failed",
                "message": str(e)
            }
        }


def batch_delete(
    ctx: Context,
    model: str,
    ids: List[int]
):
    """
    Delete multiple records
    
    Parameters:
        model: Model name
        ids: List of record IDs to delete
    
    Returns:
        Deletion result
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Deleting {len(ids)} records from {model}")
        
        # Odoo's unlink method can delete multiple records at once
        result = odoo.execute_method(model, "unlink", ids)
        
        return {
            "result": {
                "success": True,
                "deleted_count": len(ids),
                "deleted_ids": ids
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "batch_delete_failed",
                "message": str(e)
            }
        }


def batch_copy(
    ctx: Context,
    model: str,
    ids: List[int],
    default_values: Optional[Dict[str, Any]] = None
):
    """
    Copy/duplicate records with optional default values
    
    Parameters:
        model: Model name
        ids: List of record IDs to copy
        default_values: Default values for new records
    
    Returns:
        List of new record IDs
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Copying {len(ids)} records from {model}")
        
        new_ids = []
        for i, record_id in enumerate(ids):
            report_progress(ctx, f"Copying record {i+1}/{len(ids)} ({int((i+1) * 100 / len(ids))}%)")
            
            new_id = odoo.execute_method(model, "copy", record_id, default_values or {})
            new_ids.append(new_id)
        
        return {
            "result": {
                "success": True,
                "original_ids": ids,
                "new_ids": new_ids,
                "count": len(new_ids)
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "batch_copy_failed",
                "message": str(e)
            }
        }