"""
MCP tools for Odoo integration
"""

from .employee import search_employee, get_employee_details, get_employee_driver_info
from .execute import execute_method
from .holiday import search_holidays
from .models import list_models_with_stats

__all__ = [
    "execute_method", 
    "search_employee", 
    "get_employee_details",
    "get_employee_driver_info",
    "search_holidays", 
    "list_models_with_stats"
]
