"""
Advanced ORM operations for Odoo MCP
"""

from typing import Any, Dict, List, Optional, Union
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def copy_records(
    ctx: Context,
    model: str,
    record_ids: List[int],
    default_values: Optional[Dict[str, Any]] = None
):
    """
    Copy/duplicate records with optional default values

    Parameters:
        model: Model name
        record_ids: List of record IDs to copy
        default_values: Default values for new records

    Returns:
        New record IDs
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Copying {len(record_ids)} records from {model}")

        new_ids = []
        for record_id in record_ids:
            new_id = odoo.execute_method(
                model,
                'copy',
                record_id,
                default_values or {}
            )
            new_ids.append(new_id)

        return {
            "result": {
                "success": True,
                "original_ids": record_ids,
                "new_ids": new_ids,
                "count": len(new_ids)
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "copy_records_failed",
                "message": str(e)
            }
        }


def name_search(
    ctx: Context,
    model: str,
    name: str,
    args: Optional[List] = None,
    operator: str = 'ilike',
    limit: int = 100
):
    """
    Search records by display name

    Parameters:
        model: Model name
        name: Name to search
        args: Additional domain
        operator: Search operator
        limit: Result limit

    Returns:
        Matching records
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        results = odoo.execute_method(
            model,
            'name_search',
            name,
            args or [],
            operator,
            limit
        )

        # name_search returns [(id, display_name), ...]
        records = [{'id': r[0], 'display_name': r[1]} for r in results]

        return {
            "result": {
                "success": True,
                "records": records,
                "count": len(records)
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "name_search_failed",
                "message": str(e)
            }
        }


def fields_get(
    ctx: Context,
    model: str,
    fields: Optional[List[str]] = None,
    attributes: Optional[List[str]] = None
):
    """
    Get detailed field definitions for a model

    Parameters:
        model: Model name
        fields: Specific fields (None for all)
        attributes: Field attributes to return

    Returns:
        Field definitions
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Getting field definitions for {model}")

        result = odoo.execute_method(
            model,
            'fields_get',
            fields,
            attributes
        )

        return {
            "result": {
                "success": True,
                "model": model,
                "fields": result
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "fields_get_failed",
                "message": str(e)
            }
        }


def read_group(
    ctx: Context,
    model: str,
    domain: List,
    fields: List[str],
    groupby: List[str],
    offset: int = 0,
    limit: Optional[int] = None,
    orderby: Optional[str] = None,
    lazy: bool = True
):
    """
    Perform GROUP BY aggregation

    Parameters:
        model: Model name
        domain: Search domain
        fields: Fields to aggregate
        groupby: Fields to group by
        offset: Result offset
        limit: Result limit
        orderby: Sort order
        lazy: Lazy grouping

    Returns:
        Grouped results
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Performing GROUP BY on {model}")

        kwargs = {
            'offset': offset,
            'lazy': lazy
        }
        if limit:
            kwargs['limit'] = limit
        if orderby:
            kwargs['orderby'] = orderby

        result = odoo.execute_method(
            model,
            'read_group',
            domain,
            fields,
            groupby,
            **kwargs
        )

        return {
            "result": {
                "success": True,
                "groups": result,
                "count": len(result)
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "read_group_failed",
                "message": str(e)
            }
        }


