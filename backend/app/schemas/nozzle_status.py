from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NozzleStatusBase(BaseModel):
    nozzle_id: str = Field(..., max_length=50)
    is_spraying: bool = False
    flow_rate: float = Field(0.0, ge=0)
    pressure: Optional[float] = Field(None, ge=0)
    strategy_id: Optional[int] = None


class NozzleStatusCreate(NozzleStatusBase):
    recorded_at: Optional[datetime] = None


class NozzleStatus(NozzleStatusBase):
    id: int
    recorded_at: datetime

    class Config:
        from_attributes = True


class NozzleStatusListResponse(BaseModel):
    items: list[NozzleStatus]
    total: int


class NozzleStatusStats(BaseModel):
    total_nozzles: int
    spraying_count: int
    idle_count: int
    avg_flow_rate: float
