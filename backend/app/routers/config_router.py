from fastapi import APIRouter

from app.config import get_settings
from app.models.schemas import AppConfig

router = APIRouter(prefix="/api", tags=["config"])


@router.get("/config", response_model=AppConfig)
def get_app_config() -> AppConfig:
    settings = get_settings()
    return AppConfig(appName=settings.app_name, appTagline=settings.app_tagline)
