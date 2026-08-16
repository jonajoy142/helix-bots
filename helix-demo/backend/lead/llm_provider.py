"""
Single place that decides whether we talk to OpenAI or a local Ollama model.
Everything else in the app (agent.py) calls get_llm() and doesn't care which
provider is active.
"""
from backend.lead.config import settings


def get_llm(temperature: float = 0):
    if settings.LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=temperature,
        )
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=temperature,
        api_key=settings.OPENAI_API_KEY or "sk-placeholder",
    )
