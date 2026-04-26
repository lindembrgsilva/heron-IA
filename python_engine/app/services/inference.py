import google.generativeai as genai
import logging
from typing import AsyncGenerator, List, Dict, Any, Optional

from app.core.prompting import BASE_SYSTEM_PROMPT

logger = logging.getLogger('heron')

GEMINI_MODELS = {
    'pro': 'gemini-1.5-pro',
    'flash': 'gemini-1.5-flash',
}


async def stream_response(
    user_message: str,
    history: List[Dict[str, str]],
    model: str = 'flash',
    api_key: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """Gera resposta via Google Gemini API com streaming."""
    if not api_key:
        from app.core.config import get_api_key
        api_key = get_api_key()

    if not api_key:
        yield "⚠️ API key não configurada. Por favor, configure sua API key nas configurações."
        return

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        logger.error(f"Erro ao configurar Gemini: {e}")
        yield f"Erro ao configurar Gemini API: {str(e)}"
        return

    from app.services.rag import query as rag_query

    rag_chunks = rag_query(user_message, n=3)
    rag_ctx = ''
    if rag_chunks:
        rag_ctx = '\n\nCONTEXTO RELEVANTE:\n' + '\n---\n'.join(rag_chunks)

    history_contents = []
    if rag_ctx:
        history_contents.append(rag_ctx)

    for h in history:
        role = h.get('role', 'user')
        content = h.get('content', '')
        history_contents.append(f"{role.upper()}: {content}")

    history_contents.append(f"USER: {user_message}")

    generation_config = {
        "temperature": 0.9,
        "max_output_tokens": 8192,
        "top_p": 0.95,
        "top_k": 40,
    }

    try:
        model_obj = genai.GenerativeModel(
            model_name=GEMINI_MODELS.get(model, 'gemini-1.5-flash'),
            system_instruction=BASE_SYSTEM_PROMPT,
            generation_config=generation_config
        )

        chat_session = model_obj.start_chat(history=history_contents)
        response = await chat_session.send_message_async(user_message)

        for chunk in response.parts:
            if hasattr(chunk, 'text') and chunk.text:
                yield chunk.text

    except Exception as e:
        logger.error(f"Erro na chamada Gemini: {e}")
        yield f"Erro ao conectar com Gemini API: {str(e)}"


async def list_available_models(api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lista modelos disponíveis (fixos para Gemini)."""
    if not api_key:
        from app.core.config import get_api_key
        api_key = get_api_key()

    return [
        {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'description': 'Mais capaz, janela de 2M tokens'},
        {'id': 'gemini-1.5-flash', 'name': 'Gemini 1.5 Flash', 'description': 'Rápido e eficiente'},
    ]


def check_gemini_connection(api_key: Optional[str] = None) -> bool:
    """Verifica se a API key é válida."""
    if not api_key:
        from app.core.config import get_api_key
        api_key = get_api_key()

    if not api_key:
        return False

    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        return len(models) > 0
    except Exception:
        return False