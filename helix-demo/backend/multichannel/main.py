"""
Two thin channel adapters sitting on top of ONE shared agent (backend/graph.py):

  - POST /chat        -> website widget (frontend/widget.html posts here)
  - GET/POST /webhook -> WhatsApp Cloud API

Run:
    uvicorn backend.main:app --reload --port 8002
"""
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.multichannel.config import settings
from backend.multichannel.memory import init_db, log_message
from backend.multichannel.graph import run_agent
from backend.multichannel.whatsapp_client import send_whatsapp_message, parse_incoming_webhook

app = FastAPI(title="Multi-Channel AI Chatbot Platform")

# Allow the widget (served from file:// or any origin during local dev) to call /chat
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def startup():
    init_db()


# ---------------- Website widget channel ----------------
class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    escalated: bool


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    log_message("web", req.user_id, "user", req.message)
    reply, escalated = run_agent("web", req.user_id, req.message)
    log_message("web", req.user_id, "bot", reply, escalated=escalated)
    return ChatResponse(reply=reply, escalated=escalated)


# ---------------- WhatsApp channel ----------------
@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(alias="hub.mode", default=""),
    hub_challenge: str = Query(alias="hub.challenge", default=""),
    hub_verify_token: str = Query(alias="hub.verify_token", default=""),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def receive_webhook(request: Request):
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


@app.get("/health")
def health():
    return {"status": "ok", "mock_mode": settings.MOCK_MODE}
