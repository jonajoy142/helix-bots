"""
RAG layer over the FAQ knowledge base.

Uses an in-memory FAISS index built from OpenAI embeddings. FAISS in-memory
is fine for a few hundred FAQs and rebuilding on boot; at scale you'd move to
a managed vector DB (Pinecone / pgvector) and only re-embed changed rows.
"""
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from backend.whatsapp.db import all_faqs
from backend.whatsapp.llm_provider import get_embeddings

_vectorstore = None


def build_index():
    global _vectorstore
    faqs = all_faqs()
    docs = [
        Document(page_content=f"Q: {f['question']}\nA: {f['answer']}", metadata={"answer": f["answer"]})
        for f in faqs
    ]
    if not docs:
        _vectorstore = None
        return
    embeddings = get_embeddings()
    _vectorstore = FAISS.from_documents(docs, embeddings)


def search_faq(query: str, k: int = 2) -> str:
    """Returns the top-k matching FAQ answers concatenated, or '' if index is empty."""
    global _vectorstore
    if _vectorstore is None:
        build_index()
    if _vectorstore is None:
        return ""
    results = _vectorstore.similarity_search(query, k=k)
    return "\n\n".join(r.page_content for r in results)
