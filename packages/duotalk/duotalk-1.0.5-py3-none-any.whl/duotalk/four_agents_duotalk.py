# to run it, add gemini api in .env and  
# then run "python four_agents_duotalk.py console" in terminal  
  
import asyncio  
import logging  
from dataclasses import dataclass  
from typing import Optional  
  
from dotenv import load_dotenv  
from google.genai import types  
  
from livekit.agents import JobContext, WorkerOptions, cli  
from livekit.agents.voice import Agent, AgentSession  
from livekit.plugins.google.beta.realtime import RealtimeModel  
  
load_dotenv()  
logger = logging.getLogger("four-agent-conversation")  
topic = input("Enter the topic for the conversation: ")  
  
  
@dataclass  
class ConversationState:  
    topic: str = topic  
    conversation_mode: str = "roundtable"  
    turn_count: int = 0  
    max_turns: int = 20  # More turns for 4 agents  
    conversation_active: bool = True  
    current_speaker: str = "agent1"  
    last_error: Optional[str] = None  
    session_healthy: bool = True  
    agent_order: list = None  
      
    def __post_init__(self):  
        if self.agent_order is None:  
            self.agent_order = ["agent1", "agent2", "agent3", "agent4"]  
  
  
class QuadPersonaAgent(Agent):  
    def __init__(self, topic: str, mode: str):  
        instructions = f"""You are participating in a roundtable discussion about {topic}.  
        You will receive specific instructions about which perspective to take.  
        Always respond in one line only to save API costs.  
        Be engaging and contribute unique viewpoints."""  
          
        super().__init__(instructions=instructions)  
        self.topic = topic  
        self.mode = mode  
  
  
async def get_conversation_mode() -> str:  
    """Get conversation mode from user input"""  
    print("\nSelect conversation mode:")  
    print("1. Friendly discussion (2 agents)")  
    print("2. Debate format (2 agents)")  
    print("3. Roundtable discussion (4 agents)")  
      
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
            return "roundtable"  # Default to 4-agent mode  
  
  
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
    except asyncio.CancelledError:  
        logger.info("Conversation cancelled by user")  
        state.conversation_active = False  
    except Exception as e:  
        logger.error(f"Error in conversation loop: {e}")  
        state.last_error = str(e)  
        state.conversation_active = False  
  
  
async def run_four_agent_conversation(session: AgentSession, state: ConversationState):  
    """Roundtable conversation between four agents with different perspectives"""  
      
    # Initial checkpoint  
    await verify_session_health(session, state)  
    await asyncio.sleep(2)  # Give time for full initialization  
      
    # Verify realtime session is ready  
    if hasattr(session._activity, "_rt_session") and session._activity._rt_session:  
        logger.info("Realtime session confirmed ready")  
    else:  
        logger.warning("Realtime session not ready, proceeding anyway")  
      
    # Define the four agent personas and voices  
    agent_config = {  
        "agent1": {"voice": "Puck", "role": "optimist", "perspective": "positive and hopeful"},  
        "agent2": {"voice": "Charon", "role": "skeptic", "perspective": "critical and questioning"},  
        "agent3": {"voice": "Puck", "role": "pragmatist", "perspective": "practical and solution-focused"},  
        "agent4": {"voice": "Charon", "role": "theorist", "perspective": "abstract and philosophical"}  
    }  
      
    # Start with first agent  
    current_agent = agent_config["agent1"]  
    await safe_generate_reply(  
        session,   
        state,   
        instructions=f"As the {current_agent['role']}, give a {current_agent['perspective']} view on: {state.topic}",   
        voice=current_agent["voice"],   
        speaker="agent1"  
    )  
      
    # Main conversation loop  
    agent_index = 0  
    while state.conversation_active and state.turn_count < state.max_turns:  
        await asyncio.sleep(3)  
          
        if not await verify_session_health(session, state):  
            break  
              
        state.turn_count += 1  
        agent_index = (agent_index + 1) % 4  # Cycle through 4 agents  
        current_speaker = state.agent_order[agent_index]  
        current_agent = agent_config[current_speaker]  
          
        state.current_speaker = current_speaker  
          
        await safe_generate_reply(  
            session,  
            state,  
            instructions=f"As the {current_agent['role']}, respond with a {current_agent['perspective']} perspective to the previous points about: {state.topic}",  
            voice=current_agent["voice"],  
            speaker=current_speaker  
        )  
          
        logger.info(f"Completed turn {state.turn_count}/{state.max_turns} - {current_agent['role']}")  
  
  
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
                context = " Previous context: " + " | ".join(  
                    recent_messages[-2:]  
                )  # Last 2 messages  
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
    logger.info(  
        f"Conversation completed: {state.turn_count} turns, "  
        f"healthy: {state.session_healthy}, "  
        f"last_error: {state.last_error}"  
    )  
  
  
if __name__ == "__main__":  
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))