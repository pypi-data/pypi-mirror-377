"""
Aspire-specific employee tools for custom fields and functions
"""

import asyncio
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator

from mcp.server.fastmcp import Context
from ...utils.context_helpers import get_odoo_client_from_context, report_progress

from ...config.config import get_odoo_client
from ...utils.db_helpers import get_formatted_db_name
from .base import validate_field_exists


# Custom fields that might be present in Aspire International School's Odoo
ASPIRE_CUSTOM_FIELDS = [
    # Driver information
    "licence_no", "is_driver", "transport_vehicle", 
    # Banking information
    "bank_account_name", "bank_bic_code", "bank_account_number", 
    # Partner information
    "partner_id",
    # Contract and payroll
    "contract_ids", "slip_ids", "payslip_count",
    # Attendance and leaves
    "attendance_ids", "last_attendance_id", "last_check_in", "last_check_out", 
    "attendance_state", "current_leave_id",
    # Appraisals
    "appraisal_count", "appraisal_ids"
]


class EmployeeDriverInfo(BaseModel):
    """Model for employee driver information"""
    is_driver: bool = Field(default=False, description="Whether the employee is a driver")
    licence_no: Optional[str] = Field(default=None, description="Driver's license number")
    vehicle_count: int = Field(default=0, description="Number of vehicles assigned")
    vehicle_ids: List[int] = Field(default_factory=list, description="IDs of assigned vehicles")
    vehicle_names: List[str] = Field(default_factory=list, description="Names of assigned vehicles")


class PayslipInfo(BaseModel):
    """Model for employee payslip information"""
    id: int = Field(description="Payslip ID")
    name: str = Field(description="Payslip name")
    date_from: Optional[str] = Field(default=None, description="Start date of the payslip period")
    date_to: Optional[str] = Field(default=None, description="End date of the payslip period")
    state: str = Field(default="draft", description="Payslip state (draft, verify, done, cancel)")
    basic_wage: float = Field(default=0.0, description="Basic wage amount")
    gross_wage: float = Field(default=0.0, description="Gross wage amount")
    net_wage: float = Field(default=0.0, description="Net wage amount")
    worked_days: Optional[float] = Field(default=None, description="Number of days worked")
    worked_hours: Optional[float] = Field(default=None, description="Number of hours worked")
    currency: Optional[str] = Field(default=None, description="Currency code")
    
    @validator('name', 'date_from', 'date_to', 'state', 'currency', pre=True)
    def transform_text(cls, v):
        if v is False:
            return None
        return v


class ContractInfo(BaseModel):
    """Model for employee contract information"""
    id: int = Field(description="Contract ID")
    name: str = Field(description="Contract name")
    state: str = Field(default="draft", description="Contract state")
    date_start: Optional[str] = Field(default=None, description="Contract start date")
    date_end: Optional[str] = Field(default=None, description="Contract end date")
    resource_calendar_id: Optional[Dict[str, Any]] = Field(default=None, description="Work schedule")
    wage: float = Field(default=0.0, description="Wage amount")
    wage_type: str = Field(default="monthly", description="Wage type (monthly, hourly)")
    notes: Optional[str] = Field(default=None, description="Contract notes")
    currency_id: Optional[Dict[str, Any]] = Field(default=None, description="Currency")
    
    @validator('notes', pre=True)
    def transform_notes(cls, v):
        if v is False:
            return None
        return v


class AttendanceRecord(BaseModel):
    """Model for employee attendance record"""
    id: int = Field(description="Attendance record ID")
    employee_id: Dict[str, Any] = Field(description="Employee reference")
    check_in: str = Field(description="Check-in date and time")
    check_out: Optional[str] = Field(default=None, description="Check-out date and time")
    worked_hours: float = Field(default=0.0, description="Number of hours worked")


class LeaveInfo(BaseModel):
    """Model for employee leave information"""
    id: int = Field(description="Leave request ID")
    name: str = Field(description="Leave description")
    holiday_status_id: Dict[str, Any] = Field(description="Leave type")
    date_from: str = Field(description="Start date and time")
    date_to: str = Field(description="End date and time")
    number_of_days: float = Field(description="Duration in days")
    state: str = Field(description="State of the leave request")
    payslip_status: bool = Field(default=False, description="Reported in payslip")
    
    @validator('name', 'date_from', 'date_to', 'state', pre=True)
    def transform_text(cls, v):
        if v is False:
            return None
        return v


