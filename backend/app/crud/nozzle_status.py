from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from ..models.nozzle_status import NozzleStatus
from ..schemas.nozzle_status import NozzleStatusCreate


def get_nozzle_status(db: Session, status_id: int) -> Optional[NozzleStatus]:
    return db.query(NozzleStatus).filter(NozzleStatus.id == status_id).first()


def get_nozzle_statuses(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    nozzle_id: Optional[str] = None,
    minutes: Optional[int] = None,
) -> tuple[list[NozzleStatus], int]:
    query = db.query(NozzleStatus)
    if nozzle_id:
        query = query.filter(NozzleStatus.nozzle_id == nozzle_id)
    if minutes:
        since = datetime.utcnow() - timedelta(minutes=minutes)
        query = query.filter(NozzleStatus.recorded_at >= since)
    total = query.count()
    items = query.order_by(NozzleStatus.recorded_at.desc()).offset(skip).limit(limit).all()
    return items, total


def get_latest_by_nozzle(db: Session, nozzle_id: str) -> Optional[NozzleStatus]:
    return (
        db.query(NozzleStatus)
        .filter(NozzleStatus.nozzle_id == nozzle_id)
        .order_by(NozzleStatus.recorded_at.desc())
        .first()
    )


def get_all_latest_statuses(db: Session) -> list[NozzleStatus]:
    subquery = (
        db.query(
            NozzleStatus.nozzle_id,
            func.max(NozzleStatus.recorded_at).label("latest_time"),
        )
        .group_by(NozzleStatus.nozzle_id)
        .subquery()
    )
    return (
        db.query(NozzleStatus)
        .join(
            subquery,
            (NozzleStatus.nozzle_id == subquery.c.nozzle_id)
            & (NozzleStatus.recorded_at == subquery.c.latest_time),
        )
        .all()
    )


def create_nozzle_status(db: Session, status_in: NozzleStatusCreate) -> NozzleStatus:
    data = status_in.model_dump()
    if "recorded_at" not in data or data["recorded_at"] is None:
        data["recorded_at"] = datetime.utcnow()
    status = NozzleStatus(**data)
    db.add(status)
    db.commit()
    db.refresh(status)
    return status


def get_nozzle_stats(db: Session) -> dict:
    latest_statuses = get_all_latest_statuses(db)
    total = len(latest_statuses)
    spraying = sum(1 for s in latest_statuses if s.is_spraying)
    idle = total - spraying
    avg_flow = sum(s.flow_rate for s in latest_statuses) / total if total > 0 else 0.0
    return {
        "total_nozzles": total,
        "spraying_count": spraying,
        "idle_count": idle,
        "avg_flow_rate": round(avg_flow, 2),
    }
