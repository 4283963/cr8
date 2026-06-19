import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .routers import (
    spray_strategy_router,
    nozzle_status_router,
    nutrient_solution_router,
    system_alert_router,
)
from .scheduler import start_blockage_detector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="气雾栽培温室控制系统 API - 管理喷雾策略、喷头状态、营养液数据",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["根路径"])
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "api_prefix": settings.API_V1_PREFIX,
    }


@app.get("/health", tags=["健康检查"])
def health_check():
    return {"status": "healthy"}


app.include_router(spray_strategy_router, prefix=settings.API_V1_PREFIX)
app.include_router(nozzle_status_router, prefix=settings.API_V1_PREFIX)
app.include_router(nutrient_solution_router, prefix=settings.API_V1_PREFIX)
app.include_router(system_alert_router, prefix=settings.API_V1_PREFIX)

start_blockage_detector()
