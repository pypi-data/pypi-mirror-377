#!/usr/bin/env python3
"""
Enhanced YouTube Summary Agent for DuoTalk integration.
Uses the DuoTalk core modules for better integration.
"""

import asyncio
import os
import sys
from typing import Optional
from dotenv import load_dotenv

from livekit.agents import JobContext, WorkerOptions, cli, AgentSession
from livekit.plugins import google, cartesia

# Import DuoTalk modules
try:
    from duotalk.core.youtube_summarizer import YouTubeSummarizerAgent
    from duotalk.core.convenience_youtube import sync_youtube_summary
    _duotalk_available = True
except ImportError:
    _duotalk_available = False
    print("DuoTalk modules not available, using standalone mode")

load_dotenv()


async def entrypoint(ctx: JobContext):
    """Main entrypoint for YouTube summarization with DuoTalk integration"""
    await ctx.connect()
    
    # Get YouTube URL from environment variable or use default
    youtube_url = os.getenv('DUOTALK_YOUTUBE_URL')
    
    if not youtube_url:
        print("No YouTube URL provided. Please set DUOTALK_YOUTUBE_URL environment variable.")
        return
    
    if _duotalk_available:
        # Use DuoTalk's YouTube summarizer
        agent = YouTubeSummarizerAgent()
    else:
        # Fallback to basic agent
        from livekit.agents import Agent
        agent = Agent(
            instructions="You are a helpful assistant that summarizes YouTube videos. "
                        "Provide natural, conversational summaries suitable for audio delivery."
        )
    
    # Create session with high-quality voice synthesis
    session = AgentSession(
        # Use Google's Gemini for LLM
        llm=google.LLM(model="gemini-2.5-flash-lite"),
        
        # Use Cartesia for high-quality voice
        tts=cartesia.TTS(
            model="sonic-english",
            voice="a0e99841-438c-4a64-b679-ae501e7d6091",  # Professional voice
        ),
    )
    
    # Start the session
    await session.start(agent=agent, room=ctx.room)
    
    # Generate greeting and initiate summarization
    greeting = (
        f"Hello! I'm ready to summarize the YouTube video for you. "
        f"Let me extract the transcript and provide you with a natural, spoken summary. "
        f"Processing video now..."
    )
    
    await session.generate_reply(instructions=greeting)
    
    # Wait a moment for the greeting to finish
    await asyncio.sleep(2)
    
    # Now process the YouTube video
    if _duotalk_available:
        # Use the function tool approach
        summary_instruction = (
            f"Please use your get_youtube_transcript function to extract and summarize "
            f"this YouTube video: {youtube_url}. Provide a natural, conversational summary "
            f"that flows well when spoken aloud."
        )
    else:
        # Basic fallback
        summary_instruction = (
            f"I would summarize the YouTube video at {youtube_url} if I had the "
            f"transcript extraction capabilities available. For now, I can tell you "
            f"that I'm ready to help with video summarization once the proper "
            f"dependencies are installed."
        )
    
    await session.generate_reply(instructions=summary_instruction)


if __name__ == "__main__":
    # Check if URL is provided as command line argument
    if len(sys.argv) > 2:
        # If running with livekit mode and URL
        mode = sys.argv[1]
        url = sys.argv[2] if len(sys.argv) > 2 else None
        if url:
            os.environ['DUOTALK_YOUTUBE_URL'] = url
    
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))