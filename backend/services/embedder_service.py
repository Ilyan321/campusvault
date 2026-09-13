import logging
from typing import List, Union
from fastembed import TextEmbedding
from config import EMBEDDING_MODEL_NAME

logger = logging.getLogger("campusvault.embedder")

_model: Union[TextEmbedding, None] = None

def get_model() -> TextEmbedding:
    global _model
    if _model is None:
        logger.info(f"Loading FastEmbed ONNX embedding model: {EMBEDDING_MODEL_NAME}")
        # BAAI/bge-small-en-v1.5 produces normalized 384-dimensional vectors
        _model = TextEmbedding(model_name=EMBEDDING_MODEL_NAME)
    return _model

def get_embedding(text: str) -> List[float]:
    """
    Generates a normalized 384-dim vector embedding for a single text string using FastEmbed.
    """
    if not text or not text.strip():
        return [0.0] * 384
    model = get_model()
    embeddings = list(model.embed([text]))
    return embeddings[0].tolist()

def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generates normalized 384-dim vector embeddings for a list of text strings in batch.
    """
    if not texts:
        return []
    model = get_model()
    embeddings = list(model.embed(texts, batch_size=32))
    return [e.tolist() for e in embeddings]
