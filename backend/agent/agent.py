"""
Main Odoo Support Agent using LiveKit
"""
import os
import logging
from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli, llm
from livekit.plugins import openai, silero

from .prompts import SYSTEM_PROMPT, GREETING_PROMPT
from .tools import OdooTools

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OdooSupportAgent:
    """Odoo Technical Support Voice Agent"""

    def __init__(self):
        self.tools = OdooTools()

    async def entrypoint(self, ctx: JobContext):
        """Main entrypoint for the agent"""
        logger.info(f"Starting Odoo Support Agent for room: {ctx.room.name}")

        # Connect to the room
        await ctx.connect()

        # Wait for the first participant to join
        participant = await ctx.wait_for_participant()
        logger.info(f"Participant joined: {participant.identity}")

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

        logger.info("Agent started successfully")


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
