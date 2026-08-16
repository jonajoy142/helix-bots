"""
Lightweight persistence layer using plain sqlite3 (no ORM overhead — keeps
the demo dependency-free and easy to inspect with `sqlite3 support_bot.db`).

Tables:
  orders          -> mock e-commerce order data the bot can look up
  faqs            -> knowledge base used by the RAG node
  conversations   -> per-user message log (for the analytics dashboard / audit trail)
  escalations     -> tickets created when the agent hands off to a human
"""
import sqlite3
import time
from contextlib import contextmanager
from backend.whatsapp.config import settings


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
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_phone TEXT,
                product_name TEXT,
                status TEXT,
                eta TEXT
            );

            CREATE TABLE IF NOT EXISTS faqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_phone TEXT,
                role TEXT,           -- 'user' | 'bot'
                message TEXT,
                intent TEXT,
                created_at REAL
            );

            CREATE TABLE IF NOT EXISTS escalations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_phone TEXT,
                reason TEXT,
                last_message TEXT,
                status TEXT DEFAULT 'open',
                created_at REAL
            );
            """
        )


def log_message(user_phone: str, role: str, message: str, intent: str = ""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO conversations (user_phone, role, message, intent, created_at) VALUES (?,?,?,?,?)",
            (user_phone, role, message, intent, time.time()),
        )


def get_order(order_id: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
        return dict(row) if row else None


def create_escalation(user_phone: str, reason: str, last_message: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO escalations (user_phone, reason, last_message, created_at) VALUES (?,?,?,?)",
            (user_phone, reason, last_message, time.time()),
        )


def all_faqs():
    with get_conn() as conn:
        rows = conn.execute("SELECT question, answer FROM faqs").fetchall()
        return [dict(r) for r in rows]
