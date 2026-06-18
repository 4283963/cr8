from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.nozzle_status import (
    NozzleStatus,
    NozzleStatusCreate,
    NozzleStatusListResponse,
    NozzleStatusStats,
)
from ..crud import nozzle_status as crud

router = APIRouter(prefix="/nozzles", tags=["喷头状态"])


@router.get("", response_model=NozzleStatusListResponse)
def list_nozzle_statuses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    nozzle_id: Optional[str] = None,
    minutes: Optional[int] = Query(None, ge=1, description="查询最近N分钟的数据"),
    db: Session = Depends(get_db),
):
    items, total = crud.get_nozzle_statuses(
        db, skip=skip, limit=limit, nozzle_id=nozzle_id, minutes=minutes
    )
    return NozzleStatusListResponse(items=items, total=total)


@router.get("/stats", response_model=NozzleStatusStats)
def get_nozzle_stats(db: Session = Depends(get_db)):
    return crud.get_nozzle_stats(db)


@router.get("/latest", response_model=list[NozzleStatus])
def list_latest_statuses(db: Session = Depends(get_db)):
    return crud.get_all_latest_statuses(db)


@router.get("/{nozzle_id}/latest", response_model=NozzleStatus)
def get_nozzle_latest(nozzle_id: str, db: Session = Depends(get_db)):
    status = crud.get_latest_by_nozzle(db, nozzle_id)
    if not status:
        raise HTTPException(status_code=404, detail="该喷头无状态记录")
    return status


@router.get("/{status_id}", response_model=NozzleStatus)
def get_status(status_id: int, db: Session = Depends(get_db)):
    status = crud.get_nozzle_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="记录不存在")
    return status


@router.post("", response_model=NozzleStatus, status_code=201)
def create_nozzle_status(status_in: NozzleStatusCreate, db: Session = Depends(get_db)):
    return crud.create_nozzle_status(db, status_in)
