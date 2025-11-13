# Odoo Technical Support Agent

An AI-powered voice assistant for Odoo technical support with screen sharing capabilities and MCP (Model Context Protocol) integration.

## Features

- **Voice Interaction**: Natural voice conversations using LiveKit and OpenAI Realtime API
- **Odoo Integration**: Direct access to Odoo instance via XML-RPC
- **MCP Support**: Model Context Protocol for standardized AI tool interactions
- **Screen Sharing**: Visual troubleshooting capabilities
- **Railway Ready**: Optimized for easy deployment on Railway
- **No Video Avatar**: Lightweight voice-only interface

## Capabilities

The agent can help with:

- Module installation, updates, and management
- User account creation and password resets
- Database queries and operations
- Error diagnosis and log analysis
- Configuration and troubleshooting
- Best practices and guidance

## Architecture

```
technical-support-agent/
├── backend/
│   ├── agent/          # LiveKit voice agent
│   ├── api/            # FastAPI server
│   └── mcp/            # MCP server for Odoo
├── frontend/           # Next.js UI
└── docs/              # Documentation
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- pnpm (recommended) or npm
- LiveKit server (cloud or self-hosted)
- OpenAI API key
- Odoo instance (accessible via XML-RPC)

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd technical-support-agent
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-server.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Odoo Configuration
ODOO_HOST=your-odoo-instance.com
ODOO_PORT=8069
ODOO_DB=your-database-name
ODOO_USERNAME=admin
ODOO_PASSWORD=your-admin-password
```

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

The services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### 4. Run locally (development)

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start API server
python -m uvicorn api.main:app --reload --port 8000

# In another terminal, start the agent
python -m agent.agent
```

**Frontend:**

```bash
cd frontend
pnpm install
pnpm dev
```

## Deploying to Railway

### Option 1: Using Railway CLI

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Create two services (backend and frontend):

**Backend:**
```bash
railway up --service backend
```

**Frontend:**
```bash
cd frontend
railway up --service frontend
```

4. Set environment variables in Railway dashboard for each service

### Option 2: Using Railway Dashboard

1. Create a new project in Railway
2. Add services:
   - **Backend Service**:
     - Root directory: `/backend`
     - Build command: `pip install -r requirements.txt`
     - Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

   - **Agent Service**:
     - Root directory: `/backend`
     - Build command: `pip install -r requirements.txt`
     - Start command: `python -m agent.agent`

   - **Frontend Service**:
     - Root directory: `/frontend`
     - Build command: `pnpm install && pnpm build`
     - Start command: `pnpm start`

3. Configure environment variables in each service
4. Deploy!

## MCP Server Usage

The MCP server provides standardized tools for Odoo operations:

```bash
cd backend
python -m mcp.server
```

Available MCP tools:
- `list_modules`: List all Odoo modules
- `get_module_info`: Get module details
- `list_users`: List all users
- `get_user_details`: Get user information
- `search_records`: Search any Odoo model
- `get_database_info`: Get database info
- `get_company_info`: Get company details
- `check_module_dependencies`: Check module dependencies

## Environment Variables

### Backend

| Variable | Description | Required |
|----------|-------------|----------|
| `LIVEKIT_URL` | LiveKit server WebSocket URL | Yes |
| `LIVEKIT_API_KEY` | LiveKit API key | Yes |
| `LIVEKIT_API_SECRET` | LiveKit API secret | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `ODOO_HOST` | Odoo instance host | Yes |
| `ODOO_PORT` | Odoo instance port | Yes |
| `ODOO_DB` | Odoo database name | Yes |
| `ODOO_USERNAME` | Odoo admin username | Yes |
| `ODOO_PASSWORD` | Odoo admin password | Yes |
| `ODOO_LOG_FILE` | Path to Odoo log file | No |
| `PORT` | API server port | No (default: 8000) |

### Frontend

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_LIVEKIT_URL` | LiveKit server URL | Yes |

## Development

### Adding New Odoo Tools

1. Add the tool method in `backend/agent/tools.py`:

```python
@llm.ai_callable(description="Your tool description")
async def your_tool(
    self,
    param: Annotated[str, llm.TypeInfo(description="Parameter description")]
) -> str:
    # Your implementation
    pass
```

2. Register it in `backend/agent/agent.py`:

```python
tools=[
    # ... existing tools
    self.tools.your_tool,
]
```

### Adding MCP Tools

1. Implement the method in `backend/mcp/odoo_tools.py`
2. Register it in `backend/mcp/server.py` in the `list_tools()` function
3. Handle the call in `call_tool()` function

## Troubleshooting

### Connection Issues

- Verify LiveKit credentials are correct
- Check that Odoo instance is accessible
- Ensure firewall allows WebSocket connections

### Voice Not Working

- Check browser microphone permissions
- Verify OpenAI API key is valid
- Check LiveKit server status

### Odoo Connection Failed

- Verify Odoo credentials
- Check network connectivity to Odoo instance
- Ensure Odoo XML-RPC is enabled

## Security Considerations

- Never commit `.env` file with credentials
- Use Railway secrets for production credentials
- Implement rate limiting for API endpoints
- Use HTTPS/WSS in production
- Restrict Odoo user permissions to minimum required

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
