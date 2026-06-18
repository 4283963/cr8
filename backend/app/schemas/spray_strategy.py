from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SprayStrategyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    interval_seconds: int = Field(..., gt=0, description="喷雾间隔秒数")
    duration_seconds: int = Field(..., gt=0, description="喷雾持续秒数")
    start_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$", description="生效开始时间 HH:MM")
    end_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$", description="生效结束时间 HH:MM")
    is_active: bool = True
    nozzle_ids: Optional[str] = Field(None, description="逗号分隔的喷头ID列表")


class SprayStrategyCreate(SprayStrategyBase):
    pass


class SprayStrategyUpdate(SprayStrategyBase):
    pass


class SprayStrategy(SprayStrategyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SprayStrategyListResponse(BaseModel):
    items: list[SprayStrategy]
    total: int
