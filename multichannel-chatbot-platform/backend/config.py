import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # LLM provider switch
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")  # "openai" or "ollama"
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    DB_PATH: str = os.getenv("DB_PATH", "platform.db")

    WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "helix_verify_me")

    @property
    def MOCK_MODE(self) -> bool:
        return not (self.WHATSAPP_TOKEN and self.WHATSAPP_PHONE_NUMBER_ID)

    # Per-tenant bot persona config. In a real multi-tenant SaaS this would
    # live in a `bots` table keyed by API key; kept as a dict here to keep
    # the demo self-contained.
    BOT_PERSONAS = {
        "default": {
            "name": "Helix Assistant",
            "system_prompt": (
                "You are a friendly, concise AI assistant for a business using Helix. "
                "Answer helpfully in 1-3 sentences. If you don't know something specific "
                "about the business, say so honestly and offer to connect a human."
            ),
        }
    }


settings = Settings()
