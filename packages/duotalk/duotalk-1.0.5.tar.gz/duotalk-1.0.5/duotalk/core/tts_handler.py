"""
Text-to-Speech handler for DuoTalk with multiple TTS engine support.
"""

import asyncio
import os
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Optional dependencies - graceful fallback if not available
try:
    import edge_tts
    import pygame
    _edge_tts_available = True
except ImportError:
    _edge_tts_available = False

try:
    from livekit.plugins import deepgram, google, cartesia
    from livekit.agents import AgentSession
    _livekit_available = True
except ImportError:
    _livekit_available = False


class TTSHandler:
    """Handle Text-to-Speech operations with multiple engine support."""
    
    def __init__(self, engine: str = "edge", voice: Optional[str] = None):
        """
        Initialize TTS handler.
        
        Args:
            engine: TTS engine to use ("edge", "deepgram", "google", "cartesia")
            voice: Voice to use (engine-specific)
        """
        self.engine = engine.lower()
        self.voice = voice
        
        # Default voices for each engine
        self.default_voices = {
            "edge": "en-US-AriaNeural",
            "deepgram": "aura-asteria-en",
            "google": "Zephyr", 
            "cartesia": "f786b574-daa5-4673-aa0c-cbe3e8534c02"
        }
        
        if not self.voice:
            self.voice = self.default_voices.get(self.engine, self.default_voices["edge"])
    
    async def speak_text(self, text: str) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.engine == "edge":
                return await self._speak_edge_tts(text)
            elif self.engine == "deepgram" and _livekit_available:
                return await self._speak_deepgram(text)
            elif self.engine == "google" and _livekit_available:
                return await self._speak_google(text)
            elif self.engine == "cartesia" and _livekit_available:
                return await self._speak_cartesia(text)
            else:
                logger.warning(f"TTS engine '{self.engine}' not available, falling back to edge-tts")
                return await self._speak_edge_tts(text)
                
        except Exception as e:
            logger.error(f"Error in TTS: {e}")
            return False
    
    async def _speak_edge_tts(self, text: str) -> bool:
        """Use edge-tts for speech synthesis."""
        if not _edge_tts_available:
            logger.error("edge-tts not available. Install with: pip install edge-tts pygame")
            return False
        
        try:
            # Map other engine voices to edge-tts compatible voices
            edge_voice = self.voice
            if self.voice == "Zephyr":  # Google Gemini voice
                edge_voice = "en-US-AriaNeural"
            elif self.voice == "aura-asteria-en":  # Deepgram voice
                edge_voice = "en-US-JennyNeural"
            elif len(self.voice) > 20:  # Cartesia voice ID
                edge_voice = "en-US-AriaNeural"
            
            logger.info(f"Using edge-tts voice: {edge_voice}")
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_path = tmp_file.name
            
            logger.info(f"Generating speech for {len(text)} characters...")
            
            # Generate speech
            communicate = edge_tts.Communicate(text, edge_voice)
            await communicate.save(tmp_path)
            
            logger.info(f"Audio saved to {tmp_path}")
            
            # Initialize pygame mixer with error handling
            try:
                if pygame.mixer.get_init() is None:
                    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                    logger.info("Pygame mixer initialized")
                
                # Play audio using pygame
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                
                logger.info("Audio playback started...")
                
                # Wait for playback to complete with timeout
                max_wait_time = min(len(text) * 0.05 + 10, 60)  # Estimate + buffer, max 60 seconds
                wait_time = 0
                while pygame.mixer.music.get_busy() and wait_time < max_wait_time:
                    await asyncio.sleep(0.5)
                    wait_time += 0.5
                
                logger.info("Audio playback completed")
                
            except Exception as e:
                logger.error(f"Error during audio playback: {e}")
                # Try alternative playback method on Windows
                if os.name == 'nt':  # Windows
                    try:
                        import subprocess
                        subprocess.run(["start", "", tmp_path], shell=True, check=False)
                        await asyncio.sleep(min(len(text) * 0.05, 30))  # Wait estimated duration
                        logger.info("Used Windows alternative playback")
                    except Exception as e2:
                        logger.error(f"Alternative playback also failed: {e2}")
                        return False
                else:
                    return False
            
            # Cleanup
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                await asyncio.sleep(0.5)  # Give time for cleanup
                os.unlink(tmp_path)
                logger.info("Cleanup completed")
            except Exception as e:
                logger.warning(f"Cleanup warning (non-critical): {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error with edge-tts: {e}")
            return False
    
    async def _speak_deepgram(self, text: str) -> bool:
        """Use Deepgram TTS for speech synthesis."""
        try:
            # Create a simple session for TTS only
            session = AgentSession(
                tts=deepgram.TTS(model=self.voice)
            )
            
            # This would need a proper LiveKit room setup
            # For now, return False to fall back to edge-tts
            logger.info("Deepgram TTS requires LiveKit room setup, falling back to edge-tts")
            return await self._speak_edge_tts(text)
            
        except Exception as e:
            logger.error(f"Error with Deepgram TTS: {e}")
            return await self._speak_edge_tts(text)
    
    async def _speak_google(self, text: str) -> bool:
        """Use Google Gemini TTS for speech synthesis."""
        try:
            if not _livekit_available:
                logger.info("Google Gemini TTS not available, falling back to edge-tts")
                return await self._speak_edge_tts(text)
            
            # For now, use a simple approach with the direct API call
            # This is a simplified version - in a full implementation you'd use the LiveKit session
            logger.info("Google Gemini TTS: Using simplified approach")
            
            # Create the TTS instance
            from livekit.plugins.google.beta import GeminiTTS
            
            # Create a simple TTS call (this is a simplified approach)
            # In practice, this would be integrated with a LiveKit session
            tts = GeminiTTS(
                model="gemini-2.5-flash-preview-tts",
                voice_name=self.voice,
                instructions="Speak in a friendly and engaging tone.",
            )
            
            # For now, fall back to edge-tts for actual audio generation
            # This ensures audio actually plays while we work on full Gemini integration
            logger.info("Google Gemini TTS setup successful, using edge-tts for audio playback")
            return await self._speak_edge_tts(text)
            
        except Exception as e:
            logger.error(f"Error with Google Gemini TTS: {e}")
            logger.info("Falling back to edge-tts")
            return await self._speak_edge_tts(text)
    
    async def _speak_cartesia(self, text: str) -> bool:
        """Use Cartesia TTS for speech synthesis."""
        try:
            # Create a simple session for TTS only
            session = AgentSession(
                tts=cartesia.TTS(
                    model="sonic-2",
                    voice=self.voice,
                )
            )
            
            # This would need a proper LiveKit room setup
            # For now, return False to fall back to edge-tts
            logger.info("Cartesia TTS requires LiveKit room setup, falling back to edge-tts")
            return await self._speak_edge_tts(text)
            
        except Exception as e:
            logger.error(f"Error with Cartesia TTS: {e}")
            return await self._speak_edge_tts(text)


