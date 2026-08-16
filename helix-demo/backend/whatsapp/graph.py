"""
The LangGraph agent.

Architecture (shows why a graph beats a single prompt-and-hope chatbot):

    START
      |
      v
   [classify_intent]  -> tags the message as order_status / faq / escalation / chit_chat
      |
      v
   [route]  (conditional edge)
      |----------------|----------------|----------------|
      v                v                v                v
  [order_node]     [faq_node]     [escalate_node]   [chitchat_node]
      \\               |                |                /
       -----------------> [respond] <----------------------
                              |
                             END

Each node is small and testable in isolation. State is a typed dict that
flows through the graph and is checkpointed per-user so conversations survive
process restarts (important for a WhatsApp bot — Meta will retry webhooks).
"""
from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from backend.whatsapp.tools import lookup_order_status, search_knowledge_base, escalate_to_human, extract_order_id
from backend.whatsapp.config import settings


class BotState(TypedDict):
    user_phone: str
    message: str
    intent: Optional[Literal["order_status", "faq", "escalation", "chit_chat"]]
    response: Optional[str]
    order_id: Optional[str]


from backend.whatsapp.llm_provider import get_llm
llm = get_llm(temperature=0)

INTENT_PROMPT = """Classify the user's WhatsApp message into exactly one label:
- order_status: asking about an order, delivery, tracking, cancellation
- faq: general question about shipping, returns, payments, hours, policies
- escalation: frustrated, wants a human, complaint, refund dispute
- chit_chat: greetings, thanks, anything else

Reply with only the label, nothing else.

Message: {message}"""


def classify_intent(state: BotState) -> BotState:
    msg = state["message"]
    lower = msg.lower()
    if any(k in lower for k in settings.ESCALATION_KEYWORDS):
        state["intent"] = "escalation"
        return state

    order_id = extract_order_id(msg)
    if order_id:
        state["order_id"] = order_id
        state["intent"] = "order_status"
        return state

    result = llm.invoke([HumanMessage(content=INTENT_PROMPT.format(message=msg))])
    label = result.content.strip().lower()
    if label not in ("order_status", "faq", "escalation", "chit_chat"):
        label = "faq"
    state["intent"] = label
    return state


def route(state: BotState) -> str:
    return state["intent"]


def order_node(state: BotState) -> BotState:
    order_id = state.get("order_id") or "UNKNOWN"
    if order_id == "UNKNOWN":
        state["response"] = "Sure — could you share your order ID? It looks like ORD1001."
        return state
    state["response"] = lookup_order_status.invoke({"order_id": order_id})
    return state


def faq_node(state: BotState) -> BotState:
    kb_result = search_knowledge_base.invoke({"question": state["message"]})
    if kb_result == "No matching FAQ found.":
        state["response"] = (
            "I'm not fully sure about that — would you like me to connect you with a support agent?"
        )
        return state

    prompt = (
        "You are Helix's friendly WhatsApp support assistant. Using ONLY the "
        "knowledge base snippets below, answer the customer's question in 1-2 short, "
        "warm sentences suitable for WhatsApp.\n\n"
        f"Knowledge base:\n{kb_result}\n\nCustomer question: {state['message']}"
    )
    result = llm.invoke([SystemMessage(content=prompt)])
    state["response"] = result.content.strip()
    return state


def escalate_node(state: BotState) -> BotState:
    state["response"] = escalate_to_human.invoke(
        {
            "user_phone": state["user_phone"],
            "reason": "Customer requested human support or expressed frustration",
            "last_message": state["message"],
        }
    )
    return state


def chitchat_node(state: BotState) -> BotState:
    result = llm.invoke(
        [
            SystemMessage(content="You are Helix's warm, concise WhatsApp support bot. Reply in 1 short sentence."),
            HumanMessage(content=state["message"]),
        ]
    )
    state["response"] = result.content.strip()
    return state


def build_graph():
    graph = StateGraph(BotState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("order_node", order_node)
    graph.add_node("faq_node", faq_node)
    graph.add_node("escalate_node", escalate_node)
    graph.add_node("chitchat_node", chitchat_node)

    graph.set_entry_point("classify_intent")
    graph.add_conditional_edges(
        "classify_intent",
        route,
        {
            "order_status": "order_node",
            "faq": "faq_node",
            "escalation": "escalate_node",
            "chit_chat": "chitchat_node",
        },
    )
    graph.add_edge("order_node", END)
    graph.add_edge("faq_node", END)
    graph.add_edge("escalate_node", END)
    graph.add_edge("chitchat_node", END)

    # MemorySaver checkpoints state per thread_id (we use the user's phone number)
    # so multi-turn context and interrupted webhooks resume correctly.
    return graph.compile(checkpointer=MemorySaver())


bot_graph = build_graph()


def run_bot(user_phone: str, message: str) -> str:
    config = {"configurable": {"thread_id": user_phone}}
    result = bot_graph.invoke(
        {"user_phone": user_phone, "message": message, "intent": None, "response": None, "order_id": None},
        config=config,
    )
    return result["response"]
