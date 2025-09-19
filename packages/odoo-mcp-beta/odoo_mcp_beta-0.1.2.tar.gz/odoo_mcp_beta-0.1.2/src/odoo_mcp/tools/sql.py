"""
SQL execution tools for Odoo MCP via XML-RPC
"""

import json
from typing import Any, Dict, List, Optional, Union
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def _make_serializable(value):
    """Convert database values to JSON-serializable format"""
    import datetime
    import decimal

    if value is None:
        return {"_null": True}  # Replace None with a marker to avoid XML-RPC issues
    elif isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    elif isinstance(value, datetime.time):
        return value.strftime('%H:%M:%S')
    elif isinstance(value, decimal.Decimal):
        return float(value)
    elif isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    elif isinstance(value, (list, tuple)):
        return [_make_serializable(item) for item in value]
    elif isinstance(value, dict):
        return {k: _make_serializable(v) for k, v in value.items()}
    else:
        return str(value)


def execute_sql(
    ctx: Context,
    query: str,
    params: Optional[Union[List, Dict]] = None,
    database: Optional[str] = None,
    fetch_mode: str = "all",
    dict_result: bool = True,
    commit: bool = False
):
    """
    Execute SQL query directly on Odoo database via server action

    Parameters:
        query: SQL query to execute
        params: Query parameters (list or dict)
        database: Optional database name
        fetch_mode: "all", "one", "many", or "none"
        dict_result: Return results as dictionaries
        commit: Whether to commit the transaction

    Returns:
        Query results or error
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, "Preparing SQL execution")

        # Get model ID for server action
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
                    "message": "Could not find model for SQL execution"
                }
            }

        model_id = model_search[0]

        # Prepare the SQL execution code - no imports allowed, no None values
        sql_code = f"""
# Prepare query and parameters
query = {repr(query)}
params = {repr(params) if params else 'None'}
fetch_mode = {repr(fetch_mode)}
dict_result = {dict_result}

result = ""
error = ""
row_count = 0
success = False

try:
    # Execute the query
    if params != 'None':
        env.cr.execute(query, params)
    else:
        env.cr.execute(query)

    # Get row count
    row_count = env.cr.rowcount

    # Fetch results based on mode
    if fetch_mode == "none":
        result = {{"affected_rows": row_count}}
    elif fetch_mode == "one":
        row = env.cr.fetchone()
        if dict_result and row:
            columns = [desc[0] for desc in env.cr.description]
            # Convert None values to empty strings in row data
            safe_row = [str(val) if val is not None else "" for val in row]
            result = dict(zip(columns, safe_row))
        elif row:
            # Convert None values to empty strings
            result = [str(val) if val is not None else "" for val in row]
        else:
            result = {{"message": "No data found"}}
    elif fetch_mode == "many":
        rows = env.cr.fetchmany(size=100)  # Default size 100
        if dict_result and rows:
            columns = [desc[0] for desc in env.cr.description]
            safe_rows = []
            for row in rows:
                safe_row = [str(val) if val is not None else "" for val in row]
                safe_rows.append(dict(zip(columns, safe_row)))
            result = safe_rows
        elif rows:
            # Convert None values to empty strings in all rows
            result = [[str(val) if val is not None else "" for val in row] for row in rows]
        else:
            result = []
    else:  # "all"
        rows = env.cr.fetchall()
        if dict_result and rows:
            columns = [desc[0] for desc in env.cr.description]
            safe_rows = []
            for row in rows:
                safe_row = [str(val) if val is not None else "" for val in row]
                safe_rows.append(dict(zip(columns, safe_row)))
            result = safe_rows
        elif rows:
            # Convert None values to empty strings in all rows
            result = [[str(val) if val is not None else "" for val in row] for row in rows]
        else:
            result = []

    # Handle commit
    if {commit}:
        env.cr.commit()

    success = True

except Exception as e:
    error = str(e) if e else "Unknown error"
    result = {{"error": error}}
    success = False
    env.cr.rollback()

