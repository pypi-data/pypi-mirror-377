"""
Models for Odoo model information responses
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    """Information about an Odoo model including record counts and dates."""
    name: str = Field(description="Model technical name (e.g., 'res.partner')")
    display_name: Optional[str] = Field(
        default=None, description="User-friendly display name (e.g., 'Contact')"
    )
    record_count: int = Field(description="Number of records in this model")
    latest_update: Optional[datetime] = Field(
        default=None, description="Date of most recent record update"
    )
    latest_create: Optional[datetime] = Field(
        default=None, description="Date of most recent record creation"
    )
    description: Optional[str] = Field(
        default=None, description="Model description if available"
    )


class ModelInfoResponse(BaseModel):
    """Response model for enhanced model listing."""
    success: bool = Field(description="Indicates if the operation was successful")
    models: list[ModelInfo] = Field(
        default_factory=list, description="List of model information"
    )
    error: Optional[str] = Field(default=None, description="Error message, if any")
