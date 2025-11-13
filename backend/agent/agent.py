"""
Main Odoo Support Agent using LiveKit with Screen Sharing Support
"""
import os
import logging
import asyncio
import base64
from io import BytesIO
from PIL import Image
from livekit import agents, rtc
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    llm,
    RoomInputOptions,
    ImageContent,
    get_job_context
)
from livekit.plugins import openai, silero
from livekit.plugins import noise_cancellation

from .prompts import SYSTEM_PROMPT, GREETING_PROMPT, VISION_PROMPT
from .tools import OdooTools

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OdooSupportAgent:
    """Odoo Technical Support Voice Agent with Screen Sharing"""

    def __init__(self):
        self.tools = OdooTools()
        self.chat_context = []

    async def _handle_screen_capture(self, reader: rtc.ByteStreamReader):
        """Handle incoming screen capture/video frames"""
        try:
            # Read the image data asynchronously
            image_bytes = bytearray()
            async for chunk in reader:
                image_bytes += chunk

            if not image_bytes:
                logger.warning("Received empty image data")
                return

            # Convert to PIL Image and resize if needed
            image = Image.open(BytesIO(image_bytes))

            # Resize to max 1024x1024 while maintaining aspect ratio
            max_size = 1024
            if image.width > max_size or image.height > max_size:
                ratio = min(max_size / image.width, max_size / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Convert to base64 PNG
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            # Add to chat context
            image_content = ImageContent(image=f"data:image/png;base64,{image_base64}")

            logger.info(f"Screen capture received and processed (size: {image.width}x{image.height})")

            # Add to context for the agent to analyze
            self.chat_context.append({
                "role": "user",
                "content": [image_content, {"type": "text", "text": VISION_PROMPT}]
            })

        except Exception as e:
            logger.error(f"Error processing screen capture: {e}", exc_info=True)

    async def entrypoint(self, ctx: JobContext):
        """Main entrypoint for the agent"""
        logger.info(f"Starting Odoo Support Agent for room: {ctx.room.name}")

        # Connect to the room with video enabled for screen sharing
        await ctx.connect(
            room_input_options=RoomInputOptions(
                video_enabled=True,
                noise_cancellation=noise_cancellation.BVC(),
            )
        )

        # Register handler for screen sharing byte stream
        ctx.room.register_byte_stream_handler(
            "screen_capture",
            lambda reader: asyncio.create_task(self._handle_screen_capture(reader))
        )
        logger.info("Screen capture handler registered")

        # Wait for the first participant to join
        participant = await ctx.wait_for_participant()
        logger.info(f"Participant joined: {participant.identity}")

        # Subscribe to participant's video tracks for screen sharing
        async def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
            if track.kind == rtc.TrackKind.KIND_VIDEO:
                logger.info(f"Subscribed to video track: {publication.sid}")
                # Video frames can be captured here if needed

        ctx.room.on("track_subscribed", on_track_subscribed)

        # Create the agent with OpenAI Realtime API
        agent = agents.Agent(
            instructions=SYSTEM_PROMPT,
            model=openai.realtime.RealtimeModel(
                voice="alloy",
                temperature=0.7,
                instructions=SYSTEM_PROMPT,
            ),
            # Add Odoo tools
            tools=[
                self.tools.check_odoo_status,
                self.tools.get_installed_modules,
                self.tools.install_module,
                self.tools.update_module,
                self.tools.get_user_info,
                self.tools.create_user,
                self.tools.reset_user_password,
                self.tools.get_server_logs,
                self.tools.analyze_error,
            ],
        )

        # Start the agent
        agent.start(ctx.room, participant)

        # Send initial greeting
        await agent.say(GREETING_PROMPT, allow_interruptions=True)

        logger.info("Agent started successfully with screen sharing support")


def run_agent():
    """Run the agent worker"""
    agent_instance = OdooSupportAgent()

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=agent_instance.entrypoint,
            worker_type=agents.WorkerType.ROOM,
        ),
    )


if __name__ == "__main__":
    run_agent()
