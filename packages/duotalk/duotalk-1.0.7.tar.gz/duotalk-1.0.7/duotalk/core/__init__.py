"""
Core package exports.
"""

from .config import ConversationConfig, AgentConfig, VoiceType, ConversationModeType
from .runner import ConversationRunner, ConversationManager, conversation_manager
from .session import ConversationSession, SessionState, ConversationMetrics
from .demo import DemoConversationRunner, run_demo_conversation
from .convenience import (
    create_debate,
    create_roundtable,
    create_friendly_chat,
    create_interview,
    create_panel,
    create_socratic,
    create_random_conversation,
    create_business_discussion,
    create_academic_debate,
    create_creative_brainstorm,
    create_policy_discussion,
    get_random_personas,
)

__all__ = [
    # Configuration
    "ConversationConfig",
    "AgentConfig", 
    "VoiceType",
    "ConversationModeType",
    
    # Core functionality
    "ConversationRunner",
    "ConversationManager", 
    "conversation_manager",
    "ConversationSession",
    "SessionState",
    "ConversationMetrics",
    
    # Demo functionality
    "DemoConversationRunner",
    "run_demo_conversation",
    
    # Convenience functions
    "create_debate",
    "create_roundtable",
    "create_friendly_chat",
    "create_interview",
    "create_panel",
    "create_socratic",
    "create_random_conversation",
    "create_business_discussion",
    "create_academic_debate",
    "create_creative_brainstorm",
    "create_policy_discussion",
    "get_random_personas",
]
