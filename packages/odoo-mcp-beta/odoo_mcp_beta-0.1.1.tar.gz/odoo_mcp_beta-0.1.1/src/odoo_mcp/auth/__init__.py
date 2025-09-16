"""
OAuth authentication module for Odoo MCP Server
"""

from .oauth_config import OAuthConfig, OAuthProvider
from .oauth_handler import OAuthHandler

__all__ = ['OAuthConfig', 'OAuthProvider', 'OAuthHandler']