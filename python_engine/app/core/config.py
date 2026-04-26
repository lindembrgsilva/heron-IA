import json
import keyring
import logging
from pathlib import Path
from typing import Optional, Any, Dict

logger = logging.getLogger('heron')

CONFIG_PATH = Path(__file__).resolve().parents[2].parent / 'data' / 'settings.json'
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

SERVICE_NAME = "heron-ia"
API_KEY_ENTRY = "gemini-api-key"


def _load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
        except Exception as e:
            logger.warning(f"Erro ao carregar config: {e}")
    return {
        "appearance": {"theme": "dark", "fontSize": 14},
        "model": {"default_model": "flash", "temperature": 0.9},
        "voice": {"language": "pt-br", "speed": 1.0},
        "files": {"max_size_mb": 10, "auto_index": True},
        "memory": {"session": True, "persistent": True, "retention_days": 30},
        "cognition": {"tone": "neutral", "detail": "balanced"},
        "hardware": {"max_ram_mb": 8192},
        "cache": {"enabled": True, "max_size_mb": 4096},
        "security": {"confirm_destructive": True},
        "diagnostic": {"log_level": "INFO"}
    }


def _save_config(config: Dict[str, Any]) -> bool:
    try:
        CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding='utf-8')
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar config: {e}")
        return False


def get_api_key() -> Optional[str]:
    try:
        return keyring.get_password(SERVICE_NAME, API_KEY_ENTRY)
    except Exception:
        return None


def set_api_key(api_key: str) -> bool:
    try:
        keyring.set_password(SERVICE_NAME, API_KEY_ENTRY, api_key)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar API key: {e}")
        return False


def delete_api_key() -> bool:
    try:
        keyring.delete_password(SERVICE_NAME, API_KEY_ENTRY)
        return True
    except Exception:
        return False


def get_config() -> Dict[str, Any]:
    return _load_config()


def set_config(config: Dict[str, Any]) -> bool:
    return _save_config(config)


def update_config(updates: Dict[str, Any]) -> bool:
    current = _load_config()
    current.update(updates)
    return _save_config(current)