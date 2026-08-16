"""
Multichannel bot router for unified API.
"""
import logging
from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel

from backend.multichannel.config import settings
from backend.multichannel.memory import init_db, log_message
from backend.multichannel.graph import run_agent
from backend.multichannel.whatsapp_client import send_whatsapp_message, parse_incoming_webhook

router = APIRouter(prefix="/multichannel", tags=["multichannel"])
logger = logging.getLogger("multichannel_router")


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    escalated: bool


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        if not req.user_id or not req.message:
            raise HTTPException(status_code=400, detail="user_id and message are required")
            
        log_message("web", req.user_id, "user", req.message)
        reply, escalated = run_agent("web", req.user_id, req.message)
        log_message("web", req.user_id, "bot", reply, escalated=escalated)
        return ChatResponse(reply=reply, escalated=escalated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")


@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(alias="hub.mode", default=""),
    hub_challenge: str = Query(alias="hub.challenge", default=""),
    hub_verify_token: str = Query(alias="hub.verify_token", default=""),
):
    try:
        if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
            return PlainTextResponse(hub_challenge)
        logger.warning(f"Webhook verification failed: mode={hub_mode}, token={hub_verify_token}")
        raise HTTPException(status_code=403, detail="Verification failed")
    except Exception as e:
        logger.error(f"Webhook verification error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/webhook")
async def receive_webhook(request: Request):
    try:
        payload = await request.json()
        parsed = parse_incoming_webhook(payload)
        if not parsed:
            return {"status": "ignored"}

        from_number, text = parsed
        log_message("whatsapp", from_number, "user", text)
        reply, escalated = run_agent("whatsapp", from_number, text)
        log_message("whatsapp", from_number, "bot", reply, escalated=escalated)
        send_whatsapp_message(from_number, reply)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return JSONResponse(
            {"status": "error", "message": "Failed to process webhook"},
            status_code=500
        )


@router.get("/health")
def health():
    return {"status": "ok", "mock_mode": settings.MOCK_MODE}


def startup():
    init_db()
