"""
Utility functions for the Odoo MCP server
"""

from .logging import setup_logging
from .context_helpers import (
    get_odoo_client_from_context,
    has_progress_callback,
    report_progress
)

__all__ = [
    "setup_logging",
    "get_odoo_client_from_context",
    "has_progress_callback",
    "report_progress"
]
