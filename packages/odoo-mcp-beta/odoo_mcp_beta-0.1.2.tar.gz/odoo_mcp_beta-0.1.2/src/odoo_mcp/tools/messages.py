"""
Message and mail system integration tools for Odoo MCP
"""

from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def post_message(
    ctx: Context,
    model: str,
    record_id: int,
    body: str,
    subject: Optional[str] = None,
    message_type: str = 'comment',
    subtype: str = 'mail.mt_comment',
    partner_ids: Optional[List[int]] = None
):
    """
    Post a message to a record
    
    Parameters:
        model: Model name
        record_id: Record ID to post message to
        body: Message body (HTML)
        subject: Optional subject
        message_type: 'comment', 'notification', 'email'
        subtype: Message subtype
        partner_ids: List of partner IDs to notify
    
    Returns:
        Created message ID
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Posting message to {model}/{record_id}")
        
        # Post message using message_post method
        kwargs = {
            'body': body,
            'message_type': message_type,
            'subtype_xmlid': subtype
        }
        
        if subject:
            kwargs['subject'] = subject
        
        if partner_ids:
            kwargs['partner_ids'] = partner_ids
        
        message_id = odoo.execute_method(
            model, 'message_post',
            [record_id], **kwargs
        )
        
        return {
            "success": True,
            "message_id": message_id,
            "message": "Message posted successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_messages(
    ctx: Context,
    model: str,
    record_id: int,
    limit: int = 30,
    message_type: Optional[str] = None
):
    """
    Get messages for a record
    
    Parameters:
        model: Model name
        record_id: Record ID
        limit: Maximum messages to return
        message_type: Filter by message type
    
    Returns:
        List of messages
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Fetching messages for {model}/{record_id}")
        
        domain = [
            ('model', '=', model),
            ('res_id', '=', record_id)
        ]
        
        if message_type:
            domain.append(('message_type', '=', message_type))
        
        messages = odoo.execute_method(
            'mail.message', 'search_read',
            domain,
            ['body', 'subject', 'date', 'author_id', 'message_type',
             'subtype_id', 'partner_ids', 'attachment_ids'],
            0, limit, 'date desc'
        )
        
        return {
            "success": True,
            "count": len(messages),
            "messages": messages
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_followers(
    ctx: Context,
    model: str,
    record_id: int
):
    """
    Get followers of a record
    
    Parameters:
        model: Model name
        record_id: Record ID
    
    Returns:
        List of followers
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Fetching followers for {model}/{record_id}")
        
        followers = odoo.execute_method(
            'mail.followers', 'search_read',
            [('res_model', '=', model), ('res_id', '=', record_id)],
            ['partner_id', 'name', 'email']
        )
        
        return {
            "success": True,
            "count": len(followers),
            "followers": followers
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def add_followers(
    ctx: Context,
    model: str,
    record_id: int,
    partner_ids: List[int]
):
    """
    Add followers to a record
    
    Parameters:
        model: Model name
        record_id: Record ID
        partner_ids: List of partner IDs to add as followers
    
    Returns:
        Success status
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Adding followers to {model}/{record_id}")
        
        # Add followers using message_subscribe method
        odoo.execute_method(
            model, 'message_subscribe',
            [record_id], partner_ids
        )
        
        return {
            "success": True,
            "message": f"Added {len(partner_ids)} followers successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def send_email(
    ctx: Context,
    template_id: Optional[int] = None,
    model: Optional[str] = None,
    record_id: Optional[int] = None,
    email_values: Optional[Dict[str, Any]] = None
):
    """
    Send email using mail template
    
    Parameters:
        template_id: Mail template ID
        model: Model name (if using template)
        record_id: Record ID (if using template)
        email_values: Override email values (to, subject, body, etc)
    
    Returns:
        Sent mail ID
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, "Sending email")
        
        if template_id:
            # Send using template
            template = odoo.execute_method(
                'mail.template', 'browse', [template_id]
            )
            
            mail_id = odoo.execute_method(
                'mail.template', 'send_mail',
                template_id, record_id, 
                force_send=True, email_values=email_values or {}
            )
        else:
            # Create and send mail directly
            if not email_values:
                return {
                    "success": False,
                    "error": "email_values required when not using template"
                }
            
            mail_values = {
                'subject': email_values.get('subject', 'No Subject'),
                'body_html': email_values.get('body', ''),
                'email_to': email_values.get('email_to'),
                'email_from': email_values.get('email_from', 'noreply@odoo.com'),
                'auto_delete': True,
                'state': 'outgoing'
            }
            
            mail_id = odoo.execute_method(
                'mail.mail', 'create', mail_values
            )
            
            # Send the mail
            odoo.execute_method('mail.mail', 'send', [mail_id])
        
        return {
            "success": True,
            "mail_id": mail_id,
            "message": "Email sent successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_mail_templates(
    ctx: Context,
    model: Optional[str] = None,
    limit: int = 50
):
    """
    Get available mail templates
    
    Parameters:
        model: Filter by model
        limit: Maximum templates to return
    
    Returns:
        List of mail templates
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, "Fetching mail templates")
        
        domain = []
        if model:
            domain.append(('model_id.model', '=', model))
        
        templates = odoo.execute_method(
            'mail.template', 'search_read',
            domain,
            ['name', 'model_id', 'subject', 'email_from', 'email_to'],
            0, limit
        )
        
        return {
            "success": True,
            "count": len(templates),
            "templates": templates
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }