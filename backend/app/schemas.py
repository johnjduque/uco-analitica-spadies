from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any

# Auth & User Schemas
class LoginRequest(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "Analista" # Administrador, Analista

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None

class PasswordReset(BaseModel):
    email: str
    new_password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True

# System Generic Response Schema
class SystemResponse(BaseModel):
    code: str
    message: str
    data: Optional[Any] = None

# Filter Options Schema
class FilterOptionsResponse(BaseModel):
    levels: List[str]
    faculties: List[str]
    programs: List[str]
    cohorts: List[str]
    periods: List[str]

# Data Ingestion Status Schema
class IngestionStatus(BaseModel):
    loaded_periods: List[str]
    missing_periods: List[str]
    recommended_next_period: Optional[str]
    total_students: int
    total_enrollments: int
    total_graduates: int

# Analytics Query Request
class AnalyticsQueryRequest(BaseModel):
    indicator: str # TAI, TDA, TDPA, TDC, TGA
    level: Optional[str] = "Todos"
    faculty: Optional[str] = "Todos"
    program: Optional[str] = "Todos"
    cohort: Optional[str] = "Todos"
    start_year: Optional[int] = None
    end_year: Optional[int] = None

# Metric Item Response
class MetricRow(BaseModel):
    period_or_semester: str
    category: Optional[str] = None
    total_students: int
    active_count: int
    desertor_count: int
    graduated_count: int
    rate_percentage: float
