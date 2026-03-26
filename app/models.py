from typing import Optional
from pydantic import BaseModel


class InvoiceData(BaseModel):
    """Structured invoice data model"""
    invoice_no: Optional[str] = None
    secondary_invoice_date: Optional[str] = None
    end_customer_name: Optional[str] = None
    end_customer_contact_number: Optional[str] = None
    end_customer_address: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None


class UploadResponse(BaseModel):
    """API Response model"""
    success: bool
    message: str
    data: Optional[InvoiceData] = None
    processing_time: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str