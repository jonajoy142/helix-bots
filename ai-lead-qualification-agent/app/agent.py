"""
The lead-qualification agent.

Design: rather than a tool-calling ReAct agent, this uses LangChain's
structured-output pattern — on every turn, the LLM re-reads the *entire*
conversation and re-emits a full LeadProfile. This is simpler than tracking
slot-filling state by hand, self-corrects if the lead changes their answer,
and gives you a clean, typed object to score and persist after every message.
"""
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.models import LeadProfile
from app.config import settings
from app.llm_provider import get_llm

SYSTEM_PROMPT = """You are Helix's AI sales qualification assistant, chatting with a
prospective customer on WhatsApp/website chat. Your job is to warmly gather enough
information to qualify them using BANT (Budget, Authority, Need, Timeline) — WITHOUT
sounding like an interrogation. Ask ONE natural question at a time, acknowledge what
they said, and keep messages short (1-3 sentences, WhatsApp style).

Mark ready_for_handoff=true only once you have a reasonable read on budget, authority,
need, and timeline (they don't all need exact values — 'unknown' is fine for at most one).
"""


class QualificationAgent:
    def __init__(self):
        # NOTE: Structured output (Pydantic schema enforcement) is less reliable with
        # local Ollama models than with OpenAI. If JSON keeps failing to parse, consider
        # switching LLM_PROVIDER=openai, or try a larger/newer Ollama model that supports
        # tool calling well (e.g. llama3.1:70b or qwen2.5).
        llm = get_llm(temperature=0.3)
        self.structured_llm = llm.with_structured_output(LeadProfile)
        self.history: list = [SystemMessage(content=SYSTEM_PROMPT)]

    def step(self, user_message: str) -> LeadProfile:
        self.history.append(HumanMessage(content=user_message))
        profile = self.structured_llm.invoke(self.history)
        # Feed the assistant's chosen next question back into history so the
        # conversation stays coherent turn to turn.
        if profile.next_question:
            self.history.append(AIMessage(content=profile.next_question))
        return profile
