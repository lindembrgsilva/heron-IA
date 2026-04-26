import logging
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.hrm import get_system_status, get_full_status, check_internet

logger = logging.getLogger('heron')

router = APIRouter()


@router.get("/status")
async def system_status():
    """Retorna status do sistema."""
    return await get_system_status()


@router.get("/full")
async def full_status():
    """Retorna status completo."""
    return await get_full_status()