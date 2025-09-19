"""
MCP resources for Odoo integration
"""

from .models import get_models, get_model_info
from .records import get_record, search_records_resource

__all__ = ["get_models", "get_model_info", "get_record", "search_records_resource"]
