"""
Real voice conversation runner using LiveKit and Google Gemini.
This integrates the actual voice agent functionality from the original four_agents_duotalk.py
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from google.genai import types

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins.google.beta.realtime import RealtimeModel

from ..core.config import ConversationConfig, AgentConfig, VoiceType

load_dotenv()
logger = logging.getLogger("duotalk-voice")


@dataclass
class VoiceConversationState:
    """State management for voice conversations."""
    topic: str
    conversation_mode: str
    turn_count: int = 0
    max_turns: int = 20
    conversation_active: bool = True
    current_speaker: str = "agent1"
    last_error: Optional[str] = None
    session_healthy: bool = True
    agent_order: List[str] = None
    
    def __post_init__(self):
        if self.agent_order is None:
            # Default to 4 agents for roundtable, adjust based on actual agent count
            self.agent_order = ["agent1", "agent2", "agent3", "agent4"]


class DuoTalkVoiceAgent(Agent):
    """Voice agent with persona support for DuoTalk conversations."""
    
    def __init__(self, config: ConversationConfig):
        instructions = f"""You are participating in a {config.mode} discussion about {config.topic}.
        
You will receive specific instructions about which perspective to take.
Always respond in one line only to save API costs.
Be engaging and contribute unique viewpoints.
Stay in character and maintain your assigned persona throughout the conversation.
        """
        
        super().__init__(instructions=instructions)
        self.config = config


class VoiceConversationRunner:
    """Runs actual voice conversations using LiveKit and Google Gemini."""
    
    def __init__(self, config: ConversationConfig):
        self.config = config
        self.state = VoiceConversationState(
            topic=config.topic,
            conversation_mode=config.mode,
            max_turns=config.max_turns
        )
        
        # Map agent configs to voice configuration
        self.agent_voice_map = self._create_agent_voice_map()
        
    def _create_agent_voice_map(self) -> Dict[str, Dict[str, Any]]:
        """Create mapping of agents to their voice configurations."""
        voice_map = {}
        
        for i, agent in enumerate(self.config.agents):
            agent_id = f"agent{i+1}"
            
            # Map VoiceType to LiveKit voice names
            voice_name = self._get_livekit_voice_name(agent.voice)
            
            voice_map[agent_id] = {
                "voice": voice_name,
                "role": agent.persona,
                "perspective": agent.perspective,
                "name": agent.name,
                "config": agent
            }
            
        # Update agent order based on actual number of agents
        self.state.agent_order = list(voice_map.keys())
        
        return voice_map
    
    def _get_livekit_voice_name(self, voice_type: VoiceType) -> str:
        """Map DuoTalk VoiceType to LiveKit voice names."""
        voice_mapping = {
            VoiceType.PUCK: "Puck",
            VoiceType.CHARON: "Charon", 
            VoiceType.KORE: "Kore",
            VoiceType.FENRIR: "Fenrir",
            VoiceType.AOEDE: "Aoede"
        }
        return voice_mapping.get(voice_type, "Puck")
    
    async def start_conversation(self, ctx: JobContext):
        """Start the voice conversation with LiveKit context."""
        await ctx.connect()
        
        # Create the voice agent
        agent = DuoTalkVoiceAgent(self.config)
        
        # Create session with Google Gemini Realtime
        session = AgentSession[VoiceConversationState](
            userdata=self.state,
            llm=RealtimeModel(
                model="gemini-2.5-flash-preview-native-audio-dialog",
                instructions=agent.instructions,
                voice="Puck",  # Default voice, will be changed per agent
            ),
            allow_interruptions=True,
            turn_detection="realtime_llm",
            min_interruption_duration=0.3,
        )
        
        # Error handling for session events
        def on_session_error(error):
            logger.error(f"Session error: {error}")
            self.state.session_healthy = False
            self.state.conversation_active = False
        
        session.on("error", on_session_error)
        
        try:
            await session.start(agent=agent, room=ctx.room)
            logger.info(f"Voice session started successfully in {self.config.mode} mode")
            
            # Verify session is running
            if not session._started:
                raise RuntimeError("Session failed to start properly")
            
            await self._run_conversation_loop(session)
            
        except Exception as e:
            logger.error(f"Critical error in voice conversation: {e}")
            self.state.conversation_active = False
        finally:
            await self._cleanup_session(session)
    
    async def _run_conversation_loop(self, session: AgentSession):
        """Main conversation loop for voice agents."""
        
        # Initial checkpoint
        await self._verify_session_health(session)
        await asyncio.sleep(2)  # Give time for full initialization
        
        # Verify realtime session is ready
        if hasattr(session._activity, "_rt_session") and session._activity._rt_session:
            logger.info("Realtime session confirmed ready")
        else:
            logger.warning("Realtime session not ready, proceeding anyway")
        
        # Start conversation based on mode
        if self.config.mode in ["friendly", "debate"]:
            await self._run_two_agent_conversation(session)
        else:
            await self._run_multi_agent_conversation(session)
    
    async def _run_two_agent_conversation(self, session: AgentSession):
        """Run conversation between two agents."""
        if len(self.config.agents) < 2:
            logger.error("Two agent conversation requires at least 2 agents")
            return
            
        # Start with first agent
        first_agent = self.agent_voice_map["agent1"]
        await self._safe_generate_reply(
            session,
            instructions=f"As the {first_agent['role']}, give a {first_agent['perspective']} view on: {self.state.topic}",
            voice=first_agent["voice"],
            speaker="agent1"
        )
        
        # Alternate between agents
        agent_index = 0
        while self.state.conversation_active and self.state.turn_count < self.state.max_turns:
            await asyncio.sleep(3)
            
            if not await self._verify_session_health(session):
                break
            
            self.state.turn_count += 1
            agent_index = (agent_index + 1) % 2  # Alternate between 2 agents
            current_speaker = f"agent{agent_index + 1}"
            current_agent = self.agent_voice_map[current_speaker]
            
            self.state.current_speaker = current_speaker
            
            await self._safe_generate_reply(
                session,
                instructions=f"As the {current_agent['role']}, respond with a {current_agent['perspective']} perspective to the previous points about: {self.state.topic}",
                voice=current_agent["voice"],
                speaker=current_speaker
            )
            
            logger.info(f"Completed turn {self.state.turn_count}/{self.state.max_turns} - {current_agent['role']}")
    
    async def _run_multi_agent_conversation(self, session: AgentSession):
        """Run conversation between multiple agents (roundtable style)."""
        
        # Start with first agent
        first_agent = self.agent_voice_map["agent1"]
        await self._safe_generate_reply(
            session,
            instructions=f"As the {first_agent['role']}, give a {first_agent['perspective']} view on: {self.state.topic}",
            voice=first_agent["voice"],
            speaker="agent1"
        )
        
        # Cycle through all agents
        agent_index = 0
        while self.state.conversation_active and self.state.turn_count < self.state.max_turns:
            await asyncio.sleep(3)
            
            if not await self._verify_session_health(session):
                break
            
            self.state.turn_count += 1
            agent_index = (agent_index + 1) % len(self.agent_voice_map)
            current_speaker = self.state.agent_order[agent_index]
            current_agent = self.agent_voice_map[current_speaker]
            
            self.state.current_speaker = current_speaker
            
            await self._safe_generate_reply(
                session,
                instructions=f"As the {current_agent['role']}, respond with a {current_agent['perspective']} perspective to the previous points about: {self.state.topic}",
                voice=current_agent["voice"],
                speaker=current_speaker
            )
            
            logger.info(f"Completed turn {self.state.turn_count}/{self.state.max_turns} - {current_agent['role']}")
    
    async def _safe_generate_reply(
        self,
        session: AgentSession,
        instructions: str,
        voice: str,
        speaker: str,
    ) -> bool:
        """Safely generate a voice reply with error handling and retries."""
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not session._started or session._activity is None:
                    logger.warning(f"Session not ready for {speaker}")
                    return False
                
                # Update voice
                if hasattr(session.llm, "voice"):
                    session.llm.voice = voice
                
                # Get conversation history for context
                chat_history = session.history
                recent_messages = []
                if len(chat_history.items) > 1:  # Skip system message
                    # Get last 3 messages for context
                    recent_items = chat_history.items[-3:]
                    for item in recent_items:
                        if hasattr(item, "text_content") and item.text_content:
                            recent_messages.append(item.text_content)
                
                # Create context-aware instructions
                if recent_messages:
                    context = " Previous context: " + " | ".join(recent_messages[-2:])
                    contextual_instructions = f"{instructions}. {context}"
                else:
                    contextual_instructions = instructions
                
                # Get agent name for logging
                agent_info = self.agent_voice_map.get(speaker, {})
                agent_name = agent_info.get('name', speaker)
                
                # Generate voice reply
                logger.info(f"{agent_name} ({speaker}) speaking (turn {self.state.turn_count + 1})")
                speech_handle = session.generate_reply(user_input=contextual_instructions)
                
                # Wait for speech to complete with timeout
                try:
                    await asyncio.wait_for(speech_handle.wait_for_playout(), timeout=15.0)
                    logger.info(f"{agent_name} finished speaking")
                    return True
                
                except asyncio.TimeoutError:
                    if retry_count < max_retries:
                        logger.warning(f"Speech timeout for {agent_name}, retrying...")
                        retry_count += 1
                        await asyncio.sleep(2)
                        continue
                    else:
                        logger.warning(f"Max retries exceeded for {agent_name}")
                        return False
                
            except RuntimeError as e:
                if "closing" in str(e).lower() or "draining" in str(e).lower():
                    logger.warning(f"Session closing/draining for {speaker}: {e}")
                    self.state.session_healthy = False
                    return False
                else:
                    retry_count += 1
                    logger.warning(f"RuntimeError for {speaker} (attempt {retry_count}): {e}")
                    if retry_count < max_retries:
                        await asyncio.sleep(1)
                        continue
                    else:
                        logger.error(f"Max retries exceeded for {speaker}")
                        return False
            
            except Exception as e:
                retry_count += 1
                logger.error(f"Unexpected error for {speaker} (attempt {retry_count}): {e}")
                if retry_count < max_retries:
                    await asyncio.sleep(1)
                    continue
                else:
                    self.state.last_error = str(e)
                    return False
        
        return False
    
    async def _verify_session_health(self, session: AgentSession) -> bool:
        """Verify session is healthy and ready for operations."""
        
        try:
            if not session._started:
                logger.warning("Session not started")
                self.state.session_healthy = False
                return False
            
            if session._activity is None:
                logger.warning("Session activity is None")
                self.state.session_healthy = False
                return False
            
            self.state.session_healthy = True
            return True
        
        except Exception as e:
            logger.error(f"Error checking session health: {e}")
            self.state.session_healthy = False
            return False
    
    async def _cleanup_session(self, session: AgentSession):
        """Clean up session with proper error handling."""
        
        logger.info("Starting voice session cleanup...")
        
        try:
            # Try to interrupt any ongoing speech
            if session._started and session._activity:
                try:
                    await asyncio.wait_for(session.interrupt(), timeout=2.0)
                except (asyncio.TimeoutError, RuntimeError):
                    logger.warning("Could not interrupt session cleanly")
            
            # Drain the session
            if session._started:
                try:
                    await asyncio.wait_for(session.drain(), timeout=5.0)
                    logger.info("Session drained successfully")
                except asyncio.TimeoutError:
                    logger.warning("Session drain timeout")
                except RuntimeError as e:
                    logger.warning(f"Session drain error: {e}")
            
            # Close the session
            try:
                await asyncio.wait_for(session.aclose(), timeout=3.0)
                logger.info("Session closed successfully")
            except asyncio.TimeoutError:
                logger.warning("Session close timeout")
            except Exception as e:
                logger.error(f"Session close error: {e}")
        
        except Exception as e:
            logger.error(f"Critical error during cleanup: {e}")
        
        # Final status report
        logger.info(
            f"Voice conversation completed: {self.state.turn_count} turns, "
            f"healthy: {self.state.session_healthy}, "
            f"last_error: {self.state.last_error}"
        )


async def run_voice_conversation(config: ConversationConfig, ctx: JobContext):
    """Run a voice conversation with the given configuration."""
    runner = VoiceConversationRunner(config)
    await runner.start_conversation(ctx)


def create_voice_entrypoint(config: ConversationConfig):
    """Create an entrypoint function for LiveKit CLI."""
    async def entrypoint(ctx: JobContext):
        await run_voice_conversation(config, ctx)
    return entrypoint
