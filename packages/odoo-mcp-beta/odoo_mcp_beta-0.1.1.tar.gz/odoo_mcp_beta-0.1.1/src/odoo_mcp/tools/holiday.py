"""
Tools for holiday-related operations
"""

from datetime import datetime, timedelta
from typing import Optional

from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def search_holidays(
    ctx: Context,
    start_date: str,
    end_date: str,
    employee_id: Optional[int] = None,
):
    """
    Searches for holidays within a specified date range.

    Parameters:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        employee_id: Optional employee ID to filter holidays.

    Returns:
        Object containing the search results or error information.
    """
    odoo = get_odoo_client_from_context(ctx)
    # Validate date format using datetime
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        return {
            "error": {
                "code": "invalid_date_format",
                "message": "Invalid start_date format. Use YYYY-MM-DD."
            }
        }
    
    try:
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return {
            "error": {
                "code": "invalid_date_format",
                "message": "Invalid end_date format. Use YYYY-MM-DD."
            }
        }

    # Report progress (if available)
    report_progress(ctx, f"Searching for holidays between {start_date} and {end_date}")

    # Calculate adjusted start_date (subtract one day)
    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    adjusted_start_date_dt = start_date_dt - timedelta(days=1)
    adjusted_start_date = adjusted_start_date_dt.strftime("%Y-%m-%d")

    # Build the domain
    domain = [
        "&",
        ["start_datetime", "<=", f"{end_date} 22:59:59"],
        # Use adjusted date
        ["stop_datetime", ">=", f"{adjusted_start_date} 23:00:00"],
    ]
    if employee_id:
        domain.append(
            ["employee_id", "=", employee_id],
        )
        report_progress(ctx, f"Filtering by employee ID {employee_id}")

    try:
        holidays = odoo.search_read(
            model_name="hr.leave.report.calendar",
            domain=domain,
        )
        
        # Format holidays for the response
        parsed_holidays = []
        for holiday in holidays:
            # Clean up the holiday data for JSON serialization
            cleaned_holiday = {
                key: str(value) if isinstance(value, datetime) else value
                for key, value in holiday.items()
            }
            parsed_holidays.append(cleaned_holiday)
        
        # Return MCP-compliant response format
        return {
            "result": {
                "success": True,
                "data": {
                    "holidays": parsed_holidays,
                    "count": len(parsed_holidays),
                    "date_range": {
                        "start": start_date,
                        "end": end_date
                    }
                }
            }
        }

    except Exception as e:
        # Return MCP-compliant error format
        return {
            "error": {
                "code": "holiday_search_failed",
                "message": str(e)
            }
        }
