import asyncio  
import logging  
from dataclasses import dataclass  
from typing import Optional  
from dotenv import load_dotenv
import os
import sys

from livekit.agents import JobContext, WorkerOptions, cli  
from livekit.agents.voice import Agent, AgentSession  
from livekit.plugins.google.beta.realtime import RealtimeModel  
from google.genai import types  
  
load_dotenv()  
logger = logging.getLogger("dual-agent-conversation")  

# Check for topic from environment variable or prompt user
topic = os.getenv('DUOTALK_TOPIC')
if not topic:
    topic = input("Enter the topic for the conversation: ")
@dataclass  
class ConversationState:  
    topic: str = topic  
    conversation_mode: str = "debate"  # "friendly" or "debate"  
    turn_count: int = 0  
    max_turns: int = 12  
    conversation_active: bool = True  
    current_speaker: str = "agent1"  
    last_error: Optional[str] = None  
    session_healthy: bool = True
    single_agent: bool = False  # New field for single agent mode
  
class DualPersonaAgent(Agent):  
    def __init__(self, topic: str, mode: str, single_agent: bool = False):  
        if single_agent:
            # Single agent mode - interactive with user
            if mode == "friendly":  
                instructions = f"""You are a friendly AI assistant having a conversation with the user about {topic}.
                Engage naturally and ask follow-up questions to keep the conversation flowing.
                Be curious, helpful, and encouraging. Listen to what the user says and respond thoughtfully.
                Keep your responses conversational and engaging, but not too long."""
            else:  
                instructions = f"""You are an AI assistant having a discussion with the user about {topic}.
                Be engaging and thought-provoking. Ask good questions and share interesting perspectives.
                Challenge ideas constructively and encourage deeper thinking.
                Keep your responses conversational but substantive."""
        else:
            # Multi-agent mode - agents talk to each other
            if mode == "friendly":  
                instructions = f"""You are participating in a friendly discussion about {topic}.  
                You will receive specific instructions about which supportive perspective to take.  
                Always respond in one line only to save API costs.  
                Be collaborative and encouraging. """  
            else:  
                instructions = f"""You are participating in a debate about {topic}.  
                You will receive specific instructions about which perspective to take.  
                Always respond in one line only to save API costs.  
                Be direct and contrary.  """  
          
        super().__init__(instructions=instructions)  
        self.topic = topic  
        self.mode = mode
        self.single_agent = single_agent
  
async def get_conversation_mode() -> str:  
    """Get conversation mode from user input"""  
    # Check for mode from environment variable first
    env_mode = os.getenv('DUOTALK_MODE')
    if env_mode:
        return env_mode
        
    print("\nSelect conversation mode:")  
    print("1. Friendly discussion")  
    print("2. Debate format")  
      
    while True:  
        try:  
            choice = input("Enter your choice (1 or 2): ").strip()  
            if choice == "1":  
                return "friendly"  
            elif choice == "2":  
                return "debate"  
            else:  
                print("Please enter 1 or 2")  
        except (EOFError, KeyboardInterrupt):  
            return "debate"  # Default fallback  
  
async def entrypoint(ctx: JobContext):  
    await ctx.connect()  
      
    # Check if single agent mode is requested
    single_agent_mode = os.getenv('DUOTALK_SINGLE_AGENT', 'false').lower() == 'true'
    
    # Get user's preferred conversation mode  
    mode = await get_conversation_mode()  
      
    state = ConversationState(conversation_mode=mode, single_agent=single_agent_mode)  
      
    # Initialize agent with single agent mode setting
    agent = DualPersonaAgent(state.topic, mode, single_agent_mode)  
      
    # Session with comprehensive error handling  
    session = AgentSession[ConversationState](  
        userdata=state,  
        llm=RealtimeModel(  
            # model="gemini-2.0-flash-live-001",
            model= "gemini-2.5-flash-preview-native-audio-dialog",  
            instructions=agent.instructions,  
            voice="Puck",  
        ),  
        allow_interruptions=True,  
        turn_detection="realtime_llm",  
        min_interruption_duration=0.3,  
    )  
      
    # Error handling for session events  
    def on_session_error(error):  
        logger.error(f"Session error: {error}")  
        state.session_healthy = False  
        state.conversation_active = False  
      
    session.on("error", on_session_error)  
      
    try:  
        await session.start(agent=agent, room=ctx.room)  
        logger.info(f"Session started successfully in {mode} mode")  
          
        # Checkpoint: Verify session is running  
        if not session._started:  
            raise RuntimeError("Session failed to start properly")  
          
        await run_conversation(session, state)  
          
    except Exception as e:  
        logger.error(f"Critical error in entrypoint: {e}")  
        state.conversation_active = False  
    finally:  
        await cleanup_session(session, state)  
  
