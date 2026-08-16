# Serverless Compatibility Notes for Vercel Deployment

## Known Limitations

### 1. Session Persistence (Lead Qualification)
**Issue**: The lead qualification agent uses an in-memory `SESSIONS` dict to store conversation state.
**Impact**: Sessions will not persist across different serverless function invocations in Vercel.
**Current Behavior**: Works for single-session testing, but multi-user scenarios will fail.
**Production Solution**: Implement a proper session store (Redis, Vercel KV, or database-backed sessions).

### 2. SQLite Database Persistence
**Issue**: SQLite databases (`support_bot.db`, `platform.db`) are written to the local filesystem.
**Impact**: Vercel serverless functions have an ephemeral filesystem - data will be lost between invocations.
**Current Behavior**: 
- WhatsApp bot: Orders, FAQs, conversations, and escalations are stored in SQLite
- Multichannel: Conversations and checkpoints are stored in SQLite
**Production Solution**: Use an external database (PostgreSQL, MongoDB, or Vercel Postgres).

### 3. CSV File Persistence
**Issue**: Lead qualification falls back to CSV file storage when Google Sheets is not configured.
**Impact**: CSV files written to filesystem will be lost in serverless environment.
**Current Behavior**: Leads are saved to `backend/lead/data/leads.csv` 
**Production Solution**: Always use Google Sheets or external database for production.

### 4. LangGraph Checkpoint Memory
**Issue**: LangGraph uses `SqliteSaver` for conversation memory checkpoints.
**Impact**: Conversation history will not persist across serverless invocations.
**Current Behavior**: Multi-turn conversations may lose context in production.
**Production Solution**: Use `PostgresSaver` or external checkpoint storage.

## Demo-Mode Workarounds

For demonstration purposes, the current implementation will work with these limitations:
- Single-user testing
- Short-lived sessions
- Mock data for orders/FAQs
- CSV fallback for leads (data will be lost but works for demo)

## Recommended Production Changes

1. **Replace SQLite with Vercel Postgres**
   - Migrate all SQLite schemas to PostgreSQL
   - Use connection pooling for serverless
   - Update all database access code

2. **Implement Redis for Sessions**
   - Replace in-memory SESSIONS dict with Redis
   - Use Vercel KV or external Redis service

3. **Use Postgres for LangGraph Checkpoints**
   - Replace `SqliteSaver` with `PostgresSaver`
   - Ensures conversation memory persists

4. **Remove CSV Fallback**
   - Require Google Sheets or database for lead storage
   - Remove filesystem-based storage

## Current Status

The application is **deployable to Vercel** for demonstration purposes with the understanding that:
- Data persistence is not guaranteed
- Multi-user scenarios may have issues
- Conversation history may be lost between invocations

For production use, implement the recommended changes above.
