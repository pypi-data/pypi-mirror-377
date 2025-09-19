"""
Real-time operations support for Odoo MCP
"""

from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def notify_channel(
    ctx: Context,
    channel: str,
    message: str
):
    """
    Send a notification to a PostgreSQL channel

    Parameters:
        channel: Channel name
        message: Notification message

    Returns:
        Notification result
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Sending notification to channel: {channel}")

        # Use SQL to send NOTIFY
        from .sql import execute_sql

        query = f"NOTIFY {channel}, %s"
        result = execute_sql(
            ctx,
            query,
            [message],
            fetch_mode="none",
            commit=True
        )

        if result.get('error'):
            return result

        return {
            "result": {
                "success": True,
                "channel": channel,
                "message": message
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "notify_channel_failed",
                "message": str(e)
            }
        }


def trigger_cron(
    ctx: Context,
    cron_id: Optional[int] = None,
    cron_name: Optional[str] = None
):
    """
    Manually trigger a cron job

    Parameters:
        cron_id: Cron job ID
        cron_name: Cron job name (if ID not provided)

    Returns:
        Trigger result
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        if not cron_id and cron_name:
            # Find cron by name
            cron_ids = odoo.execute_method(
                'ir.cron',
                'search',
                [['name', '=', cron_name]],
                {'limit': 1}
            )
            if cron_ids:
                cron_id = cron_ids[0]
            else:
                return {
                    "error": {
                        "code": "cron_not_found",
                        "message": f"Cron job '{cron_name}' not found"
                    }
                }

        if not cron_id:
            # Trigger all crons
            report_progress(ctx, "Triggering cron processing")

            # Send notification to trigger cron processing
            return notify_channel(ctx, "cron_trigger", "manual")

        else:
            # Trigger specific cron
            report_progress(ctx, f"Triggering cron job {cron_id}")

            # Run the cron method directly
            odoo.execute_method(
                'ir.cron',
                'method_direct_trigger',
                [cron_id]
            )

            return {
                "result": {
                    "success": True,
                    "cron_id": cron_id,
                    "action": "triggered"
                }
            }

    except Exception as e:
        # Try alternative approach
        try:
            # Get cron details and execute its code
            cron = odoo.execute_method(
                'ir.cron',
                'read',
                [cron_id],
                ['model_id', 'code', 'state']
            )

            if cron and cron[0]['state'] == 'code':
                # Execute the cron code via server action
                from .shell import execute_shell
                result = execute_shell(ctx, cron[0]['code'])

                return {
                    "result": {
                        "success": True,
                        "cron_id": cron_id,
                        "action": "executed",
                        "result": result
                    }
                }
            else:
                return {
                    "error": {
                        "code": "cron_trigger_failed",
                        "message": "Could not execute cron job"
                    }
                }

        except:
            return {
                "error": {
                    "code": "trigger_cron_failed",
                    "message": str(e)
                }
            }


def clear_cache(
    ctx: Context,
    model: Optional[str] = None
):
    """
    Clear ORM caches

    Parameters:
        model: Specific model cache to clear (None for all)

    Returns:
        Cache clear result
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, "Clearing ORM caches")

        # Clear caches
        odoo.execute_method(
            'res.users',
            'clear_caches'
        )

        # Also invalidate cache for specific model if provided
        if model:
            try:
                odoo.execute_method(
                    model,
                    'invalidate_cache',
                    None,
                    None
                )
            except:
                pass  # Not all models have invalidate_cache

        return {
            "result": {
                "success": True,
                "message": f"Cache cleared for {'all models' if not model else model}"
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "clear_cache_failed",
                "message": str(e)
            }
        }


def signal_registry_change(
    ctx: Context,
    database: Optional[str] = None
):
    """
    Signal registry changes to reload

    Parameters:
        database: Database name

    Returns:
        Signal result
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, "Signaling registry changes")

        # Signal changes via SQL
        from .sql import execute_sql

        # This triggers registry reload
        result = execute_sql(
            ctx,
            "SELECT nextval('base_registry_signaling')",
            fetch_mode="one",
            commit=True
        )

        if result.get('error'):
            # Try alternative method
            odoo.execute_method(
                'res.users',
                'clear_caches'
            )

        return {
            "result": {
                "success": True,
                "message": "Registry signaled for reload"
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "signal_registry_failed",
                "message": str(e)
            }
        }


