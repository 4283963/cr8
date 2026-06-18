from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.nutrient_solution import (
    NutrientSolution,
    NutrientSolutionCreate,
    NutrientSolutionListResponse,
    NutrientLatest,
)
from ..crud import nutrient_solution as crud

router = APIRouter(prefix="/nutrient", tags=["营养液"])


@router.get("", response_model=NutrientSolutionListResponse)
def list_nutrient_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    minutes: Optional[int] = Query(None, ge=1, description="查询最近N分钟的数据"),
    db: Session = Depends(get_db),
):
    items, total = crud.get_nutrient_records(db, skip=skip, limit=limit, minutes=minutes)
    return NutrientSolutionListResponse(items=items, total=total)


@router.get("/latest", response_model=NutrientLatest)
def get_latest_nutrient(db: Session = Depends(get_db)):
    record = crud.get_latest_nutrient(db)
    if not record:
        raise HTTPException(status_code=404, detail="无营养液数据记录")
    return NutrientLatest(
        volume_liters=record.volume_liters,
        ec_value=record.ec_value,
        ph_value=record.ph_value,
        temperature=record.temperature,
        recorded_at=record.recorded_at,
    )


@router.get("/{record_id}", response_model=NutrientSolution)
def get_nutrient_record(record_id: int, db: Session = Depends(get_db)):
    record = crud.get_nutrient_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.post("", response_model=NutrientSolution, status_code=201)
def create_nutrient_record(record_in: NutrientSolutionCreate, db: Session = Depends(get_db)):
    return crud.create_nutrient_record(db, record_in)
