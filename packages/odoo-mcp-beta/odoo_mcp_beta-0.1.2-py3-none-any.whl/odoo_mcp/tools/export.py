"""
Data export and import tools for Odoo MCP
"""

import json
import csv
import io
from typing import List, Optional, Any, Dict
from mcp.server.fastmcp import Context
from ..utils.context_helpers import get_odoo_client_from_context, report_progress


def export_data(
    ctx: Context,
    model: str,
    domain: List = None,
    fields: List[str] = None,
    format: str = "json",
    limit: Optional[int] = None
):
    """
    Export data in various formats
    
    Parameters:
        model: Model name
        domain: Search domain
        fields: Fields to export
        format: Export format (json, csv, xml)
        limit: Maximum records to export
    
    Returns:
        Exported data in requested format
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    if domain is None:
        domain = []
    
    try:
        report_progress(ctx, f"Exporting data from {model} in {format} format")
        
        # Get the data
        kwargs = {}
        if fields:
            kwargs["fields"] = fields
        if limit:
            kwargs["limit"] = limit
            
        records = odoo.search_read(model, domain, **kwargs)
        
        # Format the data based on requested format
        if format == "csv":
            if not records:
                return {
                    "result": {
                        "success": True,
                        "format": "csv",
                        "data": "",
                        "count": 0
                    }
                }
            
            # Create CSV
            output = io.StringIO()
            fieldnames = fields or list(records[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in records:
                # Clean values for CSV
                csv_record = {}
                for field in fieldnames:
                    value = record.get(field, '')
                    # Handle special types
                    if isinstance(value, (list, tuple)) and len(value) == 2:
                        # Many2one field [id, name]
                        value = value[1] if value else ''
                    elif isinstance(value, list):
                        # One2many or many2many
                        value = ','.join(str(v) for v in value)
                    elif value is False:
                        value = ''
                    csv_record[field] = value
                writer.writerow(csv_record)
            
            csv_data = output.getvalue()
            return {
                "result": {
                    "success": True,
                    "format": "csv",
                    "data": csv_data,
                    "count": len(records),
                    "fields": fieldnames
                }
            }
        
        elif format == "xml":
            # Simple XML format
            xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>\n<odoo>']
            xml_parts.append('  <data>')
            
            for record in records:
                xml_parts.append(f'    <record id="record_{record.get("id", "")}" model="{model}">')
                
                for key, value in record.items():
                    if key == "id":
                        continue
                    
                    # Handle different field types
                    if isinstance(value, (list, tuple)) and len(value) == 2:
                        # Many2one field
                        xml_parts.append(f'      <field name="{key}" ref="record_{value[0]}"/>')
                    elif isinstance(value, list):
                        # One2many or many2many
                        xml_parts.append(f'      <field name="{key}" eval="[(6, 0, {value})]"/>')
                    elif isinstance(value, bool):
                        xml_parts.append(f'      <field name="{key}" eval="{value}"/>')
                    elif isinstance(value, (int, float)):
                        xml_parts.append(f'      <field name="{key}" eval="{value}"/>')
                    elif value:
                        # String value - escape XML characters
                        value_str = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        xml_parts.append(f'      <field name="{key}">{value_str}</field>')
                    
                xml_parts.append('    </record>')
            
            xml_parts.append('  </data>')
            xml_parts.append('</odoo>')
            
            return {
                "result": {
                    "success": True,
                    "format": "xml",
                    "data": "\n".join(xml_parts),
                    "count": len(records)
                }
            }
        
        else:  # json (default)
            return {
                "result": {
                    "success": True,
                    "format": "json",
                    "data": records,
                    "count": len(records),
                    "fields": fields or (list(records[0].keys()) if records else [])
                }
            }
            
    except Exception as e:
        return {
            "error": {
                "code": "export_failed",
                "message": str(e)
            }
        }


def import_data(
    ctx: Context,
    model: str,
    data: Any,
    format: str = "json",
    update_existing: bool = False,
    key_field: str = "id"
):
    """
    Import data from various formats
    
    Parameters:
        model: Model name
        data: Data to import (format depends on format parameter)
        format: Data format (json, csv)
        update_existing: Whether to update existing records
        key_field: Field to use for matching existing records
    
    Returns:
        Import results
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Importing data into {model} from {format} format")
        
        records_to_import = []
        
        # Parse data based on format
        if format == "csv":
            # Parse CSV data
            csv_file = io.StringIO(data)
            reader = csv.DictReader(csv_file)
            records_to_import = list(reader)
            
            # Convert string values to appropriate types
            for record in records_to_import:
                for key, value in record.items():
                    if value == '':
                        record[key] = False
                    elif value.lower() == 'true':
                        record[key] = True
                    elif value.lower() == 'false':
                        record[key] = False
                    elif value.isdigit():
                        record[key] = int(value)
                    elif '.' in value and value.replace('.', '').replace('-', '').isdigit():
                        try:
                            record[key] = float(value)
                        except:
                            pass  # Keep as string
        
        elif format == "json":
            if isinstance(data, str):
                records_to_import = json.loads(data)
            else:
                records_to_import = data
        
        else:
            return {
                "error": {
                    "code": "unsupported_format",
                    "message": f"Unsupported import format: {format}"
                }
            }
        
        # Import records
        created_ids = []
        updated_ids = []
        errors = []
        
        for i, record in enumerate(records_to_import):
            report_progress(ctx, f"Importing record {i+1}/{len(records_to_import)}", 
                           percent=int((i+1) * 100 / len(records_to_import)))
            
            try:
                if update_existing and key_field in record:
                    # Check if record exists
                    key_value = record[key_field]
                    existing = odoo.search_read(
                        model,
                        [[key_field, "=", key_value]],
                        ["id"],
                        limit=1
                    )
                    
                    if existing:
                        # Update existing record
                        record_id = existing[0]["id"]
                        update_data = {k: v for k, v in record.items() if k != "id"}
                        odoo.execute_method(model, "write", [record_id], update_data)
                        updated_ids.append(record_id)
                    else:
                        # Create new record
                        create_data = {k: v for k, v in record.items() if k != "id"}
                        new_id = odoo.execute_method(model, "create", create_data)
                        created_ids.append(new_id)
                else:
                    # Always create new record
                    create_data = {k: v for k, v in record.items() if k != "id"}
                    new_id = odoo.execute_method(model, "create", create_data)
                    created_ids.append(new_id)
                    
            except Exception as e:
                errors.append({
                    "record_index": i,
                    "error": str(e),
                    "record": record
                })
        
        return {
            "result": {
                "success": len(errors) == 0,
                "created": len(created_ids),
                "updated": len(updated_ids),
                "failed": len(errors),
                "created_ids": created_ids,
                "updated_ids": updated_ids,
                "errors": errors[:10]  # Limit error details
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "import_failed",
                "message": str(e)
            }
        }


