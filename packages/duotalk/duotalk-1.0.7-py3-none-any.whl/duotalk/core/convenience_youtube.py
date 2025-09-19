"""
Convenience functions for YouTube summarization in DuoTalk.
"""

import asyncio
from typing import Dict, Any, Optional
from .youtube_summarizer import YouTubeSummarizer, validate_youtube_url


async def create_youtube_summary(
    youtube_url: str,
    max_length: int = 8000,
    voice_enabled: bool = True,
    summary_mode: str = "detailed"
) -> Dict[str, Any]:
    """
    Create a YouTube video summary.
    
    Args:
        youtube_url: YouTube video URL
        max_length: Maximum transcript length to process
        voice_enabled: Whether voice synthesis is enabled
        summary_mode: Summary length mode - "short" or "detailed"
        
    Returns:
        Dictionary with summary results
    """
    if not validate_youtube_url(youtube_url):
        return {
            "success": False,
            "error": "Invalid YouTube URL provided",
            "summary": None
        }
    
    summarizer = YouTubeSummarizer()
    return await summarizer.summarize_video(
        youtube_url, 
        use_voice=voice_enabled,
        summary_mode=summary_mode
    )


def quick_youtube_summary(youtube_url: str, voice: bool = True, summary_mode: str = "detailed") -> Dict[str, Any]:
    """
    Quick synchronous wrapper for YouTube summarization.
    
    Args:
        youtube_url: YouTube video URL
        voice: Enable voice synthesis
        summary_mode: Summary length mode - "short" or "detailed"
        
    Returns:
        Summary results
    """
    try:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're in a running loop, we need to handle this differently
            import concurrent.futures
            
            def run_in_thread():
                return asyncio.run(create_youtube_summary(youtube_url, voice_enabled=voice, summary_mode=summary_mode))
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            return asyncio.run(create_youtube_summary(youtube_url, voice_enabled=voice, summary_mode=summary_mode))
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to summarize video: {str(e)}",
            "summary": None
        }


# Sync wrapper for easier CLI integration
def sync_youtube_summary(youtube_url: str, voice: bool = True, summary_mode: str = "detailed") -> Dict[str, Any]:
    """Synchronous YouTube summary function."""
    return quick_youtube_summary(youtube_url, voice, summary_mode)


__all__ = [
    "create_youtube_summary",
    "quick_youtube_summary", 
    "sync_youtube_summary",
]