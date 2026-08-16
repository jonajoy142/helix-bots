# Helix - AI Chatbot Systems

A collection of AI-powered chatbot systems demonstrating various conversational AI capabilities including WhatsApp support automation, lead qualification, and multi-channel platforms.

## Overview

Helix consists of three independent but complementary chatbot projects, each showcasing different aspects of modern conversational AI systems:

### Projects

1. **whatsapp-support-bot-langgraph** - WhatsApp AI customer support bot with RAG and human handoff
2. **ai-lead-qualification-agent** - Conversational lead qualification agent with BANT scoring
3. **multichannel-chatbot-platform** - Multi-channel platform supporting web widget and WhatsApp with analytics

## Project Details

### WhatsApp Support Bot (LangGraph + RAG)

An AI customer-support agent for WhatsApp that handles order tracking, FAQ questions via RAG, and escalates to human agents when needed.

**Features:**
- LangGraph state machine architecture
- RAG over FAQ knowledge base (FAISS + embeddings)
- Intent classification and routing
- Human handoff with ticket creation
- Per-user conversation memory via LangGraph checkpointer
- Mock mode for development without WhatsApp credentials

**Tech Stack:**
- LangGraph, LangChain, FastAPI
- FAISS vector store
- SQLite for persistence
- Meta WhatsApp Cloud API integration

### AI Lead Qualification Agent

A conversational agent that qualifies prospects using BANT (Budget, Authority, Need, Timeline), scores leads, and integrates with CRM systems.

**Features:**
- Structured output using Pydantic schemas
- BANT-based lead scoring
- Google Sheets/CSV persistence
- Automation webhook integration
- Session-based conversation management

**Tech Stack:**
- LangChain structured outputs
- Pydantic for data validation
- Google Sheets API
- FastAPI

### Multi-Channel Chatbot Platform

A platform architecture where one shared LangGraph agent serves both web chat widgets and WhatsApp, with unified analytics.

**Features:**
- Single agent, multiple channel adapters
- Durable per-user memory via SqliteSaver
- Embeddable JavaScript chat widget
- Streamlit analytics dashboard
- Message volume and escalation tracking

**Tech Stack:**
- LangGraph, LangChain
- FastAPI backend
- Streamlit dashboard
- SQLite with LangGraph checkpointing

## Common Features Across Projects

- **LLM Provider Flexibility**: All projects support both OpenAI and local Ollama models via configurable provider switch
- **Environment-based Configuration**: All settings managed through `.env` files
- **Durable Memory**: Conversation state persists across sessions
- **Production-ready Patterns**: Mock modes for development, real integrations for production

## Setup

Each project has its own setup instructions in its respective README.md file. Common requirements:

```bash
# For any project
cd <project-directory>
pip install -r requirements.txt
cp .env.example .env
# Configure your .env file with API keys
```

## LLM Provider Configuration

All projects support switching between OpenAI and local Ollama models:

```bash
# Use OpenAI (default)
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key-here

# Use local Ollama
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434
```

## Architecture Philosophy

These projects demonstrate modern conversational AI patterns:

- **State Machine Architecture**: Using LangGraph for predictable, debuggable conversation flows
- **Separation of Concerns**: Channel adapters separate from core agent logic
- **Tool Calling**: Structured interactions with external systems
- **Memory Management**: Durable, per-user conversation state
- **RAG Integration**: Knowledge base retrieval for accurate responses

## Development

Each project can run independently in development mode with mock configurations, allowing full testing without external service dependencies.

## License

These are demonstration projects for educational and development purposes.
