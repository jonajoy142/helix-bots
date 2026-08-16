"""
Unified FastAPI backend for Helix.

This is the main entry point for Vercel serverless deployment.
It combines all three bot systems (WhatsApp, Lead Qualification, Multichannel)
into a single API with modular routers.

For Vercel deployment, this file is mounted at /api/*.
For local development, run with: python -m uvicorn api.index:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers from each module
from backend.whatsapp.router import router as whatsapp_router, startup as whatsapp_startup
from backend.lead.router import router as lead_router
from backend.multichannel.router import router as multichannel_router, startup as multichannel_startup

app = FastAPI(
    title="Helix Unified API",
    description="AI Chatbot Systems - WhatsApp Support, Lead Qualification, Multi-Channel",
    version="1.0.0"
)

# CORS - allow all origins for development, tighten for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers with /api prefix
app.include_router(whatsapp_router, prefix="/api")
app.include_router(lead_router, prefix="/api")
app.include_router(multichannel_router, prefix="/api")


@app.on_event("startup")
def startup():
    """Initialize databases and services from all modules."""
    whatsapp_startup()
    multichannel_startup()


@app.get("/")
def root():
    return {
        "message": "Helix Unified API",
        "version": "1.0.0",
        "endpoints": {
            "whatsapp": "/api/whatsapp/*",
            "lead": "/api/lead/*",
            "multichannel": "/api/multichannel/*"
        }
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "helix-unified-api"}


# Vercel serverless function handler
def handler(request):
    """Vercel serverless function entry point."""
    return app(request)
