# Odoo MCP Server

[![PyPI Version](https://img.shields.io/pypi/v/odoo-mcp-beta.svg)](https://pypi.org/project/odoo-mcp-beta/)
[![Python Versions](https://img.shields.io/pypi/pyversions/odoo-mcp-beta.svg)](https://pypi.org/project/odoo-mcp-beta/)
[![License](https://img.shields.io/pypi/l/odoo-mcp-beta.svg)](https://github.com/ali205412/mcp-odoo/blob/main/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/ali205412/mcp-odoo?style=social)](https://github.com/ali205412/mcp-odoo)


An MCP server implementation that integrates with Odoo ERP systems, enabling AI assistants like Claude to interact with Odoo data and functionality through the Model Context Protocol.

## 🎯 Quick Start

```bash
# Install the package
pip install odoo-mcp-beta

# Configure your Odoo connection
export ODOO_URL="https://your-odoo.com"
export ODOO_DB="your-database"
export ODOO_USERNAME="your-username"
export ODOO_PASSWORD="your-password"

# Run the server
python -m odoo_mcp
```

## Features

* **Comprehensive Odoo Integration**: Full access to Odoo models, records, and methods
* **XML-RPC Communication**: Secure connection to Odoo instances via XML-RPC
* **Flexible Configuration**: Support for config files and environment variables
* **Resource Pattern System**: URI-based access to Odoo data structures
* **Error Handling**: Standardized error codes and messages following MCP specification
* **Resource Subscriptions**: Support for subscribing to resource changes and notifications
* **MCP Specification Compliant**: Fully compatible with the latest MCP specification (1.6.0+)
* **Progress Reporting**: Real-time progress updates during tool execution
* **Batch Operations**: Execute multiple operations efficiently in batch
* **Advanced Search**: Complex filtering with AND/OR logic, aggregations, and fuzzy search
* **Metadata Exploration**: Discover model schemas, constraints, and relationships
* **Data Export/Import**: Export data in JSON/CSV/XML formats, import with validation
* **Security Management**: User access control, field-level permissions, sudo operations
* **Workflow Management**: State transitions, workflow actions, and history tracking

## Tools

### Core Operations

* **execute_method** - Execute any Odoo model method with full flexibility
* **list_models** - List available models with statistics and record counts

### Batch Operations

* **batch_execute** - Execute multiple operations in a single transaction
* **batch_create** - Create multiple records efficiently
* **batch_update** - Update multiple records with different values
* **batch_delete** - Delete multiple records safely
* **batch_copy** - Duplicate records with optional default values

### Advanced Search

* **advanced_search** - Complex filtering with AND/OR logic
* **search_with_aggregation** - GROUP BY queries with aggregations
* **search_distinct** - Get unique values for a field
* **fuzzy_search** - Fuzzy text search across multiple fields

### Metadata & Schema

* **get_field_metadata** - Detailed field information and validation rules
* **get_model_constraints** - SQL and Python constraints
* **get_model_relations** - Many2one, One2many, Many2many relationships
* **get_model_methods** - Available methods for a model
* **get_model_views** - Form, tree, kanban view definitions

### Data Import/Export

* **export_data** - Export in JSON, CSV, or XML formats
* **import_data** - Import with validation and update options
* **export_template** - Generate import templates with sample data

### Security & Access Control

* **get_user_info** - Current user information and settings
* **get_model_access_rights** - CRUD permissions for models
* **check_field_access** - Field-level permission checks
* **get_user_groups** - User group memberships
* **sudo_execute** - Execute with elevated privileges

### Workflow Management

* **get_record_state** - Current workflow state of records
* **execute_workflow_action** - Trigger workflow transitions
* **get_available_actions** - Available actions based on state
* **bulk_state_transition** - Bulk workflow operations
* **get_workflow_history** - Audit trail of state changes

### HR & Employee Tools

* **search_employee** - Search employees by name
* **get_employee_details** - Comprehensive employee information
* **get_employee_driver_info** - Driver and vehicle details
* **get_employee_banking_info** - Banking information
* **get_employee_payslips** - Payroll records
* **get_employee_contracts** - Employment contracts
* **get_employee_attendance** - Attendance records
* **get_employee_leaves** - Leave requests and allocations
* **get_employee_appraisals** - Performance appraisals
* **search_holidays** - Search holidays by date range

All tools follow the MCP specification for error handling with standardized error codes and messages.

## Resources

* **odoo://models**
  * Lists all available models in the Odoo system
  * Returns: Resource with MIME type `application/json` containing model information

* **odoo://model/{model_name}**
  * Get information about a specific model including fields
  * Example: `odoo://model/res.partner`
  * Returns: Resource with MIME type `application/json` containing model metadata and field definitions

* **odoo://record/{model_name}/{record_id}**
  * Get a specific record by ID
  * Example: `odoo://record/res.partner/1`
  * Returns: Resource with MIME type `application/json` containing record data

* **odoo://search/{model_name}/{domain}**
  * Search for records that match a domain
  * Example: `odoo://search/res.partner/[["is_company","=",true]]`
  * Returns: Resource with MIME type `application/json` containing matching records (limited to 10 by default)

### Resource Subscriptions

This server implements MCP resource subscriptions, allowing clients to be notified when resources change:

* **resources/subscribe**
  * Subscribe to changes in a specific resource
  * Parameters: `uri` - the resource URI to subscribe to
  * Returns: Confirmation of subscription success

* **resources/unsubscribe**
  * Unsubscribe from changes in a specific resource
  * Parameters: `uri` - the resource URI to unsubscribe from
  * Returns: Confirmation of unsubscription success

## Configuration

### Odoo Connection Setup

1. Create a configuration file named `odoo_config.json`:

```json
{
  "url": "https://your-odoo-instance.com",
  "db": "your-database-name",
  "username": "your-username",
  "password": "your-password-or-api-key",
  "mcp_prefix": "my_odoo_production"
}
```

2. Alternatively, use environment variables:
   * `ODOO_URL`: Your Odoo server URL
   * `ODOO_DB`: Database name
   * `ODOO_USERNAME`: Login username
   * `ODOO_PASSWORD`: Password or API key
   * `ODOO_MCP_PREFIX`: Custom prefix for MCP commands and resources (default: database name)
   * `ODOO_TIMEOUT`: Connection timeout in seconds (default: 30)
   * `ODOO_VERIFY_SSL`: Whether to verify SSL certificates (default: true)
   * `HTTP_PROXY`: Force the ODOO connection to use an HTTP proxy

#### Multi-Database Support

When running multiple Odoo MCP servers connected to different databases, you can use the `ODOO_MCP_PREFIX` parameter to create unique command names for each server, avoiding conflicts in AI environments:

```bash
# For production Odoo server
export ODOO_MCP_PREFIX="aspire_production"
# Commands will appear as: aspire_production_execute_method

# For development Odoo server
export ODOO_MCP_PREFIX="aspire_dev"
# Commands will appear as: aspire_dev_execute_method
```

Without this setting, the database name will be used as a prefix by default. The MCP prefix ensures tools and resources have distinct names when using multiple Odoo instances with a single LLM.

## Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "python",
      "args": [
        "-m",
        "odoo_mcp"
      ],
      "env": {
        "ODOO_URL": "https://your-odoo-instance.com",
        "ODOO_DB": "your-database-name",
        "ODOO_USERNAME": "your-username",
        "ODOO_PASSWORD": "your-password-or-api-key",
        "ODOO_MCP_PREFIX": "my_odoo"
      }
    }
  }
}
```

### Docker

```json
{
  "mcpServers": {
    "odoo": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "ODOO_URL",
        "-e",
        "ODOO_DB",
        "-e",
        "ODOO_USERNAME",
        "-e",
        "ODOO_PASSWORD",
        "mcp/odoo"
      ],
      "env": {
        "ODOO_URL": "https://your-odoo-instance.com",
        "ODOO_DB": "your-database-name",
        "ODOO_USERNAME": "your-username",
        "ODOO_PASSWORD": "your-password-or-api-key",
        "ODOO_MCP_PREFIX": "my_odoo"
      }
    }
  }
}
```

## Installation

### Python Package

```bash
# Install the beta version with all new features
pip install odoo-mcp-beta

# Or install the stable version
pip install odoo-mcp
```

### Running the Server

```bash
# Using the installed package
odoo-mcp  # or python -m odoo_mcp

# Using the MCP development tools
mcp dev odoo_mcp/server.py

# With additional dependencies
mcp dev odoo_mcp/server.py --with pandas --with numpy

# Mount local code for development
mcp dev odoo_mcp/server.py --with-editable .
```

## Build

Docker build:

```bash
docker build -t mcp/odoo:latest -f Dockerfile .
```

## Parameter Formatting Guidelines

When using the MCP tools for Odoo, pay attention to these parameter formatting guidelines:

1. **Domain Parameter**:
   * The following domain formats are supported:
     * List format: `[["field", "operator", value], ...]`
     * Object format: `{"conditions": [{"field": "...", "operator": "...", "value": "..."}]}`
     * JSON string of either format
   * Examples:
     * List format: `[["is_company", "=", true]]`
     * Object format: `{"conditions": [{"field": "date_order", "operator": ">=", "value": "2025-03-01"}]}`
     * Multiple conditions: `[["date_order", ">=", "2025-03-01"], ["date_order", "<=", "2025-03-31"]]`

2. **Fields Parameter**:
   * Should be an array of field names: `["name", "email", "phone"]`
   * The server will try to parse string inputs as JSON

## Development

### Building from Source

```bash
git clone https://github.com/ali205412/mcp-odoo.git
cd mcp-odoo
pip install -e .
```

### Running Tests

```bash
pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This MCP server is licensed under the MIT License.

## Support

For issues, questions, or contributions, please visit our [GitHub repository](https://github.com/ali205412/mcp-odoo).
