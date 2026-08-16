"""
RAG layer over the FAQ knowledge base.

Keeps an in-memory numpy matrix of OpenAI embeddings and ranks by cosine
similarity. That is plenty for a few hundred FAQs rebuilt on boot, and avoids
pulling a vector-search library into the serverless bundle; at scale you'd move
to a managed vector DB (Pinecone / pgvector) and only re-embed changed rows.
"""
import numpy as np

from backend.whatsapp.db import all_faqs
from backend.whatsapp.llm_provider import get_embeddings

_documents: list[str] = []
_matrix: np.ndarray | None = None


def build_index():
    global _documents, _matrix
    faqs = all_faqs()
    _documents = [f"Q: {f['question']}\nA: {f['answer']}" for f in faqs]
    if not _documents:
        _matrix = None
        return
    vectors = np.asarray(get_embeddings().embed_documents(_documents), dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    _matrix = vectors / np.maximum(norms, 1e-12)


def search_faq(query: str, k: int = 2) -> str:
    """Returns the top-k matching FAQ answers concatenated, or '' if index is empty."""
    if _matrix is None:
        build_index()
    if _matrix is None:
        return ""
    query_vector = np.asarray(get_embeddings().embed_query(query), dtype=np.float32)
    query_vector /= max(float(np.linalg.norm(query_vector)), 1e-12)
    scores = _matrix @ query_vector
    top = np.argsort(scores)[::-1][:k]
    return "\n\n".join(_documents[i] for i in top)
