# Helix Vercel Deployment Guide

## A. Final Folder Structure

```
helix-demo/                          ← Vercel Root Directory
├── app/                             ← Next.js frontend
│   ├── favicon.ico
│   ├── globals.css
│   ├── layout.tsx
│   ├── page.tsx                     ← Landing page
│   ├── lead-qualification/
│   │   └── page.tsx                 ← Lead qualification UI
│   ├── multi-channel/
│   │   └── page.tsx                 ← Multi-channel UI
│   └── whatsapp-support/
│       └── page.tsx                 ← WhatsApp support UI
├── api/                             ← Unified FastAPI backend
│   └── index.py                     ← Main FastAPI entry point
├── backend/                         ← Modular backend modules
│   ├── whatsapp/                    ← WhatsApp bot module
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── graph.py
│   │   ├── llm_provider.py
│   │   ├── main.py                  ← Original main (kept for reference)
│   │   ├── rag.py
│   │   ├── router.py               ← API router
│   │   ├── seed_data.py
│   │   ├── tools.py
│   │   └── whatsapp_client.py
│   ├── lead/                        ← Lead qualification module
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── config.py
│   │   ├── llm_provider.py
│   │   ├── main.py                  ← Original main (kept for reference)
│   │   ├── models.py
│   │   ├── notify.py
│   │   ├── router.py               ← API router
│   │   ├── scoring.py
│   │   └── sheets_client.py
│   └── multichannel/                ← Multi-channel module
│       ├── __init__.py
│       ├── config.py
│       ├── graph.py
│       ├── llm_provider.py
│       ├── main.py                  ← Original main (kept for reference)
│       ├── memory.py
│       ├── router.py               ← API router
│       └── whatsapp_client.py
├── public/                          ← Static assets
├── .env.example                     ← Environment variables template
├── .gitignore
├── LOCAL_SETUP.md                   ← Local development guide
├── package.json                     ← Node.js dependencies
├── requirements.txt                 ← Python dependencies
├── SERVERLESS_LIMITATIONS.md        ← Serverless compatibility notes
├── vercel.json                      ← Vercel configuration
├── next.config.ts
├── tsconfig.json
└── README.md
```

## B. Exact Vercel Settings

### Project Configuration
- **Root Directory**: `helix-demo`
- **Framework Preset**: Next.js
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: default (`npm install`) — Python dependencies in `requirements.txt` are installed automatically by the Python runtime

### vercel.json Configuration
```json
{
  "framework": "nextjs",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/index.py"
    }
  ],
  "env": {
    "LLM_PROVIDER": "openai",
    "LLM_MODEL": "gpt-4o-mini"
  },
  "functions": {
    "api/index.py": {
      "maxDuration": 60
    }
  }
}
```

## C. Required Vercel Environment Variables

### Required for Production
```
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key-here
LLM_MODEL=gpt-4o-mini
```

### Optional (WhatsApp Integration)
```
WHATSAPP_TOKEN=your-whatsapp-token-here
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id-here
WHATSAPP_VERIFY_TOKEN=helix_verify_me
WHATSAPP_API_VERSION=v20.0
```

### Optional (Lead Qualification)
```
GOOGLE_SHEET_ID=
GOOGLE_CREDENTIALS_JSON=
AUTOMATION_WEBHOOK_URL=
HOT_LEAD_SCORE_THRESHOLD=70
```

### Optional (Database - for demo purposes only)
```
WHATSAPP_DB_PATH=support_bot.db
MULTICHANNEL_DB_PATH=platform.db
```

### Local Development Only (Ollama)
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

## D. Local Run Commands

### Full Stack (Frontend + Backend)
```bash
# Terminal 1 - Backend
cd helix-demo
python -m uvicorn api.index:app --reload --port 8003

# Terminal 2 - Frontend
cd helix-demo
npm run dev
```

### Backend Only
```bash
cd helix-demo
python -m uvicorn api.index:app --reload --port 8003
```

### Frontend Only
```bash
cd helix-demo
npm run dev
```

### Production Build Test
```bash
cd helix-demo
npm run build
npm start
```

## E. API Endpoint List

### Root Endpoints
- `GET /` - API information
- `GET /health` - Health check

### WhatsApp Bot Endpoints
- `GET /api/whatsapp/health` - WhatsApp module health check
- `GET /api/whatsapp/webhook` - WhatsApp webhook verification (Meta)
- `POST /api/whatsapp/webhook` - WhatsApp webhook handler (Meta)
- `POST /api/whatsapp/chat` - Chat endpoint for testing

### Lead Qualification Endpoints
- `GET /api/lead/health` - Lead module health check
- `POST /api/lead/session/start` - Start a lead qualification session
- `POST /api/lead/session/{session_id}/message` - Send message to session