class AppraisalInfo(BaseModel):
    """Model for employee appraisal information"""
    id: int = Field(description="Appraisal ID")
    employee_id: Dict[str, Any] = Field(description="Employee reference")
    date_close: Optional[str] = Field(default=None, description="Date closed")
    date_final_interview: Optional[str] = Field(default=None, description="Final interview date")
    state: str = Field(description="State of the appraisal")
    manager_ids: List[Dict[str, Any]] = Field(default_factory=list, description="Appraisal managers")
    note: Optional[str] = Field(default=None, description="Appraisal notes")
    
    @validator('date_close', 'date_final_interview', 'state', 'note', pre=True)
    def transform_text(cls, v):
        if v is False:
            return None
        return v


class FinancialRecord(BaseModel):
    """Model for employee financial record information (loans, etc.)"""
    id: int = Field(description="Record ID")
    name: str = Field(description="Record name/number")
    date: str = Field(description="Record date")
    journal_id: Dict[str, Any] = Field(description="Journal")
    account_id: Dict[str, Any] = Field(description="Account")
    partner_id: Optional[Dict[str, Any]] = Field(default=None, description="Partner")
    debit: float = Field(default=0.0, description="Debit amount")
    credit: float = Field(default=0.0, description="Credit amount")
    balance: float = Field(default=0.0, description="Balance")
    
    @validator('name', 'date', pre=True)
    def transform_text(cls, v):
        if v is False:
            return None
        return v


async def get_employee_driver_info(
    ctx: Context,
    employee_id: int
):
    """
    Get driver-related information for an employee.
    This is a custom extension specific to Aspire International School.
    
    Parameters:
        employee_id: The ID of the employee to retrieve driver info for.
               
    Returns:
        Object containing employee driver details or error information.
    """
    try:
        # Report progress (if available)
        if hasattr(ctx, 'progress'):
            await ctx.progress(description=f"Retrieving driver info for employee ID {employee_id}", percent=10)
        
        # Get Odoo client from context
        odoo = get_odoo_client_from_context(ctx)
        employee_model = "hr.employee"
        vehicle_model = "transport.vehicle"
        
        # Check if required fields exist
        required_fields = ["is_driver", "licence_no", "transport_vehicle"]
        for field in required_fields:
            if not await validate_field_exists(odoo, employee_model, field):
                return {
                    "success": False,
                    "error": f"Required field '{field}' does not exist in the hr.employee model"
                }
        
        # Check if vehicle model exists
        models = odoo.get_models()
        if vehicle_model not in models:
            return {
                "success": False,
                "error": f"The '{vehicle_model}' model does not exist in this Odoo instance"
            }
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Reading employee data", percent=30)
        
        # Get basic driver info
        employee_fields = ["is_driver", "licence_no", "transport_vehicle"]
        employee_data = odoo.read_records(employee_model, [employee_id], employee_fields)
        
        if not employee_data:
            return {
                "success": False,
                "error": f"Employee with ID {employee_id} not found"
            }
        
        employee = employee_data[0]
        
        # Initialize driver info
        driver_info = EmployeeDriverInfo(
            is_driver=employee.get("is_driver", False),
            licence_no=employee.get("licence_no", "")
        )
        
        # Get vehicle info if employee is a driver
        if driver_info.is_driver and "transport_vehicle" in employee:
            if hasattr(ctx, 'progress'):
                await ctx.progress(description="Reading vehicle data", percent=60)
            
            vehicle_ids = employee.get("transport_vehicle", [])
            driver_info.vehicle_ids = vehicle_ids
            driver_info.vehicle_count = len(vehicle_ids)
            
            if vehicle_ids:
                # Get vehicle names
                vehicles = odoo.read_records(vehicle_model, vehicle_ids, ["name"])
                driver_info.vehicle_names = [v.get("name", "") for v in vehicles]
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Complete", percent=100)
        
        return {
            "success": True,
            "data": driver_info.dict()
        }
    except Exception as e:
        error_msg = f"Error getting employee driver info: {str(e)}"
        return {
            "success": False,
            "error": error_msg
        }


