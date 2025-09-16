"""
Accounting specific tools for Odoo MCP
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def get_journal_entries(
    ctx: Context,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    journal_id: Optional[int] = None,
    state: Optional[str] = None,
    limit: int = 100
):
    """
    Get journal entries (account.move)
    
    Parameters:
        date_from: Start date (YYYY-MM-DD)
        date_to: End date (YYYY-MM-DD)
        journal_id: Filter by journal
        state: 'draft' or 'posted'
        limit: Maximum entries to return
    
    Returns:
        List of journal entries
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, "Fetching journal entries")
        
        domain = []
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        if journal_id:
            domain.append(('journal_id', '=', journal_id))
        if state:
            domain.append(('state', '=', state))
        
        entries = odoo.execute_method(
            'account.move', 'search_read',
            domain,
            ['name', 'date', 'journal_id', 'state', 'amount_total',
             'currency_id', 'partner_id', 'ref'],
            0, limit, 'date desc'
        )
        
        return {
            "success": True,
            "count": len(entries),
            "entries": entries
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_account_balances(
    ctx: Context,
    account_ids: Optional[List[int]] = None,
    date: Optional[str] = None
):
    """
    Get account balances
    
    Parameters:
        account_ids: List of account IDs (or all if None)
        date: Balance as of date (current if None)
    
    Returns:
        Account balances
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, "Calculating account balances")
        
        # Get accounts
        domain = []
        if account_ids:
            domain.append(('id', 'in', account_ids))
        
        accounts = odoo.execute_method(
            'account.account', 'search_read',
            domain,
            ['code', 'name', 'account_type', 'currency_id']
        )
        
        # Calculate balances
        context = {}
        if date:
            context['date_to'] = date
        
        for account in accounts:
            # Get balance using read with context
            balance_data = odoo.execute_method(
                'account.account', 'read',
                [account['id']], ['balance'], context
            )
            if balance_data:
                account['balance'] = balance_data[0].get('balance', 0.0)
        
        return {
            "success": True,
            "accounts": accounts,
            "as_of_date": date or datetime.now().strftime('%Y-%m-%d')
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_invoices(
    ctx: Context,
    move_type: str = 'out_invoice',
    state: Optional[str] = None,
    partner_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 100
):
    """
    Get invoices/bills
    
    Parameters:
        move_type: 'out_invoice', 'in_invoice', 'out_refund', 'in_refund'
        state: 'draft', 'posted', 'cancel'
        partner_id: Filter by partner
        date_from: Start date
        date_to: End date
        limit: Maximum invoices to return
    
    Returns:
        List of invoices
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Fetching {move_type} invoices")
        
        domain = [('move_type', '=', move_type)]
        
        if state:
            domain.append(('state', '=', state))
        if partner_id:
            domain.append(('partner_id', '=', partner_id))
        if date_from:
            domain.append(('invoice_date', '>=', date_from))
        if date_to:
            domain.append(('invoice_date', '<=', date_to))
        
        invoices = odoo.execute_method(
            'account.move', 'search_read',
            domain,
            ['name', 'invoice_date', 'invoice_date_due', 'partner_id',
             'amount_total', 'amount_residual', 'state', 'payment_state',
             'currency_id', 'invoice_origin'],
            0, limit, 'invoice_date desc'
        )
        
        return {
            "success": True,
            "count": len(invoices),
            "invoices": invoices
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def create_invoice(
    ctx: Context,
    partner_id: int,
    invoice_lines: List[Dict[str, Any]],
    move_type: str = 'out_invoice',
    invoice_date: Optional[str] = None,
    currency_id: Optional[int] = None
):
    """
    Create an invoice
    
    Parameters:
        partner_id: Customer/Vendor ID
        invoice_lines: List of invoice line data
        move_type: 'out_invoice' or 'in_invoice'
        invoice_date: Invoice date (today if None)
        currency_id: Currency ID
    
    Returns:
        Created invoice ID
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, "Creating invoice")
        
        invoice_data = {
            'partner_id': partner_id,
            'move_type': move_type,
            'invoice_date': invoice_date or datetime.now().strftime('%Y-%m-%d'),
            'invoice_line_ids': []
        }
        
        if currency_id:
            invoice_data['currency_id'] = currency_id
        
        # Prepare invoice lines
        for line in invoice_lines:
            line_data = (0, 0, {
                'name': line.get('name', 'Invoice Line'),
                'quantity': line.get('quantity', 1),
                'price_unit': line.get('price_unit', 0),
                'product_id': line.get('product_id'),
                'account_id': line.get('account_id'),
                'tax_ids': [(6, 0, line.get('tax_ids', []))]
            })
            invoice_data['invoice_line_ids'].append(line_data)
        
        invoice_id = odoo.execute_method('account.move', 'create', invoice_data)
        
        return {
            "success": True,
            "invoice_id": invoice_id,
            "message": f"Invoice created successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def post_invoice(
    ctx: Context,
    invoice_id: int
):
    """
    Post/validate an invoice
    
    Parameters:
        invoice_id: Invoice ID to post
    
    Returns:
        Success status
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Posting invoice {invoice_id}")
        
        # Post the invoice
        odoo.execute_method('account.move', 'action_post', [invoice_id])
        
        return {
            "success": True,
            "message": f"Invoice {invoice_id} posted successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_payments(
    ctx: Context,
    partner_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    payment_type: Optional[str] = None,
    limit: int = 100
):
    """
    Get payments
    
    Parameters:
        partner_id: Filter by partner
        date_from: Start date
        date_to: End date
        payment_type: 'inbound' or 'outbound'
        limit: Maximum payments to return
    
    Returns:
        List of payments
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, "Fetching payments")
        
        domain = []
        if partner_id:
            domain.append(('partner_id', '=', partner_id))
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        if payment_type:
            domain.append(('payment_type', '=', payment_type))
        
        payments = odoo.execute_method(
            'account.payment', 'search_read',
            domain,
            ['name', 'date', 'partner_id', 'amount', 'currency_id',
             'payment_type', 'state', 'payment_method_id', 'journal_id'],
            0, limit, 'date desc'
        )
        
        return {
            "success": True,
            "count": len(payments),
            "payments": payments
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_tax_report(
    ctx: Context,
    date_from: str,
    date_to: str
):
    """
    Get tax report summary
    
    Parameters:
        date_from: Start date
        date_to: End date
    
    Returns:
        Tax summary
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, "Generating tax report")
        
        # Get tax lines for the period
        domain = [
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('tax_line_id', '!=', False)
        ]
        
        tax_lines = odoo.execute_method(
            'account.move.line', 'search_read',
            domain,
            ['tax_line_id', 'debit', 'credit', 'balance', 'move_id']
        )
        
        # Aggregate by tax
        tax_summary = {}
        for line in tax_lines:
            tax_id = line['tax_line_id'][0]
            tax_name = line['tax_line_id'][1]
            
            if tax_id not in tax_summary:
                tax_summary[tax_id] = {
                    'tax_name': tax_name,
                    'total_base': 0,
                    'total_tax': 0
                }
            
            tax_summary[tax_id]['total_tax'] += line['balance']
        
        return {
            "success": True,
            "period": f"{date_from} to {date_to}",
            "tax_summary": list(tax_summary.values())
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }