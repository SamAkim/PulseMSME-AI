"""FastAPI application entrypoint.

Serves the API under /api/* and, when a production frontend build exists
at frontend/dist, serves it as static files at /. One process, one
deployment target (Render/Railway/Docker).

SPA routing note: on page reload FastAPI must return index.html for every
non-/api path so React Router can handle the route client-side. This is
done via a 404 exception handler — StaticFiles raises 404 for unknown
paths (e.g. /msme, /msme/add) which we catch and serve index.html instead.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.data_store import get_data_store
from app.routers import config_router, dashboard, msme

settings = get_settings()

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
_INDEX_HTML = FRONTEND_DIST / "index.html"


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


@app.exception_handler(404)
async def spa_fallback(request: Request, exc: Exception) -> FileResponse | JSONResponse:
    """Return index.html for any frontend route reloaded directly in the browser.

    /api/* paths that are genuinely missing still get a JSON 404.
    All other 404s (e.g. /msme, /msme/add, /msme/:id/health-card) serve the
    React bundle so the client-side router can take over.
    """
    if request.url.path.startswith("/api"):
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    if _INDEX_HTML.exists():
        return FileResponse(str(_INDEX_HTML))
    return JSONResponse({"detail": "Frontend build not found"}, status_code=404)


if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")

