from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class SprayStrategy(Base):
    __tablename__ = "spray_strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    interval_seconds = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    start_time = Column(String(5), nullable=True)
    end_time = Column(String(5), nullable=True)
    is_active = Column(Boolean, default=True)
    nozzle_ids = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    nozzle_statuses = relationship("NozzleStatus", back_populates="strategy")