# Return results - ensure no None values
action = {{
    'type': 'ir.actions.act_window_close',
    'tag': 'sql_result',
    'params': {{
        'result': result,
        'row_count': row_count,
        'error': error,
        'success': success
    }}
}}
"""

        report_progress(ctx, "Creating server action for SQL execution")

        # Create the server action
        action_id = odoo.execute_method(
            'ir.actions.server',
            'create',
            {
                'name': 'MCP SQL Execution',
                'model_id': model_id,
                'state': 'code',
                'code': sql_code
            }
        )

        report_progress(ctx, "Executing SQL query")

        # Run the action - just call run on the server action
        result = odoo.execute_method(
            'ir.actions.server',
            'run',
            [action_id]
        )

        # Clean up
        odoo.execute_method(
            'ir.actions.server',
            'unlink',
            [action_id]
        )

        # Process the result
        if isinstance(result, dict) and result.get('tag') == 'sql_result':
            params = result.get('params', {})
            # Check if there was an error (empty string means no error)
            if params.get('error') and params.get('error') != "":
                return {
                    "error": {
                        "code": "sql_execution_error",
                        "message": params['error']
                    }
                }
            else:
                # Get result - should never be None now
                raw_result = params.get('result', {"message": "No data returned"})
                serializable_result = _make_serializable(raw_result)
                return {
                    "result": {
                        "success": params.get('success', True),
                        "data": serializable_result,
                        "row_count": params.get('row_count', 0),
                        "type": "sql_query"
                    }
                }
        else:
            # Handle case where result format is unexpected
            safe_result = result if result is not None else {"message": "Query executed successfully"}
            return {
                "result": {
                    "success": True,
                    "data": _make_serializable(safe_result),
                    "type": "sql_query"
                }
            }

    except Exception as e:
        return {
            "error": {
                "code": "sql_execution_failed",
                "message": str(e)
            }
        }


def execute_sql_script(
    ctx: Context,
    script: str,
    database: Optional[str] = None,
    stop_on_error: bool = True,
    commit_mode: str = "all"
):
    """
    Execute SQL script with multiple statements

    Parameters:
        script: SQL script with multiple statements
        database: Optional database name
        stop_on_error: Stop if a statement fails
        commit_mode: "all", "each", or "none"

    Returns:
        Execution results
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, "Parsing SQL script")

        # Split script into individual statements
        # Simple split by semicolon (more sophisticated parsing might be needed)
        statements = [s.strip() for s in script.split(';') if s.strip()]

        results = []

        report_progress(ctx, f"Executing {len(statements)} SQL statements")

        for i, statement in enumerate(statements):
            report_progress(ctx, f"Executing statement {i+1}/{len(statements)}")

            # Determine if this statement should commit
            should_commit = (
                commit_mode == "each" or
                (commit_mode == "all" and i == len(statements) - 1)
            )

            result = execute_sql(
                ctx,
                statement,
                fetch_mode="none" if statement.upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER')) else "all",
                commit=should_commit
            )

            results.append({
                'index': i,
                'statement': statement[:100] + ('...' if len(statement) > 100 else ''),
                'success': not result.get('error'),
                'result': result
            })

            if stop_on_error and result.get('error'):
                break

        return {
            "result": {
                "success": all(r['success'] for r in results),
                "results": results,
                "executed": len(results),
                "total": len(statements)
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "sql_script_failed",
                "message": str(e)
            }
        }


def get_table_info(
    ctx: Context,
    table_name: Optional[str] = None,
    schema_name: str = "public",
    database: Optional[str] = None
):
    """
    Get database table structure and information

    Parameters:
        table_name: Specific table or None for all tables
        schema_name: Database schema (default: public)
        database: Optional database name

    Returns:
        Table structure information
    """
    try:
        if table_name:
            # Get specific table info
            query = """
                SELECT
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    c.column_default,
                    c.character_maximum_length,
                    c.numeric_precision,
                    c.numeric_scale
                FROM information_schema.columns c
                WHERE c.table_schema = %s AND c.table_name = %s
                ORDER BY c.ordinal_position
            """
            result = execute_sql(ctx, query, [schema_name, table_name])

            if result.get('error'):
                return result

            # Also get constraints
            constraint_query = """
                SELECT
                    tc.constraint_name,
                    tc.constraint_type,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints tc
                LEFT JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                LEFT JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.table_schema = %s AND tc.table_name = %s
            """
            constraints = execute_sql(ctx, constraint_query, [schema_name, table_name])

            return {
                "result": {
                    "success": True,
                    "table_name": table_name,
                    "schema_name": schema_name,
                    "columns": result.get('result', {}).get('data', []),
                    "constraints": constraints.get('result', {}).get('data', [])
                }
            }
        else:
            # Get all tables
            query = """
                SELECT
                    t.table_name,
                    t.table_type,
                    obj_description(c.oid, 'pg_class') as table_comment,
                    pg_size_pretty(pg_total_relation_size(c.oid)) as total_size,
                    c.reltuples::BIGINT as row_estimate
                FROM information_schema.tables t
                JOIN pg_class c ON c.relname = t.table_name
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE t.table_schema = %s
                    AND n.nspname = %s
                ORDER BY t.table_name
            """
            result = execute_sql(ctx, query, [schema_name, schema_name])

            return {
                "result": {
                    "success": True,
                    "schema_name": schema_name,
                    "tables": result.get('result', {}).get('data', [])
                }
            }

    except Exception as e:
        return {
            "error": {
                "code": "table_info_failed",
                "message": str(e)
            }
        }


def analyze_query(
    ctx: Context,
    query: str,
    params: Optional[Union[List, Dict]] = None,
    database: Optional[str] = None
):
    """
    Analyze SQL query execution plan

    Parameters:
        query: SQL query to analyze
        params: Query parameters
        database: Optional database name

    Returns:
        Query execution plan
    """
    try:
        # Wrap query with EXPLAIN ANALYZE
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"

        result = execute_sql(
            ctx,
            explain_query,
            params=params,
            fetch_mode="one",
            dict_result=False
        )

        if result.get('error'):
            return result

        plan = result.get('result', {}).get('data')

        # Also get basic EXPLAIN without execution
        explain_simple = f"EXPLAIN {query}"
        simple_result = execute_sql(
            ctx,
            explain_simple,
            params=params,
            fetch_mode="all",
            dict_result=False
        )

        return {
            "result": {
                "success": True,
                "execution_plan": plan,
                "plan_text": simple_result.get('result', {}).get('data', []),
                "query": query
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "query_analysis_failed",
                "message": str(e)
            }
        }