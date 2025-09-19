"""
System administration tools for Odoo MCP
"""

from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def get_system_parameters(
    ctx: Context,
    key: Optional[str] = None
):
    """
    Get system parameters from ir.config_parameter

    Parameters:
        key: Specific parameter key or None for all

    Returns:
        System parameters
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        if key:
            # Get specific parameter
            value = odoo.execute_method(
                'ir.config_parameter',
                'get_param',
                key
            )
            return {
                "result": {
                    "success": True,
                    "key": key,
                    "value": value
                }
            }
        else:
            # Get all parameters
            params = odoo.execute_method(
                'ir.config_parameter',
                'search_read',
                [],
                ['key', 'value']
            )
            return {
                "result": {
                    "success": True,
                    "parameters": params
                }
            }

    except Exception as e:
        return {
            "error": {
                "code": "get_system_parameters_failed",
                "message": str(e)
            }
        }


def set_system_parameter(
    ctx: Context,
    key: str,
    value: str
):
    """
    Set a system parameter

    Parameters:
        key: Parameter key
        value: Parameter value

    Returns:
        Success status
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        odoo.execute_method(
            'ir.config_parameter',
            'set_param',
            key,
            value
        )

        return {
            "result": {
                "success": True,
                "key": key,
                "value": value
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "set_system_parameter_failed",
                "message": str(e)
            }
        }


def get_installed_modules(
    ctx: Context,
    include_details: bool = False
):
    """
    Get list of installed modules

    Parameters:
        include_details: Include module details

    Returns:
        List of installed modules
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        domain = [['state', '=', 'installed']]
        fields = ['name', 'display_name', 'latest_version']

        if include_details:
            fields.extend(['summary', 'author', 'website', 'category_id', 'depends'])

        modules = odoo.execute_method(
            'ir.module.module',
            'search_read',
            domain,
            fields
        )

        return {
            "result": {
                "success": True,
                "modules": modules,
                "count": len(modules)
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "get_installed_modules_failed",
                "message": str(e)
            }
        }


def install_module(
    ctx: Context,
    module_name: str
):
    """
    Install an Odoo module

    Parameters:
        module_name: Name of the module to install

    Returns:
        Installation result
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Installing module {module_name}")

        # Find the module
        module_id = odoo.execute_method(
            'ir.module.module',
            'search',
            [['name', '=', module_name]],
            limit=1
        )

        if not module_id:
            return {
                "error": {
                    "code": "module_not_found",
                    "message": f"Module {module_name} not found"
                }
            }

        # Install the module
        odoo.execute_method(
            'ir.module.module',
            'button_immediate_install',
            module_id
        )

        return {
            "result": {
                "success": True,
                "module": module_name,
                "action": "installed"
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "install_module_failed",
                "message": str(e)
            }
        }


def uninstall_module(
    ctx: Context,
    module_name: str
):
    """
    Uninstall an Odoo module

    Parameters:
        module_name: Name of the module to uninstall

    Returns:
        Uninstallation result
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Uninstalling module {module_name}")

        # Find the module
        module_id = odoo.execute_method(
            'ir.module.module',
            'search',
            [['name', '=', module_name], ['state', '=', 'installed']],
            limit=1
        )

        if not module_id:
            return {
                "error": {
                    "code": "module_not_installed",
                    "message": f"Module {module_name} is not installed"
                }
            }

        # Uninstall the module
        odoo.execute_method(
            'ir.module.module',
            'button_immediate_uninstall',
            module_id
        )

        return {
            "result": {
                "success": True,
                "module": module_name,
                "action": "uninstalled"
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "uninstall_module_failed",
                "message": str(e)
            }
        }


def update_module_list(
    ctx: Context
):
    """
    Update the list of available modules

    Returns:
        Update result
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, "Updating module list")

        # This updates the module list from the file system
        result = odoo.execute_method(
            'ir.module.module',
            'update_list'
        )

        return {
            "result": {
                "success": True,
                "message": "Module list updated",
                "result": result
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "update_module_list_failed",
                "message": str(e)
            }
        }


def get_system_logs(
    ctx: Context,
    level: Optional[str] = None,
    limit: int = 100,
    model: Optional[str] = None
):
    """
    Get system logs from ir.logging

    Parameters:
        level: Log level filter (ERROR, WARNING, INFO)
        limit: Number of logs to return
        model: Filter by model

    Returns:
        System logs
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        domain = []

        if level:
            domain.append(['level', '=', level])

        if model:
            domain.append(['name', '=', model])

        logs = odoo.execute_method(
            'ir.logging',
            'search_read',
            domain,
            ['create_date', 'create_uid', 'name', 'type', 'level', 'message', 'path', 'line', 'func'],
            limit=limit,
            order='create_date desc'
        )

        return {
            "result": {
                "success": True,
                "logs": logs,
                "count": len(logs)
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "get_system_logs_failed",
                "message": str(e)
            }
        }


def clear_cache(
    ctx: Context
):
    """
    Clear Odoo caches

    Returns:
        Cache clear result
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, "Clearing Odoo caches")

        # Clear the cache using the env
        result = odoo.execute_method(
            'res.users',
            'clear_caches'
        )

        return {
            "result": {
                "success": True,
                "message": "Caches cleared successfully"
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "clear_cache_failed",
                "message": str(e)
            }
        }


def get_server_info(
    ctx: Context
):
    """
    Get Odoo server information

    Returns:
        Server information
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        # Get various server information
        info = {}

        # Get database size
        try:
            db_size_query = "SELECT pg_database_size(current_database())"
            size_result = odoo.execute_method(
                'ir.model',
                'search_read',
                [['model', '=', 'ir.model']],
                ['id'],
                limit=1
            )
            if size_result:
                info['database_name'] = odoo.db
        except:
            pass

        # Get user count
        try:
            user_count = odoo.execute_method(
                'res.users',
                'search_count',
                []
            )
            info['user_count'] = user_count
        except:
            pass

        # Get company info
        try:
            company = odoo.execute_method(
                'res.company',
                'search_read',
                [],
                ['name', 'email', 'phone'],
                limit=1
            )
            if company:
                info['company'] = company[0]
        except:
            pass

        # Get module count
        try:
            module_count = odoo.execute_method(
                'ir.module.module',
                'search_count',
                [['state', '=', 'installed']]
            )
            info['installed_modules'] = module_count
        except:
            pass

        return {
            "result": {
                "success": True,
                "server_info": info
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "get_server_info_failed",
                "message": str(e)
            }
        }