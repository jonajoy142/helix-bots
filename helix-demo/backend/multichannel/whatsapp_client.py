import logging
import requests
from backend.multichannel.config import settings

logger = logging.getLogger("whatsapp_client")
logging.basicConfig(level=logging.INFO)


def send_whatsapp_message(to: str, body: str):
    if settings.MOCK_MODE:
        logger.info(f"[MOCK WHATSAPP SEND] -> {to}: {body}")
        return {"mock": True}

    url = f"https://graph.facebook.com/v20.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}}
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def parse_incoming_webhook(payload: dict):
    try:
        change = payload["entry"][0]["changes"][0]["value"]
        messages = change.get("messages")
        if not messages:
            return None
        msg = messages[0]
        if msg.get("type") != "text":
            return None
        return msg["from"], msg["text"]["body"]
    except (KeyError, IndexError):
        return None
