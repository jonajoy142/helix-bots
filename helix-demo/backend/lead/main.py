"""
FastAPI app exposing a stateful lead-qualification chat session.

Run:
    uvicorn app.main:app --reload --port 8001

Flow:
    POST /session/start                 -> creates a session_id
    POST /session/{session_id}/message  -> send a chat message, get bot reply
                                             + current lead profile + score
    When ready_for_handoff flips true, the lead is auto-saved (Sheets/CSV)
    and, if hot, an automation webhook fires.
"""
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.lead.agent import QualificationAgent
from backend.lead.scoring import score_lead, classify
from backend.lead.sheets_client import save_lead
from backend.lead.notify import notify_hot_lead
from backend.lead.config import settings

app = FastAPI(title="AI Lead Qualification Agent")

# CORS configuration for Helix frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS: dict[str, QualificationAgent] = {}


class MessageRequest(BaseModel):
    message: str


@app.post("/session/start")
def start_session():
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = QualificationAgent()
    return {
        "session_id": session_id,
        "bot_message": "Hi! Thanks for reaching out 👋 What are you hoping to solve with an AI chatbot / automation setup?",
    }


@app.post("/session/{session_id}/message")
def send_message(session_id: str, req: MessageRequest):
    agent = SESSIONS.get(session_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Unknown session. Call /session/start first.")

    lead = agent.step(req.message)
    score = score_lead(lead)
    category = classify(score, settings.HOT_LEAD_SCORE_THRESHOLD)

    result = {
        "bot_message": lead.next_question or "Thanks — I've got what I need! A member of our team will reach out shortly.",
        "lead_profile": lead.model_dump(),
        "score": score,
        "category": category,
        "ready_for_handoff": lead.ready_for_handoff,
    }

    if lead.ready_for_handoff:
        save_lead(lead, score, category)
        if category == "hot":
            notify_hot_lead(lead, score)

    return result


@app.get("/health")
def health():
    return {"status": "ok", "sheets_enabled": settings.SHEETS_ENABLED}
