"""
Persistence for the multi-channel platform:

1. `conversations` table - a flat log of every message across every channel,
   used by the Streamlit analytics dashboard (volume, top intents, escalation
   rate, channel breakdown).
2. LangGraph's SqliteSaver - the actual agent *memory* (message state),
   keyed by thread_id = "{channel}:{user_id}", so a user's context persists
   across restarts and is isolated per channel.
"""
import sqlite3
import time
from contextlib import contextmanager
from langgraph.checkpoint.sqlite import SqliteSaver
from backend.multichannel.config import settings


@contextmanager
def get_conn():
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel TEXT,          -- 'web' | 'whatsapp'
                user_id TEXT,
                role TEXT,             -- 'user' | 'bot'
                message TEXT,
                intent TEXT,
                escalated INTEGER DEFAULT 0,
                created_at REAL
            )
            """
        )


def log_message(channel: str, user_id: str, role: str, message: str, intent: str = "", escalated: bool = False):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO conversations (channel, user_id, role, message, intent, escalated, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (channel, user_id, role, message, intent, int(escalated), time.time()),
        )


def get_checkpointer():
    """LangGraph checkpointer backed by the same sqlite file, giving every
    channel durable, resumable multi-turn memory per user."""
    conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
    return SqliteSaver(conn)
