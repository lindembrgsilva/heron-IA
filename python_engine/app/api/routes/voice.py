import logging
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.voice import transcribe, synthesize

logger = logging.getLogger('heron')

router = APIRouter()


class SynthesizeRequest(BaseModel):
    text: str
    language: str = "pt"


@router.post("/transcribe")
async def voice_transcribe(file: UploadFile = File(...)):
    """Transcreve áudio com Whisper."""
    audio_bytes = await file.read()
    
    try:
        text = await transcribe(audio_bytes, language="pt")
        return {"transcription": text}
    except Exception as e:
        logger.error(f"Erro na transcrição: {e}")
        return {"transcription": "", "error": str(e)}


@router.post("/synthesize")
async def voice_synthesize(req: SynthesizeRequest):
    """Sintetiza texto com TTS."""
    try:
        audio_bytes = await synthesize(req.text, req.language)
        
        return StreamingResponse(
            content=audio_bytes,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=output.wav"}
        )
    except Exception as e:
        logger.error(f"Erro na síntese: {e}")
        raise HTTPException(status_code=500, detail=str(e))