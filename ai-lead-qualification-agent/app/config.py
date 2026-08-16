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

    # Google Sheets (optional). If GOOGLE_SHEET_ID or credentials are missing,
    # the app automatically falls back to writing leads into data/leads.csv,
    # so the whole pipeline is demoable with zero Google Cloud setup.
    GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")
    GOOGLE_CREDENTIALS_JSON: str = os.getenv("GOOGLE_CREDENTIALS_JSON", "")

    # Automation webhook (Zapier / Make / n8n / your own CRM endpoint).
    # If unset, the notifier just logs what it *would* have sent.
    AUTOMATION_WEBHOOK_URL: str = os.getenv("AUTOMATION_WEBHOOK_URL", "")

    HOT_LEAD_SCORE_THRESHOLD: int = int(os.getenv("HOT_LEAD_SCORE_THRESHOLD", "70"))

    @property
    def SHEETS_ENABLED(self) -> bool:
        return bool(self.GOOGLE_SHEET_ID and self.GOOGLE_CREDENTIALS_JSON)


settings = Settings()
