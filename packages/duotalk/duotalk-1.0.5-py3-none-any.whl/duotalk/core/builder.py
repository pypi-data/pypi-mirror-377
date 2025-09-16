"""
ConversationBuilder - Fluent API for creating conversations.
Provides an easy-to-use builder pattern for creating complex conversation configurations.
"""

from typing import List, Optional, Union, Dict, Any, Callable
import random

from ..config.enhanced_config import DuoTalkConfig
from ..core.config import ConversationConfig, AgentConfig
from ..personas import ALL_PERSONAS, get_persona_by_name, get_random_personas
from ..modes import get_mode, ALL_MODES


class ConversationBuilder:
    """
    Fluent API builder for creating conversations.
    
    Example:
        conversation = (ConversationBuilder()
            .with_topic("AI Ethics")
            .with_mode("debate")
            .with_agents(2)
            .with_max_turns(15)
            .with_custom_instructions("Be respectful")
            .build())
    """
    
    def __init__(self, config: Optional[DuoTalkConfig] = None):
        """Initialize the builder with optional configuration."""
        self.config = config or DuoTalkConfig()
        
        # Conversation parameters
        self._topic: Optional[str] = None
        self._mode: str = "friendly"
        self._agents: List[Union[str, AgentConfig]] = []
        self._max_turns: int = self.config.max_turns
        self._custom_instructions: Optional[str] = None
        self._turn_timeout: float = self.config.turn_timeout
        self._interruptions: bool = self.config.interruption_enabled
        self._conversation_delay: float = self.config.conversation_delay
        
        # Advanced options
        self._voice_enabled: bool = True
        self._demo_mode: bool = False
        self._fast_mode: bool = False
        self._callbacks: Dict[str, Callable] = {}
        self._metadata: Dict[str, Any] = {}
    
    def with_topic(self, topic: str) -> 'ConversationBuilder':
        """Set the conversation topic."""
        self._topic = topic
        return self
    
    def with_mode(self, mode: str) -> 'ConversationBuilder':
        """Set the conversation mode."""
        if mode not in ALL_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Available: {ALL_MODES}")
        self._mode = mode
        return self
    
    def with_agents(self, count_or_personas: Union[int, List[str], List[AgentConfig]]) -> 'ConversationBuilder':
        """
        Set the agents for the conversation.
        
        Args:
            count_or_personas: Either a number of agents (will auto-select), 
                             or a list of persona names, or a list of AgentConfig objects
        """
        if isinstance(count_or_personas, int):
            # Auto-select agents based on mode and count
            self._agents = self._auto_select_agents(count_or_personas)
        elif isinstance(count_or_personas, list):
            if all(isinstance(x, str) for x in count_or_personas):
                # List of persona names
                self._agents = [get_persona_by_name(name) for name in count_or_personas]
            elif all(isinstance(x, AgentConfig) for x in count_or_personas):
                # List of AgentConfig objects
                self._agents = count_or_personas
            else:
                raise ValueError("Agents list must contain either all strings or all AgentConfig objects")
        else:
            raise ValueError("Agents must be int, list of strings, or list of AgentConfig")
        
        return self
    
    def with_personas(self, *persona_names: str) -> 'ConversationBuilder':
        """Set agents using persona names."""
        self._agents = [get_persona_by_name(name) for name in persona_names]
        return self
    
    def with_random_agents(self, count: int, collection: str = "all") -> 'ConversationBuilder':
        """Set random agents from a collection."""
        self._agents = get_random_personas(count, collection)
        return self
    
    def with_max_turns(self, max_turns: int) -> 'ConversationBuilder':
        """Set the maximum number of conversation turns."""
        self._max_turns = max_turns
        return self
    
    def with_custom_instructions(self, instructions: str) -> 'ConversationBuilder':
        """Add custom instructions for all agents."""
        self._custom_instructions = instructions
        return self
    
    def with_turn_timeout(self, timeout: float) -> 'ConversationBuilder':
        """Set the timeout for each conversation turn."""
        self._turn_timeout = timeout
        return self
    
    def with_interruptions(self, enabled: bool) -> 'ConversationBuilder':
        """Enable or disable interruptions during conversation."""
        self._interruptions = enabled
        return self
    
    def with_conversation_delay(self, delay: float) -> 'ConversationBuilder':
        """Set delay between conversation turns."""
        self._conversation_delay = delay
        return self
    
    def with_voice_enabled(self, enabled: bool) -> 'ConversationBuilder':
        """Enable or disable voice synthesis."""
        self._voice_enabled = enabled
        return self
    
    def with_demo_mode(self, enabled: bool = True) -> 'ConversationBuilder':
        """Enable demo mode (text-based simulation)."""
        self._demo_mode = enabled
        return self
    
    def with_fast_mode(self, enabled: bool = True) -> 'ConversationBuilder':
        """Enable fast mode (no typing animations, shorter delays)."""
        self._fast_mode = enabled
        return self
    
    def with_callback(self, event: str, callback: Callable) -> 'ConversationBuilder':
        """Add an event callback."""
        self._callbacks[event] = callback
        return self
    
    def with_metadata(self, **metadata) -> 'ConversationBuilder':
        """Add metadata to the conversation."""
        self._metadata.update(metadata)
        return self
    
    def _auto_select_agents(self, count: int) -> List[AgentConfig]:
        """Auto-select appropriate agents based on mode and count."""
        mode_agent_preferences = {
            "debate": ["optimist", "skeptic"],
            "friendly": ["optimist", "enthusiast"],
            "roundtable": ["optimist", "skeptic", "pragmatist", "theorist"],
            "interview": ["educator", "analyst"],
            "panel": ["educator", "analyst", "pragmatist", "theorist"],
            "socratic": ["theorist", "skeptic"]
        }
        
        preferred_personas = mode_agent_preferences.get(self._mode, ["optimist", "skeptic"])
        
        # Extend or truncate to match requested count
        if count <= len(preferred_personas):
            selected_personas = preferred_personas[:count]
        else:
            # Add random personas to reach desired count
            available_personas = [p.persona for p in ALL_PERSONAS if p.persona not in preferred_personas]
            additional_count = count - len(preferred_personas)
            additional_personas = random.sample(available_personas, min(additional_count, len(available_personas)))
            selected_personas = preferred_personas + additional_personas
        
        return [get_persona_by_name(name) for name in selected_personas]
    
    def build(self) -> ConversationConfig:
        """Build the conversation configuration."""
        if not self._topic:
            raise ValueError("Topic is required. Use with_topic() to set it.")
        
        if not self._agents:
            # Default to 2 agents if none specified
            self._agents = self._auto_select_agents(2)
        
        # Apply custom instructions if provided
        if self._custom_instructions:
            for agent in self._agents:
                if agent.instructions:
                    agent.instructions += f"\n\nAdditional instructions: {self._custom_instructions}"
                else:
                    agent.instructions = self._custom_instructions
        
        # Get mode object
        mode_obj = get_mode(self._mode)
        
        # Create conversation config
        conversation_config = ConversationConfig(
            topic=self._topic,
            agents=self._agents,
            mode=self._mode,
            max_turns=self._max_turns,
            turn_timeout=self._turn_timeout,
            allow_interruptions=self._interruptions,
            audio_enabled=self._voice_enabled,
            session_metadata=self._metadata
        )
        
        return conversation_config
    
    def build_and_start(self, voice_mode: bool = True) -> 'ConversationRunner':
        """Build the configuration and start the conversation."""
        from ..core.runner import ConversationRunner
        
        config = self.build()
        runner = ConversationRunner(config, demo_mode=not voice_mode or self._demo_mode)
        
        # Add callbacks
        for event, callback in self._callbacks.items():
            runner.add_event_callback(event, callback)
        
        return runner
    
    def preview(self) -> Dict[str, Any]:
        """Preview the conversation configuration without building."""
        return {
            "topic": self._topic,
            "mode": self._mode,
            "agents": [agent.name if isinstance(agent, AgentConfig) else agent for agent in self._agents],
            "max_turns": self._max_turns,
            "voice_enabled": self._voice_enabled,
            "demo_mode": self._demo_mode,
            "fast_mode": self._fast_mode,
            "metadata": self._metadata
        }
    
    def clone(self) -> 'ConversationBuilder':
        """Create a copy of this builder."""
        new_builder = ConversationBuilder(self.config)
        new_builder._topic = self._topic
        new_builder._mode = self._mode
        new_builder._agents = self._agents.copy()
        new_builder._max_turns = self._max_turns
        new_builder._custom_instructions = self._custom_instructions
        new_builder._turn_timeout = self._turn_timeout
        new_builder._interruptions = self._interruptions
        new_builder._conversation_delay = self._conversation_delay
        new_builder._voice_enabled = self._voice_enabled
        new_builder._demo_mode = self._demo_mode
        new_builder._fast_mode = self._fast_mode
        new_builder._callbacks = self._callbacks.copy()
        new_builder._metadata = self._metadata.copy()
        return new_builder


# Convenience function for quick access
def conversation() -> ConversationBuilder:
    """Create a new ConversationBuilder instance."""
    return ConversationBuilder()
