"""
Shell execution tools for Odoo MCP via XML-RPC
"""

import json
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def execute_shell(
    ctx: Context,
    code: str,
    database: Optional[str] = None,
    local_vars: Optional[Dict[str, Any]] = None,
    use_environment: bool = True
):
    """
    Execute Python code in an Odoo shell environment

    This uses ir.actions.server to safely execute Python code with access to:
    - env: Odoo environment
    - model: Current model
    - time, datetime, dateutil, timezone: Time libraries
    - float_compare: Utility function
    - log: Logging function
    - UserError: Exception class
    - Command: x2many commands

    Parameters:
        code: Python code to execute
        database: Optional database name (uses current if not provided)
        local_vars: Optional dictionary of local variables
        use_environment: Whether to include Odoo environment variables

    Returns:
        Execution result or error
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, "Preparing shell execution environment")

        # Create a server action for code execution
        # First, get the base model ID
        model_search = odoo.execute_method(
            'ir.model',
            'search',
            [['model', '=', 'res.users']],
            limit=1
        )

        if not model_search:
            return {
                "error": {
                    "code": "model_not_found",
                    "message": "Could not find res.users model for shell execution"
                }
            }

        model_id = model_search[0]

        # Prepare the code with proper context
        # Properly indent user code for the try block
        indented_code = '\n'.join('    ' + line for line in code.split('\n'))

        wrapped_code = f"""
# Shell execution context - no imports allowed in safe_eval
result = ""
output = ""
success = False

try:
    # User code starts here
{indented_code}
    # User code ends here
    success = True

except Exception as e:
    result = ""
    output = str(e) if e else "Unknown error"
    success = False

# Return results - same pattern as SQL tool
action = {{
    'type': 'ir.actions.act_window_close',
    'tag': 'shell_result',
    'params': {{
        'result': result,
        'output': output,
        'success': success
    }}
}}
"""

        # Add local variables if provided
        if local_vars:
            var_setup = "\n".join([f"{k} = {repr(v)}" for k, v in local_vars.items()])
            wrapped_code = var_setup + "\n" + wrapped_code

        report_progress(ctx, "Creating server action for code execution")

        # Create the server action
        action_id = odoo.execute_method(
            'ir.actions.server',
            'create',
            {
                'name': 'MCP Shell Execution',
                'model_id': model_id,
                'state': 'code',
                'code': wrapped_code
            }
        )

        report_progress(ctx, "Executing code")

        # Run the action - just call run on the server action
        # The server action will run with default context
        result = odoo.execute_method(
            'ir.actions.server',
            'run',
            [action_id]
        )

        # Clean up - delete the temporary action
        odoo.execute_method(
            'ir.actions.server',
            'unlink',
            [action_id]
        )

        # Process the result
        if isinstance(result, dict) and result.get('tag') == 'shell_result':
            params = result.get('params', {})
            return {
                "result": {
                    "success": params.get('success', False),
                    "result": params.get('result', ""),
                    "output": params.get('output', ''),
                    "type": "shell_execution"
                }
            }
        else:
            # Ensure result is serializable
            safe_result = result if result is not None else ""
            if hasattr(safe_result, '__dict__') or isinstance(safe_result, (list, tuple, dict)):
                safe_result = str(safe_result)

            return {
                "result": {
                    "success": True,
                    "result": safe_result,
                    "output": "",
                    "type": "shell_execution"
                }
            }

    except Exception as e:
        return {
            "error": {
                "code": "shell_execution_failed",
                "message": str(e)
            }
        }


def execute_shell_multi(
    ctx: Context,
    scripts: List[Dict[str, Any]],
    stop_on_error: bool = True
):
    """
    Execute multiple Python scripts in sequence

    Parameters:
        scripts: List of script configurations with 'code' and optional 'local_vars'
        stop_on_error: Stop execution if a script fails

    Returns:
        List of execution results
    """
    results = []

    try:
        report_progress(ctx, f"Executing {len(scripts)} shell scripts")

        for i, script in enumerate(scripts):
            report_progress(ctx, f"Executing script {i+1}/{len(scripts)}")

            code = script.get('code', '')
            local_vars = script.get('local_vars', {})

            result = execute_shell(ctx, code, local_vars=local_vars)

            results.append({
                'index': i,
                'success': not result.get('error'),
                'result': result
            })

            # Check if we should stop on error
            if stop_on_error and result.get('error'):
                break

        return {
            "result": {
                "success": all(r['success'] for r in results),
                "results": results,
                "executed": len(results),
                "total": len(scripts)
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "multi_shell_execution_failed",
                "message": str(e)
            }
        }


def execute_shell_code(
    ctx: Context,
    code: str,
    database: Optional[str] = None,
    local_vars: Optional[Dict[str, Any]] = None,
    use_environment: bool = True
):
    """
    Execute Python code in Odoo shell environment (alias for execute_shell)

    Parameters:
        code: Python code to execute
        database: Optional database name
        local_vars: Optional local variables
        use_environment: Include Odoo environment

    Returns:
        Execution result
    """
    return execute_shell(ctx, code, database, local_vars, use_environment)