def export_template(
    ctx: Context,
    model: str,
    fields: List[str] = None,
    format: str = "csv",
    include_sample: bool = False
):
    """
    Generate an import template for a model
    
    Parameters:
        model: Model name
        fields: Fields to include in template
        format: Template format (csv, json)
        include_sample: Include sample data row
    
    Returns:
        Import template
    """
    # Get the Odoo client from the context

    odoo = get_odoo_client_from_context(ctx)
    
    try:
        report_progress(ctx, f"Generating import template for {model}")
        
        # Get model fields if not specified
        if not fields:
            all_fields = odoo.get_model_fields(model)
            # Select important fields
            fields = []
            for field_name, field_info in all_fields.items():
                # Skip system fields and computed fields
                if (not field_name.startswith('_') and 
                    not field_info.get('compute') and
                    field_info.get('store', True) and
                    not field_info.get('readonly', False)):
                    fields.append(field_name)
        
        # Get field metadata for the template
        field_metadata = odoo.get_model_fields(model)
        template_fields = []
        
        for field in fields:
            if field in field_metadata:
                field_info = field_metadata[field]
                template_fields.append({
                    "name": field,
                    "type": field_info.get("type"),
                    "string": field_info.get("string", field),
                    "required": field_info.get("required", False),
                    "help": field_info.get("help", ""),
                })
        
        # Generate template based on format
        if format == "csv":
            output = io.StringIO()
            
            # Write header with field names
            writer = csv.writer(output)
            header = [f["name"] for f in template_fields]
            writer.writerow(header)
            
            # Write comment row with field descriptions
            descriptions = [f"{f['string']} ({f['type']})" for f in template_fields]
            writer.writerow(descriptions)
            
            # Add sample data if requested
            if include_sample:
                sample_row = []
                for field in template_fields:
                    if field["type"] == "char":
                        sample_row.append("Sample Text")
                    elif field["type"] == "integer":
                        sample_row.append("123")
                    elif field["type"] == "float":
                        sample_row.append("123.45")
                    elif field["type"] == "boolean":
                        sample_row.append("True")
                    elif field["type"] == "date":
                        sample_row.append("2024-01-01")
                    elif field["type"] == "datetime":
                        sample_row.append("2024-01-01 10:00:00")
                    elif field["type"] == "many2one":
                        sample_row.append("1")  # ID reference
                    else:
                        sample_row.append("")
                writer.writerow(sample_row)
            
            template_data = output.getvalue()
            
            return {
                "result": {
                    "success": True,
                    "format": "csv",
                    "template": template_data,
                    "fields": template_fields
                }
            }
        
        elif format == "json":
            template = []
            
            if include_sample:
                sample_record = {}
                for field in template_fields:
                    if field["type"] == "char":
                        sample_record[field["name"]] = "Sample Text"
                    elif field["type"] == "integer":
                        sample_record[field["name"]] = 123
                    elif field["type"] == "float":
                        sample_record[field["name"]] = 123.45
                    elif field["type"] == "boolean":
                        sample_record[field["name"]] = True
                    elif field["type"] == "date":
                        sample_record[field["name"]] = "2024-01-01"
                    elif field["type"] == "datetime":
                        sample_record[field["name"]] = "2024-01-01 10:00:00"
                    elif field["type"] == "many2one":
                        sample_record[field["name"]] = 1
                    elif field["type"] in ["one2many", "many2many"]:
                        sample_record[field["name"]] = []
                    else:
                        sample_record[field["name"]] = None
                template.append(sample_record)
            else:
                # Empty template with field names
                empty_record = {field["name"]: None for field in template_fields}
                template.append(empty_record)
            
            return {
                "result": {
                    "success": True,
                    "format": "json",
                    "template": template,
                    "fields": template_fields
                }
            }
        
        else:
            return {
                "error": {
                    "code": "unsupported_format",
                    "message": f"Unsupported template format: {format}"
                }
            }
            
    except Exception as e:
        return {
            "error": {
                "code": "template_generation_failed",
                "message": str(e)
            }
        }