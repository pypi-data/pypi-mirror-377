"""
CLI command for running real voice conversations using LiveKit.
This integrates the original four_agents_duotalk.py functionality.
"""

import os
import sys
import asyncio
import logging
from typing import List, Optional

from livekit.agents import JobContext, WorkerOptions, cli
from dotenv import load_dotenv

from ..core.config import ConversationConfig
from ..core.voice_runner import VoiceConversationRunner, create_voice_entrypoint
from ..core.convenience import create_debate, create_roundtable
from ..personas import get_persona_by_name

load_dotenv()
logger = logging.getLogger("duotalk-voice-cli")


def check_voice_requirements() -> tuple[bool, List[str]]:
    """Check if all requirements for voice conversations are met."""
    missing_requirements = []
    
    # Check environment variables
    required_env_vars = ["GOOGLE_API_KEY"]
    for var in required_env_vars:
        if not os.getenv(var):
            missing_requirements.append(f"Environment variable: {var}")
    
    # Check optional LiveKit variables (will use defaults if not provided)
    livekit_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"]
    for var in livekit_vars:
        if not os.getenv(var):
            logger.warning(f"Optional {var} not set, will use LiveKit defaults")
    
    # Check required packages
    try:
        import livekit.agents
        from livekit.plugins.google.beta.realtime import RealtimeModel
    except ImportError as e:
        missing_requirements.append(f"Missing package: {e}")
    
    return len(missing_requirements) == 0, missing_requirements


def run_voice_conversation(
    topic: str,
    mode: str = "debate",
    personas: Optional[List[str]] = None,
    max_turns: int = 10
):
    """
    Run a voice conversation using LiveKit CLI.
    
    Args:
        topic: The conversation topic
        mode: Conversation mode (debate, roundtable, friendly, etc.)
        personas: List of persona names to use
        max_turns: Maximum number of conversation turns
    """
    
    # Check requirements
    requirements_met, missing = check_voice_requirements()
    if not requirements_met:
        print("❌ Voice conversation requirements not met:")
        for item in missing:
            print(f"  - {item}")
        print("\nPlease install required packages and set environment variables.")
        print("Example .env file:")
        print("GOOGLE_API_KEY=your_google_api_key_here")
        print("LIVEKIT_URL=wss://your-livekit-url")
        print("LIVEKIT_API_KEY=your_livekit_api_key")
        print("LIVEKIT_API_SECRET=your_livekit_api_secret")
        return False
    
    # Create conversation configuration
    try:
        if mode == "debate":
            if not personas:
                personas = ["optimist", "skeptic"]
            config = create_debate(topic, personas[:2])
        elif mode == "roundtable":
            if not personas:
                # Default roundtable personas
                personas = ["optimist", "skeptic", "pragmatist", "theorist"]
            config = create_roundtable(topic, agent_names=personas[:4])
        else:
            # Create custom configuration
            if not personas:
                personas = ["optimist", "skeptic"]
            
            from ..modes import get_mode
            agents = [get_persona_by_name(p) for p in personas]
            mode_obj = get_mode(mode)
            
            config = ConversationConfig(
                topic=topic,
                agents=agents,
                mode=mode_obj,
                max_turns=max_turns
            )
        
        print(f"🎙️ Starting voice conversation: {topic}")
        print(f"📊 Mode: {config.mode}")
        print(f"👥 Agents: {[agent.name for agent in config.agents]}")
        print(f"🔄 Max turns: {config.max_turns}")
        print("\n🚀 Launching LiveKit voice session...")
        
        # Create entrypoint for LiveKit CLI
        entrypoint = create_voice_entrypoint(config)
        
        # Run with LiveKit CLI
        worker_options = WorkerOptions(entrypoint_fnc=entrypoint)
        cli.run_app(worker_options)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating voice conversation: {e}")
        return False


if __name__ == "__main__":
    # Example usage for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m duotalk.cli.voice_cli <topic> [mode] [personas...]")
        print("Example: python -m duotalk.cli.voice_cli 'AI Ethics' debate optimist skeptic")
        sys.exit(1)
    
    topic = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "debate"
    personas = sys.argv[3:] if len(sys.argv) > 3 else None
    
    success = run_voice_conversation(topic, mode, personas)
    sys.exit(0 if success else 1)