async def run_conversation(session: AgentSession, state: ConversationState):  
    """Main conversation loop supporting both single agent and multi-agent modes"""  
      
    try:  
        if state.single_agent:
            logger.info("Starting single agent conversation with user...")
            await run_single_agent_conversation(session, state)
        elif state.conversation_mode == "friendly":  
            logger.info("Starting friendly conversation...")  
            await run_friendly_conversation(session, state)  
        else:  
            logger.info("Starting debate conversation...")  
            await run_debate_conversation(session, state)  
              
    except asyncio.CancelledError:  
        logger.info("Conversation cancelled by user")  
        state.conversation_active = False  
    except Exception as e:  
        logger.error(f"Error in conversation loop: {e}")  
        state.last_error = str(e)  
        state.conversation_active = False  

async def run_single_agent_conversation(session: AgentSession, state: ConversationState):
    """Single agent conversation - agent talks with the user interactively"""
    
    # Initial checkpoint  
    await verify_session_health(session, state)

    await asyncio.sleep(2)  # Give time for full initialization  
      
    # Verify realtime session is ready  
    if hasattr(session._activity, '_rt_session') and session._activity._rt_session:  
        logger.info("Realtime session confirmed ready for single agent mode")  
    else:  
        logger.warning("Realtime session not ready, proceeding anyway")  
    
    # Send initial greeting to start the conversation
    welcome_message = f"Hello! I'm here to chat with you about {state.topic}. What would you like to discuss about this topic?"
    
    try:
        # Start the conversation with a welcome message using generate_reply
        logger.info("Starting single agent conversation with user...")
        speech_handle = session.generate_reply(user_input=welcome_message)
        await asyncio.wait_for(speech_handle.wait_for_playout(), timeout=15.0)
        logger.info("Welcome message delivered")
        
        # In single agent mode, the conversation continues naturally
        # The LiveKit session will handle user input and agent responses automatically
        # We just need to keep the session alive and healthy
        
        while state.conversation_active:
            await asyncio.sleep(2)  # Keep session alive
            
            # Check if session is still healthy
            if not await verify_session_health(session, state):
                break
                
            # The conversation is handled by LiveKit's realtime interaction
            # User speaks -> automatic transcription -> agent processes -> agent responds
            # No need for manual intervention in the conversation loop
            
    except Exception as e:
        logger.error(f"Error in single agent conversation: {e}")
        state.conversation_active = False
  
async def run_friendly_conversation(session: AgentSession, state: ConversationState):  
    """Friendly conversation between two collaborative agents"""  
      
    # Initial checkpoint  
    await verify_session_health(session, state)  

    await asyncio.sleep(2)  # Give time for full initialization  
      
    # Verify realtime session is ready  
    if hasattr(session._activity, '_rt_session') and session._activity._rt_session:  
        logger.info("Realtime session confirmed ready")  
    else:  
        logger.warning("Realtime session not ready, proceeding anyway")  
      
    # Start with first agent - use direct content instruction  
    await safe_generate_reply(  
        session, state,  
        instructions=topic,    
        voice="Puck",  
        speaker="agent1"  
    )  
      
    # Main conversation loop  
    while state.conversation_active and state.turn_count < state.max_turns:  
        await asyncio.sleep(3)  
          
        if not await verify_session_health(session, state):  
            break  
          
        state.turn_count += 1  
          
        if state.current_speaker == "agent1":  
            state.current_speaker = "agent2"  
            await safe_generate_reply(  
                session, state,  
                instructions=topic,   
                voice="Charon",  
                speaker="agent2"  
            )  
        else:  
            state.current_speaker = "agent1"  
            await safe_generate_reply(  
                session, state,  
                instructions=topic,  
                voice="Puck",  
                speaker="agent1"  
            )  
          
        logger.info(f"Completed turn {state.turn_count}/{state.max_turns}")
  
