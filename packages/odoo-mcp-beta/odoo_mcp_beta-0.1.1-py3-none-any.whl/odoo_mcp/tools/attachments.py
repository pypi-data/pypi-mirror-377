"""
Attachment handling tools for Odoo MCP
"""

import base64
import mimetypes
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def upload_attachment(
    ctx: Context,
    model: str,
    record_id: int,
    file_content: str,
    filename: str,
    description: Optional[str] = None
):
    """
    Upload an attachment to a record
    
    Parameters:
        model: Model name
        record_id: Record ID to attach to
        file_content: Base64 encoded file content
        filename: Name of the file
        description: Optional description
    
    Returns:
        Attachment ID and details
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Uploading attachment {filename}")
        
        # Detect mimetype
        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        # Create attachment
        attachment_data = {
            'name': filename,
            'datas': file_content,
            'res_model': model,
            'res_id': record_id,
            'type': 'binary',
            'mimetype': mime_type,
        }
        
        if description:
            attachment_data['description'] = description
        
        attachment_id = odoo.execute_method('ir.attachment', 'create', attachment_data)
        
        # Read back the created attachment
        attachment = odoo.execute_method(
            'ir.attachment', 'read', [attachment_id],
            ['name', 'file_size', 'mimetype', 'create_date']
        )
        
        return {
            "success": True,
            "attachment_id": attachment_id,
            "details": attachment[0] if attachment else {}
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_attachments(
    ctx: Context,
    model: str,
    record_id: int,
    limit: int = 50
):
    """
    Get attachments for a record
    
    Parameters:
        model: Model name
        record_id: Record ID
        limit: Maximum attachments to return
    
    Returns:
        List of attachments
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Fetching attachments for {model}/{record_id}")
        
        domain = [
            ('res_model', '=', model),
            ('res_id', '=', record_id)
        ]
        
        attachments = odoo.execute_method(
            'ir.attachment', 'search_read',
            domain,
            ['name', 'file_size', 'mimetype', 'create_date', 'create_uid'],
            0, limit
        )
        
        return {
            "success": True,
            "count": len(attachments),
            "attachments": attachments
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def download_attachment(
    ctx: Context,
    attachment_id: int
):
    """
    Download an attachment by ID
    
    Parameters:
        attachment_id: Attachment ID
    
    Returns:
        Attachment content and metadata
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Downloading attachment {attachment_id}")
        
        attachment = odoo.execute_method(
            'ir.attachment', 'read',
            [attachment_id],
            ['name', 'datas', 'mimetype', 'file_size']
        )
        
        if not attachment:
            return {
                "success": False,
                "error": f"Attachment {attachment_id} not found"
            }
        
        return {
            "success": True,
            "attachment": attachment[0]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def delete_attachment(
    ctx: Context,
    attachment_id: int
):
    """
    Delete an attachment
    
    Parameters:
        attachment_id: Attachment ID to delete
    
    Returns:
        Deletion result
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Deleting attachment {attachment_id}")
        
        # Check if attachment exists
        exists = odoo.execute_method(
            'ir.attachment', 'search_count',
            [('id', '=', attachment_id)]
        )
        
        if not exists:
            return {
                "success": False,
                "error": f"Attachment {attachment_id} not found"
            }
        
        # Delete attachment
        odoo.execute_method('ir.attachment', 'unlink', [attachment_id])
        
        return {
            "success": True,
            "message": f"Attachment {attachment_id} deleted successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }