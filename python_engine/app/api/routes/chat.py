import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.session import ChatMessage
from app.services.inference import stream_response, list_available_models

logger = logging.getLogger('heron')

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    model: str = "flash"
    system_instructions: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


@router.post("")
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """Endpoint de chat via POST."""
    history = db.query(ChatMessage).order_by(ChatMessage.created_at).all()
    history_data = [{"role": m.role, "content": m.content} for m in history]
    
    response_parts = []
    async for part in stream_response(req.message, history_data, req.model):
        response_parts.append(part)
    
    reply = "".join(response_parts)
    
    user_msg = ChatMessage(role="user", content=req.message, model=req.model)
    assistant_msg = ChatMessage(role="assistant", content=reply, model=req.model)
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()
    
    return ChatResponse(reply=reply)


@router.get("/history")
async def get_history(db: Session = Depends(get_db)):
    """Retorna histórico de chat."""
    messages = db.query(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(100).all()
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content[:200] + "..." if len(m.content) > 200 else m.content,
            "model": m.model,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]


@router.delete("/history/{msg_id}")
async def delete_history(msg_id: int, db: Session = Depends(get_db)):
    """Deleta mensagem do histórico."""
    msg = db.query(ChatMessage).filter(ChatMessage.id == msg_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    
    db.delete(msg)
    db.commit()
    return {"deleted": True}


@router.get("/models")
async def get_models():
    """Lista modelos disponíveis."""
    return {"available_models": await list_available_models()}