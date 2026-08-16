"""
Centralized configuration. Everything is read from environment variables so the
same code runs locally (mock mode), in Docker, or in production behind the
WhatsApp Cloud API — you only ever change .env, never the code.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- LLM ---
    # --- LLM provider switch ---
    # For Vercel production, default to OpenAI. For local development, can use Ollama.
    # Set LLM_PROVIDER=ollama in .env for local Ollama development.
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # "openai" or "ollama"
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # --- WhatsApp Cloud API (Meta) ---
    WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "helix_verify_me")
    WHATSAPP_API_VERSION: str = os.getenv("WHATSAPP_API_VERSION", "v20.0")

    # If no real WhatsApp credentials are set, the client runs in MOCK_MODE:
    # it logs the outgoing message instead of calling the Meta Graph API.
    # This lets you demo/run the whole thing with zero external accounts.
    @property
    def MOCK_MODE(self) -> bool:
        return not (self.WHATSAPP_TOKEN and self.WHATSAPP_PHONE_NUMBER_ID)

    # --- App ---
    DB_PATH: str = os.getenv("DB_PATH", "support_bot.db")
    ESCALATION_KEYWORDS = ["talk to human", "agent please", "not helpful", "refund now", "angry", "complaint"]


settings = Settings()
