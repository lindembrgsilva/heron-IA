import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.core.config import get_rag_chunk_size, get_rag_overlap

logger = logging.getLogger('heron')

_collection = None
_embedding_model = None

DATA_PATH = Path(__file__).resolve().parents[3].parent / 'data'
VECTORSTORE_PATH = DATA_PATH / 'vectorstore'
VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)


def get_collection():
    """Retorna ChromaDB collection singleton."""
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=str(VECTORSTORE_PATH))
        _collection = client.get_or_create_collection("heron_memory")
    return _collection


def get_embedding_model():
    """Retorna modelo de embeddings singleton."""
    global _embedding_model
    if _embedding_model is None:
        embeddings_path = Path(__file__).resolve().parents[3].parent / 'models' / 'embeddings'
        if embeddings_path.exists():
            _embedding_model = SentenceTransformer(str(embeddings_path))
        else:
            _embedding_model = SentenceTransformer("nomic-ai/nomic-embed-text-v1")
        logger.info("Modelo de embeddings carregado")
    return _embedding_model


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Divide texto em chunks."""
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    
    return chunks


def index_document(doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None):
    """Indexa documento no ChromaDB."""
    collection = get_collection()
    model = get_embedding_model()
    
    chunks = _chunk_text(text)
    embeddings = model.encode(chunks).tolist()
    
    metadatas = [metadata or {} for _ in chunks]
    for i, m in enumerate(metadatas):
        m['chunk_index'] = i
    
    collection.upsert(
        ids=[f"{doc_id}_{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    logger.info(f"Documento {doc_id} indexado com {len(chunks)} chunks")


def query(text: str, n: int = 4) -> List[str]:
    """Consulta documentos similares."""
    collection = get_collection()
    model = get_embedding_model()
    
    query_embedding = model.encode([text]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n
    )
    
    return results.get('documents', [[]])[0]


def index_conversation(session_id: str, messages: List[Dict[str, str]]):
    """Indexa conversa no ChromaDB."""
    text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    index_document(
        doc_id=f"session_{session_id}",
        text=text,
        metadata={"type": "conversation", "session_id": session_id}
    )


def delete_document(doc_id: str):
    """Deleta documento do ChromaDB."""
    collection = get_collection()
    collection.delete(where={"$or": [
        {"doc_id": doc_id},
        {"session_id": doc_id.replace("session_", "")}
    ]})