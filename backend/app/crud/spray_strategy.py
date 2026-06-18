from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.spray_strategy import SprayStrategy
from ..schemas.spray_strategy import SprayStrategyCreate, SprayStrategyUpdate


def get_strategy(db: Session, strategy_id: int) -> Optional[SprayStrategy]:
    return db.query(SprayStrategy).filter(SprayStrategy.id == strategy_id).first()


def get_strategies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
) -> tuple[list[SprayStrategy], int]:
    query = db.query(SprayStrategy)
    if is_active is not None:
        query = query.filter(SprayStrategy.is_active == is_active)
    total = query.count()
    items = query.order_by(SprayStrategy.updated_at.desc()).offset(skip).limit(limit).all()
    return items, total


def get_active_strategies(db: Session) -> list[SprayStrategy]:
    now = datetime.utcnow().strftime("%H:%M")
    query = db.query(SprayStrategy).filter(SprayStrategy.is_active == True)
    strategies = query.all()
    result = []
    for s in strategies:
        if s.start_time and s.end_time:
            if s.start_time <= now <= s.end_time:
                result.append(s)
        else:
            result.append(s)
    return result


def create_strategy(db: Session, strategy_in: SprayStrategyCreate) -> SprayStrategy:
    strategy = SprayStrategy(**strategy_in.model_dump())
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return strategy


def update_strategy(
    db: Session,
    strategy_id: int,
    strategy_in: SprayStrategyUpdate,
) -> Optional[SprayStrategy]:
    strategy = get_strategy(db, strategy_id)
    if not strategy:
        return None
    for field, value in strategy_in.model_dump().items():
        setattr(strategy, field, value)
    strategy.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(strategy)
    return strategy


def toggle_strategy_active(
    db: Session,
    strategy_id: int,
    is_active: bool,
) -> Optional[SprayStrategy]:
    strategy = get_strategy(db, strategy_id)
    if not strategy:
        return None
    strategy.is_active = is_active
    strategy.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(strategy)
    return strategy


def delete_strategy(db: Session, strategy_id: int) -> bool:
    strategy = get_strategy(db, strategy_id)
    if not strategy:
        return False
    db.delete(strategy)
    db.commit()
    return True
