"""
DuoTalk: Advanced Multi-Agent Voice Conversation System

A sophisticated Python package for creating dynamic conversations between AI agents
with voice synthesis, multiple conversation modes, and comprehensive monitoring.

Quick Start:
    from duotalk import quick_debate, quick_roundtable
    import asyncio
    
    # Start a voice debate
    runner = quick_debate("Should AI replace human creativity?")
    asyncio.run(runner.start())
    
    # Or use the builder pattern
    from duotalk import conversation
    
    runner = (conversation()
        .with_topic("Future of renewable energy")
        .with_mode("roundtable")
        .with_agents(4)
        .with_voice_enabled(True)
        .build_and_start())
"""

from .core.config import ConversationConfig, AgentConfig
from .core.runner import ConversationRunner
from .core.demo import run_demo_conversation

# Enhanced features
try:
    from .core.builder import ConversationBuilder, conversation
    from .config.enhanced_config import DuoTalkConfig
    from .quick import (
        quick_debate, quick_roundtable, quick_friendly, quick_interview,
        quick_panel, quick_socratic, quick_start, sync_run
    )
    from .stats import (
        ConversationStats, PerformanceMonitor, StatisticsStore,
        get_monitor, get_store
    )
    _enhanced_features = True
except ImportError:
    _enhanced_features = False

# Core personas and modes
from .personas import (
    OPTIMIST, PESSIMIST, PRAGMATIST, THEORIST, SKEPTIC, ENTHUSIAST,
    MEDIATOR, ANALYST, CREATIVE, LOGICAL, ALL_PERSONA_NAMES,
    get_persona_by_name, get_random_personas
)
from .modes import (
    FriendlyMode, DebateMode, RoundtableMode, InterviewMode,
    PanelMode, SocraticMode, ALL_MODES, get_mode
)

# Convenience functions for backward compatibility
from .core.convenience import (
    create_debate, create_roundtable, create_friendly_chat,
    create_interview, create_panel, create_socratic,
    create_random_conversation, create_business_discussion,
    create_academic_debate, create_creative_brainstorm,
    create_policy_discussion, create_youtube_summary,
    create_youtube_summary_async
)

# YouTube functionality (when dependencies available)
try:
    from .core.youtube_summarizer import (
        YouTubeSummarizer, validate_youtube_url, extract_video_id,
        summarize_youtube_video
    )
    _youtube_available = True
except ImportError:
    _youtube_available = False

# Voice functionality (when available)
try:
    from .core.voice_runner import VoiceConversationRunner, run_voice_conversation
    _voice_available = True
except ImportError:
    _voice_available = False

__version__ = "2.0.0"
__author__ = "DuoTalk Team"
__description__ = "Advanced Multi-Agent Voice Conversation System"

# Build __all__ dynamically based on available features
__all__ = [
    # Core classes
    'ConversationConfig', 'AgentConfig', 'ConversationRunner',
    
    # Core personas
    'OPTIMIST', 'PESSIMIST', 'PRAGMATIST', 'THEORIST', 'SKEPTIC', 'ENTHUSIAST',
    'MEDIATOR', 'ANALYST', 'CREATIVE', 'LOGICAL', 'ALL_PERSONA_NAMES',
    'get_persona_by_name', 'get_random_personas',
    
    # Modes
    'FriendlyMode', 'DebateMode', 'RoundtableMode', 'InterviewMode',
    'PanelMode', 'SocraticMode', 'ALL_MODES', 'get_mode',
    
    # Legacy convenience functions
    'create_debate', 'create_roundtable', 'create_friendly_chat',
    'create_interview', 'create_panel', 'create_socratic',
    'create_random_conversation', 'create_business_discussion',
    'create_academic_debate', 'create_creative_brainstorm',
    'create_policy_discussion', 'create_youtube_summary',
    'create_youtube_summary_async',
    'run_demo_conversation',
    
    # Metadata
    '__version__', '__author__', '__description__'
]

# Add enhanced features if available
if _enhanced_features:
    __all__.extend([
        'ConversationBuilder', 'conversation', 'DuoTalkConfig',
        'quick_debate', 'quick_roundtable', 'quick_friendly', 'quick_interview',
        'quick_panel', 'quick_socratic', 'quick_start', 'sync_run',
        'ConversationStats', 'PerformanceMonitor', 'StatisticsStore',
        'get_monitor', 'get_store'
    ])

# Add voice features if available
if _voice_available:
    __all__.extend([
        'VoiceConversationRunner', 'run_voice_conversation'
    ])

# Add YouTube features if available
if _youtube_available:
    __all__.extend([
        'YouTubeSummarizer', 'validate_youtube_url', 'extract_video_id',
        'summarize_youtube_video'
    ])
