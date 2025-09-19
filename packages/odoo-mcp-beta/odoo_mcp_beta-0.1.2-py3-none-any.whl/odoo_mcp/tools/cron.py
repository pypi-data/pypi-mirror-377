"""
Scheduled actions (cron) management tools for Odoo MCP
"""

from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def list_cron_jobs(
    ctx: Context,
    active_only: bool = True,
    limit: int = 50
):
    """
    List scheduled cron jobs
    
    Parameters:
        active_only: Only show active jobs
        limit: Maximum jobs to return
    
    Returns:
        List of cron jobs
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, "Fetching scheduled jobs")
        
        domain = []
        if active_only:
            domain.append(('active', '=', True))
        
        crons = odoo.execute_method(
            'ir.cron', 'search_read',
            domain,
            ['cron_name', 'ir_actions_server_id', 'interval_number', 
             'interval_type', 'nextcall', 'active', 'numbercall', 'user_id'],
            0, limit
        )
        
        return {
            "success": True,
            "count": len(crons),
            "cron_jobs": crons
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_cron_details(
    ctx: Context,
    cron_id: int
):
    """
    Get detailed information about a cron job
    
    Parameters:
        cron_id: Cron job ID
    
    Returns:
        Detailed cron job information
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Fetching details for cron job {cron_id}")
        
        cron = odoo.execute_method(
            'ir.cron', 'read',
            [cron_id],
            ['cron_name', 'ir_actions_server_id', 'interval_number',
             'interval_type', 'nextcall', 'active', 'numbercall',
             'doall', 'priority', 'user_id', 'lastcall']
        )
        
        if not cron:
            return {
                "success": False,
                "error": f"Cron job {cron_id} not found"
            }
        
        return {
            "success": True,
            "cron_job": cron[0]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def execute_cron_job(
    ctx: Context,
    cron_id: int
):
    """
    Manually execute a cron job
    
    Parameters:
        cron_id: Cron job ID to execute
    
    Returns:
        Execution result
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Executing cron job {cron_id}")
        
        # Method to manually trigger cron
        odoo.execute_method('ir.cron', 'method_direct_trigger', [cron_id])
        
        return {
            "success": True,
            "message": f"Cron job {cron_id} executed successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def toggle_cron_job(
    ctx: Context,
    cron_id: int,
    active: bool
):
    """
    Enable or disable a cron job
    
    Parameters:
        cron_id: Cron job ID
        active: True to enable, False to disable
    
    Returns:
        Update result
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        if hasattr(ctx, 'progress'):
            action = "Enabling" if active else "Disabling"
            ctx.progress(f"{action} cron job {cron_id}")
        
        odoo.execute_method(
            'ir.cron', 'write',
            [cron_id], {'active': active}
        )
        
        status = "enabled" if active else "disabled"
        return {
            "success": True,
            "message": f"Cron job {cron_id} {status} successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def create_cron_job(
    ctx: Context,
    name: str,
    model: str,
    code: str,
    interval_number: int = 1,
    interval_type: str = 'days',
    active: bool = True,
    user_id: Optional[int] = None
):
    """
    Create a new cron job
    
    Parameters:
        name: Job name
        model: Model to run on
        code: Python code to execute
        interval_number: Interval frequency
        interval_type: 'minutes', 'hours', 'days', 'weeks', 'months'
        active: Whether to activate immediately
        user_id: User ID to run the cron as (defaults to current user)
    
    Returns:
        Created cron job ID
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Creating cron job: {name}")
        
        # First create the server action
        action_data = {
            'name': name,
            'model_id': odoo.execute_method(
                'ir.model', 'search',
                [('model', '=', model)], 0, 1
            )[0] if model else False,
            'state': 'code',
            'code': code,
            'usage': 'ir_cron'
        }
        
        action_id = odoo.execute_method('ir.actions.server', 'create', action_data)
        
        # Then create the cron with the server action
        cron_data = {
            'ir_actions_server_id': action_id,
            'interval_number': interval_number,
            'interval_type': interval_type,
            'numbercall': -1,  # Unlimited calls
            'active': active
        }
        
        if user_id:
            cron_data['user_id'] = user_id
        
        cron_id = odoo.execute_method('ir.cron', 'create', cron_data)
        
        return {
            "success": True,
            "cron_id": cron_id,
            "message": f"Cron job '{name}' created successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }