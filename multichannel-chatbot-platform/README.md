# Multi-Channel AI Chatbot Platform (LangGraph core + Web Widget + WhatsApp + Analytics)

The systems-design piece of the portfolio: **one shared LangGraph agent**
serves both an embeddable website chat widget and WhatsApp, with a live
Streamlit analytics dashboard on top — the actual shape of a product like
UrbanChat (many channels, one bot brain, one dashboard).

## Why this project

- **One agent, many channel adapters.** `backend/graph.py` has zero
  knowledge of WhatsApp or HTTP — it just takes `(channel, user_id,
  message)`. `backend/main.py` has two thin adapters (`/chat` for the widget,
  `/webhook` for WhatsApp) that both call the same `run_agent()`. This is the
  difference between "I built a bot" and "I built a platform."
- **Durable per-user memory** via LangGraph's `SqliteSaver`, keyed by
  `"{channel}:{user_id}"` — a user's context survives server restarts and
  is correctly isolated between channels.
- **A real embeddable widget** (`frontend/widget.html`) — a floating
  launcher + chat panel, no framework, drop it into any site.
- **Analytics dashboard** (`dashboard/analytics_app.py`) reading the same
  SQLite file: message volume by channel, escalation rate, recent
  conversations — the kind of view a merchant using UrbanChat would actually
  want to see.

## Architecture

```
        website visitor                 WhatsApp user
              |                               |
        frontend/widget.html          Meta Cloud API
              |                               |
        POST /chat                     POST/GET /webhook
              \\_____________  _______________/
                            \\/
                    backend/main.py (FastAPI)
                            |
                    backend/graph.py
                 (shared LangGraph agent,
                  SqliteSaver memory)
                            |
                    platform.db (SQLite)
                       /         \\
              conversations   checkpoints
                   table       (LangGraph)
                     |
        dashboard/analytics_app.py (Streamlit)
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env      # add OPENAI_API_KEY
uvicorn backend.main:app --reload --port 8002
```

Open `frontend/widget.html` directly in a browser (or serve it with any
static server) — click the launcher bubble and chat.

In a second terminal, run the analytics dashboard:

```bash
streamlit run dashboard/analytics_app.py
```

## Resume bullet

> Architected a multi-channel AI chatbot platform on a single shared
> LangGraph agent (web widget + WhatsApp Cloud API) with per-user durable
> memory via SqliteSaver, an embeddable JS chat widget, and a Streamlit
> analytics dashboard tracking message volume and escalation rate across
> channels — mirroring the architecture of commercial WhatsApp automation
> platforms.
