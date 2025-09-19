"""
Enhanced configuration management for DuoTalk.
Supports environment variables, YAML/JSON config files, and programmatic configuration.
"""

import os
import yaml
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union
from pathlib import Path


@dataclass
class DuoTalkConfig:
    """Main configuration class for DuoTalk with enterprise-grade options."""
    
    # API Configuration
    google_api_key: Optional[str] = None
    livekit_url: Optional[str] = None
    livekit_api_key: Optional[str] = None
    livekit_api_secret: Optional[str] = None
    
    # Model Configuration
    model_name: str = "gemini-2.5-flash-preview-native-audio-dialog"
    
    # Conversation Settings
    max_turns: int = 15
    turn_timeout: float = 20.0
    interruption_enabled: bool = True
    min_interruption_duration: float = 0.5
    conversation_delay: float = 2.0
    response_length_limit: str = "short"  # short, medium, long
    
    # Audio Settings
    audio_enabled: bool = True
    sample_rate: int = 48000
    channels: int = 1
    
    # Reliability Settings
    max_retries: int = 3
    retry_delay: float = 1.0
    health_check_interval: float = 5.0
    
    # Logging Configuration
    log_level: str = "INFO"
    log_conversation: bool = True
    save_audio: bool = False
    output_dir: Optional[str] = None
    
    # Performance Settings
    concurrent_sessions: int = 1
    memory_limit_mb: int = 1024
    
    # Custom Settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Load configuration from environment variables and config files."""
        self._load_from_env()
        self._load_from_config_file()
        self._validate_config()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'GOOGLE_API_KEY': 'google_api_key',
            'GEMINI_API_KEY': 'google_api_key',  # Alternative name
            'LIVEKIT_URL': 'livekit_url',
            'LIVEKIT_API_KEY': 'livekit_api_key',
            'LIVEKIT_API_SECRET': 'livekit_api_secret',
            'DUOTALK_MAX_TURNS': 'max_turns',
            'DUOTALK_TURN_TIMEOUT': 'turn_timeout',
            'DUOTALK_INTERRUPTIONS': 'interruption_enabled',
            'DUOTALK_LOG_LEVEL': 'log_level',
            'DUOTALK_OUTPUT_DIR': 'output_dir',
        }
        
        for env_var, config_attr in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if config_attr in ['max_turns', 'sample_rate', 'channels', 'max_retries', 'concurrent_sessions', 'memory_limit_mb']:
                    value = int(value)
                elif config_attr in ['turn_timeout', 'min_interruption_duration', 'conversation_delay', 'retry_delay', 'health_check_interval']:
                    value = float(value)
                elif config_attr in ['interruption_enabled', 'audio_enabled', 'log_conversation', 'save_audio']:
                    value = value.lower() in ('true', '1', 'yes', 'on')
                
                setattr(self, config_attr, value)
    
    def _load_from_config_file(self):
        """Load configuration from YAML or JSON config file."""
        config_files = [
            'duotalk_config.yaml',
            'duotalk_config.yml', 
            'duotalk_config.json',
            '.duotalk.yaml',
            '.duotalk.yml',
            '.duotalk.json'
        ]
        
        for config_file in config_files:
            if Path(config_file).exists():
                try:
                    with open(config_file, 'r') as f:
                        if config_file.endswith('.json'):
                            config_data = json.load(f)
                        else:
                            config_data = yaml.safe_load(f)
                    
                    # Update configuration with file data
                    for key, value in config_data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
                        else:
                            self.custom_settings[key] = value
                    
                    break
                except Exception as e:
                    print(f"Warning: Could not load config file {config_file}: {e}")
    
    def _validate_config(self):
        """Validate configuration values."""
        if self.max_turns <= 0:
            raise ValueError("max_turns must be positive")
        
        if self.turn_timeout <= 0:
            raise ValueError("turn_timeout must be positive")
        
        if self.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError(f"Invalid log_level: {self.log_level}")
        
        if self.response_length_limit not in ['short', 'medium', 'long']:
            raise ValueError(f"Invalid response_length_limit: {self.response_length_limit}")
    
    def save_to_file(self, filepath: str):
        """Save current configuration to a file."""
        config_dict = self.to_dict()
        
        if filepath.endswith('.json'):
            with open(filepath, 'w') as f:
                json.dump(config_dict, f, indent=2)
        else:
            with open(filepath, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config_dict = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                config_dict[key] = value
        return config_dict
    
    @classmethod
    def from_file(cls, filepath: str) -> 'DuoTalkConfig':
        """Load configuration from a file."""
        with open(filepath, 'r') as f:
            if filepath.endswith('.json'):
                config_data = json.load(f)
            else:
                config_data = yaml.safe_load(f)
        
        return cls(**config_data)
    
    @classmethod
    def get_default(cls) -> 'DuoTalkConfig':
        """Get default configuration."""
        return cls()
    
    def merge_with(self, other_config: 'DuoTalkConfig') -> 'DuoTalkConfig':
        """Merge this config with another, with other taking precedence."""
        merged_dict = self.to_dict()
        merged_dict.update(other_config.to_dict())
        return DuoTalkConfig(**merged_dict)
    
    def get_response_length_tokens(self) -> int:
        """Get token limit based on response length setting."""
        length_mapping = {
            'short': 50,
            'medium': 150,
            'long': 300
        }
        return length_mapping.get(self.response_length_limit, 50)


# Global default configuration instance
default_config = DuoTalkConfig()


def get_config() -> DuoTalkConfig:
    """Get the current global configuration."""
    return default_config


def set_config(config: DuoTalkConfig):
    """Set the global configuration."""
    global default_config
    default_config = config


def load_config_from_file(filepath: str):
    """Load global configuration from file."""
    global default_config
    default_config = DuoTalkConfig.from_file(filepath)


def create_sample_config(filepath: str = "duotalk_config.yaml"):
    """Create a sample configuration file."""
    sample_config = DuoTalkConfig()
    sample_config.save_to_file(filepath)
    print(f"Sample configuration saved to {filepath}")