def bulk_create(
    ctx: Context,
    model: str,
    records: List[Dict[str, Any]],
    batch_size: int = 100
):
    """
    Bulk create records in batches

    Parameters:
        model: Model name
        records: List of record data
        batch_size: Records per batch

    Returns:
        Created record IDs
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Bulk creating {len(records)} records in {model}")

        created_ids = []

        # Process in batches
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            report_progress(ctx, f"Creating batch {i//batch_size + 1}")

            # Use create method for batch
            if len(batch) == 1:
                # Single record
                new_id = odoo.execute_method(model, 'create', batch[0])
                created_ids.append(new_id)
            else:
                # Multiple records - Odoo supports batch create
                new_ids = odoo.execute_method(model, 'create', batch)
                created_ids.extend(new_ids if isinstance(new_ids, list) else [new_ids])

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
                "code": "bulk_create_failed",
                "message": str(e)
            }
        }


def bulk_write(
    ctx: Context,
    model: str,
    updates: List[Dict[str, Any]],
    batch_size: int = 100
):
    """
    Bulk update records with different values

    Each update dict should have 'ids' and 'values' keys

    Parameters:
        model: Model name
        updates: List of update specifications
        batch_size: Updates per batch

    Returns:
        Update results
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        report_progress(ctx, f"Bulk updating records in {model}")

        results = []

        for i, update in enumerate(updates):
            record_ids = update.get('ids', [])
            values = update.get('values', {})

            if not record_ids or not values:
                continue

            report_progress(ctx, f"Updating {len(record_ids)} records")

            # Update records
            result = odoo.execute_method(
                model,
                'write',
                record_ids,
                values
            )

            results.append({
                'ids': record_ids,
                'success': result
            })

        return {
            "result": {
                "success": True,
                "updates": results,
                "count": len(results)
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "bulk_write_failed",
                "message": str(e)
            }
        }


def search_count(
    ctx: Context,
    model: str,
    domain: List
):
    """
    Count records matching domain

    Parameters:
        model: Model name
        domain: Search domain

    Returns:
        Record count
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        count = odoo.execute_method(
            model,
            'search_count',
            domain
        )

        return {
            "result": {
                "success": True,
                "count": count,
                "domain": domain
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "search_count_failed",
                "message": str(e)
            }
        }


def exists(
    ctx: Context,
    model: str,
    record_ids: List[int]
):
    """
    Check if records exist

    Parameters:
        model: Model name
        record_ids: Record IDs to check

    Returns:
        Existing record IDs
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        # Use exists method to check
        existing = odoo.execute_method(
            model,
            'exists',
            record_ids
        )

        # exists returns recordset, extract IDs
        if isinstance(existing, list):
            existing_ids = existing
        else:
            # Try to extract IDs from result
            existing_ids = []
            for record_id in record_ids:
                try:
                    result = odoo.execute_method(
                        model,
                        'search',
                        [['id', '=', record_id]],
                        limit=1
                    )
                    if result:
                        existing_ids.append(record_id)
                except:
                    pass

        return {
            "result": {
                "success": True,
                "requested_ids": record_ids,
                "existing_ids": existing_ids,
                "missing_ids": [id for id in record_ids if id not in existing_ids]
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "exists_check_failed",
                "message": str(e)
            }
        }


def get_metadata(
    ctx: Context,
    model: str,
    record_ids: List[int]
):
    """
    Get record metadata (create/write dates, users)

    Parameters:
        model: Model name
        record_ids: Record IDs

    Returns:
        Record metadata
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        metadata = odoo.execute_method(
            model,
            'get_metadata',
            record_ids
        )

        return {
            "result": {
                "success": True,
                "metadata": metadata
            }
        }

    except Exception as e:
        # Fallback to reading metadata fields
        try:
            records = odoo.execute_method(
                model,
                'read',
                record_ids,
                ['create_date', 'create_uid', 'write_date', 'write_uid', '__last_update']
            )

            return {
                "result": {
                    "success": True,
                    "metadata": records
                }
            }
        except:
            return {
                "error": {
                    "code": "get_metadata_failed",
                    "message": str(e)
                }
            }


def default_get(
    ctx: Context,
    model: str,
    fields: List[str]
):
    """
    Get default values for fields

    Parameters:
        model: Model name
        fields: Field names

    Returns:
        Default values
    """
    odoo = get_odoo_client_from_context(ctx)

    try:
        defaults = odoo.execute_method(
            model,
            'default_get',
            fields
        )

        return {
            "result": {
                "success": True,
                "defaults": defaults,
                "model": model
            }
        }

    except Exception as e:
        return {
            "error": {
                "code": "default_get_failed",
                "message": str(e)
            }
        }