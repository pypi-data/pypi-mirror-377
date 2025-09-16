"""
Employee tools module for Odoo MCP
"""

from .base import search_employee, get_employee_details
from .aspire import (
    get_employee_driver_info,
    get_employee_banking_info,
    get_employee_payslips,
    get_employee_contracts,
    get_employee_attendance,
    get_employee_leaves,
    get_employee_appraisals,
    get_employee_financial_records
)

__all__ = [
    "search_employee", 
    "get_employee_details",
    "get_employee_driver_info",
    "get_employee_banking_info",
    "get_employee_payslips",
    "get_employee_contracts",
    "get_employee_attendance",
    "get_employee_leaves",
    "get_employee_appraisals",
    "get_employee_financial_records"
]

def register_tools(mcp):
    """Register all employee tools"""
    from .base import register_base_tools
    from .aspire import register_aspire_tools
    
    # Register standard tools
    register_base_tools(mcp)
    
    # Register Aspire-specific tools
    register_aspire_tools(mcp)
    
    # This function is called by src/odoo_mcp/tools/registration.py
    # which is in turn called by src/odoo_mcp/server.py
