"""
Thin wrapper over Meta's WhatsApp Cloud API.

Runs in MOCK_MODE (just logs to console) when no WHATSAPP_TOKEN /
WHATSAPP_PHONE_NUMBER_ID are configured, so you can demo the entire bot
end-to-end without a Meta Business account. Flip MOCK_MODE off by filling
.env and it calls the real Graph API.
"""
import logging
import requests
from backend.whatsapp.config import settings

logger = logging.getLogger("whatsapp_client")
logging.basicConfig(level=logging.INFO)


def send_whatsapp_message(to: str, body: str):
    if settings.MOCK_MODE:
        logger.info(f"[MOCK WHATSAPP SEND] -> {to}: {body}")
        return {"mock": True, "to": to, "body": body}

    url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    if not resp.ok:
        print("WHATSAPP API ERROR:", resp.status_code)
        print("WHATSAPP API RESPONSE:", resp.text)

    resp.raise_for_status()
    return resp.json()


def parse_incoming_webhook(payload: dict):
    """Extracts (from_number, message_text) from a Meta webhook POST body.
    Returns None if the payload isn't a user text message (e.g. delivery receipts)."""
    try:
        entry = payload["entry"][0]
        change = entry["changes"][0]["value"]
        messages = change.get("messages")
        if not messages:
            return None
        msg = messages[0]
        if msg.get("type") != "text":
            return None
        return msg["from"], msg["text"]["body"]
    except (KeyError, IndexError):
        return None
