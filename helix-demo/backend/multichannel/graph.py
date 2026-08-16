"""
The channel-agnostic agent core.

This is the key architectural idea of this project: ONE LangGraph agent
definition powers both the website widget and WhatsApp. Channels only differ
in (a) how a message arrives (HTTP POST vs Meta webhook) and (b) how the
reply is delivered (JSON response vs WhatsApp Cloud API call) — see
backend/main.py. The agent itself, its tools, and its memory are shared.

This mirrors how a real platform like Helix is built: one bot brain,
many channel adapters.
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

from backend.multichannel.config import settings
from backend.multichannel.memory import get_checkpointer
from backend.multichannel.llm_provider import get_llm

ESCALATION_KEYWORDS = ["human", "agent", "manager", "not helpful", "angry", "refund"]


@tool
def request_human_handoff(reason: str) -> str:
    """Escalate the conversation to a human agent. Use when the user explicitly
    asks for a person, or is clearly frustrated / the bot can't help."""
    return "Got it — I'm flagging this for a member of our team to follow up with you shortly."


TOOLS = [request_human_handoff]


class PlatformState(TypedDict):
    channel: str            # "web" | "whatsapp"
    user_id: str
    message: str
    persona_key: str
    response: Optional[str]
    escalated: bool


def _llm():
    # Note: Tool calling reliability depends on the Ollama model supporting function
    # calling well. Recommend llama3.1 or qwen2.5 rather than smaller/older models.
    return get_llm(temperature=0.4).bind_tools(TOOLS)


def agent_node(state: PlatformState) -> PlatformState:
    persona = settings.BOT_PERSONAS.get(state["persona_key"], settings.BOT_PERSONAS["default"])
    lower = state["message"].lower()
    forced_escalate = any(k in lower for k in ESCALATION_KEYWORDS)

    messages = [
        SystemMessage(content=persona["system_prompt"]),
        HumanMessage(content=state["message"]),
    ]
    result = _llm().invoke(messages)

    tool_called = bool(result.tool_calls)
    state["escalated"] = forced_escalate or tool_called

    if state["escalated"]:
        state["response"] = "I'm connecting you with a member of our team — they'll follow up with you shortly here."
    else:
        state["response"] = result.content.strip()
    return state


def build_graph():
    graph = StateGraph(PlatformState)
    graph.add_node("agent", agent_node)
    graph.set_entry_point("agent")
    graph.add_edge("agent", END)
    return graph.compile(checkpointer=get_checkpointer())


_graph = None


def run_agent(channel: str, user_id: str, message: str, persona_key: str = "default"):
    global _graph
    if _graph is None:
        _graph = build_graph()

    thread_id = f"{channel}:{user_id}"
    config = {"configurable": {"thread_id": thread_id}}
    result = _graph.invoke(
        {"channel": channel, "user_id": user_id, "message": message, "persona_key": persona_key,
         "response": None, "escalated": False},
        config=config,
    )
    return result["response"], result["escalated"]