async def get_employee_banking_info(
    ctx: Context,
    employee_id: int
):
    """
    Get banking information for an employee.
    This is a custom extension specific to Aspire International School.
    
    Parameters:
        employee_id: The ID of the employee to retrieve banking info for.
               
    Returns:
        Object containing employee banking details or error information.
    """
    try:
        # Report progress (if available)
        if hasattr(ctx, 'progress'):
            await ctx.progress(description=f"Retrieving banking info for employee ID {employee_id}", percent=10)
        
        # Get Odoo client from context
        odoo = get_odoo_client_from_context(ctx)
        employee_model = "hr.employee"
        
        # Check if required fields exist
        banking_fields = ["bank_account_id", "bank_account_name", "bank_bic_code"]
        existing_fields = []
        for field in banking_fields:
            if await validate_field_exists(odoo, employee_model, field):
                existing_fields.append(field)
        
        if not existing_fields:
            return {
                "success": False,
                "error": "No banking fields exist in the hr.employee model"
            }
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Reading employee data", percent=50)
        
        # Get banking info
        employee_data = odoo.read_records(employee_model, [employee_id], existing_fields)
        
        if not employee_data:
            return {
                "success": False,
                "error": f"Employee with ID {employee_id} not found"
            }
        
        banking_info = {}
        for field in existing_fields:
            if field in employee_data[0]:
                # Special handling for bank_account_id which is a many2one field
                if field == "bank_account_id" and employee_data[0][field]:
                    banking_info[field] = {
                        "id": employee_data[0][field][0],
                        "name": employee_data[0][field][1]
                    }
                else:
                    banking_info[field] = employee_data[0][field]
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Complete", percent=100)
        
        return {
            "success": True,
            "data": banking_info
        }
    except Exception as e:
        error_msg = f"Error getting employee banking info: {str(e)}"
        return {
            "success": False,
            "error": error_msg
        }


async def get_employee_payslips(
    ctx: Context,
    employee_id: int,
    limit: int = 10
):
    """
    Get payslip information for an employee.
    This is a custom extension specific to Aspire International School.
    
    Parameters:
        employee_id: The ID of the employee to retrieve payslips for.
        limit: Maximum number of payslips to return (default: 10).
               
    Returns:
        Object containing employee payslip details or error information.
    """
    try:
        # Report progress (if available)
        if hasattr(ctx, 'progress'):
            await ctx.progress(description=f"Retrieving payslips for employee ID {employee_id}", percent=10)
        
        # Get Odoo client from context
        odoo = get_odoo_client_from_context(ctx)
        employee_model = "hr.employee"
        payslip_model = "hr.payslip"
        
        # Check if required models exist
        models = odoo.get_models()
        if payslip_model not in models:
            return {
                "success": False,
                "error": f"The '{payslip_model}' model does not exist in this Odoo instance"
            }
        
        # Check if employee exists
        employee = odoo.read_records(employee_model, [employee_id], ["name", "slip_ids"])
        if not employee:
            return {
                "success": False,
                "error": f"Employee with ID {employee_id} not found"
            }
        
        # Get payslip IDs from employee record
        payslip_ids = employee[0].get("slip_ids", [])
        if not payslip_ids:
            return {
                "success": True,
                "result": []
            }
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Reading payslip data", percent=50)
        
        # Get payslip details (limited to the most recent ones)
        payslip_ids = payslip_ids[:limit]  # Limit to requested number
        payslip_fields = [
            "name", "date_from", "date_to", "state", "basic_wage", 
            "gross_wage", "net_wage", "worked_days", "worked_hours", "currency_id"
        ]
        
        payslips_data = odoo.read_records(payslip_model, payslip_ids, payslip_fields)
        
        # Format payslip data
        payslips = []
        for payslip in payslips_data:
            currency = None
            if payslip.get("currency_id"):
                currency = payslip["currency_id"][1]  # Currency name/code
                
            payslips.append(PayslipInfo(
                id=payslip["id"],
                name=payslip["name"],
                date_from=payslip.get("date_from"),
                date_to=payslip.get("date_to"),
                state=payslip.get("state", "draft"),
                basic_wage=payslip.get("basic_wage", 0.0),
                gross_wage=payslip.get("gross_wage", 0.0),
                net_wage=payslip.get("net_wage", 0.0),
                worked_days=payslip.get("worked_days"),
                worked_hours=payslip.get("worked_hours"),
                currency=currency
            ))
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Complete", percent=100)
        
        return {
            "success": True,
            "result": [p.dict() for p in payslips]
        }
    except Exception as e:
        error_msg = f"Error getting employee payslips: {str(e)}"
        return {
            "success": False,
            "error": error_msg
        }


