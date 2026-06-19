from .spray_strategy import router as spray_strategy_router
from .nozzle_status import router as nozzle_status_router
from .nutrient_solution import router as nutrient_solution_router
from .system_alert import router as system_alert_router

__all__ = [
    "spray_strategy_router",
    "nozzle_status_router",
    "nutrient_solution_router",
    "system_alert_router",
]
