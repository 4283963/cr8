from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..models.nutrient_solution import NutrientSolution
from ..schemas.nutrient_solution import NutrientSolutionCreate


def get_nutrient_record(db: Session, record_id: int) -> Optional[NutrientSolution]:
    return db.query(NutrientSolution).filter(NutrientSolution.id == record_id).first()


def get_nutrient_records(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    minutes: Optional[int] = None,
) -> tuple[list[NutrientSolution], int]:
    query = db.query(NutrientSolution)
    if minutes:
        since = datetime.utcnow() - timedelta(minutes=minutes)
        query = query.filter(NutrientSolution.recorded_at >= since)
    total = query.count()
    items = query.order_by(NutrientSolution.recorded_at.desc()).offset(skip).limit(limit).all()
    return items, total


def get_latest_nutrient(db: Session) -> Optional[NutrientSolution]:
    return (
        db.query(NutrientSolution)
        .order_by(NutrientSolution.recorded_at.desc())
        .first()
    )


def create_nutrient_record(db: Session, record_in: NutrientSolutionCreate) -> NutrientSolution:
    data = record_in.model_dump()
    if "recorded_at" not in data or data["recorded_at"] is None:
        data["recorded_at"] = datetime.utcnow()
    record = NutrientSolution(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
