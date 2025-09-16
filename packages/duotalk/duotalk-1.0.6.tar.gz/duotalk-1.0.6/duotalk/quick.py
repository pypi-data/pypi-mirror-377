"""
Quick Start Functions - Simple entry points for common conversation patterns.
These functions provide the easiest way to start conversations with minimal setup.
"""

from typing import List, Optional, Dict, Any
import asyncio
import sys

from .builder import ConversationBuilder
from .runner import ConversationRunner
from ..config.enhanced_config import DuoTalkConfig


def quick_debate(
    topic: str,
    agents: Optional[List[str]] = None,
    max_turns: int = 15,
    voice: bool = True,
    **kwargs
) -> ConversationRunner:
    """
    Quick setup for a debate conversation.
    
    Args:
        topic: The debate topic
        agents: Optional list of persona names (defaults to ["optimist", "skeptic"])
        max_turns: Maximum conversation turns
        voice: Enable voice synthesis
        **kwargs: Additional configuration options
    
    Returns:
        ConversationRunner instance ready to start
    
    Example:
        runner = quick_debate("Should AI replace human creativity?")
        asyncio.run(runner.start())
    """
    builder = ConversationBuilder()
    
    if agents is None:
        agents = ["optimist", "skeptic"]
    
    conversation = (builder
        .with_topic(topic)
        .with_mode("debate")
        .with_personas(*agents)
        .with_max_turns(max_turns)
        .with_voice_enabled(voice)
        .with_custom_instructions("Engage in thoughtful debate with respect for opposing views")
    )
    
    # Apply additional kwargs
    for key, value in kwargs.items():
        method_name = f"with_{key}"
        if hasattr(conversation, method_name):
            getattr(conversation, method_name)(value)
    
    config = conversation.build()
    return ConversationRunner(config, demo_mode=not voice)


def quick_roundtable(
    topic: str,
    agents: Optional[List[str]] = None,
    max_turns: int = 20,
    voice: bool = True,
    **kwargs
) -> ConversationRunner:
    """
    Quick setup for a roundtable discussion.
    
    Args:
        topic: The discussion topic
        agents: Optional list of persona names (defaults to 4 diverse personas)
        max_turns: Maximum conversation turns
        voice: Enable voice synthesis
        **kwargs: Additional configuration options
    
    Returns:
        ConversationRunner instance ready to start
    
    Example:
        runner = quick_roundtable("Future of renewable energy", max_turns=25)
        asyncio.run(runner.start())
    """
    builder = ConversationBuilder()
    
    if agents is None:
        agents = ["optimist", "skeptic", "pragmatist", "theorist"]
    
    conversation = (builder
        .with_topic(topic)
        .with_mode("roundtable")
        .with_personas(*agents)
        .with_max_turns(max_turns)
        .with_voice_enabled(voice)
        .with_custom_instructions("Participate in collaborative discussion, building on others' ideas")
    )
    
    # Apply additional kwargs
    for key, value in kwargs.items():
        method_name = f"with_{key}"
        if hasattr(conversation, method_name):
            getattr(conversation, method_name)(value)
    
    config = conversation.build()
    return ConversationRunner(config, demo_mode=not voice)


def quick_friendly(
    topic: str,
    agents: Optional[List[str]] = None,
    max_turns: int = 12,
    voice: bool = True,
    **kwargs
) -> ConversationRunner:
    """
    Quick setup for a friendly conversation.
    
    Args:
        topic: The conversation topic
        agents: Optional list of persona names (defaults to ["optimist", "enthusiast"])
        max_turns: Maximum conversation turns
        voice: Enable voice synthesis
        **kwargs: Additional configuration options
    
    Returns:
        ConversationRunner instance ready to start
    
    Example:
        runner = quick_friendly("Favorite books and why we love them")
        asyncio.run(runner.start())
    """
    builder = ConversationBuilder()
    
    if agents is None:
        agents = ["optimist", "enthusiast"]
    
    conversation = (builder
        .with_topic(topic)
        .with_mode("friendly")
        .with_personas(*agents)
        .with_max_turns(max_turns)
        .with_voice_enabled(voice)
        .with_custom_instructions("Have a warm, engaging conversation with curiosity and enthusiasm")
    )
    
    # Apply additional kwargs
    for key, value in kwargs.items():
        method_name = f"with_{key}"
        if hasattr(conversation, method_name):
            getattr(conversation, method_name)(value)
    
    config = conversation.build()
    return ConversationRunner(config, demo_mode=not voice)


