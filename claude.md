# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered voice assistant for Odoo technical support using LiveKit (real-time voice), Google Gemini Live API (speech-to-speech with video), and Odoo XML-RPC integration. Three-tier architecture: Next.js frontend, FastAPI backend, and LiveKit voice agent. Speaks Egyptian Arabic by default.

## Commands

### Backend (from `backend/` directory)
```bash
pip install -r requirements.txt           # Install dependencies
python -m uvicorn api.main:app --reload --port 8000  # Start API server
python -m agent.agent dev                  # Start voice agent (dev mode with hot reload)
python -m agent.agent                      # Start voice agent (production)
python -m mcp.server                       # Run MCP server (stdio mode)
```

### Frontend (from `frontend/` directory)
```bash
pnpm install          # Install dependencies (or: npm install)
pnpm dev              # Development server (port 3000)
pnpm build            # Production build
pnpm lint             # ESLint
pnpm format           # Prettier format
```

### Docker
```bash
docker-compose up --build  # Run all services
```

## Architecture

### Backend (`backend/`)

- **`api/main.py`**: FastAPI REST server
  - `POST /create-room` - Create LiveKit room (returns `room_name`, `sid`)
  - `POST /token` - Generate LiveKit access token for participant
  - `GET /health` - Health check with config status
  - `GET /config` - Frontend configuration (LiveKit URL, features)
  - `WS /ws` - WebSocket endpoint (echo for custom messaging)
- **`agent/agent.py`**: LiveKit voice agent using Google Gemini Live API with vision support. Creates `AgentSession` with `google.realtime.RealtimeModel` and Silero VAD
- **`agent/tools.py`**: Odoo operations via XML-RPC using `@function_tool` decorator. Global `odoo_conn` singleton for connection reuse
- **`agent/prompts.py`**: System prompt (Egyptian Arabic) and greeting. Lists all available tools for the agent
- **`mcp/server.py`**: MCP server implementation with tool routing via `@server.list_tools()` and `@server.call_tool()` decorators
- **`mcp/odoo_tools.py`**: MCP tool implementations with model allowlist in `ALLOWED_MODELS` for `search_records` security

### Frontend (`frontend/`)

- **`app/page.tsx`**: Main page with VoiceAgent component
- **`components/VoiceAgent.tsx`**: LiveKit room connection with `useVoiceAssistant` hook for state management (listening/thinking/speaking/idle), screen sharing via `localParticipant.setScreenShareEnabled()`

### Data Flow

1. Frontend creates room via `/create-room`, gets token via `/token`
2. Frontend connects to LiveKit with token using `LiveKitRoom` component
3. Voice agent joins room, starts Gemini Live session with vision enabled
4. User speech → Gemini → tool calls → Odoo XML-RPC → response → speech
5. Screen share video streamed to Gemini for visual analysis

## Key Patterns

### Adding Voice Agent Tools
1. Add function with `@function_tool` decorator in `backend/agent/tools.py`:
```python
@function_tool
async def your_tool(param: str) -> str:
    """Tool description.

    Args:
        param: Parameter description
    """
    def _sync_operation():
        odoo = odoo_conn.connect()
        # ... odoorpc operations
        return result
    return await asyncio.to_thread(_sync_operation)
```
2. Import and add to tools list in `OdooSupportAgent.__init__()` in `backend/agent/agent.py`
3. Update Available Tools section in `backend/agent/prompts.py`

### Adding MCP Tools
1. Add method to `OdooMCPTools` in `backend/mcp/odoo_tools.py`
2. Add Tool schema in `list_tools()` in `backend/mcp/server.py`
3. Add handler in `call_tool()` switch
4. For new models in `search_records`, add to `ALLOWED_MODELS` set

### Async Pattern for Odoo
All Odoo operations use `asyncio.to_thread()` wrapper since `odoorpc` is synchronous:
```python
async def method(self):
    def _sync():
        odoo = odoo_conn.connect()
        # synchronous odoorpc calls
        return result
    return await asyncio.to_thread(_sync)
```

### Gemini Live Configuration
Voice agent uses `google.realtime.RealtimeModel` with:
- `model="gemini-2.0-flash-exp"` - Realtime model with video support
- `voice="Kore"` - Options: Puck, Charon, Kore, Fenrir, Aoede
- `room_io.RoomOptions(video_input=True)` - Enable screen share/camera
- Egyptian Arabic is configured via system prompt (not `language` param - unsupported by model)

## Environment Variables

Required: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `GOOGLE_API_KEY`

Odoo (required for tools): `ODOO_HOST`, `ODOO_PORT`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD`

Frontend: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_LIVEKIT_URL`

Optional: `CORS_ORIGINS` (comma-separated), `ODOO_LOG_FILE`, `PORT`, `MCP_SERVER_URL`, `MCP_SERVER_NAME`
