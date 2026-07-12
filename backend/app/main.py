"""FastAPI application entrypoint.

Serves the API under /api/* and, when a production frontend build exists
at frontend/dist, serves it as static files at /. One process, one
deployment target (Render/Railway/Docker).
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.data_store import get_data_store
from app.routers import config_router, dashboard, msme

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_data_store()  # fail fast at startup if synthetic data is missing/invalid
    yield


app = FastAPI(
    title=settings.app_name,
    description=settings.app_tagline,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config_router.router)
app.include_router(msme.router)
app.include_router(dashboard.router)


FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