### Multi-Channel Endpoints
- `GET /api/multichannel/health` - Multi-channel module health check
- `POST /api/multichannel/chat` - Multi-channel chat endpoint
- `GET /api/multichannel/webhook` - Multi-channel webhook verification
- `POST /api/multichannel/webhook` - Multi-channel webhook handler

## F. WhatsApp Meta Webhook URL

After deploying to Vercel, configure your WhatsApp webhook URL as:

```
https://your-vercel-domain.vercel.app/api/whatsapp/webhook
```

Replace `your-vercel-domain` with your actual Vercel project domain.

**Webhook verification token**: `helix_verify_me` (configurable via `WHATSAPP_VERIFY_TOKEN` env var)

## G. Limitations Caused by Vercel Serverless

### 1. Session Persistence
- **Issue**: Lead qualification uses in-memory sessions
- **Impact**: Sessions don't persist across serverless function invocations
- **Workaround**: Works for single-session testing
- **Production Solution**: Implement Redis or Vercel KV for session storage

### 2. SQLite Database Persistence
- **Issue**: SQLite databases are written to ephemeral filesystem
- **Impact**: Data lost between function invocations
- **Workaround**: Works for demo purposes
- **Production Solution**: Use Vercel Postgres or external database

### 3. CSV File Persistence
- **Issue**: Lead CSV fallback uses filesystem storage
- **Impact**: CSV data lost in serverless environment
- **Workaround**: Use Google Sheets for production
- **Production Solution**: Always use external database or storage

### 4. LangGraph Checkpoint Memory
- **Issue**: LangGraph uses SQLiteSaver for conversation memory
- **Impact**: Conversation history may be lost between invocations
- **Workaround**: Works for short-lived conversations
- **Production Solution**: Use PostgresSaver or external checkpoint storage

### 5. Function Duration
- **Limit**: Vercel serverless functions have 60-second timeout
- **Impact**: Long-running LLM calls may timeout
- **Workaround**: Use faster models or optimize prompts
- **Production Solution**: Consider Vercel Pro for longer timeouts

## H. Exact Files Changed

### New Files Created
- `api/index.py` - Unified FastAPI entry point
- `backend/whatsapp/router.py` - WhatsApp API router
- `backend/lead/router.py` - Lead qualification API router
- `backend/multichannel/router.py` - Multi-channel API router
- `requirements.txt` - Merged Python runtime dependencies (bundled into the Vercel function)
- `requirements-dev.txt` - Local-only extras (uvicorn, ollama provider, streamlit dashboard, pytest)
- `.env.example` - Environment variables template
- `vercel.json` - Vercel configuration
- `SERVERLESS_LIMITATIONS.md` - Serverless compatibility documentation
- `LOCAL_SETUP.md` - Local development guide
- `DEPLOYMENT_GUIDE.md` - This deployment guide

### Modified Files
- `.gitignore` - Updated to allow .env.example
- `backend/whatsapp/config.py` - Updated LLM provider default to OpenAI
- `backend/lead/config.py` - Updated LLM provider default to OpenAI
- `backend/multichannel/config.py` - Updated LLM provider default to OpenAI
- `backend/whatsapp/*.py` - Fixed imports to use new module structure
- `backend/lead/*.py` - Fixed imports to use new module structure
- `backend/multichannel/*.py` - Fixed imports to use new module structure
- `app/lead-qualification/page.tsx` - Updated API URL to `/api/lead`
- `app/whatsapp-support/page.tsx` - Updated API URL to `/api/whatsapp` and added real chat
- `app/multi-channel/page.tsx` - Updated API URL to `/api/multichannel` and added real chat

### Files Copied (from original projects)
- `backend/whatsapp/*` - From whatsapp-support-bot-langgraph/app/*
- `backend/lead/*` - From ai-lead-qualification-agent/app/*
- `backend/multichannel/*` - From multichannel-chatbot-platform/backend/*

## Summary

The Helix project has been successfully restructured for single Vercel deployment. The unified backend exposes all three bot systems through a single FastAPI application with modular routers. The Next.js frontend now calls relative `/api/` endpoints, enabling the same code to work locally and on Vercel.

**Key Achievements:**
- ✅ Unified FastAPI backend with modular routers
- ✅ All three bot systems integrated (WhatsApp, Lead, Multi-channel)
- ✅ Frontend updated to use relative API endpoints
- ✅ LLM provider abstraction (OpenAI for production, Ollama for local)
- ✅ Comprehensive error handling on all endpoints
- ✅ Serverless compatibility audit documented
- ✅ Vercel configuration complete
- ✅ Local development setup documented
- ✅ Python imports tested successfully
- ✅ Next.js build tested successfully
- ✅ API endpoints tested successfully

**Next Steps for Production:**
1. Set up Vercel project with root directory `helix-demo`
2. Configure environment variables in Vercel dashboard
3. Deploy to Vercel
4. Configure WhatsApp webhook URL in Meta dashboard
5. Test all endpoints in production environment
6. Implement production-grade persistence (Redis, Postgres) for session and data storage
