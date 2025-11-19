import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="Freelancer Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility to validate object id strings

def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id format")


# --- Minimal DTOs for create endpoints ---
class ClientCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

class ProjectCreate(BaseModel):
    name: str
    client_id: Optional[str] = None
    hourly_rate: Optional[float] = None
    status: Optional[str] = "active"
    notes: Optional[str] = None

class TimeLogCreate(BaseModel):
    project_id: str
    client_id: Optional[str] = None
    date: str
    hours: float
    description: Optional[str] = None
    hourly_rate: Optional[float] = None

class InvoiceCreate(BaseModel):
    client_id: str
    project_id: Optional[str] = None
    number: Optional[str] = None
    amount: float
    due_date: Optional[str] = None
    status: Optional[str] = "draft"
    notes: Optional[str] = None

class PaymentCreate(BaseModel):
    invoice_id: Optional[str] = None
    client_id: Optional[str] = None
    amount: float
    method: Optional[str] = None
    date: str
    notes: Optional[str] = None


@app.get("/")
def read_root():
    return {"message": "Freelancer Manager API"}


# --- CRUD: Clients ---
@app.post("/api/clients")
def create_client(payload: ClientCreate):
    doc_id = create_document("client", payload.model_dump())
    return {"id": doc_id}

@app.get("/api/clients")
def list_clients():
    items = get_documents("client")
    for i in items:
        i["id"] = str(i.pop("_id"))
    return items


# --- CRUD: Projects ---
@app.post("/api/projects")
def create_project(payload: ProjectCreate):
    data = payload.model_dump()
    if data.get("client_id"):
        # store as raw string; viewer keeps string ids
        pass
    doc_id = create_document("project", data)
    return {"id": doc_id}

@app.get("/api/projects")
def list_projects(client_id: Optional[str] = None):
    filt = {"client_id": client_id} if client_id else {}
    items = get_documents("project", filt)
    for i in items:
        i["id"] = str(i.pop("_id"))
    return items


# --- Time Logs ---
@app.post("/api/timelogs")
def create_timelog(payload: TimeLogCreate):
    data = payload.model_dump()
    doc_id = create_document("timelog", data)
    return {"id": doc_id}

@app.get("/api/timelogs")
def list_timelogs(project_id: Optional[str] = None, client_id: Optional[str] = None):
    filt = {}
    if project_id:
        filt["project_id"] = project_id
    if client_id:
        filt["client_id"] = client_id
    items = get_documents("timelog", filt)
    for i in items:
        i["id"] = str(i.pop("_id"))
    return items


# --- Invoices ---
@app.post("/api/invoices")
def create_invoice(payload: InvoiceCreate):
    data = payload.model_dump()
    doc_id = create_document("invoice", data)
    return {"id": doc_id}

@app.get("/api/invoices")
def list_invoices(client_id: Optional[str] = None, status: Optional[str] = None):
    filt = {}
    if client_id:
        filt["client_id"] = client_id
    if status:
        filt["status"] = status
    items = get_documents("invoice", filt)
    for i in items:
        i["id"] = str(i.pop("_id"))
    return items


# --- Payments ---
@app.post("/api/payments")
def create_payment(payload: PaymentCreate):
    data = payload.model_dump()
    doc_id = create_document("payment", data)
    return {"id": doc_id}

@app.get("/api/payments")
def list_payments(client_id: Optional[str] = None, invoice_id: Optional[str] = None):
    filt = {}
    if client_id:
        filt["client_id"] = client_id
    if invoice_id:
        filt["invoice_id"] = invoice_id
    items = get_documents("payment", filt)
    for i in items:
        i["id"] = str(i.pop("_id"))
    return items


# --- Simple metrics endpoints ---
@app.get("/api/metrics")
def get_metrics():
    # totals for dashboard
    clients = len(get_documents("client"))
    projects = len(get_documents("project"))
    timelogs = get_documents("timelog")
    invoices = get_documents("invoice")
    payments = get_documents("payment")

    total_hours = sum(float(t.get("hours", 0)) for t in timelogs)
    invoice_total = sum(float(i.get("amount", 0)) for i in invoices)
    payment_total = sum(float(p.get("amount", 0)) for p in payments)
    outstanding = invoice_total - payment_total

    return {
        "clients": clients,
        "projects": projects,
        "total_hours": total_hours,
        "invoice_total": invoice_total,
        "payment_total": payment_total,
        "outstanding": outstanding,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
