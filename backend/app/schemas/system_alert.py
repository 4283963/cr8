from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SystemAlertBase(BaseModel):
    alert_type: str = Field(..., max_length=50)
    severity: str = Field(..., max_length=20)
    title: str = Field(..., max_length=200)
    message: Optional[str] = None
    related_nozzle_id: Optional[str] = Field(None, max_length=50)
    is_resolved: bool = False


class SystemAlertCreate(SystemAlertBase):
    created_at: Optional[datetime] = None


class SystemAlertUpdate(BaseModel):
    is_resolved: bool
    resolved_at: Optional[datetime] = None


class SystemAlert(SystemAlertBase):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SystemAlertListResponse(BaseModel):
    items: list[SystemAlert]
    total: int


class SystemAlertSummary(BaseModel):
    total: int
    unresolved_count: int
    warning_count: int
    critical_count: int
