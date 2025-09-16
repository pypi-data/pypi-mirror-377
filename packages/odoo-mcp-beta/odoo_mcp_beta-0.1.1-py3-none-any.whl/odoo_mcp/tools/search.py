"""
Advanced search tools for Odoo MCP
"""

from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def advanced_search(
    ctx: Context,
    model: str,
    filters: List[Dict[str, Any]],
    logic: str = "AND",
    fields: Optional[List[str]] = None,
    order: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
):
    """
    Advanced search with complex filtering logic
    
    Parameters:
        model: Model name
        filters: List of filter conditions with 'field', 'operator', 'value'
        logic: Logical operator (AND/OR)
        fields: Fields to return
        order: Sort order
        limit: Max records
        offset: Skip records
    
    Returns:
        Search results
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Performing advanced search on {model}")
        
        # Build domain from filters
        domain = []
        
        # Add logical operator if needed
        if len(filters) > 1:
            if logic.upper() == "OR":
                # Add OR operators between conditions
                for i, filter_item in enumerate(filters):
                    if i > 0:
                        domain.insert(0, "|")
                    condition = [
                        filter_item.get("field"),
                        filter_item.get("operator", "="),
                        filter_item.get("value")
                    ]
                    domain.append(condition)
            else:  # AND (default)
                for filter_item in filters:
                    condition = [
                        filter_item.get("field"),
                        filter_item.get("operator", "="),
                        filter_item.get("value")
                    ]
                    domain.append(condition)
        elif filters:
            # Single filter
            filter_item = filters[0]
            condition = [
                filter_item.get("field"),
                filter_item.get("operator", "="),
                filter_item.get("value")
            ]
            domain.append(condition)
        
        # Prepare search kwargs
        search_kwargs = {}
        if fields:
            search_kwargs["fields"] = fields
        if order:
            search_kwargs["order"] = order
        if limit:
            search_kwargs["limit"] = limit
        if offset:
            search_kwargs["offset"] = offset
        
        # Execute search
        results = odoo.search_read(model, domain, **search_kwargs)
        
        # Also get total count without limit
        total_count = odoo.execute_method(model, "search_count", domain)
        
        return {
            "result": {
                "success": True,
                "records": results,
                "count": len(results),
                "total_count": total_count,
                "has_more": total_count > (offset or 0) + len(results)
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "advanced_search_failed",
                "message": str(e)
            }
        }


def search_with_aggregation(
    ctx: Context,
    model: str,
    domain: List = None,
    group_by: List[str] = None,
    aggregates: Dict[str, str] = None,
    having: List = None
):
    """
    Search with aggregation (GROUP BY functionality)
    
    Parameters:
        model: Model name
        domain: Search domain
        group_by: Fields to group by
        aggregates: Aggregation functions (field: function)
        having: HAVING clause conditions
    
    Returns:
        Aggregated results
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    if domain is None:
        domain = []
    if group_by is None:
        group_by = []
    if aggregates is None:
        aggregates = {}
    
    try:
        report_progress(ctx, f"Performing aggregated search on {model}")
        
        # Use read_group for aggregation
        fields = list(aggregates.keys()) + group_by
        
        # Build aggregation spec
        agg_specs = []
        for field, func in aggregates.items():
            agg_specs.append(f"{field}:{func}")
        
        # Perform grouped read
        result = odoo.execute_method(
            model,
            "read_group",
            domain,
            fields,
            group_by,
            lazy=False
        )
        
        return {
            "result": {
                "success": True,
                "groups": result,
                "group_count": len(result)
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "aggregation_failed",
                "message": str(e)
            }
        }


def search_distinct(
    ctx: Context,
    model: str,
    field: str,
    domain: List = None
):
    """
    Get distinct values for a field
    
    Parameters:
        model: Model name
        field: Field to get distinct values for
        domain: Optional domain filter
    
    Returns:
        List of distinct values
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    if domain is None:
        domain = []
    
    try:
        report_progress(ctx, f"Getting distinct values for {field} in {model}")
        
        # Use read_group to get distinct values
        result = odoo.execute_method(
            model,
            "read_group",
            domain,
            [field],
            [field],
            lazy=False
        )
        
        # Extract distinct values
        distinct_values = []
        for group in result:
            if field in group and group[field]:
                distinct_values.append(group[field])
        
        return {
            "result": {
                "success": True,
                "field": field,
                "distinct_values": distinct_values,
                "count": len(distinct_values)
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "distinct_failed",
                "message": str(e)
            }
        }


def fuzzy_search(
    ctx: Context,
    model: str,
    search_term: str,
    fields: List[str],
    limit: int = 20
):
    """
    Fuzzy search across multiple fields
    
    Parameters:
        model: Model name
        search_term: Term to search for
        fields: Fields to search in
        limit: Max results
    
    Returns:
        Search results
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Performing fuzzy search for '{search_term}' in {model}")
        
        # Build OR domain for fuzzy search
        domain = []
        if len(fields) > 1:
            # Add OR operators
            for i in range(len(fields) - 1):
                domain.insert(0, "|")
        
        # Add ilike conditions for each field
        for field in fields:
            domain.append([field, "ilike", search_term])
        
        # Execute search
        results = odoo.search_read(model, domain, limit=limit)
        
        # Calculate relevance scores (simple scoring based on exact matches)
        for result in results:
            score = 0
            search_lower = search_term.lower()
            for field in fields:
                if field in result and result[field]:
                    field_value = str(result[field]).lower()
                    if search_lower == field_value:
                        score += 10  # Exact match
                    elif search_lower in field_value:
                        score += 5   # Partial match
                    elif any(word in field_value for word in search_lower.split()):
                        score += 2   # Word match
            result["_relevance_score"] = score
        
        # Sort by relevance
        results.sort(key=lambda x: x.get("_relevance_score", 0), reverse=True)
        
        return {
            "result": {
                "success": True,
                "search_term": search_term,
                "results": results,
                "count": len(results)
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "fuzzy_search_failed",
                "message": str(e)
            }
        }