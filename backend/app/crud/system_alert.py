from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.system_alert import SystemAlert
from ..schemas.system_alert import SystemAlertCreate, SystemAlertUpdate


def get_alert(db: Session, alert_id: int) -> Optional[SystemAlert]:
    return db.query(SystemAlert).filter(SystemAlert.id == alert_id).first()


def get_alerts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_resolved: Optional[bool] = None,
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
) -> tuple[list[SystemAlert], int]:
    query = db.query(SystemAlert)
    if is_resolved is not None:
        query = query.filter(SystemAlert.is_resolved == is_resolved)
    if severity:
        query = query.filter(SystemAlert.severity == severity)
    if alert_type:
        query = query.filter(SystemAlert.alert_type == alert_type)
    total = query.count()
    items = query.order_by(SystemAlert.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def get_alerts_summary(db: Session) -> dict:
    total = db.query(SystemAlert).count()
    unresolved = db.query(SystemAlert).filter(SystemAlert.is_resolved == False).count()
    warning = (
        db.query(SystemAlert)
        .filter(SystemAlert.severity == "warning", SystemAlert.is_resolved == False)
        .count()
    )
    critical = (
        db.query(SystemAlert)
        .filter(SystemAlert.severity == "critical", SystemAlert.is_resolved == False)
        .count()
    )
    return {
        "total": total,
        "unresolved_count": unresolved,
        "warning_count": warning,
        "critical_count": critical,
    }


def create_alert(db: Session, alert_in: SystemAlertCreate) -> SystemAlert:
    data = alert_in.model_dump()
    if "created_at" not in data or data["created_at"] is None:
        data["created_at"] = datetime.utcnow()
    alert = SystemAlert(**data)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def update_alert(
    db: Session,
    alert_id: int,
    alert_in: SystemAlertUpdate,
) -> Optional[SystemAlert]:
    alert = get_alert(db, alert_id)
    if not alert:
        return None
    alert.is_resolved = alert_in.is_resolved
    if alert_in.is_resolved and alert_in.resolved_at is None:
        alert.resolved_at = datetime.utcnow()
    elif alert_in.resolved_at:
        alert.resolved_at = alert_in.resolved_at
    db.commit()
    db.refresh(alert)
    return alert


def delete_alert(db: Session, alert_id: int) -> bool:
    alert = get_alert(db, alert_id)
    if not alert:
        return False
    db.delete(alert)
    db.commit()
    return True


def create_blockage_alert(
    db: Session,
    nozzle_id: str,
    blockage_score: float,
    pressure_before: float,
    pressure_after: float,
) -> SystemAlert:
    message = (
        f"喷头 {nozzle_id} 在喷雾指令下发后，管道压力未出现预期下降。"
        f"喷雾前压力: {pressure_before:.3f} MPa，喷雾后压力: {pressure_after:.3f} MPa。"
        f"堵塞嫌疑度: {blockage_score:.1%}。建议尽快检查清洗喷头，防止钙化堵塞。"
    )
    alert_in = SystemAlertCreate(
        alert_type="nozzle_blockage",
        severity="warning" if blockage_score < 0.8 else "critical",
        title=f"喷头 {nozzle_id} 疑似堵塞",
        message=message,
        related_nozzle_id=nozzle_id,
        is_resolved=False,
    )
    return create_alert(db, alert_in)


def has_unresolved_blockage_alert(db: Session, nozzle_id: str) -> bool:
    return (
        db.query(SystemAlert)
        .filter(
            SystemAlert.related_nozzle_id == nozzle_id,
            SystemAlert.alert_type == "nozzle_blockage",
            SystemAlert.is_resolved == False,
        )
        .first()
        is not None
    )