def get_active_users(
    ctx: Context,
    minutes: int = 15
):
    """
    Get currently active users

    Parameters:
        minutes: Consider users active if seen within this many minutes

    Returns:
        Active users
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        # Query for active sessions
        from .sql import execute_sql

        query = """
            SELECT
                u.id,
                u.login,
                p.name as partner_name,
                MAX(s.date_login) as last_login
            FROM res_users u
            JOIN res_partner p ON u.partner_id = p.id
            LEFT JOIN res_users_log s ON u.id = s.user_id
            WHERE s.date_login > (NOW() - INTERVAL '%s minutes')
            GROUP BY u.id, u.login, p.name
            ORDER BY last_login DESC
        """

        result = execute_sql(
            ctx,
            query,
            [minutes],
            dict_result=True
        )

        if result.get('error'):
            # Fallback to simpler query
            users = odoo.execute_method(
                'res.users',
                'search_read',
                [],
                ['login', 'name', 'last_login']
            )
            return {
                "result": {
                    "success": True,
                    "active_users": users[:10]  # Return recent users
                }
            }

        return {
            "result": {
                "success": True,
                "active_users": result.get('result', {}).get('data', []),
                "timeframe_minutes": minutes
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "get_active_users_failed",
                "message": str(e)
            }
        }


def broadcast_message(
    ctx: Context,
    message: str,
    title: Optional[str] = None,
    sticky: bool = False,
    type: str = "info"
):
    """
    Broadcast a message to all users

    Parameters:
        message: Message content
        title: Message title
        sticky: Keep message visible
        type: Message type (info, warning, danger)

    Returns:
        Broadcast result
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, "Broadcasting message to users")

        # Create a notification using the bus
        notification_data = {
            'message': message,
            'title': title or 'System Message',
            'sticky': sticky,
            'type': type
        }

        # Try to use bus.bus for notifications
        try:
            odoo.execute_method(
                'bus.bus',
                'sendmany',
                [[['broadcast', 'notification', notification_data]]]
            )
        except:
            # Fallback to mail message
            odoo.execute_method(
                'mail.message',
                'create',
                {
                    'subject': title or 'System Message',
                    'body': message,
                    'message_type': 'notification',
                    'subtype_id': 1  # Note subtype
                }
            )

        return {
            "result": {
                "success": True,
                "message": message,
                "broadcast": True
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "broadcast_message_failed",
                "message": str(e)
            }
        }


def monitor_locks(
    ctx: Context
):
    """
    Monitor database locks

    Returns:
        Current database locks
    """
    try:
        from .sql import execute_sql

        query = """
            SELECT
                l.pid,
                l.mode,
                l.granted,
                d.datname,
                l.relation::regclass,
                a.usename,
                a.application_name,
                a.client_addr,
                a.query_start,
                a.state,
                substring(a.query, 1, 100) as query_snippet
            FROM pg_locks l
            JOIN pg_database d ON l.database = d.oid
            JOIN pg_stat_activity a ON l.pid = a.pid
            WHERE l.relation IS NOT NULL
            ORDER BY l.granted, l.pid
        """

        result = execute_sql(ctx, query, dict_result=True)

        if result.get('error'):
            return result

        locks = result.get('result', {}).get('data', [])

        return {
            "result": {
                "success": True,
                "locks": locks,
                "count": len(locks)
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "monitor_locks_failed",
                "message": str(e)
            }
        }


def get_database_stats(
    ctx: Context
):
    """
    Get database performance statistics

    Returns:
        Database statistics
    """
    try:
        from .sql import execute_sql

        # Get database size
        size_query = """
            SELECT
                pg_database_size(current_database()) as size_bytes,
                pg_size_pretty(pg_database_size(current_database())) as size_pretty
        """
        size_result = execute_sql(ctx, size_query, fetch_mode="one", dict_result=True)

        # Get connection stats
        conn_query = """
            SELECT
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active_connections,
                count(*) FILTER (WHERE state = 'idle') as idle_connections,
                count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
            FROM pg_stat_activity
            WHERE datname = current_database()
        """
        conn_result = execute_sql(ctx, conn_query, fetch_mode="one", dict_result=True)

        # Get table stats
        table_query = """
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes,
                n_live_tup as live_tuples,
                n_dead_tup as dead_tuples
            FROM pg_stat_user_tables
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 10
        """
        table_result = execute_sql(ctx, table_query, dict_result=True)

        stats = {
            "database_size": size_result.get('result', {}).get('data', {}),
            "connections": conn_result.get('result', {}).get('data', {}),
            "top_tables": table_result.get('result', {}).get('data', [])
        }

        return {
            "result": {
                "success": True,
                "statistics": stats
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "get_database_stats_failed",
                "message": str(e)
            }
        }