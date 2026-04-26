import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List

from app.services.files import persist_upload, extract_text, list_uploaded_files, delete_upload
from app.services.rag import index_document

logger = logging.getLogger('heron')

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Envia e indexa arquivo."""
    file_bytes = await file.read()
    
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande (máx 10MB)")
    
    file_path = persist_upload(file_bytes, file.filename)
    text = extract_text(file_path)
    
    indexed = False
    if text:
        try:
            index_document(doc_id=file.filename, text=text, metadata={"source": "upload"})
            indexed = True
        except Exception as e:
            logger.error(f"Erro ao indexar: {e}")
    
    return {"filename": file.filename, "indexed": indexed, "path": file_path}


@router.get("/list")
async def list_files():
    """Lista arquivos enviados."""
    return {"files": list_uploaded_files()}


@router.delete("/{file_name}")
async def delete_file(file_name: str):
    """Deleta arquivo."""
    return {"deleted": delete_upload(file_name)}