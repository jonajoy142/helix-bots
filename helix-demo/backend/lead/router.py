"""
Lead qualification router for unified API.
"""
import uuid
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.lead.agent import QualificationAgent
from backend.lead.scoring import score_lead, classify
from backend.lead.sheets_client import save_lead
from backend.lead.notify import notify_hot_lead
from backend.lead.config import settings

router = APIRouter(prefix="/lead", tags=["lead"])
logger = logging.getLogger("lead_router")

# NOTE: In serverless, sessions won't persist across function invocations.
# For production Vercel deployment, this should use a proper session store like Redis.
# For demo purposes, we'll use in-memory sessions which work for single-session testing.
SESSIONS: dict[str, QualificationAgent] = {}


class MessageRequest(BaseModel):
    message: str


@router.post("/session/start")
def start_session():
    try:
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = QualificationAgent()
        return {
            "session_id": session_id,
            "bot_message": "Hi! Thanks for reaching out 👋 What are you hoping to solve with an AI chatbot / automation setup?",
        }
    except Exception as e:
        logger.error(f"Session start error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start session")


@router.post("/session/{session_id}/message")
def send_message(session_id: str, req: MessageRequest):
    try:
        if not req.message or not req.message.strip():
            raise HTTPException(status_code=400, detail="Message is required")
            
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
            try:
                save_lead(lead, score, category)
            except Exception as e:
                logger.error(f"Failed to save lead: {e}")
            if category == "hot":
                try:
                    notify_hot_lead(lead, score)
                except Exception as e:
                    logger.error(f"Failed to notify hot lead: {e}")

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Message processing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")


@router.get("/health")
def health():
    return {"status": "ok", "sheets_enabled": settings.SHEETS_ENABLED}