async def get_employee_contracts(
    ctx: Context,
    employee_id: int
):
    """
    Get contract information for an employee.
    This is a custom extension specific to Aspire International School.
    
    Parameters:
        employee_id: The ID of the employee to retrieve contracts for.
               
    Returns:
        Object containing employee contract details or error information.
    """
    try:
        # Report progress (if available)
        if hasattr(ctx, 'progress'):
            await ctx.progress(description=f"Retrieving contracts for employee ID {employee_id}", percent=10)
        
        # Get Odoo client from context
        odoo = get_odoo_client_from_context(ctx)
        employee_model = "hr.employee"
        contract_model = "hr.contract"
        
        # Check if required models exist
        models = odoo.get_models()
        if contract_model not in models:
            return {
                "success": False,
                "error": f"The '{contract_model}' model does not exist in this Odoo instance"
            }
        
        # Check if employee exists
        employee = odoo.read_records(employee_model, [employee_id], ["name", "contract_ids"])
        if not employee:
            return {
                "success": False,
                "error": f"Employee with ID {employee_id} not found"
            }
        
        # Get contract IDs from employee record
        contract_ids = employee[0].get("contract_ids", [])
        if not contract_ids:
            return {
                "success": True,
                "result": []
            }
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Reading contract data", percent=50)
        
        # Get contract details
        contract_fields = [
            "name", "state", "date_start", "date_end", "resource_calendar_id",
            "wage", "wage_type", "notes", "currency_id"
        ]
        
        contracts_data = odoo.read_records(contract_model, contract_ids, contract_fields)
        
        # Format contract data
        contracts = []
        for contract in contracts_data:
            resource_calendar = None
            if contract.get("resource_calendar_id"):
                resource_calendar = {
                    "id": contract["resource_calendar_id"][0],
                    "name": contract["resource_calendar_id"][1]
                }
                
            currency = None
            if contract.get("currency_id"):
                currency = {
                    "id": contract["currency_id"][0],
                    "name": contract["currency_id"][1]
                }
                
            contracts.append(ContractInfo(
                id=contract["id"],
                name=contract["name"],
                state=contract.get("state", "draft"),
                date_start=contract.get("date_start"),
                date_end=contract.get("date_end"),
                resource_calendar_id=resource_calendar,
                wage=contract.get("wage", 0.0),
                wage_type=contract.get("wage_type", "monthly"),
                notes=contract.get("notes"),
                currency_id=currency
            ))
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Complete", percent=100)
        
        return {
            "success": True,
            "result": [c.dict() for c in contracts]
        }
    except Exception as e:
        error_msg = f"Error getting employee contracts: {str(e)}"
        return {
            "success": False,
            "error": error_msg
        }


async def get_employee_attendance(
    ctx: Context,
    employee_id: int,
    limit: int = 20
):
    """
    Get attendance records for an employee.
    This is a custom extension specific to Aspire International School.
    
    Parameters:
        employee_id: The ID of the employee to retrieve attendance for.
        limit: Maximum number of attendance records to return (default: 20).
               
    Returns:
        Object containing employee attendance details or error information.
    """
    try:
        # Report progress (if available)
        if hasattr(ctx, 'progress'):
            await ctx.progress(description=f"Retrieving attendance for employee ID {employee_id}", percent=10)
        
        # Get Odoo client from context
        odoo = get_odoo_client_from_context(ctx)
        attendance_model = "hr.attendance"
        
        # Check if required models exist
        models = odoo.get_models()
        if attendance_model not in models:
            return {
                "success": False,
                "error": f"The '{attendance_model}' model does not exist in this Odoo instance"
            }
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Reading attendance data", percent=40)
        
        # Search for attendance records for this employee
        domain = [("employee_id", "=", employee_id)]
        attendance_ids = odoo.search_read(attendance_model, domain, ["id"], limit=limit, order="check_in desc")
        
        if not attendance_ids:
            return {
                "success": True,
                "result": []
            }
        
        # Get attendance details
        attendance_id_list = [a["id"] for a in attendance_ids]
        fields = ["employee_id", "check_in", "check_out", "worked_hours"]
        attendance_data = odoo.read_records(attendance_model, attendance_id_list, fields)
        
        # Format attendance data
        attendance_records = []
        for record in attendance_data:
            attendance_records.append(AttendanceRecord(
                id=record["id"],
                employee_id={
                    "id": record["employee_id"][0],
                    "name": record["employee_id"][1]
                },
                check_in=record["check_in"],
                check_out=record.get("check_out"),
                worked_hours=record.get("worked_hours", 0.0)
            ))
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Complete", percent=100)
        
        return {
            "success": True,
            "result": [a.dict() for a in attendance_records]
        }
    except Exception as e:
        error_msg = f"Error getting employee attendance: {str(e)}"
        return {
            "success": False,
            "error": error_msg
        }


