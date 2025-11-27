"""
FastAPI server for the Odoo Support Agent
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (parent of backend directory)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import asyncio

from livekit import api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Odoo Technical Support Agent API")

# Configure CORS
# Get allowed origins from environment, default to localhost for development
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionRequest(BaseModel):
    """Request model for LiveKit connection"""
    room_name: str
    participant_name: str


class TokenResponse(BaseModel):
    """Response model for LiveKit token"""
    token: str
    url: str


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "Odoo Technical Support Agent"}


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "livekit_configured": bool(os.getenv("LIVEKIT_URL")),
        "odoo_configured": bool(os.getenv("ODOO_HOST")),
    }


@app.post("/token", response_model=TokenResponse)
async def create_token(request: ConnectionRequest):
    """
    Create a LiveKit access token for a participant
    """
    try:
        livekit_url = os.getenv("LIVEKIT_URL")
        livekit_api_key = os.getenv("LIVEKIT_API_KEY")
        livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")

        if not all([livekit_url, livekit_api_key, livekit_api_secret]):
            raise HTTPException(
                status_code=500,
                detail="LiveKit credentials not configured"
            )

        # Create access token
        token = api.AccessToken(livekit_api_key, livekit_api_secret)
        token.with_identity(request.participant_name)
        token.with_name(request.participant_name)
        token.with_grants(
            api.VideoGrants(
                room_join=True,
                room=request.room_name,
                can_publish=True,
                can_publish_sources=["microphone", "camera", "screen_share", "screen_share_audio"],
                can_subscribe=True,
            )
        )

        jwt_token = token.to_jwt()

        return TokenResponse(
            token=jwt_token,
            url=livekit_url
        )

    except Exception as e:
        logger.error(f"Error creating token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create-room")
async def create_room(request: ConnectionRequest):
    """
    Create a new LiveKit room for the support session
    """
    try:
        livekit_url = os.getenv("LIVEKIT_URL")
        livekit_api_key = os.getenv("LIVEKIT_API_KEY")
        livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")

        if not all([livekit_url, livekit_api_key, livekit_api_secret]):
            raise HTTPException(
                status_code=500,
                detail="LiveKit credentials not configured"
            )

        # Create LiveKit API client (new SDK syntax)
        lkapi = api.LiveKitAPI(
            livekit_url,
            api_key=livekit_api_key,
            api_secret=livekit_api_secret
        )

        try:
            # Create the room using the new API
            room = await lkapi.room.create_room(
                api.CreateRoomRequest(
                    name=request.room_name,
                    empty_timeout=300,  # 5 minutes
                    max_participants=2,  # User + Agent
                )
            )

            logger.info(f"Created room: {room.name}")

            return {
                "room_name": room.name,
                "sid": room.sid,
            }
        finally:
            await lkapi.aclose()

    except Exception as e:
        logger.error(f"Error creating room: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication
    """
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message: {data}")

            # Echo back for now - can be extended for custom messaging
            await websocket.send_text(f"Echo: {data}")

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


@app.get("/config")
async def get_config():
    """
    Get frontend configuration
    """
    return {
        "livekit_url": os.getenv("LIVEKIT_URL", ""),
        "features": {
            "voice": True,
            "screen_sharing": True,
            "mcp": True,
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
