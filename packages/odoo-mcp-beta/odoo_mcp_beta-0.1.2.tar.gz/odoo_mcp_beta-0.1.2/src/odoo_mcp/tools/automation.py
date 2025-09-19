"""
Workflow and automation tools for Odoo MCP
"""

from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def create_server_action(
    ctx: Context,
    name: str,
    model_name: str,
    action_type: str = "code",
    code: Optional[str] = None,
    sequence: int = 10
):
    """
    Create a server action for automation

    Parameters:
        name: Action name
        model_name: Model to attach action to
        action_type: Type of action (code, object_create, object_write, multi)
        code: Python code for 'code' type actions
        sequence: Execution sequence

    Returns:
        Created action ID
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Creating server action: {name}")

        # Get model ID
        model_id = odoo.execute_method(
            'ir.model',
            'search',
            [['model', '=', model_name]],
            limit=1
        )

        if not model_id:
            return {
                "error": {
                    "code": "model_not_found",
                    "message": f"Model {model_name} not found"
                }
            }

        # Create server action
        action_data = {
            'name': name,
            'model_id': model_id[0],
            'state': action_type,
            'sequence': sequence
        }

        if code and action_type == 'code':
            action_data['code'] = code

        action_id = odoo.execute_method(
            'ir.actions.server',
            'create',
            action_data
        )

        return {
            "result": {
                "success": True,
                "action_id": action_id,
                "name": name
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "create_server_action_failed",
                "message": str(e)
            }
        }


def execute_server_action(
    ctx: Context,
    action_id: int,
    record_ids: Optional[List[int]] = None
):
    """
    Execute a server action

    Parameters:
        action_id: Server action ID
        record_ids: Optional record IDs to run action on

    Returns:
        Action execution result
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Executing server action {action_id}")

        # Get the action
        action = odoo.execute_method(
            'ir.actions.server',
            'read',
            [action_id],
            ['model_id', 'state', 'code']
        )

        if not action:
            return {
                "error": {
                    "code": "action_not_found",
                    "message": f"Server action {action_id} not found"
                }
            }

        # Execute the action - just call run on the server action
        result = odoo.execute_method(
            'ir.actions.server',
            'run',
            [action_id]
        )

        return {
            "result": {
                "success": True,
                "result": result,
                "action_id": action_id
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "execute_server_action_failed",
                "message": str(e)
            }
        }


def create_automated_action(
    ctx: Context,
    name: str,
    model_name: str,
    trigger: str,
    action_server_id: int,
    filter_domain: Optional[List] = None
):
    """
    Create an automated action (base.automation)

    Parameters:
        name: Automation name
        model_name: Model to trigger on
        trigger: Trigger type (on_create, on_write, on_unlink, on_time)
        action_server_id: Server action to execute
        filter_domain: Optional domain filter

    Returns:
        Created automation ID
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Creating automated action: {name}")

        # Get model ID
        model_id = odoo.execute_method(
            'ir.model',
            'search',
            [['model', '=', model_name]],
            limit=1
        )

        if not model_id:
            return {
                "error": {
                    "code": "model_not_found",
                    "message": f"Model {model_name} not found"
                }
            }

        # Create automated action
        automation_data = {
            'name': name,
            'model_id': model_id[0],
            'trigger': trigger,
            'action_server_id': action_server_id,
            'active': True
        }

        if filter_domain:
            automation_data['filter_domain'] = filter_domain

        automation_id = odoo.execute_method(
            'base.automation',
            'create',
            automation_data
        )

        return {
            "result": {
                "success": True,
                "automation_id": automation_id,
                "name": name
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "create_automated_action_failed",
                "message": str(e)
            }
        }


def trigger_workflow(
    ctx: Context,
    model: str,
    record_id: int,
    signal: str
):
    """
    Trigger a workflow signal on a record

    Parameters:
        model: Model name
        record_id: Record ID
        signal: Workflow signal name

    Returns:
        Workflow trigger result
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Triggering workflow signal '{signal}' on {model}:{record_id}")

        # Trigger workflow signal
        result = odoo.execute_method(
            model,
            'signal_workflow',
            [record_id],
            signal
        )

        return {
            "result": {
                "success": True,
                "model": model,
                "record_id": record_id,
                "signal": signal,
                "result": result
            }
        }

    except Exception as e:
        # Try alternative method for newer Odoo versions
        try:
            # In newer versions, workflows might be handled differently
            result = odoo.execute_method(
                model,
                signal,
                [record_id]
            )

            return {
                "result": {
                    "success": True,
                    "model": model,
                    "record_id": record_id,
                    "signal": signal,
                    "result": result
                }
            }
        except:
            return {
                "error": {
                    "code": "trigger_workflow_failed",
                    "message": str(e)
                }
            }