async def get_employee_leaves(
    ctx: Context,
    employee_id: int,
    include_allocations: bool = False
):
    """
    Get leave records for an employee.
    This is a custom extension specific to Aspire International School.
    
    Parameters:
        employee_id: The ID of the employee to retrieve leaves for.
        include_allocations: Whether to include leave allocation records (default: False).
               
    Returns:
        Object containing employee leave details or error information.
    """
    try:
        # Report progress (if available)
        if hasattr(ctx, 'progress'):
            await ctx.progress(description=f"Retrieving leaves for employee ID {employee_id}", percent=10)
        
        # Get Odoo client from context
        odoo = get_odoo_client_from_context(ctx)
        leave_model = "hr.leave"
        allocation_model = "hr.leave.allocation"
        
        # Check if required models exist
        models = odoo.get_models()
        if leave_model not in models:
            return {
                "success": False,
                "error": f"The '{leave_model}' model does not exist in this Odoo instance"
            }
        
        result = {
            "leaves": [],
            "allocations": []
        }
        
        # Get leave records
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Reading leave data", percent=30)
        
        # Search for leave records for this employee
        domain = [("employee_id", "=", employee_id)]
        leave_fields = [
            "name", "holiday_status_id", "date_from", "date_to",
            "number_of_days", "state", "payslip_status"
        ]
        leaves_data = odoo.search_read(leave_model, domain, leave_fields, limit=50, order="date_from desc")
        
        # Format leave data
        for leave in leaves_data:
            result["leaves"].append(LeaveInfo(
                id=leave["id"],
                name=leave["name"],
                holiday_status_id={
                    "id": leave["holiday_status_id"][0],
                    "name": leave["holiday_status_id"][1]
                },
                date_from=leave["date_from"],
                date_to=leave["date_to"],
                number_of_days=leave["number_of_days"],
                state=leave["state"],
                payslip_status=leave.get("payslip_status", False)
            ).dict())
        
        # Get leave allocations if requested
        if include_allocations and allocation_model in models:
            if hasattr(ctx, 'progress'):
                await ctx.progress(description="Reading leave allocations", percent=60)
            
            allocation_fields = [
                "name", "holiday_status_id", "number_of_days", "state"
            ]
            allocations_data = odoo.search_read(
                allocation_model, domain, allocation_fields, limit=20
            )
            
            # Format allocation data
            for allocation in allocations_data:
                result["allocations"].append({
                    "id": allocation["id"],
                    "name": allocation["name"],
                    "leave_type": {
                        "id": allocation["holiday_status_id"][0],
                        "name": allocation["holiday_status_id"][1]
                    },
                    "number_of_days": allocation["number_of_days"],
                    "state": allocation["state"]
                })
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Complete", percent=100)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        error_msg = f"Error getting employee leaves: {str(e)}"
        return {
            "success": False,
            "error": error_msg
        }


