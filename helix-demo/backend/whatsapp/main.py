"""
FastAPI entrypoint.

Two ways to talk to the bot:
  1. GET/POST /webhook   -> real WhatsApp Cloud API webhook (verification + incoming messages)
  2. POST /chat          -> plain JSON endpoint for local testing / a web widget, no WhatsApp needed

Run:
    uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from backend.whatsapp.config import settings
from backend.whatsapp.db import init_db, log_message
from backend.whatsapp.graph import run_bot
from backend.whatsapp.whatsapp_client import send_whatsapp_message, parse_incoming_webhook

app = FastAPI(title="Helix WhatsApp AI Support Bot")


@app.on_event("startup")
def startup():
    init_db()


# ---------- WhatsApp webhook verification (Meta calls this once on setup) ----------
@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(alias="hub.mode", default=""),
    hub_challenge: str = Query(alias="hub.challenge", default=""),
    hub_verify_token: str = Query(alias="hub.verify_token", default=""),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


# ---------- WhatsApp incoming message webhook ----------
@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    parsed = parse_incoming_webhook(payload)
    if not parsed:
        return {"status": "ignored"}

    from_number, text = parsed
    log_message(from_number, "user", text)

    reply = run_bot(from_number, text)

    log_message(from_number, "bot", reply)
    send_whatsapp_message(from_number, reply)
    return {"status": "ok"}


# ---------- Plain chat endpoint for local testing / a web widget ----------
class ChatRequest(BaseModel):
    user_phone: str
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    log_message(req.user_phone, "user", req.message)
    reply = run_bot(req.user_phone, req.message)
    log_message(req.user_phone, "bot", reply)
    return ChatResponse(reply=reply)


@app.get("/health")
def health():
    return {"status": "ok", "mock_mode": settings.MOCK_MODE}
