from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.system_alert import (
    SystemAlert,
    SystemAlertCreate,
    SystemAlertUpdate,
    SystemAlertListResponse,
    SystemAlertSummary,
)
from ..crud import system_alert as crud

router = APIRouter(prefix="/alerts", tags=["系统通知"])


@router.get("", response_model=SystemAlertListResponse)
def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_resolved: Optional[bool] = None,
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    items, total = crud.get_alerts(
        db, skip=skip, limit=limit, is_resolved=is_resolved, severity=severity, alert_type=alert_type
    )
    return SystemAlertListResponse(items=items, total=total)


@router.get("/summary", response_model=SystemAlertSummary)
def get_alerts_summary(db: Session = Depends(get_db)):
    return crud.get_alerts_summary(db)


@router.get("/{alert_id}", response_model=SystemAlert)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = crud.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="通知不存在")
    return alert


@router.post("", response_model=SystemAlert, status_code=201)
def create_alert(alert_in: SystemAlertCreate, db: Session = Depends(get_db)):
    return crud.create_alert(db, alert_in)


@router.patch("/{alert_id}", response_model=SystemAlert)
def update_alert(
    alert_id: int,
    alert_in: SystemAlertUpdate,
    db: Session = Depends(get_db),
):
    alert = crud.update_alert(db, alert_id, alert_in)
    if not alert:
        raise HTTPException(status_code=404, detail="通知不存在")
    return alert


@router.delete("/{alert_id}", status_code=204)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    if not crud.delete_alert(db, alert_id):
        raise HTTPException(status_code=404, detail="通知不存在")
    return None
