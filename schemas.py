"""
Database Schemas for Freelancer Manager

Each Pydantic model represents a collection in MongoDB. The collection name is the lowercase of the class name.

- Client -> "client"
- Project -> "project"
- TimeLog -> "timelog"
- Invoice -> "invoice"
- Payment -> "payment"
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

class Client(BaseModel):
    name: str = Field(..., description="Client or company name")
    email: Optional[str] = Field(None, description="Primary contact email")
    phone: Optional[str] = Field(None, description="Primary contact phone")
    notes: Optional[str] = Field(None, description="Additional details about the client")

class Project(BaseModel):
    name: str = Field(..., description="Project name")
    client_id: Optional[str] = Field(None, description="Related client id (string ObjectId)")
    hourly_rate: Optional[float] = Field(None, ge=0, description="Hourly rate for this project")
    status: Literal["planned", "active", "paused", "completed"] = Field("active", description="Project status")
    notes: Optional[str] = Field(None, description="Project notes")

class TimeLog(BaseModel):
    project_id: str = Field(..., description="Related project id (string ObjectId)")
    client_id: Optional[str] = Field(None, description="Related client id (string ObjectId)")
    date: date = Field(..., description="Work date")
    hours: float = Field(..., gt=0, description="Hours worked")
    description: Optional[str] = Field(None, description="Description of work performed")
    hourly_rate: Optional[float] = Field(None, ge=0, description="Hourly rate used for this entry")

class Invoice(BaseModel):
    client_id: str = Field(..., description="Client id (string ObjectId)")
    project_id: Optional[str] = Field(None, description="Project id (string ObjectId)")
    number: Optional[str] = Field(None, description="Invoice number")
    amount: float = Field(..., ge=0, description="Invoice total amount")
    due_date: Optional[date] = Field(None, description="Due date")
    status: Literal["draft", "sent", "paid", "overdue"] = Field("draft", description="Invoice status")
    notes: Optional[str] = Field(None, description="Invoice notes")

class Payment(BaseModel):
    invoice_id: Optional[str] = Field(None, description="Invoice id (string ObjectId)")
    client_id: Optional[str] = Field(None, description="Client id (string ObjectId)")
    amount: float = Field(..., ge=0, description="Payment amount")
    method: Optional[str] = Field(None, description="Payment method (bank, card, cash, etc.)")
    date: date = Field(..., description="Payment date")
    notes: Optional[str] = Field(None, description="Payment notes")
