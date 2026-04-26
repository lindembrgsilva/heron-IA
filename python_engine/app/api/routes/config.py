import logging
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_config, set_config, update_config

logger = logging.getLogger('heron')

router = APIRouter()


class ConfigUpdate(BaseModel):
    config: dict
    api_key: str = None


@router.get("")
async def get_settings():
    """Retorna configurações."""
    config = get_config()
    return {
        "config": config,
        "gemini_configured": bool(config.get("gemini_configured")),
    }


@router.post("")
async def save_settings(update: ConfigUpdate):
    """Salva configurações."""
    if update.api_key:
        from app.core.config import set_api_key
        set_api_key(update.api_key)
    
    if update.config:
        update_config(update.config)
    
    return {"saved": True}