# AI Lead Qualification & CRM Automation Agent

A conversational agent that chats with a prospect (WhatsApp / website widget),
qualifies them using BANT (Budget, Authority, Need, Timeline), scores the
lead, writes it to Google Sheets (or CSV), and fires a real-time automation
webhook when a **hot** lead is found — the "lead automation" pitch UrbanChat
sells to merchants, built end to end.

## Why this project

- **Structured output, not free text.** Every turn, the LLM emits a typed
  `LeadProfile` (Pydantic) instead of prose — this is what makes a chatbot
  usable by a CRM instead of just "readable."
- **Deterministic scoring.** The BANT score is plain rule-based Python, not
  another LLM call — sales teams can audit and tune exactly why a lead is
  "hot," which matters a lot more than it sounds in real deployments.
- **CSV fallback for Sheets.** Demoable with zero Google Cloud setup; swap in
  a real Google Sheet with two env vars and nothing else changes.
- **Automation-webhook pattern.** Mirrors exactly how Zapier/Make/n8n hot-lead
  alerts work — fire a JSON POST, let the automation tool fan it out to
  Slack/email/CRM.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env      # add OPENAI_API_KEY
uvicorn app.main:app --reload --port 8001
```

## Try it

```bash
# start a session
curl -X POST http://localhost:8001/session/start

# send messages using the returned session_id
curl -X POST http://localhost:8001/session/<session_id>/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi, I run a 20-person D2C brand and we are losing leads on WhatsApp"}'
```

Keep sending messages — once the agent has enough BANT signal it sets
`ready_for_handoff: true`, writes the row to `data/leads.csv`, and (if hot)
logs a mock automation trigger to the console.

## Wiring to a real CRM/automation stack

- **Google Sheets:** create a service account, share the sheet with its
  email, set `GOOGLE_SHEET_ID` + `GOOGLE_CREDENTIALS_JSON` in `.env`.
- **Notifications:** set `AUTOMATION_WEBHOOK_URL` to a Zapier "Catch Hook",
  Make webhook, n8n webhook node, or Slack incoming webhook — no code changes.

## Resume bullet

> Designed an AI lead-qualification agent using LangChain structured
> outputs (Pydantic) to convert freeform chat into BANT-qualified lead
> records; implemented rule-based lead scoring, Google Sheets/CSV
> persistence, and a Zapier/Make-style webhook automation that alerts sales
> in real time for hot leads.
