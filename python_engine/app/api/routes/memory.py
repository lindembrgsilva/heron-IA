import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.session import Memory
from app.services.rag import query as rag_query

logger = logging.getLogger('heron')

router = APIRouter()


@router.get("/query")
async def query_memory(q: str = Query(...), db: Session = Depends(get_db)):
    """Consulta memória via RAG."""
    results = rag_query(q, n=4)
    return {"results": results}


@router.get("/all")
async def get_all_memories(db: Session = Depends(get_db)):
    """Lista todas as memórias."""
    memories = db.query(Memory).all()
    return [
        {"id": m.id, "key": m.key, "value": m.value[:100], "created_at": m.created_at.isoformat()}
        for m in memories
    ]


@router.delete("/{memory_id}")
async def delete_memory(memory_id: int, db: Session = Depends(get_db)):
    """Deleta memória."""
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memória não encontrada")
    
    db.delete(memory)
    db.commit()
    return {"deleted": True}


@router.post("")
async def add_memory(key: str, value: str, db: Session = Depends(get_db)):
    """Adiciona memória."""
    existing = db.query(Memory).filter(Memory.key == key).first()
    if existing:
        existing.value = value
    else:
        memory = Memory(key=key, value=value)
        db.add(memory)
    
    db.commit()
    return {"saved": True}