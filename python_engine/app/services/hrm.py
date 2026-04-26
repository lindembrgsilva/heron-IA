import logging
import psutil
import systeminformation as si
from typing import Dict, Any, Optional
import socket

logger = logging.getLogger('heron')


async def get_system_status() -> Dict[str, Any]:
    """Retorna status do sistema."""
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('C:\\' if os.name == 'nt' else '/')
    
    internet = await check_internet()
    gemini_configured = await check_gemini_configured()
    
    alerts = []
    if ram.percent >= 85:
        alerts.append(f"RAM em {ram.percent:.1f}%")
    if disk.percent >= 90:
        alerts.append(f"Disco em {disk.percent:.1f}%")
    if not internet:
        alerts.append("Sem conexão com a internet")
    
    return {
        "ram": {
            "total": ram.total,
            "used": ram.used,
            "percent": ram.percent,
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "percent": disk.percent,
        },
        "internet": internet,
        "gemini_configured": gemini_configured,
        "alerts": alerts,
    }


async def get_disk_usage() -> Dict[str, Any]:
    """Retorna uso de disco."""
    disk = psutil.disk_usage('C:\\' if os.name == 'nt' else '/')
    return {
        "total": disk.total,
        "used": disk.used,
        "free": disk.free,
        "percent": disk.percent,
    }


async def get_full_status() -> Dict[str, Any]:
    """Retorna status completo."""
    status = await get_system_status()
    
    return {
        "system": status,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def check_internet(host: str = "8.8.8.8", port: int = 53, timeout: int = 3) -> bool:
    """Verifica conexão com a internet."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False


async def check_gemini_configured() -> bool:
    """Verifica se API key está configurada."""
    from app.core.config import get_api_key
    api_key = get_api_key()
    return api_key is not None and len(api_key) > 0