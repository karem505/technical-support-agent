"""
Main Odoo Support Agent using LiveKit with Vision Support
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    room_io,
)
from livekit.plugins import google, silero

from .prompts import SYSTEM_PROMPT, GREETING_PROMPT
from .tools import (
    check_odoo_status,
    get_installed_modules,
    install_module,
    update_module,
    get_user_info,
    create_user,
    reset_user_password,
    get_server_logs,
    analyze_error,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OdooSupportAgent(Agent):
    """Odoo Technical Support Voice Agent with Vision"""

    def __init__(self):
        super().__init__(
            instructions=SYSTEM_PROMPT,
            tools=[
                check_odoo_status,
                get_installed_modules,
                install_module,
                update_module,
                get_user_info,
                create_user,
                reset_user_password,
                get_server_logs,
                analyze_error,
            ],
        )


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the agent"""
    logger.info(f"Starting Odoo Support Agent for room: {ctx.room.name}")

    # Connect to the room
    await ctx.connect()

    # Create the AgentSession with Google Gemini Live API
    # Native speech-to-speech with real-time video support at 1 FPS
    # Egyptian Arabic is configured via system prompt (language param not supported)
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Kore",  # Options: Puck, Charon, Kore, Fenrir, Aoede
            temperature=0.7,
            instructions=SYSTEM_PROMPT,
        ),
        vad=silero.VAD.load(),
    )

    # Create the agent instance
    agent = OdooSupportAgent()

    # Start the session with video input enabled for screen sharing
    await session.start(
        room=ctx.room,
        agent=agent,
        room_options=room_io.RoomOptions(
            video_input=True,  # Enable screen share/camera input
        ),
    )

    logger.info("Agent session started successfully with vision support")

    # Send initial greeting
    await session.generate_reply(
        instructions=GREETING_PROMPT
    )


def run_agent():
    """Run the agent worker"""
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        ),
    )


if __name__ == "__main__":
    run_agent()
