# to run it, add gemini api in .env and  
# then run "python four_agents_duotalk.py console" in terminal  
  
import asyncio  
import logging  
import os
from dataclasses import dataclass  
from typing import Optional  
  
from dotenv import load_dotenv  
from google.genai import types  
  
from livekit.agents import JobContext, WorkerOptions, cli  
from livekit.agents.voice import Agent, AgentSession  
from livekit.plugins.google.beta.realtime import RealtimeModel  
  
load_dotenv()  
logger = logging.getLogger("four-agent-conversation")  

# Check for topic from environment variable or prompt user
topic = os.getenv('DUOTALK_TOPIC')
if not topic:
    topic = input("Enter the topic for the conversation: ")

# Check for mode from environment variable
env_mode = os.getenv('DUOTALK_MODE', 'roundtable')

# Check for number of agents from environment variable
env_agents = int(os.getenv('DUOTALK_AGENTS', '3'))

@dataclass  
class ConversationState:  
    topic: str = topic  
    conversation_mode: str = env_mode
    turn_count: int = 0  
    max_turns: int = 20  # More turns for multiple agents  
    conversation_active: bool = True  
    current_speaker: str = "agent1"  
    last_error: Optional[str] = None  
    session_healthy: bool = True  
    agent_order: list = None  
    num_agents: int = env_agents  # Use agents from environment variable
      
    def __post_init__(self):  
        if self.agent_order is None:
            # Create agent order based on the number of agents from environment
            self.agent_order = [f"agent{i+1}" for i in range(self.num_agents)]  
  
  
class QuadPersonaAgent(Agent):  
    def __init__(self, topic: str, mode: str):  
        if mode == "panel":
            instructions = f"""You are participating in an expert panel discussion about {topic}.  
            You will receive specific instructions about your area of expertise.  
            Keep your responses brief - maximum 2 sentences with professional insight.  
            Share expert knowledge and evidence-based viewpoints."""
        else:
            instructions = f"""You are participating in a roundtable discussion about {topic}.  
            You will receive specific instructions about which perspective to take.  
            Keep your responses brief - maximum 2 sentences to ensure smooth conversation flow.  
            Be engaging and contribute unique viewpoints without interrupting others."""  
          
        super().__init__(instructions=instructions)  
        self.topic = topic  
        self.mode = mode  
  
  
async def get_conversation_mode() -> str:  
    """Get conversation mode from user input"""  
    # Check for mode from environment variable first
    env_mode = os.getenv('DUOTALK_MODE')
    if env_mode:
        return env_mode
        
    print("\nSelect conversation mode:")  
    print("1. Friendly discussion (2 agents)")  
    print("2. Debate format (2 agents)")  
    print("3. Roundtable discussion (3+ agents)")  
      
    while True:  
        try:  
            choice = input("Enter your choice (1, 2, or 3): ").strip()  
            if choice == "1":  
                return "friendly"  
            elif choice == "2":  
                return "debate"  
            elif choice == "3":  
                return "roundtable"  
            else:  
                print("Please enter 1, 2, or 3")  
        except (EOFError, KeyboardInterrupt):  
            return "roundtable"  # Default to roundtable mode  
  
  
