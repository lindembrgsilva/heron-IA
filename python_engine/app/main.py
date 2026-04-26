import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.api.routes import chat, voice, files, system, config, memory

LOG_DIR = Path(__file__).resolve().parents[2].parent / 'user' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'heron.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('heron')

app = FastAPI(title='Heron IA', version='1.5')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(chat.router, prefix='/chat')
app.include_router(voice.router, prefix='/voice')
app.include_router(files.router, prefix='/files')
app.include_router(system.router, prefix='/system')
app.include_router(config.router, prefix='/config')
app.include_router(memory.router, prefix='/memory')


@app.on_event('startup')
def on_startup():
    init_db()
    logger.info('Heron IA v1.5 iniciado. Backend pronto.')