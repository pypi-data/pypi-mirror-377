"""
Models for employee-related data and responses
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class EmployeeSearchResult(BaseModel):
    """Represents a single employee search result."""
    id: int = Field(description="Employee ID")
    name: str = Field(description="Employee name")


class SearchEmployeeResponse(BaseModel):
    """Response model for the search_employee tool."""
    success: bool = Field(description="Indicates if the search was successful")
    result: Optional[List[EmployeeSearchResult]] = Field(
        default=None, description="List of employee search results"
    )
    error: Optional[str] = Field(default=None, description="Error message, if any")
