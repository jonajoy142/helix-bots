# Helix Local Development Setup

## Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key (for production LLM) OR Ollama (for local development)

## Installation

1. **Install Python dependencies:**
```bash
cd helix-demo
pip install -r requirements-dev.txt
```

`requirements.txt` holds only the runtime dependencies that get bundled into the
Vercel serverless function (500 MB limit). `requirements-dev.txt` includes those
plus local-only extras (uvicorn, langchain-ollama, streamlit/pandas/plotly, pytest).

2. **Install Node.js dependencies:**
```bash
npm install
```

3. **Set up environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and configure:
- For local development with Ollama: Set `LLM_PROVIDER=ollama`
- For production/testing with OpenAI: Set `LLM_PROVIDER=openai` and add your `OPENAI_API_KEY`

## Running the Application

### Option 1: Run both frontend and backend together

**Terminal 1 - Start the Python backend:**
```bash
cd helix-demo
python -m uvicorn api.index:app --reload --port 8003
```

**Terminal 2 - Start the Next.js frontend:**
```bash
cd helix-demo
npm run dev
```

Then open http://localhost:3000 in your browser.

### Option 2: Run backend only (for API testing)

```bash
cd helix-demo
python -m uvicorn api.index:app --reload --port 8003
```

API will be available at http://localhost:8003

### Option 3: Run frontend only (if backend is already running)

```bash
cd helix-demo
npm run dev
```

## API Endpoints

### WhatsApp Bot
- `GET /api/whatsapp/health` - Health check
- `GET /api/whatsapp/webhook` - WhatsApp webhook verification
- `POST /api/whatsapp/webhook` - WhatsApp webhook handler
- `POST /api/whatsapp/chat` - Chat endpoint for testing

### Lead Qualification
- `GET /api/lead/health` - Health check
- `POST /api/lead/session/start` - Start a lead qualification session
- `POST /api/lead/session/{session_id}/message` - Send message to session

### Multi-Channel
- `GET /api/multichannel/health` - Health check
- `POST /api/multichannel/chat` - Multi-channel chat endpoint
- `GET /api/multichannel/webhook` - Multi-channel webhook verification
- `POST /api/multichannel/webhook` - Multi-channel webhook handler

## Testing the API

### Test WhatsApp chat:
```bash
curl -X POST http://localhost:8003/api/whatsapp/chat \
  -H "Content-Type: application/json" \
  -d '{"user_phone": "+1234567890", "message": "Where is my order ORD1001?"}'
```

### Test Lead Qualification:
```bash
# Start session
curl -X POST http://localhost:8003/api/lead/session/start

# Send message (replace SESSION_ID)
curl -X POST http://localhost:8003/api/lead/session/{SESSION_ID}/message \
  -H "Content-Type: application/json" \
  -d '{"message": "We need an AI customer support system"}'
```

### Test Multi-Channel:
```bash
curl -X POST http://localhost:8003/api/multichannel/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "message": "Hello"}'
```

## Building for Production

```bash
# Build Next.js
npm run build

# Test production build locally
npm start
```

## Vercel Deployment

The project is configured for Vercel deployment with:
- Root Directory: `helix-demo`
- Build Command: `npm run build`
- Output Directory: `.next`
- Install Command: default (`npm install`); Python deps come from `requirements.txt` automatically

See `vercel.json` for the complete configuration.