async def get_employee_appraisals(
    ctx: Context,
    employee_id: int
):
    """
    Get appraisal records for an employee.
    This is a custom extension specific to Aspire International School.
    
    Parameters:
        employee_id: The ID of the employee to retrieve appraisals for.
               
    Returns:
        Object containing employee appraisal details or error information.
    """
    try:
        # Report progress (if available)
        if hasattr(ctx, 'progress'):
            await ctx.progress(description=f"Retrieving appraisals for employee ID {employee_id}", percent=10)
        
        # Get Odoo client from context
        odoo = get_odoo_client_from_context(ctx)
        appraisal_model = "hr.appraisal"
        
        # Check if required models exist
        models = odoo.get_models()
        if appraisal_model not in models:
            return {
                "success": False,
                "error": f"The '{appraisal_model}' model does not exist in this Odoo instance"
            }
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Reading appraisal data", percent=40)
        
        # Search for appraisal records for this employee
        domain = [("employee_id", "=", employee_id)]
        fields = [
            "employee_id", "date_close", "date_final_interview", 
            "state", "manager_ids", "note"
        ]
        appraisals_data = odoo.search_read(appraisal_model, domain, fields, limit=20, order="date_close desc")
        
        if not appraisals_data:
            return {
                "success": True,
                "result": []
            }
        
        # Format appraisal data
        appraisals = []
        for appraisal in appraisals_data:
            # Format manager data if available
            managers = []
            if "manager_ids" in appraisal and appraisal["manager_ids"]:
                manager_records = odoo.read_records("hr.employee", appraisal["manager_ids"], ["name"])
                for manager in manager_records:
                    managers.append({
                        "id": manager["id"],
                        "name": manager["name"]
                    })
            
            appraisals.append(AppraisalInfo(
                id=appraisal["id"],
                employee_id={
                    "id": appraisal["employee_id"][0],
                    "name": appraisal["employee_id"][1]
                },
                date_close=appraisal.get("date_close"),
                date_final_interview=appraisal.get("date_final_interview"),
                state=appraisal.get("state", "new"),
                manager_ids=managers,
                note=appraisal.get("note")
            ).dict())
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Complete", percent=100)
        
        return {
            "success": True,
            "result": appraisals
        }
    except Exception as e:
        error_msg = f"Error getting employee appraisals: {str(e)}"
        return {
            "success": False,
            "error": error_msg
        }


async def get_employee_financial_records(
    ctx: Context,
    employee_id: int,
    record_type: str = "loan",
    limit: int = 20
):
    """
    Get financial records for an employee including loans and other financial transactions.
    This is a custom extension specific to Aspire International School.
    
    Parameters:
        employee_id: The ID of the employee to retrieve financial records for.
        record_type: Type of financial record to retrieve (default: "loan").
        limit: Maximum number of records to return (default: 20).
               
    Returns:
        Object containing employee financial records or error information.
    """
    try:
        # Report progress (if available)
        if hasattr(ctx, 'progress'):
            await ctx.progress(description=f"Retrieving financial records for employee ID {employee_id}", percent=10)
        
        # Get Odoo client from context
        odoo = get_odoo_client_from_context(ctx)
        employee_model = "hr.employee"
        account_move_line_model = "account.move.line"
        loan_model = "hr.loan"
        
        # Check if employee exists
        employee = odoo.read_records(employee_model, [employee_id], ["name", "partner_id"])
        if not employee:
            return {
                "success": False,
                "error": f"Employee with ID {employee_id} not found"
            }
        
        # Get the partner_id associated with the employee
        partner_id = None
        if employee[0].get("partner_id"):
            partner_id = employee[0]["partner_id"][0]
        
        # If no partner_id is found, we can't proceed with financial records
        if not partner_id:
            return {
                "success": False,
                "error": "Employee has no associated partner record for financial transactions"
            }
        
        # Check which models exist
        models = odoo.get_models()
        result = {
            "loans": [],
            "transactions": []
        }
        
        # First try to get loan records if the model exists
        if loan_model in models and record_type.lower() == "loan":
            if hasattr(ctx, 'progress'):
                await ctx.progress(description="Reading loan data", percent=30)
            
            domain = [("employee_id", "=", employee_id)]
            fields = ["name", "date", "state", "amount", "balance_amount", "payment_date"]
            
            try:
                loans_data = odoo.search_read(loan_model, domain, fields, limit=limit)
                
                for loan in loans_data:
                    result["loans"].append({
                        "id": loan["id"],
                        "name": loan["name"],
                        "date": loan.get("date"),
                        "state": loan.get("state"),
                        "amount": loan.get("amount", 0.0),
                        "balance": loan.get("balance_amount", 0.0),
                        "payment_date": loan.get("payment_date")
                    })
            except Exception:
                # If loan model search fails, continue with account move lines
                pass
        
        # Get account move lines (financial transactions)
        if account_move_line_model in models:
            if hasattr(ctx, 'progress'):
                await ctx.progress(description="Reading financial transactions", percent=60)
            
            # Search for financial transactions for this partner
            domain = [("partner_id", "=", partner_id)]
            if record_type.lower() == "loan":
                # Try to find loan-related transactions
                domain.append(("name", "ilike", "loan"))
            
            fields = [
                "name", "date", "journal_id", "account_id", 
                "partner_id", "debit", "credit", "balance"
            ]
            
            transactions = odoo.search_read(
                account_move_line_model, domain, fields, 
                limit=limit, order="date desc"
            )
            
            # Format transaction data
            for transaction in transactions:
                result["transactions"].append(FinancialRecord(
                    id=transaction["id"],
                    name=transaction["name"],
                    date=transaction["date"],
                    journal_id={
                        "id": transaction["journal_id"][0],
                        "name": transaction["journal_id"][1]
                    },
                    account_id={
                        "id": transaction["account_id"][0],
                        "name": transaction["account_id"][1]
                    },
                    partner_id={
                        "id": transaction["partner_id"][0],
                        "name": transaction["partner_id"][1]
                    } if transaction.get("partner_id") else None,
                    debit=transaction.get("debit", 0.0),
                    credit=transaction.get("credit", 0.0),
                    balance=transaction.get("balance", 0.0)
                ).dict())
        
        if hasattr(ctx, 'progress'):
            await ctx.progress(description="Complete", percent=100)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        error_msg = f"Error getting employee financial records: {str(e)}"
        return {
            "success": False,
            "error": error_msg
        }


