"""
Pydantic models for the Odoo MCP Server
"""

from .domain import DomainCondition, SearchDomain
from .employee import EmployeeSearchResult, SearchEmployeeResponse
from .holiday import Holiday, SearchHolidaysResponse
from .model_info import ModelInfo, ModelInfoResponse

__all__ = [
    "DomainCondition", 
    "SearchDomain",
    "EmployeeSearchResult", 
    "SearchEmployeeResponse",
    "Holiday", 
    "SearchHolidaysResponse",
    "ModelInfo",
    "ModelInfoResponse"
]
