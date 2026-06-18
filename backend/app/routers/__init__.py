from fastapi import APIRouter

from . import spray_strategy, nozzle_status, nutrient_solution

api_router = APIRouter()
api_router.include_router(spray_strategy.router)
api_router.include_router(nozzle_status.router)
api_router.include_router(nutrient_solution.router)

__all__ = ["api_router"]