# Convenience functions
async def speak_text(text: str, engine: str = "edge", voice: Optional[str] = None) -> bool:
    """
    Quick function to speak text using specified TTS engine.
    
    Args:
        text: Text to speak
        engine: TTS engine ("edge", "deepgram", "google", "cartesia")
        voice: Voice to use (engine-specific)
        
    Returns:
        True if successful, False otherwise
    """
    handler = TTSHandler(engine=engine, voice=voice)
    return await handler.speak_text(text)


def speak_text_sync(text: str, engine: str = "edge", voice: Optional[str] = None) -> bool:
    """
    Synchronous wrapper for speak_text.
    
    Args:
        text: Text to speak
        engine: TTS engine to use
        voice: Voice to use
        
    Returns:
        True if successful, False otherwise
    """
    try:
        return asyncio.run(speak_text(text, engine, voice))
    except Exception as e:
        logger.error(f"Error in synchronous TTS: {e}")
        return False


def get_available_engines() -> Dict[str, bool]:
    """Get status of available TTS engines."""
    return {
        "edge": _edge_tts_available,
        "google": _livekit_available,
        "deepgram": _livekit_available,
        "cartesia": _livekit_available,
    }


def get_engine_voices(engine: str) -> Dict[str, Any]:
    """Get available voices for a TTS engine."""
    handler = TTSHandler(engine=engine)
    return {
        "default": handler.voice,
        "engine": engine,
        "available": get_available_engines()[engine.lower()]
    }