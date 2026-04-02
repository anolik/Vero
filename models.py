from pydantic import BaseModel, EmailStr
from datetime import datetime


class SessionCreate(BaseModel):
    firm_name: str
    contact_name: str
    contact_email: str


class SessionResponse(BaseModel):
    id: int
    token: str
    firm_name: str
    contact_name: str
    contact_email: str
    status: str
    expires_at: str
    created_at: str


class ConsentForm(BaseModel):
    consent_given: bool


class IdentityForm(BaseModel):
    first_name: str
    last_name: str
    email: str


class DomainForm(BaseModel):
    has_existing: bool
    domain_value: str
