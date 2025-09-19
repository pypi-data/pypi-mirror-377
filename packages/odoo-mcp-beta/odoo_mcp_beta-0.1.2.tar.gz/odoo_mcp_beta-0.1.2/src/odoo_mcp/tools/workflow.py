"""
Workflow and state management tools for Odoo MCP
"""

from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def get_record_state(
    ctx: Context,
    model: str,
    record_ids: List[int]
):
    """
    Get the current state of records
    
    Parameters:
        model: Model name
        record_ids: List of record IDs
    
    Returns:
        Current state information
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Getting state for {len(record_ids)} records in {model}")
        
        # Common state field names in Odoo
        state_fields = ["state", "status", "stage_id"]
        
        # Get model fields to find state field
        fields = odoo.get_model_fields(model)
        available_state_fields = [f for f in state_fields if f in fields]
        
        if not available_state_fields:
            return {
                "error": {
                    "code": "no_state_field",
                    "message": f"Model {model} does not have a state field"
                }
            }
        
        # Read state information
        records = odoo.read_records(model, record_ids, available_state_fields)
        
        # Format results
        states = []
        for record in records:
            state_info = {"id": record["id"]}
            for field in available_state_fields:
                if field in record:
                    value = record[field]
                    if isinstance(value, (list, tuple)) and len(value) == 2:
                        # Many2one field (like stage_id)
                        state_info[field] = {"id": value[0], "name": value[1]}
                    else:
                        state_info[field] = value
            states.append(state_info)
        
        return {
            "result": {
                "success": True,
                "model": model,
                "states": states,
                "state_fields": available_state_fields
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "get_state_failed",
                "message": str(e)
            }
        }


def execute_workflow_action(
    ctx: Context,
    model: str,
    record_ids: List[int],
    action: str
):
    """
    Execute a workflow action on records
    
    Parameters:
        model: Model name
        record_ids: List of record IDs
        action: Action name (e.g., 'action_confirm', 'action_cancel')
    
    Returns:
        Action execution results
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Executing {action} on {len(record_ids)} records in {model}")
        
        results = []
        errors = []
        
        for i, record_id in enumerate(record_ids):
            report_progress(ctx, f"Processing record {i+1}/{len(record_ids)}", 
                           percent=int((i+1) * 100 / len(record_ids)))
            
            try:
                # Execute the action
                result = odoo.execute_method(model, action, [record_id])
                results.append({
                    "id": record_id,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "id": record_id,
                    "success": False,
                    "error": str(e)
                })
                errors.append({"record_id": record_id, "error": str(e)})
        
        return {
            "result": {
                "success": len(errors) == 0,
                "model": model,
                "action": action,
                "results": results,
                "processed": len(record_ids),
                "succeeded": len(record_ids) - len(errors),
                "failed": len(errors)
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "workflow_action_failed",
                "message": str(e)
            }
        }


