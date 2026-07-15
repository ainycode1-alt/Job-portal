from __future__ import annotations

import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager

from prometheus_fastapi_instrumentator import Instrumentator

from app.database import init_pgvector
from app.middleware.cors import setup_cors
from app.middleware.logging_middleware import LoggingMiddleware
from app.routers import auth

import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists and add file logging handler
os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/fastapi.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(file_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Job Portal API...")
    # Initialize pgvector extension
    await init_pgvector()
    logger.info("pgvector extension initialized!")
    yield
    logger.info("Shutting down Job Portal API...")


app = FastAPI(
    title="Job Portal API",
    description="Staffing/Job Portal with Client-Vendor model + pgvector",
    version="1.0.0",
    lifespan=lifespan,
)

setup_cors(app)
app.add_middleware(LoggingMiddleware)

# Expose metrics at /metrics for Prometheus & Grafana
Instrumentator().instrument(app).expose(app)

app.include_router(auth.router)


@app.get("/")
async def root():
    return {
        "message": "Job Portal API with pgvector",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "pgvector": "enabled"}
