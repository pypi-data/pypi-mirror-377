"""
Odoo client module for XML-RPC communication
"""

from .odoo_client import OdooClient, RedirectTransport

__all__ = ["OdooClient", "RedirectTransport"]
