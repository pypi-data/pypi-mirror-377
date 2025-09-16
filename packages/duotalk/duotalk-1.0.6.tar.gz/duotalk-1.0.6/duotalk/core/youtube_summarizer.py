"""
YouTube video summarization module for DuoTalk.
Extracts transcripts from YouTube videos and provides conversational summaries.
"""

import asyncio
import os
import re
import requests
from typing import Optional, Dict, Any
import logging
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Optional dependencies - graceful fallback if not available
try:
    import yt_dlp
    _ytdlp_available = True
except ImportError:
    _ytdlp_available = False

from livekit.agents import Agent, AgentSession, JobContext, function_tool
from livekit.plugins import google

logger = logging.getLogger(__name__)


class YouTubeTranscriptExtractor:
    """Handles YouTube transcript extraction."""
    
    @staticmethod
    def extract_transcript(youtube_url: str) -> str:
        """Extract transcript from YouTube video using yt-dlp"""
        
        if not _ytdlp_available:
            raise ImportError("yt-dlp is required for YouTube transcript extraction. Install with: pip install yt-dlp")
        
        # First try: Direct subtitle extraction through yt-dlp
        try:
            return YouTubeTranscriptExtractor._extract_direct_subtitles(youtube_url)
        except Exception as e:
            logger.warning(f"Direct subtitle extraction failed: {e}, trying fallback method...")
            
        # Fallback: Manual URL extraction and download
        try:
            return YouTubeTranscriptExtractor._extract_via_manual_download(youtube_url)
        except Exception as e:
            logger.error(f"All transcript extraction methods failed: {e}")
            raise Exception(f"Failed to extract transcript: {str(e)}")
    
    @staticmethod
    def _extract_direct_subtitles(youtube_url: str) -> str:
        """Try to extract subtitles directly using yt-dlp's subtitle extraction."""
        import tempfile
        import os
        
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'outtmpl': '%(title)s.%(ext)s',
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts['outtmpl'] = os.path.join(temp_dir, '%(title)s.%(ext)s')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
                # Check if we can get subtitles info
                if 'subtitles' not in info and 'automatic_captions' not in info:
                    raise Exception("No subtitles available for this video")
                
                # Try to download subtitles to temp directory
                try:
                    ydl.download([youtube_url])
                    
                    # Look for subtitle files in temp directory
                    for file in os.listdir(temp_dir):
                        if file.endswith(('.vtt', '.srt')):
                            with open(os.path.join(temp_dir, file), 'r', encoding='utf-8') as f:
                                content = f.read()
                                return YouTubeTranscriptExtractor._clean_transcript(content)
                    
                    raise Exception("No subtitle files were downloaded")
                    
                except Exception as e:
                    logger.warning(f"yt-dlp direct download failed: {e}")
                    raise
    
    @staticmethod
    def _extract_via_manual_download(youtube_url: str) -> str:
        """Fallback method: Extract subtitle URLs and download manually."""
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            
            # Try to get manual subtitles first, then automatic
            subtitles = info.get('subtitles', {})
            auto_subtitles = info.get('automatic_captions', {})
            
            transcript_text = ""
            subtitle_url = None
            
            # Check for English subtitles
            if 'en' in subtitles and subtitles['en']:
                subtitle_url = subtitles['en'][0]['url']
            elif 'en' in auto_subtitles and auto_subtitles['en']:
                # Find the best format (prefer vtt)
                for sub in auto_subtitles['en']:
                    if sub.get('ext') == 'vtt':
                        subtitle_url = sub['url']
                        break
                if not subtitle_url and auto_subtitles['en']:
                    subtitle_url = auto_subtitles['en'][0]['url']
            
            # Download and parse the subtitle file
            if subtitle_url:
                max_retries = 5
                base_delay = 5
                
                for download_attempt in range(max_retries):
                    try:
                        # Add random jitter to avoid thundering herd
                        import random
                        jitter = random.uniform(0.5, 1.5)
                        
                        # Use session with headers to appear more like a regular browser
                        session = requests.Session()
                        session.headers.update({
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'Accept': 'text/vtt,text/plain,*/*',
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Connection': 'keep-alive',
                        })
                        
                        response = session.get(subtitle_url, timeout=45)
                        
                        if response.status_code == 429:  # Rate limited
                            if download_attempt < max_retries - 1:
                                # Progressive backoff: 5s, 15s, 30s, 60s
                                wait_time = base_delay * (2 ** download_attempt) * jitter
                                logger.warning(f"Rate limited (429), waiting {wait_time:.1f}s before retry {download_attempt + 1}/{max_retries}")
                                import time
                                time.sleep(wait_time)
                                continue
                            else:
                                raise Exception(f"Failed to download subtitles after {max_retries} attempts: YouTube is heavily rate limiting. Please try again later.")
                        
                        response.raise_for_status()
                        transcript_text = response.text
                        break  # Success, exit retry loop
                        
                    except requests.exceptions.RequestException as e:
                        if download_attempt < max_retries - 1:
                            wait_time = base_delay * (download_attempt + 1) * jitter
                            logger.warning(f"Download attempt {download_attempt + 1} failed: {e}, retrying in {wait_time:.1f}s...")
                            import time
                            time.sleep(wait_time)
                            continue
                        else:
                            logger.error(f"Error downloading subtitles: {e}")
                            raise Exception(f"Failed to download subtitles: {e}")
            
            # Clean up the transcript
            if transcript_text:
                return YouTubeTranscriptExtractor._clean_transcript(transcript_text)
            
            return ""
    
    @staticmethod
    def _clean_transcript(transcript_text: str) -> str:
        """Clean up transcript text by removing VTT formatting and timestamps."""
        # Remove VTT formatting and timestamps
        lines = transcript_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip WEBVTT header, timestamps, and empty lines
            if (line and 
                not line.startswith('WEBVTT') and
                not re.match(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', line) and
                not re.match(r'^\d+$', line) and
                not line.startswith('NOTE')):
                # Remove HTML tags and formatting
                line = re.sub(r'<[^>]+>', '', line)
                if line:
                    cleaned_lines.append(line)
        
        transcript_text = ' '.join(cleaned_lines)
        # Clean up extra whitespace
        transcript_text = re.sub(r'\s+', ' ', transcript_text)
        
        return transcript_text.strip()


class YouTubeSummarizerAgent(Agent):
    """YouTube summarization agent for DuoTalk."""
    
    def __init__(self):
        super().__init__(
            instructions=(
                "You are a helpful AI assistant integrated into DuoTalk that can summarize YouTube videos. "
                "When a user provides a YouTube URL, you will extract the transcript "
                "and provide a natural, conversational summary suitable for audio delivery. "
                "Structure your response as a flowing narrative, starting with phrases like "
                "'The main crux of this video revolves around...' or 'This video primarily focuses on...' "
                "Avoid using markdown formatting, bullet points, or symbols since this will be spoken aloud. "
                "Instead, use natural transitions like 'First,', 'Additionally,', 'Furthermore,', and 'Finally,'. "
                "Keep the summary engaging and conversational, as if you're explaining it to a friend. "
                "Aim for a summary that takes 1-2 minutes to speak when delivered as audio."
            ),
        )
        self.transcript_extractor = YouTubeTranscriptExtractor()
    
    @function_tool
    async def get_youtube_transcript(self, youtube_url: str) -> str:
        """
        Extract transcript from a YouTube video and prepare it for summarization.
        
        Args:
            youtube_url: The YouTube video URL to extract transcript from
        """
        try:
            logger.info(f"Extracting transcript from: {youtube_url}")
            
            # Extract transcript from YouTube video
            transcript = self.transcript_extractor.extract_transcript(youtube_url)
            
            if not transcript:
                return "Sorry, I couldn't extract the transcript from this video. The video might not have captions available or the video might be private/restricted."
            
            logger.info(f"Successfully extracted transcript, length: {len(transcript)} characters")
            
            # Truncate transcript if too long to avoid token limits
            if len(transcript) > 8000:
                transcript = transcript[:8000] + "... [transcript truncated due to length]"
            
            result = f"""I successfully extracted the transcript from the YouTube video. Here's the content to summarize:

{transcript}

Please provide me with a conversational summary that flows naturally when spoken aloud. Start with something like 'The main crux of this video revolves around...' and avoid any markdown formatting or bullet points since this will be delivered as speech. Make it engaging and informative, suitable for a 1-2 minute audio summary."""
            
            return result
            
        except Exception as e:
            error_msg = f"I encountered an error while extracting the transcript: {str(e)}"
            logger.error(f"Error in get_youtube_transcript: {e}")
            return error_msg


class YouTubeSummarizer:
    """Main YouTube summarization class for integration with DuoTalk."""
    
    def __init__(self):
        self.transcript_extractor = YouTubeTranscriptExtractor()
    
    async def summarize_video(
        self, 
        youtube_url: str, 
        use_voice: bool = True,
        voice_model: str = "cartesia",
        summary_mode: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Summarize a YouTube video and optionally deliver via voice.
        
        Args:
            youtube_url: YouTube video URL
            use_voice: Whether to use voice synthesis
            voice_model: Voice model to use (cartesia, google, etc.)
            summary_mode: Summary length mode - "short" or "detailed"
            
        Returns:
            Dict containing summary text, audio info, and metadata
        """
        try:
            # Extract transcript
            logger.info(f"Starting YouTube summarization for: {youtube_url}")
            transcript = self.transcript_extractor.extract_transcript(youtube_url)
            
            if not transcript:
                return {
                    "success": False,
                    "error": "Could not extract transcript from video",
                    "summary": None,
                    "audio_delivered": False
                }
            
            # Generate summary using Gemini
            summary = await self._generate_summary(transcript, summary_mode)
            
            result = {
                "success": True,
                "summary": summary,
                "transcript_length": len(transcript),
                "youtube_url": youtube_url,
                "summary_mode": summary_mode,
                "audio_delivered": False
            }
            
            # If voice is requested, we'll handle that at the CLI level
            # to integrate with DuoTalk's existing voice system
            if use_voice:
                result["voice_ready"] = True
                result["voice_model"] = voice_model
            
            return result
            
        except Exception as e:
            logger.error(f"Error in summarize_video: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": None,
                "audio_delivered": False
            }
    
    async def _generate_summary(self, transcript: str, summary_mode: str = "detailed") -> str:
        """Generate a conversational summary from the transcript using Google Gemini 2.5 Flash Lite.
        
        Args:
            transcript: The video transcript text
            summary_mode: "short" for concise summary, "detailed" for comprehensive summary
        """
        
        # Truncate if too long to fit within token limits
        if len(transcript) > 15000:
            transcript = transcript[:15000] + "... [content truncated due to length]"
        
        try:
            # Initialize Gemini
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.warning("No Google API key found. Using fallback summarization.")
                return await self._fallback_summary(transcript, summary_mode)
            
            genai.configure(api_key=api_key)
            
            # Use Gemini 2.5 Flash Lite model
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            
            # Create detailed prompts based on summary mode
            if summary_mode == "short":
                prompt = f"""
You are an expert video content analyst. I need you to create a concise but informative summary of this YouTube video transcript that will be spoken aloud as audio.

IMPORTANT GUIDELINES:
1. Start with "The main crux of this video revolves around..." or similar natural opening
2. Create a 2-3 sentence summary that captures the core message and key insights
3. Use conversational, flowing language suitable for audio delivery
4. NO bullet points, markdown, or formatting - this will be spoken
5. Make it engaging and informative enough that someone gets real value from just this summary
6. Focus on the most important takeaways and insights

Video Transcript:
{transcript}

Please provide a short, crisp, and insightful summary:"""
                
            else:  # detailed mode
                prompt = f"""
You are an expert video content analyst. I need you to create a comprehensive, detailed summary of this YouTube video transcript that will be spoken aloud as audio.

IMPORTANT GUIDELINES:
1. Start with "The main crux of this video revolves around..." or similar natural opening
2. Create a detailed 4-6 sentence summary that provides comprehensive insights
3. Include key points, important details, examples, and actionable insights
4. Use natural transitions like "Additionally," "Furthermore," "The video also explores," etc.
5. Use conversational, flowing language suitable for audio delivery - NO bullet points or markdown
6. Make it so detailed and insightful that someone listening gets a thorough understanding of the video content
7. Include specific details, numbers, examples, or key concepts mentioned
8. End with a concluding thought about the overall value or impact

Video Transcript:
{transcript}

Please provide a detailed, comprehensive, and highly insightful summary:"""
            
            # Generate the summary
            logger.info(f"Generating {summary_mode} summary using Gemini 2.5 Flash Lite")
            response = model.generate_content(prompt)
            
            if response and response.text:
                summary = response.text.strip()
                logger.info(f"Successfully generated {summary_mode} summary with Gemini")
                return summary
            else:
                logger.warning("Gemini returned empty response, using fallback")
                return await self._fallback_summary(transcript, summary_mode)
                
        except Exception as e:
            logger.error(f"Error with Gemini summarization: {e}")
            logger.info("Falling back to basic summarization")
            return await self._fallback_summary(transcript, summary_mode)
    
    async def _fallback_summary(self, transcript: str, summary_mode: str = "detailed") -> str:
        """Fallback summary generation when Gemini is not available."""
        
        # Clean up the transcript for better processing
        cleaned_transcript = transcript.replace('\n', ' ')
        cleaned_transcript = ' '.join(cleaned_transcript.split())  # Remove extra whitespace
        
        # Extract key phrases and content
        words = cleaned_transcript.lower().split()
        
        # Look for common patterns to understand the content better
        topic_keywords = []
        if any(word in words for word in ['ai', 'artificial', 'intelligence', 'machine', 'learning']):
            topic_keywords.append('artificial intelligence and machine learning')
        if any(word in words for word in ['stock', 'invest', 'trading', 'market', 'finance']):
            topic_keywords.append('financial markets and investment strategies')
        if any(word in words for word in ['technology', 'tech', 'software', 'programming']):
            topic_keywords.append('technology and software development')
        if any(word in words for word in ['business', 'company', 'startup', 'entrepreneur']):
            topic_keywords.append('business and entrepreneurship')
        if any(word in words for word in ['crypto', 'bitcoin', 'blockchain', 'currency']):
            topic_keywords.append('cryptocurrency and blockchain technology')
        
        # Try to extract the first few meaningful sentences
        sentences = [s.strip() for s in cleaned_transcript.split('.') if len(s.strip()) > 20]
        meaningful_sentences = []
        
        for sentence in sentences[:15]:  # Look at first 15 sentences
            if len(sentence) > 30 and len(sentence) < 300:  # Good length sentences
                # Skip sentences that look like captions artifacts
                if not sentence.lower().startswith(('kind:', 'language:', 'ai ai ai', 'music', 'applause')):
                    # Clean the sentence
                    sentence = re.sub(r'\[.*?\]', '', sentence)  # Remove bracketed content
                    sentence = re.sub(r'\(.*?\)', '', sentence)  # Remove parenthetical content
                    sentence = sentence.strip()
                    if len(sentence) > 20:
                        meaningful_sentences.append(sentence)
                        if len(meaningful_sentences) >= 5:
                            break
        
        # Generate summary based on extracted content
        if topic_keywords:
            topic_focus = ' and '.join(topic_keywords[:2])  # Use up to 2 topics
            summary = f"The main crux of this video revolves around {topic_focus}. "
        else:
            summary = "The main crux of this video revolves around important topics and insights. "
        
        if meaningful_sentences:
            if summary_mode == "short":
                # Short summary - focus on first key point
                if len(meaningful_sentences) >= 1:
                    summary += f"The video explores {meaningful_sentences[0].lower()}. "
                if len(meaningful_sentences) >= 2:
                    summary += f"It also discusses {meaningful_sentences[1].lower()}."
            else:
                # Detailed summary - more comprehensive
                for i, sentence in enumerate(meaningful_sentences[:4]):
                    if i == 0:
                        summary += f"The video explores {sentence.lower()}. "
                    elif i == 1:
                        summary += f"Additionally, it discusses {sentence.lower()}. "
                    elif i == 2:
                        summary += f"Furthermore, the content covers {sentence.lower()}. "
                    elif i == 3:
                        summary += f"The video also examines {sentence.lower()}. "
                
                summary += "This comprehensive content provides valuable insights and practical information on the subject matter."
        else:
            # Ultimate fallback
            if summary_mode == "short":
                summary += "The content provides valuable insights and information."
            else:
                summary += "The content provides comprehensive insights, detailed analysis, and practical information. This video appears to be informative and covers multiple important aspects of the subject matter with depth and clarity."
        
        return summary


# Convenience functions for easy integration
async def summarize_youtube_video(
    url: str, 
    use_voice: bool = True,
    voice_model: str = "cartesia",
    summary_mode: str = "detailed"
) -> Dict[str, Any]:
    """
    Convenience function to summarize a YouTube video.
    
    Args:
        url: YouTube video URL
        use_voice: Whether to enable voice output
        voice_model: Voice model to use
        summary_mode: Summary length mode - "short" or "detailed"
        
    Returns:
        Dictionary with summary results
    """
    summarizer = YouTubeSummarizer()
    return await summarizer.summarize_video(url, use_voice, voice_model, summary_mode)


def validate_youtube_url(url: str) -> bool:
    """Validate if the provided URL is a valid YouTube URL."""
    youtube_patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in youtube_patterns:
        if re.search(pattern, url):
            return True
    return False


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None