def register_aspire_tools(mcp):
    """Register Aspire-specific employee MCP tools"""
    
    db_prefix = get_formatted_db_name()
    
    # Get Odoo client to check fields and models
    client = get_odoo_client()
    
    # Only register if we can verify the required models and fields exist
    try:
        models = client.get_models()
        
        # Register driver info tool if the transport.vehicle model exists
        if "hr.employee" in models and "transport.vehicle" in models:
            # Check if the hr.employee model has the is_driver field
            fields = client.get_model_fields("hr.employee")
            if "is_driver" in fields:
                mcp.add_tool(
                    f"{db_prefix}_get_employee_driver_info",
                    get_employee_driver_info,
                    "Get driver information for an employee (Aspire-specific)"
                )
        
        # Register banking info tool if the relevant fields exist
        if "hr.employee" in models:
            fields = client.get_model_fields("hr.employee")
            banking_fields = ["bank_account_id", "bank_account_name", "bank_bic_code"]
            if any(field in fields for field in banking_fields):
                mcp.add_tool(
                    f"{db_prefix}_get_employee_banking_info",
                    get_employee_banking_info,
                    "Get banking information for an employee (Aspire-specific)"
                )
        
        # Register payslip tools if the model exists
        if "hr.employee" in models and "hr.payslip" in models:
            mcp.add_tool(
                f"{db_prefix}_get_employee_payslips",
                get_employee_payslips,
                "Get payslip information for an employee (Aspire-specific)"
            )
        
        # Register contract tools if the model exists
        if "hr.employee" in models and "hr.contract" in models:
            mcp.add_tool(
                f"{db_prefix}_get_employee_contracts",
                get_employee_contracts,
                "Get contract information for an employee (Aspire-specific)"
            )
            
        # Register attendance tools if the model exists
        if "hr.employee" in models and "hr.attendance" in models:
            mcp.add_tool(
                f"{db_prefix}_get_employee_attendance",
                get_employee_attendance,
                "Get attendance records for an employee (Aspire-specific)"
            )
            
        # Register leave tools if the model exists
        if "hr.employee" in models and "hr.leave" in models:
            mcp.add_tool(
                f"{db_prefix}_get_employee_leaves",
                get_employee_leaves,
                "Get leave records for an employee (Aspire-specific)"
            )
            
        # Register appraisal tools if the model exists
        if "hr.employee" in models and "hr.appraisal" in models:
            mcp.add_tool(
                f"{db_prefix}_get_employee_appraisals",
                get_employee_appraisals,
                "Get appraisal records for an employee (Aspire-specific)"
            )
            
        # Register financial record tools if the models exist
        if "hr.employee" in models and "account.move.line" in models:
            mcp.add_tool(
                f"{db_prefix}_get_employee_financial_records",
                get_employee_financial_records,
                "Get financial records for an employee (loans, etc.) (Aspire-specific)"
            )
    except Exception as e:
        print(f"Warning: Could not register Aspire-specific employee tools: {str(e)}")