def get_available_actions(
    ctx: Context,
    model: str,
    record_id: int
):
    """
    Get available workflow actions for a record
    
    Parameters:
        model: Model name
        record_id: Record ID
    
    Returns:
        Available actions based on current state
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Getting available actions for {model} record {record_id}")
        
        # Common workflow actions by model
        model_actions = {
            "sale.order": {
                "draft": ["action_confirm", "action_cancel"],
                "sent": ["action_confirm", "action_cancel"],
                "sale": ["action_done", "action_cancel"],
                "done": [],
                "cancel": ["action_draft"]
            },
            "purchase.order": {
                "draft": ["button_confirm", "button_cancel"],
                "sent": ["button_confirm", "button_cancel"],
                "to approve": ["button_approve", "button_cancel"],
                "purchase": ["button_done", "button_cancel"],
                "done": [],
                "cancel": ["button_draft"]
            },
            "account.move": {
                "draft": ["action_post", "button_cancel"],
                "posted": ["button_draft", "button_cancel"],
                "cancel": ["button_draft"]
            },
            "stock.picking": {
                "draft": ["action_confirm", "action_cancel"],
                "waiting": ["action_assign", "action_cancel"],
                "confirmed": ["action_assign", "action_cancel"],
                "assigned": ["button_validate", "action_cancel"],
                "done": [],
                "cancel": []
            },
            "mrp.production": {
                "draft": ["action_confirm", "action_cancel"],
                "confirmed": ["button_plan", "action_cancel"],
                "planned": ["button_produce", "action_cancel"],
                "progress": ["button_mark_done", "action_cancel"],
                "to_close": ["button_mark_done", "action_cancel"],
                "done": [],
                "cancel": []
            },
            "project.task": {
                "01_in_progress": ["action_fsm_validate"],
                "02_changes_requested": ["action_fsm_validate"],
                "03_approved": [],
                "04_waiting_normal": [],
                "1_done": [],
                "1_canceled": []
            }
        }
        
        # Get current state
        state_fields = ["state", "status"]
        fields = odoo.get_model_fields(model)
        state_field = next((f for f in state_fields if f in fields), None)
        
        available_actions = []
        
        if state_field:
            # Get current state
            record = odoo.read_records(model, [record_id], [state_field])
            if record:
                current_state = record[0].get(state_field)
                
                # Get actions based on model and state
                if model in model_actions:
                    state_actions = model_actions[model].get(current_state, [])
                    for action in state_actions:
                        available_actions.append({
                            "name": action,
                            "type": "workflow",
                            "from_state": current_state
                        })
        
        # Try to detect actions from view buttons
        try:
            # Get form view to find buttons
            view_result = odoo.execute_method(
                model,
                "fields_view_get",
                view_type="form"
            )
            
            # Parse arch to find button actions (simplified)
            import xml.etree.ElementTree as ET
            if "arch" in view_result:
                try:
                    root = ET.fromstring(view_result["arch"])
                    buttons = root.findall(".//button[@name]")
                    for button in buttons:
                        action_name = button.get("name")
                        if action_name and action_name not in [a["name"] for a in available_actions]:
                            available_actions.append({
                                "name": action_name,
                                "type": "button",
                                "string": button.get("string", action_name)
                            })
                except:
                    pass  # XML parsing failed
        except:
            pass  # View not available
        
        return {
            "result": {
                "success": True,
                "model": model,
                "record_id": record_id,
                "current_state": current_state if state_field else None,
                "available_actions": available_actions
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "get_actions_failed",
                "message": str(e)
            }
        }


def bulk_state_transition(
    ctx: Context,
    model: str,
    transitions: List[Dict[str, Any]]
):
    """
    Perform bulk state transitions
    
    Parameters:
        model: Model name
        transitions: List of transitions with 'ids', 'from_state', 'to_state', 'action'
    
    Returns:
        Transition results
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Performing bulk state transitions in {model}")
        
        results = []
        
        for i, transition in enumerate(transitions):
            report_progress(ctx, f"Processing transition {i+1}/{len(transitions)}", 
                           percent=int((i+1) * 100 / len(transitions)))
            
            record_ids = transition.get("ids", [])
            action = transition.get("action")
            from_state = transition.get("from_state")
            to_state = transition.get("to_state")
            
            # Verify current state if specified
            if from_state:
                state_field = "state"  # Assume standard field
                current_records = odoo.read_records(model, record_ids, [state_field])
                valid_ids = [
                    r["id"] for r in current_records 
                    if r.get(state_field) == from_state
                ]
            else:
                valid_ids = record_ids
            
            # Execute action on valid records
            if valid_ids and action:
                try:
                    for record_id in valid_ids:
                        odoo.execute_method(model, action, [record_id])
                    
                    results.append({
                        "transition": i,
                        "success": True,
                        "processed_ids": valid_ids,
                        "count": len(valid_ids)
                    })
                except Exception as e:
                    results.append({
                        "transition": i,
                        "success": False,
                        "error": str(e)
                    })
            else:
                results.append({
                    "transition": i,
                    "success": False,
                    "error": "No valid records or action not specified"
                })
        
        succeeded = sum(1 for r in results if r.get("success"))
        
        return {
            "result": {
                "success": succeeded == len(transitions),
                "results": results,
                "total_transitions": len(transitions),
                "succeeded": succeeded,
                "failed": len(transitions) - succeeded
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "bulk_transition_failed",
                "message": str(e)
            }
        }


def get_workflow_history(
    ctx: Context,
    model: str,
    record_id: int,
    limit: int = 20
):
    """
    Get workflow transition history for a record
    
    Parameters:
        model: Model name
        record_id: Record ID
        limit: Maximum history entries
    
    Returns:
        Workflow history
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Getting workflow history for {model} record {record_id}")
        
        history = []
        
        # Try to get history from mail.message (workflow changes are often logged there)
        try:
            messages = odoo.search_read(
                "mail.message",
                [["model", "=", model], ["res_id", "=", record_id]],
                ["date", "body", "subtype_id", "tracking_value_ids"],
                limit=limit,
                order="date desc"
            )
            
            for message in messages:
                # Check if this is a state change message
                if message.get("tracking_value_ids"):
                    tracking_values = odoo.read_records(
                        "mail.tracking.value",
                        message["tracking_value_ids"],
                        ["field", "old_value_char", "new_value_char"]
                    )
                    
                    for tracking in tracking_values:
                        if tracking.get("field") == "state":
                            history.append({
                                "date": message["date"],
                                "type": "state_change",
                                "from_state": tracking.get("old_value_char"),
                                "to_state": tracking.get("new_value_char"),
                                "message_id": message["id"]
                            })
        except:
            pass  # Mail module might not be installed
        
        # Get basic record info
        record = odoo.read_records(model, [record_id], ["create_date", "write_date", "state"])
        if record:
            record_data = record[0]
            
            return {
                "result": {
                    "success": True,
                    "model": model,
                    "record_id": record_id,
                    "current_state": record_data.get("state"),
                    "created": record_data.get("create_date"),
                    "last_modified": record_data.get("write_date"),
                    "history": history,
                    "history_count": len(history)
                }
            }
        else:
            return {
                "error": {
                    "code": "record_not_found",
                    "message": f"Record {record_id} not found in {model}"
                }
            }
            
    except Exception as e:
        return {
            "error": {
                "code": "history_failed",
                "message": str(e)
            }
        }