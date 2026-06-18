from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class NozzleStatus(Base):
    __tablename__ = "nozzle_statuses"

    id = Column(Integer, primary_key=True, index=True)
    nozzle_id = Column(String(50), nullable=False, index=True)
    is_spraying = Column(Boolean, default=False)
    flow_rate = Column(Float, default=0.0)
    pressure = Column(Float, nullable=True)
    strategy_id = Column(Integer, ForeignKey("spray_strategies.id"), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    strategy = relationship("SprayStrategy", back_populates="nozzle_statuses")