def quick_interview(
    topic: str,
    interviewer: str = "educator",
    interviewee: str = "analyst",
    max_turns: int = 15,
    voice: bool = True,
    **kwargs
) -> ConversationRunner:
    """
    Quick setup for an interview conversation.
    
    Args:
        topic: The interview topic
        interviewer: Persona name for the interviewer
        interviewee: Persona name for the interviewee
        max_turns: Maximum conversation turns
        voice: Enable voice synthesis
        **kwargs: Additional configuration options
    
    Returns:
        ConversationRunner instance ready to start
    
    Example:
        runner = quick_interview("Climate change solutions", "educator", "scientist")
        asyncio.run(runner.start())
    """
    builder = ConversationBuilder()
    
    conversation = (builder
        .with_topic(topic)
        .with_mode("interview")
        .with_personas(interviewer, interviewee)
        .with_max_turns(max_turns)
        .with_voice_enabled(voice)
        .with_custom_instructions("Conduct a thoughtful interview with insightful questions and detailed answers")
    )
    
    # Apply additional kwargs
    for key, value in kwargs.items():
        method_name = f"with_{key}"
        if hasattr(conversation, method_name):
            getattr(conversation, method_name)(value)
    
    config = conversation.build()
    return ConversationRunner(config, demo_mode=not voice)


def quick_panel(
    topic: str,
    agents: Optional[List[str]] = None,
    max_turns: int = 25,
    voice: bool = True,
    **kwargs
) -> ConversationRunner:
    """
    Quick setup for a panel discussion.
    
    Args:
        topic: The panel topic
        agents: Optional list of persona names (defaults to expert panel)
        max_turns: Maximum conversation turns
        voice: Enable voice synthesis
        **kwargs: Additional configuration options
    
    Returns:
        ConversationRunner instance ready to start
    
    Example:
        runner = quick_panel("The future of artificial intelligence")
        asyncio.run(runner.start())
    """
    builder = ConversationBuilder()
    
    if agents is None:
        agents = ["educator", "analyst", "pragmatist", "theorist"]
    
    conversation = (builder
        .with_topic(topic)
        .with_mode("panel")
        .with_personas(*agents)
        .with_max_turns(max_turns)
        .with_voice_enabled(voice)
        .with_custom_instructions("Engage as expert panelists sharing professional insights")
    )
    
    # Apply additional kwargs
    for key, value in kwargs.items():
        method_name = f"with_{key}"
        if hasattr(conversation, method_name):
            getattr(conversation, method_name)(value)
    
    config = conversation.build()
    return ConversationRunner(config, demo_mode=not voice)


def quick_socratic(
    topic: str,
    teacher: str = "theorist",
    student: str = "skeptic",
    max_turns: int = 18,
    voice: bool = True,
    **kwargs
) -> ConversationRunner:
    """
    Quick setup for a Socratic dialogue.
    
    Args:
        topic: The exploration topic
        teacher: Persona name for the teacher/questioner
        student: Persona name for the student/explorer
        max_turns: Maximum conversation turns
        voice: Enable voice synthesis
        **kwargs: Additional configuration options
    
    Returns:
        ConversationRunner instance ready to start
    
    Example:
        runner = quick_socratic("What is consciousness?")
        asyncio.run(runner.start())
    """
    builder = ConversationBuilder()
    
    conversation = (builder
        .with_topic(topic)
        .with_mode("socratic")
        .with_personas(teacher, student)
        .with_max_turns(max_turns)
        .with_voice_enabled(voice)
        .with_custom_instructions("Explore ideas through questioning and discovery")
    )
    
    # Apply additional kwargs
    for key, value in kwargs.items():
        method_name = f"with_{key}"
        if hasattr(conversation, method_name):
            getattr(conversation, method_name)(value)
    
    config = conversation.build()
    return ConversationRunner(config, demo_mode=not voice)


