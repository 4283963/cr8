from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NutrientSolutionBase(BaseModel):
    volume_liters: float = Field(..., ge=0, description="营养液体积(升)")
    ec_value: float = Field(..., ge=0, description="EC电导率值(mS/cm)")
    ph_value: Optional[float] = Field(None, ge=0, le=14)
    temperature: Optional[float] = Field(None, description="温度(℃)")


class NutrientSolutionCreate(NutrientSolutionBase):
    recorded_at: Optional[datetime] = None


class NutrientSolution(NutrientSolutionBase):
    id: int
    recorded_at: datetime

    class Config:
        from_attributes = True


class NutrientSolutionListResponse(BaseModel):
    items: list[NutrientSolution]
    total: int


class NutrientLatest(BaseModel):
    volume_liters: float
    ec_value: float
    ph_value: Optional[float]
    temperature: Optional[float]
    recorded_at: datetime