async def run_debate_conversation(session: AgentSession, state: ConversationState):  
    """Debate conversation between optimist and skeptic"""  
      
    # Initial checkpoint  
    await verify_session_health(session, state)  

    await asyncio.sleep(2)  # Give time for full initialization  
      
    # Verify realtime session is ready  
    if hasattr(session._activity, '_rt_session') and session._activity._rt_session:  
        logger.info("Realtime session confirmed ready")  
    else:  
        logger.warning("Realtime session not ready, proceeding anyway") 
      
    # Start with optimist perspective  
    await safe_generate_reply(  
        session, state,  
        instructions=topic,  # Direct content  
        voice="Puck",  
        speaker="optimist"  
    )  
      
    # Main conversation loop  
    while state.conversation_active and state.turn_count < state.max_turns:  
        await asyncio.sleep(3)  
          
        if not await verify_session_health(session, state):  
            break  
          
        state.turn_count += 1  
          
        if state.current_speaker == "optimist":  
            state.current_speaker = "skeptic"  
            await safe_generate_reply(  
                session, state,  
                instructions=topic,  # Direct content  
                voice="Charon",  
                speaker="skeptic"  
            )  
        else:  
            state.current_speaker = "optimist"  
            await safe_generate_reply(  
                session, state,  
                instructions=topic,  # Direct content  
                voice="Puck",  
                speaker="optimist"  
            )  
          
        logger.info(f"Completed turn {state.turn_count}/{state.max_turns}")
  
async def safe_generate_reply(  
    session: AgentSession,   
    state: ConversationState,   
    instructions: str,   
    voice: str,   
    speaker: str  
) -> bool:  
    """Safely generate a reply with error handling and retries"""  
      
    max_retries = 3  
    retry_count = 0  
      
    while retry_count < max_retries:  
        try:  
            # Checkpoint: Verify session before generating reply  
            if not session._started or session._activity is None:  
                logger.warning(f"Session not ready for {speaker}")  
                return False  
              
            # Update voice  
            if hasattr(session.llm, 'voice'):  
                session.llm.voice = voice  
              
            # Get conversation history for context  
            chat_history = session.history  
            recent_messages = []  
            if len(chat_history.items) > 1:  # Skip system message  
                # Get last 3 messages for context  
                recent_items = chat_history.items[-3:]  
                for item in recent_items:  
                    if hasattr(item, 'text_content') and item.text_content:  
                        recent_messages.append(item.text_content)  
              
            # Create context-aware instructions  
            if recent_messages:  
                context = " Previous context: " + " | ".join(recent_messages[-2:])  # Last 2 messages  
                contextual_instructions = f"{instructions}. {context}"  
            else:  
                contextual_instructions = instructions  
              
            # Generate reply with context  
            logger.info(f"{speaker.capitalize()} speaking (turn {state.turn_count + 1})")  
            speech_handle = session.generate_reply(user_input=contextual_instructions)  
              
            # Wait for speech to complete with timeout  
            try:  
                await asyncio.wait_for(speech_handle.wait_for_playout(), timeout=15.0)  
                logger.info(f"{speaker.capitalize()} finished speaking")  
                return True  
                  
            except asyncio.TimeoutError:  
                if retry_count < max_retries:  
                    logger.warning(f"Speech timeout for {speaker}, retrying...")  
                    retry_count += 1  
                    await asyncio.sleep(2)  
                    continue  
                else:  
                    logger.warning(f"Max retries exceeded for {speaker}")  
                    return False  
                      
        except RuntimeError as e:  
            if "closing" in str(e).lower() or "draining" in str(e).lower():  
                logger.warning(f"Session closing/draining for {speaker}: {e}")  
                state.session_healthy = False  
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
                state.last_error = str(e)  
                return False  
      
    return False
  
async def verify_session_health(session: AgentSession, state: ConversationState) -> bool:  
    """Verify session is healthy and ready for operations"""  
      
    try:  
        if not session._started:  
            logger.warning("Session not started")  
            state.session_healthy = False  
            return False  
          
        if session._activity is None:  
            logger.warning("Session activity is None")  
            state.session_healthy = False  
            return False  
          
        state.session_healthy = True  
        return True  
          
    except Exception as e:  
        logger.error(f"Error checking session health: {e}")  
        state.session_healthy = False  
        return False  
  
async def cleanup_session(session: AgentSession, state: ConversationState):  
    """Clean up session with proper error handling"""  
      
    logger.info("Starting session cleanup...")  
      
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
    logger.info(f"Conversation completed: {state.turn_count} turns, "  
                f"healthy: {state.session_healthy}, "  
                f"last_error: {state.last_error}")  
  
if __name__ == "__main__":  
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))