def quick_start(
    topic: str,
    mode: str = "friendly",
    agents: Optional[List[str]] = None,
    voice: bool = True,
    **kwargs
) -> ConversationRunner:
    """
    Universal quick start function that can create any type of conversation.
    
    Args:
        topic: The conversation topic
        mode: The conversation mode
        agents: Optional list of persona names
        voice: Enable voice synthesis
        **kwargs: Additional configuration options
    
    Returns:
        ConversationRunner instance ready to start
    
    Example:
        runner = quick_start("Space exploration", mode="debate", max_turns=20)
        asyncio.run(runner.start())
    """
    # Use mode-specific quick functions if available
    mode_functions = {
        "debate": quick_debate,
        "roundtable": quick_roundtable,
        "friendly": quick_friendly,
        "interview": quick_interview,
        "panel": quick_panel,
        "socratic": quick_socratic
    }
    
    if mode in mode_functions:
        return mode_functions[mode](topic, agents=agents, voice=voice, **kwargs)
    
    # Generic setup for other modes
    builder = ConversationBuilder()
    
    conversation = (builder
        .with_topic(topic)
        .with_mode(mode)
        .with_voice_enabled(voice)
    )
    
    if agents:
        conversation = conversation.with_personas(*agents)
    else:
        conversation = conversation.with_agents(2)
    
    # Apply additional kwargs
    for key, value in kwargs.items():
        method_name = f"with_{key}"
        if hasattr(conversation, method_name):
            getattr(conversation, method_name)(value)
    
    config = conversation.build()
    return ConversationRunner(config, demo_mode=not voice)


# Async convenience functions for direct execution
async def run_quick_debate(topic: str, **kwargs) -> None:
    """Run a quick debate conversation and return when complete."""
    runner = quick_debate(topic, **kwargs)
    await runner.start()


async def run_quick_roundtable(topic: str, **kwargs) -> None:
    """Run a quick roundtable discussion and return when complete."""
    runner = quick_roundtable(topic, **kwargs)
    await runner.start()


async def run_quick_friendly(topic: str, **kwargs) -> None:
    """Run a quick friendly conversation and return when complete."""
    runner = quick_friendly(topic, **kwargs)
    await runner.start()


async def run_quick_interview(topic: str, **kwargs) -> None:
    """Run a quick interview and return when complete."""
    runner = quick_interview(topic, **kwargs)
    await runner.start()


async def run_quick_panel(topic: str, **kwargs) -> None:
    """Run a quick panel discussion and return when complete."""
    runner = quick_panel(topic, **kwargs)
    await runner.start()


async def run_quick_socratic(topic: str, **kwargs) -> None:
    """Run a quick Socratic dialogue and return when complete."""
    runner = quick_socratic(topic, **kwargs)
    await runner.start()


def sync_run(conversation_runner: ConversationRunner) -> None:
    """
    Synchronously run a conversation runner.
    Handles event loop creation and cleanup.
    """
    try:
        # Try to run in existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're in an async context, can't use run()
            import warnings
            warnings.warn("Already in async context. Use 'await conversation_runner.start()' instead.")
            return
    except RuntimeError:
        # No event loop exists
        pass
    
    # Create new event loop and run
    asyncio.run(conversation_runner.start())


# Export convenience functions
__all__ = [
    'quick_debate', 'quick_roundtable', 'quick_friendly', 
    'quick_interview', 'quick_panel', 'quick_socratic', 'quick_start',
    'run_quick_debate', 'run_quick_roundtable', 'run_quick_friendly',
    'run_quick_interview', 'run_quick_panel', 'run_quick_socratic',
    'sync_run'
]
