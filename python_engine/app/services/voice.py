import io
import logging
import os
import tempfile
from typing import Optional

logger = logging.getLogger('heron')

_stt_model = None
_tts_model = None

MODELS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')


def get_stt():
    """Retorna modelo Whisper singleton."""
    global _stt_model
    if _stt_model is None:
        try:
            from faster_whisper import WhisperModel
            _stt_model = WhisperModel(
                "medium",
                device="cuda",
                compute_type="float16"
            )
            logger.info("Modelo Whisper Medium carregado (CUDA)")
        except Exception as e:
            logger.warning(f"CUDA não disponível, usando CPU: {e}")
            _stt_model = WhisperModel(
                "medium",
                device="cpu",
                compute_type="int8"
            )
            logger.info("Modelo Whisper Medium carregado (CPU)")
    return _stt_model


def get_tts():
    """Retorna modelo TTS singleton."""
    global _tts_model
    if _tts_model is None:
        try:
            from TTS.api import TTS
            tts_path = os.path.join(MODELS_PATH, 'tts', 'xtts-v2')
            if os.path.exists(tts_path):
                _tts_model = TTS(model_path=tts_path, gpu=True)
            else:
                _tts_model = TTS(model_name="tts_models/multilingual/male/vits_拟似1")
            logger.info("Modelo XTTS-v2 carregado")
        except Exception as e:
            logger.error(f"Erro ao carregar TTS: {e}")
            raise
    return _tts_model


async def transcribe(audio_bytes: bytes, language: str = "pt") -> str:
    """Transcreve áudio usando Whisper."""
    model = get_stt()
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    
    try:
        segments, info = model.transcribe(tmp_path, language=language)
        result = " ".join([seg.text for seg in segments])
        return result.strip()
    finally:
        os.unlink(tmp_path)


async def synthesize(text: str, language: str = "pt") -> bytes:
    """Sintetiza texto usando XTTS-v2."""
    tts = get_tts()
    ref_wav = os.path.join(MODELS_PATH, 'heron_voice_ref.wav')
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        output_path = tmp.name
    
    try:
        tts.tts_to_file(
            text=text,
            file_path=output_path,
            speaker_wav=ref_wav if os.path.exists(ref_wav) else None,
            language=language
        )
        with open(output_path, 'rb') as f:
            return f.read()
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)