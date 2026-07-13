from __future__ import annotations

import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import init_pgvector
from app.middleware.cors import setup_cors
from app.middleware.logging_middleware import LoggingMiddleware
from app.routers import auth

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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