async def entrypoint(ctx: JobContext):  
    await ctx.connect()  
  
    # Get user's preferred conversation mode  
    mode = await get_conversation_mode()  
  
    state = ConversationState(conversation_mode=mode)  
  
    # Agent with quad persona support  
    agent = QuadPersonaAgent(state.topic, mode)  
  
    # Session with comprehensive error handling  
    session = AgentSession[ConversationState](  
        userdata=state,  
        llm=RealtimeModel(  
            model="gemini-2.5-flash-preview-native-audio-dialog",  
            instructions=agent.instructions,  
            voice="Puck",  
        ),  
        allow_interruptions=True,  # Keep as True for RealtimeModel compatibility
        turn_detection="realtime_llm",  # Use realtime LLM detection that works
        min_interruption_duration=1.0,  
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
    """Main conversation loop supporting friendly, debate, and roundtable modes"""  
      
    try:  
        if state.conversation_mode == "friendly":  
            logger.info("Starting friendly conversation...")  
            await run_friendly_conversation(session, state)  
        elif state.conversation_mode == "debate":  
            logger.info("Starting debate conversation...")  
            await run_debate_conversation(session, state)  
        elif state.conversation_mode == "roundtable":  
            logger.info("Starting roundtable conversation...")  
            await run_four_agent_conversation(session, state)  
        elif state.conversation_mode == "panel":  
            logger.info("Starting expert panel discussion...")  
            await run_four_agent_conversation(session, state)  # Use same function but with panel personas
        else:
            logger.info(f"Starting {state.conversation_mode} conversation...")  
            await run_four_agent_conversation(session, state)  # Default to multi-agent  
    except asyncio.CancelledError:  
        logger.info("Conversation cancelled by user")  
        state.conversation_active = False  
    except Exception as e:  
        logger.error(f"Error in conversation loop: {e}")  
        state.last_error = str(e)  
        state.conversation_active = False  
  
  
async def run_four_agent_conversation(session: AgentSession, state: ConversationState):  
    """Roundtable conversation between multiple agents with different perspectives"""  
      
    # Initial checkpoint  
    await verify_session_health(session, state)  
    await asyncio.sleep(2)  # Give time for full initialization  
      
    # Verify realtime session is ready  
    if hasattr(session._activity, "_rt_session") and session._activity._rt_session:  
        logger.info("Realtime session confirmed ready")  
    else:  
        logger.warning("Realtime session not ready, proceeding anyway")  
      
    # Define agent personas and voices - dynamically support any number of agents
    def generate_agent_config(num_agents, mode="roundtable"):
        """Generate agent configuration for any number of agents"""
        voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede", "Alloy", "Echo", "Fable", "Onyx", "Nova"]
        
        if mode == "panel":
            # Expert panel mode - use academic/professional personas
            roles = ["researcher", "analyst", "scientist", "economist", "strategist", "educator", "consultant", "philosopher", "engineer", "historian"]
            perspectives = [
                "research-based and evidence-driven",
                "analytical and data-focused", 
                "scientific and methodical",
                "economic and market-oriented",
                "strategic and long-term focused",
                "educational and explanatory",
                "practical and advisory",
                "theoretical and conceptual",
                "technical and solution-oriented",
                "historical and context-aware"
            ]
        else:
            # Regular roundtable mode
            roles = ["optimist", "skeptic", "pragmatist", "theorist", "analyst", "creative", "realist", "visionary", "diplomat", "rebel"]
            perspectives = [
                "positive and hopeful",
                "critical and questioning", 
                "practical and solution-focused",
                "abstract and philosophical",
                "analytical and data-driven",
                "innovative and imaginative",
                "grounded and realistic",
                "forward-thinking and aspirational",
                "balanced and diplomatic",
                "unconventional and challenging"
            ]
        
        config = {}
        for i in range(num_agents):
            agent_id = f"agent{i+1}"
            config[agent_id] = {
                "voice": voices[i % len(voices)],
                "role": roles[i % len(roles)],
                "perspective": perspectives[i % len(perspectives)]
            }
        return config
    
    agent_config = generate_agent_config(len(state.agent_order), state.conversation_mode)  
      
    # Start with first agent  
    current_agent = agent_config["agent1"]  
    await safe_generate_reply(  
        session,   
        state,   
        instructions=f"as the {current_agent['role']}, give your brief {current_agent['perspective']} view on: {state.topic}",   
        voice=current_agent["voice"],   
        speaker="agent1"  
    )  
      
    # Main conversation loop  
    agent_index = 0  
    num_agents = len(state.agent_order)  # Use dynamic agent count
    logger.info(f"Starting roundtable with {num_agents} agents: {state.agent_order}")
    
    while state.conversation_active and state.turn_count < state.max_turns:  
        await asyncio.sleep(3)  # Increased delay between agents for better audio quality
          
        if not await verify_session_health(session, state):  
            break  
              
        state.turn_count += 1  
        agent_index = (agent_index + 1) % num_agents  # Cycle through dynamic number of agents  
        current_speaker = state.agent_order[agent_index]  
        current_agent = agent_config[current_speaker]  
          
        state.current_speaker = current_speaker  
          
        # Generate simple, direct instructions  
        simple_instructions = f"as the {current_agent['role']}, share your brief {current_agent['perspective']} thoughts on: {state.topic}"
        
        success = await safe_generate_reply(  
            session,  
            state,  
            instructions=simple_instructions,  
            voice=current_agent["voice"],  
            speaker=current_speaker  
        )  
        
        if success:
            logger.info(f"Completed turn {state.turn_count}/{state.max_turns} - {current_agent['role']} ({current_speaker})")  
        else:
            logger.warning(f"Failed turn {state.turn_count}/{state.max_turns} - {current_agent['role']} ({current_speaker}), continuing...")
            # Continue the conversation even if one agent fails  
  
  
# Include original 2-agent functions for backward compatibility  
async def run_friendly_conversation(session: AgentSession, state: ConversationState):  
    """Friendly conversation between two collaborative agents"""  
      
    await verify_session_health(session, state)  
    await asyncio.sleep(2)  
      
    if hasattr(session._activity, "_rt_session") and session._activity._rt_session:  
        logger.info("Realtime session confirmed ready")  
    else:  
        logger.warning("Realtime session not ready, proceeding anyway")  
  
    await safe_generate_reply(session, state, instructions=topic, voice="Puck", speaker="agent1")  
  
    while state.conversation_active and state.turn_count < state.max_turns:  
        await asyncio.sleep(3)  
  
        if not await verify_session_health(session, state):  
            break  
  
        state.turn_count += 1  
  
        if state.current_speaker == "agent1":  
            state.current_speaker = "agent2"  
            await safe_generate_reply(  
                session, state, instructions=topic, voice="Charon", speaker="agent2"  
            )  
        else:  
            state.current_speaker = "agent1"  
            await safe_generate_reply(  
                session, state, instructions=topic, voice="Puck", speaker="agent1"  
            )  
  
        logger.info(f"Completed turn {state.turn_count}/{state.max_turns}")  
  
  
async def run_debate_conversation(session: AgentSession, state: ConversationState):  
    """Debate conversation between optimist and skeptic"""  
      
    await verify_session_health(session, state)  
    await asyncio.sleep(2)  
      
    if hasattr(session._activity, "_rt_session") and session._activity._rt_session:  
        logger.info("Realtime session confirmed ready")  
    else:  
        logger.warning("Realtime session not ready, proceeding anyway")  
  
    await safe_generate_reply(  
        session, state, instructions=topic, voice="Puck", speaker="optimist"  
    )  
  
    while state.conversation_active and state.turn_count < state.max_turns:  
        await asyncio.sleep(3)  
  
        if not await verify_session_health(session, state):  
            break  
  
        state.turn_count += 1  
  
        if state.current_speaker == "optimist":  
            state.current_speaker = "skeptic"  
            await safe_generate_reply(  
                session, state, instructions=topic, voice="Charon", speaker="skeptic"  
            )  
        else:  
            state.current_speaker = "optimist"  
            await safe_generate_reply(  
                session, state, instructions=topic, voice="Puck", speaker="optimist"  
            )  
  
        logger.info(f"Completed turn {state.turn_count}/{state.max_turns}")  
  
  
async def safe_generate_reply(  
    session: AgentSession,  
    state: ConversationState,  
    instructions: str,  
    voice: str,  
    speaker: str,  
) -> bool:  
    """Safely generate a reply with error handling and retries"""  
  
    max_retries = 3  
    retry_count = 0  
  
    while retry_count < max_retries:  
        try:  
            if not session._started or session._activity is None:  
                logger.warning(f"Session not ready for {speaker}")  
                return False  
  
            # Update voice and ensure it's set properly
            if hasattr(session.llm, "voice"):  
                session.llm.voice = voice  
                # Add small delay to allow voice change to register
                await asyncio.sleep(0.5)
  
            # Simplify instructions to reduce generation complexity - no context needed
            # Keep instructions short and direct for better audio quality
            short_instructions = f"In 1-2 sentences, {instructions}"
  
            # Generate reply with simplified instructions  
            logger.info(f"{speaker.capitalize()} speaking (turn {state.turn_count + 1})")  
            speech_handle = session.generate_reply(user_input=short_instructions)  
  
            # Wait for speech to complete with more generous timeout for multi-agent scenarios
            try:  
                await asyncio.wait_for(speech_handle.wait_for_playout(), timeout=20.0)  # Increased timeout for quality
                logger.info(f"{speaker.capitalize()} finished speaking")  
                # Add pause between speakers to prevent audio conflicts
                await asyncio.sleep(1.0)  
                return True  
  
            except asyncio.TimeoutError:  
                if retry_count < max_retries - 1:  # Give one less retry
                    logger.warning(f"Speech timeout for {speaker}, retrying...")  
                    retry_count += 1  
                    await asyncio.sleep(1)  # Reduced sleep time
                    continue  
                else:  
                    logger.warning(f"Max retries exceeded for {speaker}, skipping turn")  
                    return True  # Return True to continue conversation instead of failing  
  
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
    logger.info(  
        f"Conversation completed: {state.turn_count} turns, "  
        f"healthy: {state.session_healthy}, "  
        f"last_error: {state.last_error}"  
    )  
  
  
if __name__ == "__main__":  
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))