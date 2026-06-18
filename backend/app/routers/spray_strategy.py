from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.spray_strategy import (
    SprayStrategy,
    SprayStrategyCreate,
    SprayStrategyUpdate,
    SprayStrategyListResponse,
)
from ..crud import spray_strategy as crud

router = APIRouter(prefix="/strategies", tags=["喷雾策略"])


@router.get("", response_model=SprayStrategyListResponse)
def list_strategies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    items, total = crud.get_strategies(db, skip=skip, limit=limit, is_active=is_active)
    return SprayStrategyListResponse(items=items, total=total)


@router.get("/active", response_model=list[SprayStrategy])
def list_active_strategies(db: Session = Depends(get_db)):
    return crud.get_active_strategies(db)


@router.get("/{strategy_id}", response_model=SprayStrategy)
def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    strategy = crud.get_strategy(db, strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")
    return strategy


@router.post("", response_model=SprayStrategy, status_code=201)
def create_strategy(strategy_in: SprayStrategyCreate, db: Session = Depends(get_db)):
    return crud.create_strategy(db, strategy_in)


@router.put("/{strategy_id}", response_model=SprayStrategy)
def update_strategy(
    strategy_id: int,
    strategy_in: SprayStrategyUpdate,
    db: Session = Depends(get_db),
):
    strategy = crud.update_strategy(db, strategy_id, strategy_in)
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")
    return strategy


@router.patch("/{strategy_id}/toggle", response_model=SprayStrategy)
def toggle_strategy(
    strategy_id: int,
    is_active: bool = Query(..., description="是否启用"),
    db: Session = Depends(get_db),
):
    strategy = crud.toggle_strategy_active(db, strategy_id, is_active)
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")
    return strategy


@router.delete("/{strategy_id}", status_code=204)
def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    if not crud.delete_strategy(db, strategy_id):
        raise HTTPException(status_code=404, detail="策略不存在")
    return None