def create_activity(
    ctx: Context,
    model: str,
    record_id: int,
    activity_type: str,
    summary: str,
    user_id: Optional[int] = None,
    date_deadline: Optional[str] = None,
    note: Optional[str] = None
):
    """
    Create an activity for a record

    Parameters:
        model: Model name
        record_id: Record ID
        activity_type: Type of activity
        summary: Activity summary
        user_id: Assigned user ID
        date_deadline: Deadline date
        note: Activity note

    Returns:
        Created activity
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Creating activity for {model}:{record_id}")

        # Get model ID
        model_id = odoo.execute_method(
            'ir.model',
            'search',
            [['model', '=', model]],
            limit=1
        )

        if not model_id:
            return {
                "error": {
                    "code": "model_not_found",
                    "message": f"Model {model} not found"
                }
            }

        # Get activity type ID
        activity_type_id = odoo.execute_method(
            'mail.activity.type',
            'search',
            [['name', '=', activity_type]],
            limit=1
        )

        if not activity_type_id:
            # Create activity type if it doesn't exist
            activity_type_id = odoo.execute_method(
                'mail.activity.type',
                'create',
                {'name': activity_type, 'res_model': model}
            )
        else:
            activity_type_id = activity_type_id[0]

        # Create activity
        activity_data = {
            'res_model_id': model_id[0],
            'res_id': record_id,
            'activity_type_id': activity_type_id,
            'summary': summary
        }

        if user_id:
            activity_data['user_id'] = user_id
        if date_deadline:
            activity_data['date_deadline'] = date_deadline
        if note:
            activity_data['note'] = note

        activity_id = odoo.execute_method(
            'mail.activity',
            'create',
            activity_data
        )

        return {
            "result": {
                "success": True,
                "activity_id": activity_id,
                "summary": summary
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "create_activity_failed",
                "message": str(e)
            }
        }


def schedule_action(
    ctx: Context,
    name: str,
    model_name: str,
    method_name: str,
    cron_expression: str = "0 0 * * *",
    args: Optional[str] = "[]",
    active: bool = True
):
    """
    Schedule a recurring action (cron job)

    Parameters:
        name: Cron job name
        model_name: Model containing the method
        method_name: Method to call
        cron_expression: Cron expression or interval
        args: Method arguments as string
        active: Whether to activate immediately

    Returns:
        Created cron job
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Scheduling action: {name}")

        # Get model ID
        model_id = odoo.execute_method(
            'ir.model',
            'search',
            [['model', '=', model_name]],
            limit=1
        )

        if not model_id:
            return {
                "error": {
                    "code": "model_not_found",
                    "message": f"Model {model_name} not found"
                }
            }

        # Parse cron expression to Odoo format
        # Simple mapping - more sophisticated parsing might be needed
        interval_number = 1
        interval_type = 'days'

        if cron_expression == "0 * * * *":  # Hourly
            interval_type = 'hours'
        elif cron_expression == "*/5 * * * *":  # Every 5 minutes
            interval_number = 5
            interval_type = 'minutes'
        elif cron_expression == "0 0 * * 0":  # Weekly
            interval_type = 'weeks'
        elif cron_expression == "0 0 1 * *":  # Monthly
            interval_type = 'months'

        # Create cron job
        cron_data = {
            'name': name,
            'model_id': model_id[0],
            'state': 'code',
            'code': f"model.{method_name}({args})",
            'interval_number': interval_number,
            'interval_type': interval_type,
            'active': active,
            'user_id': 1  # Admin user
        }

        cron_id = odoo.execute_method(
            'ir.cron',
            'create',
            cron_data
        )

        return {
            "result": {
                "success": True,
                "cron_id": cron_id,
                "name": name
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "schedule_action_failed",
                "message": str(e)
            }
        }


def get_scheduled_actions(
    ctx: Context,
    active_only: bool = True
):
    """
    Get list of scheduled actions (cron jobs)

    Parameters:
        active_only: Only return active jobs

    Returns:
        List of scheduled actions
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        domain = []
        if active_only:
            domain.append(['active', '=', True])

        crons = odoo.execute_method(
            'ir.cron',
            'search_read',
            domain,
            ['name', 'model_id', 'interval_number', 'interval_type',
             'nextcall', 'active', 'state', 'code']
        )

        return {
            "result": {
                "success": True,
                "scheduled_actions": crons,
                "count": len(crons)
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "get_scheduled_actions_failed",
                "message": str(e)
            }
        }