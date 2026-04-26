import logging
import os
import re
import io
from pathlib import Path
from typing import Optional, List
import pdfplumber
from docx import Document

logger = logging.getLogger('heron')

UPLOADS_PATH = Path(__file__).resolve().parents[3].parent / 'user' / 'uploads'
UPLOADS_PATH.mkdir(parents=True, exist_ok=True)


def safe_filename(filename: str) -> str:
    """Sanitiza nome de arquivo."""
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename[:200]


def persist_upload(file_bytes: bytes, filename: str) -> str:
    """Salva arquivo enviado."""
    safe_name = safe_filename(filename)
    file_path = UPLOADS_PATH / safe_name
    
    counter = 1
    while file_path.exists():
        name, ext = os.path.splitext(safe_name)
        file_path = UPLOADS_PATH / f"{name}_{counter}{ext}"
        counter += 1
    
    file_path.write_bytes(file_bytes)
    logger.info(f"Arquivo salvo: {file_path}")
    
    return str(file_path)


def extract_text(file_path: str) -> str:
    """Extrai texto de arquivo por extensão."""
    path = Path(file_path)
    ext = path.suffix.lower()
    
    try:
        if ext in ['.txt', '.md', '.py', '.js', '.ts', '.json', '.html', '.css']:
            return path.read_text(encoding='utf-8')
        
        elif ext == '.pdf':
            text_parts = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return '\n'.join(text_parts)
        
        elif ext in ['.docx', '.doc']:
            doc = Document(path)
            return '\n'.join([para.text for para in doc.paragraphs])
        
        else:
            logger.warning(f"Extensão não suportada: {ext}")
            return ""
    
    except Exception as e:
        logger.error(f"Erro ao extrair texto de {file_path}: {e}")
        return ""


def list_uploaded_files() -> List[dict]:
    """Lista arquivos enviados."""
    files = []
    for f in UPLOADS_PATH.iterdir():
        if f.is_file():
            stat = f.stat()
            files.append({
                "name": f.name,
                "path": str(f),
                "size": stat.st_size,
                "created": stat.st_ctime
            })
    return sorted(files, key=lambda x: x['created'], reverse=True)


def delete_upload(file_path: str) -> bool:
    """Deleta arquivo enviado."""
    try:
        Path(file_path).unlink()
        return True
    except Exception as e:
        logger.error(f"Erro ao deletar {file_path}: {e}")
        return False