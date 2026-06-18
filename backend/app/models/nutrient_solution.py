from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime

from ..database import Base


class NutrientSolution(Base):
    __tablename__ = "nutrient_solutions"

    id = Column(Integer, primary_key=True, index=True)
    volume_liters = Column(Float, nullable=False)
    ec_value = Column(Float, nullable=False)
    ph_value = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
