"""
Fires a webhook (Zapier / Make / n8n / a Slack incoming webhook / your CRM's
inbound endpoint — anything that accepts JSON) whenever a HOT lead is
qualified, so a sales rep gets pinged in real time instead of checking a
spreadsheet. If AUTOMATION_WEBHOOK_URL isn't set, we just log the payload —
this is the "automations" layer Helix sells on top of the chatbot.
"""
import logging
import requests
from app.config import settings
from app.models import LeadProfile

logger = logging.getLogger("notify")
logging.basicConfig(level=logging.INFO)


def notify_hot_lead(lead: LeadProfile, score: int):
    payload = {
        "event": "hot_lead_qualified",
        "name": lead.name,
        "company": lead.company,
        "email": lead.email,
        "phone": lead.phone,
        "score": score,
        "summary": lead.summary,
    }

    if not settings.AUTOMATION_WEBHOOK_URL:
        logger.info(f"[MOCK AUTOMATION TRIGGER] Would notify sales team: {payload}")
        return {"mock": True, "payload": payload}

    resp = requests.post(settings.AUTOMATION_WEBHOOK_URL, json=payload, timeout=10)
    resp.raise_for_status()
    return {"mock": False, "status_code": resp.status_code}
