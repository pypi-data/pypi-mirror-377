"""
Helper functions for handling context access in MCP tools
"""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import Context
    from ..client.odoo_client import OdooClient


def get_odoo_client_from_context(ctx: 'Context') -> 'OdooClient':
    """
    Safely extract the Odoo client from the context, handling all possible formats.

    This function handles:
    1. Object-based context (ctx.request_context.lifespan_context.odoo)
    2. Dictionary-based context (ctx.request_context.lifespan_context['odoo'])
    3. Direct dictionary access (ctx['odoo'])
    4. Fallback to getting client directly from config

    Args:
        ctx: The MCP context object

    Returns:
        OdooClient: The Odoo client instance
    """
    # Try different access patterns in order of likelihood
    try:
        # Pattern 1: Standard object attribute access (most common in production)
        return ctx.request_context.lifespan_context.odoo
    except AttributeError:
        pass

    try:
        # Pattern 2: Dictionary access for lifespan_context
        return ctx.request_context.lifespan_context['odoo']
    except (AttributeError, KeyError, TypeError):
        pass

    try:
        # Pattern 3: Direct dictionary access (some test scenarios)
        if isinstance(ctx, dict):
            return ctx['odoo']
    except (KeyError, TypeError):
        pass

    try:
        # Pattern 4: Check if context has odoo directly (simplified test scenarios)
        if hasattr(ctx, 'odoo'):
            return ctx.odoo
    except AttributeError:
        pass

    # Pattern 5: Fallback to getting client directly from config
    # This ensures the function always returns a valid client
    from ..config.config import get_odoo_client
    return get_odoo_client()


def has_progress_callback(ctx: Any) -> bool:
    """
    Check if the context has a progress callback function.

    Args:
        ctx: The context object

    Returns:
        bool: True if progress callback exists, False otherwise
    """
    return hasattr(ctx, 'progress') and callable(ctx.progress)


def report_progress(ctx: Any, message: str) -> None:
    """
    Safely report progress if the context supports it.

    Args:
        ctx: The context object
        message: The progress message to report
    """
    if has_progress_callback(ctx):
        try:
            ctx.progress(message)
        except Exception:
            # Silently ignore progress reporting errors
            pass