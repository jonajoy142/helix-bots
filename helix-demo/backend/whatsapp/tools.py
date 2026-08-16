"""
Tools exposed to the LangGraph agent. Each tool is a plain Python function
decorated with @tool so the LLM can call it by name with structured args.
"""
import re
from langchain_core.tools import tool
from backend.whatsapp.db import get_order, create_escalation
from backend.whatsapp.rag import search_faq


@tool
def lookup_order_status(order_id: str) -> str:
    """Look up the current status of a customer's order using their order ID (format ORDxxxx)."""
    order_id = order_id.strip().upper()
    order = get_order(order_id)
    if not order:
        return f"I couldn't find any order with ID {order_id}. Could you double check the ID?"
    return (
        f"Order {order['order_id']} ({order['product_name']}) is currently "
        f"'{order['status']}'. Estimated: {order['eta']}."
    )


@tool
def search_knowledge_base(question: str) -> str:
    """Search the store's FAQ knowledge base for an answer to a general question
    (shipping, returns, payment methods, business hours, etc.)."""
    result = search_faq(question)
    return result if result else "No matching FAQ found."


@tool
def escalate_to_human(user_phone: str, reason: str, last_message: str) -> str:
    """Create a support ticket and hand the conversation off to a human agent.
    Use this when the customer is frustrated, asks for a human explicitly, or the
    request is something the bot cannot resolve (e.g. refunds, complaints)."""
    create_escalation(user_phone, reason, last_message)
    return "I've created a ticket and a support agent will reach out to you shortly on this WhatsApp number."


def extract_order_id(text: str):
    match = re.search(r"\bORD\d{3,}\b", text.upper())
    return match.group(0) if match else None


ALL_TOOLS = [lookup_order_status, search_knowledge_base, escalate_to_human]
