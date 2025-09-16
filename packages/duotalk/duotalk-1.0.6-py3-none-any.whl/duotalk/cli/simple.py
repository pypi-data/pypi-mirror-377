#!/usr/bin/env python3
"""Simple CLI interface for DuoTalk"""

import asyncio
import typer
import sys
import os
import subprocess
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.text import Text

app = typer.Typer(
    help="DuoTalk - AI conversation platform",
    no_args_is_help=True,
    rich_markup_mode="rich"
)

console = Console()

def show_duotalk_banner():
    """Show the amazing DuoTalk banner"""
    
    # Create the ASCII art for DuoTalk
    ascii_art = """
██████╗ ██╗   ██╗ ██████╗ ████████╗ █████╗ ██╗     ██╗  ██╗
██╔══██╗██║   ██║██╔═══██╗╚══██╔══╝██╔══██╗██║     ██║ ██╔╝
██║  ██║██║   ██║██║   ██║   ██║   ███████║██║     █████╔╝ 
██║  ██║██║   ██║██║   ██║   ██║   ██╔══██║██║     ██╔═██╗ 
██████╔╝╚██████╔╝╚██████╔╝   ██║   ██║  ██║███████╗██║  ██╗
╚═════╝  ╚═════╝  ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""
    
    # Create rich text with gradient colors
    banner_text = Text()
    lines = ascii_art.strip().split('\n')
    
    # Color gradient from blue to purple to cyan
    colors = ["#00D4FF", "#0597F8","#0099FF", "#3366FF", "#062581", "#200220"]
    
    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        banner_text.append(line + "\n", style=f"bold {color}")
    
    # Create subtitle
    subtitle = Text()
    subtitle.append("🎭 ", style="bold yellow")
    subtitle.append("Agent Conversation Platform", style="bold white")
    subtitle.append(" by Abhyuday Patel ", style="dim cyan")
    
    # Create version text
    version_text = Text("v1.0.6", style="dim cyan")
    
    # Create description
    description = Text()
    description.append("Create dynamic conversations between AI agents with voice synthesis\n", style="white")
    description.append("Perfect for debates, interviews, panels, and friendly chats!", style="dim white")
    
    # Display the banner - all centered
    console.print()
    console.print(banner_text, justify="center", end="")
    console.print(subtitle, justify="center")
    console.print(version_text, justify="center")
    console.print()
    console.print(description, justify="center")
    console.print()

# Try to import enhanced features, fall back to basic if not available
try:
    from duotalk.enhanced import (
        quick_debate, quick_roundtable, quick_friendly, quick_interview, quick_panel,
        sync_run, get_available_personas
    )
    _enhanced_available = True
except ImportError:
    _enhanced_available = False
    # Import the working voice system
    import subprocess
    import sys
    import os

def show_banner(conversation_type: str, topic: str, agents: int):
    """Show conversation banner"""
    console.print(f"\n[bold blue]🎭 DuoTalk {conversation_type.title()}[/bold blue]")
    console.print(f"[cyan]Topic:[/cyan] {topic}")
    console.print(f"[cyan]Agents:[/cyan] {agents}")
    console.print(f"[dim]Enhanced mode: {'✓' if _enhanced_available else '✗'}[/dim]\n")

def run_voice_conversation(topic: str, mode: str = "debate", livekit_mode: str = "console", single_agent: bool = False):
    """Run voice conversation using the existing dual_voice_agents.py"""
    try:
        if single_agent:
            console.print(f"[green]🎙️ Starting single agent voice chat about: {topic}[/green]")
            console.print(f"[cyan]Mode: {mode} (Single Agent)[/cyan]")
        else:
            console.print(f"[green]🎙️ Starting voice conversation about: {topic}[/green]")
            console.print(f"[cyan]Mode: {mode}[/cyan]")
        
        console.print(f"[dim]LiveKit mode: {livekit_mode}[/dim]")
        console.print("[dim]Setting up LiveKit session...[/dim]")
        
        # Set environment variables for the voice script
        env = os.environ.copy()
        env['DUOTALK_TOPIC'] = topic
        env['DUOTALK_MODE'] = mode
        env['DUOTALK_SINGLE_AGENT'] = "true" if single_agent else "false"
        
        # Find the dual_voice_agents.py script
        # First try the package directory
        package_dir = Path(__file__).parent.parent
        voice_script = package_dir / "dual_voice_agents.py"
        
        # If not found in package, try current directory (for development)
        if not voice_script.exists():
            voice_script = Path.cwd() / "dual_voice_agents.py"
        
        # If still not found, try the directory where this script is located
        if not voice_script.exists():
            voice_script = Path(__file__).parent / "dual_voice_agents.py"
        
        if not voice_script.exists():
            console.print(f"[red]Error: dual_voice_agents.py not found. Please ensure the voice system is properly installed.[/red]")
            console.print(f"[dim]Searched in: {package_dir}, {Path.cwd()}, {Path(__file__).parent}[/dim]")
            return False
        
        # Run the dual_voice_agents.py script with specified mode
        result = subprocess.run([
            sys.executable, str(voice_script), livekit_mode
        ], env=env)
        
        return result.returncode == 0
                
    except Exception as e:
        console.print(f"[red]Error starting voice conversation: {e}[/red]")
        return False

@app.command()
def debate(
    topic: str = typer.Option(..., "-t", "--topic", help="Debate topic"),
    turns: int = typer.Option(10, "-n", "--turns", help="Max conversation turns"),
    voice: bool = typer.Option(True, "--voice/--no-voice", help="Enable voice synthesis"),
    personas: Optional[str] = typer.Option(None, "-p", "--personas", help="Comma-separated personas"),
    mode: str = typer.Option("console", "--mode", help="LiveKit mode: console, dev, or start")
):
    """Start a debate between two opposing viewpoints."""
    show_banner("debate", topic, 2)
    
    try:
        if _enhanced_available:
            if personas:
                selected_personas = personas.split(",")[:2]
            else:
                selected_personas = ["optimist", "skeptic"]
            
            runner = quick_debate(topic, pro_agent=selected_personas[0], con_agent=selected_personas[1] if len(selected_personas) > 1 else "skeptic", max_turns=turns, voice=voice)
            if voice:
                console.print("🎙️ Starting voice conversation...")
            sync_run(runner)
        else:
            # Use the existing voice system
            if voice:
                console.print("[blue]🎙️ Using built-in voice system...[/blue]")
                success = run_voice_conversation(topic, mode="debate", livekit_mode=mode)
                if not success:
                    console.print("[red]Voice conversation failed to start[/red]")
            else:
                console.print("[yellow]Voice disabled. No fallback text conversation available.[/yellow]")
                console.print("[dim]Tip: Use --voice to enable voice conversation[/dim]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Conversation stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@app.command()
def roundtable(
    topic: str = typer.Option(..., "-t", "--topic", help="Discussion topic"),
    agents: int = typer.Option(3, "-a", "--agents", help="Number of participants (default: 3)"),
    turns: int = typer.Option(12, "-n", "--turns", help="Max conversation turns"),
    voice: bool = typer.Option(True, "--voice/--no-voice", help="Enable voice synthesis"),
    personas: Optional[str] = typer.Option(None, "-p", "--personas", help="Comma-separated personas"),
    mode: str = typer.Option("console", "--mode", help="LiveKit mode: console, dev, or start")
):
    """Start a roundtable discussion with multiple participants."""
    show_banner("roundtable", topic, agents)
    
    try:
        if _enhanced_available:
            if personas:
                selected_personas = personas.split(",")[:agents]
            else:
                selected_personas = ["optimist", "analyst", "creative"][:agents]
            
            runner = quick_roundtable(topic, agents=selected_personas, max_turns=turns, voice=voice)
            if voice:
                console.print("🎙️ Starting voice conversation...")
            sync_run(runner)
        else:
            # Use the existing voice system - roundtable will use friendly mode
            if voice:
                console.print("[blue]🎙️ Using built-in voice system...[/blue]")
                success = run_voice_conversation(topic, mode="friendly", livekit_mode=mode)
                if not success:
                    console.print("[red]Voice conversation failed to start[/red]")
            else:
                console.print("[yellow]Voice disabled. No fallback text conversation available.[/yellow]")
                console.print("[dim]Tip: Use --voice to enable voice conversation[/dim]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Conversation stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@app.command()
def chat(
    topic: str = typer.Option(..., "-t", "--topic", help="Chat topic"),
    agents: int = typer.Option(2, "-a", "--agents", help="Number of agents: 1 for user-agent chat, 2+ for multi-agent conversation"),
    turns: int = typer.Option(10, "-n", "--turns", help="Max conversation turns"),
    voice: bool = typer.Option(True, "--voice/--no-voice", help="Enable voice synthesis"),
    personas: Optional[str] = typer.Option(None, "-p", "--personas", help="Comma-separated personas"),
    mode: str = typer.Option("console", "--mode", help="LiveKit mode: console, dev, or start")
):
    """Start a friendly chat conversation. Use -a 1 for single agent chatting with you, or -a 2+ for multi-agent conversations."""
    show_banner("friendly chat", topic, agents)
    
    try:
        if _enhanced_available:
            if agents == 1:
                # Single agent mode - interactive chat with user
                if personas:
                    selected_persona = personas.split(",")[0]
                else:
                    selected_persona = "friendly"
                
                console.print(f"[green]🤖 Starting single agent chat with {selected_persona} persona[/green]")
                console.print(f"[blue]💭 Topic: {topic}[/blue]")
                
                if voice:
                    console.print("[blue]🎙️ Starting voice chat with single agent...[/blue]")
                    success = run_voice_conversation(topic, mode="friendly", livekit_mode=mode, single_agent=True)
                    if not success:
                        console.print("[red]Voice conversation failed to start[/red]")
                else:
                    console.print("[yellow]Voice disabled for single agent mode. Starting text interaction...[/yellow]")
                    # For now, inform user that text mode isn't implemented for single agent
                    console.print("[dim]Note: Single agent text mode not yet implemented. Use --voice for full functionality.[/dim]")
            else:
                # Multi-agent mode - agents chat with each other
                if personas:
                    selected_personas = personas.split(",")[:agents]
                else:
                    selected_personas = ["optimist", "enthusiast"] if agents == 2 else ["optimist", "enthusiast", "creative"][:agents]
                
                runner = quick_friendly(topic, agents=selected_personas, max_turns=turns, voice=voice)
                if voice:
                    console.print("🎙️ Starting multi-agent voice conversation...")
                sync_run(runner)
        else:
            # Use the existing voice system
            if voice:
                console.print("[blue]🎙️ Using built-in voice system...[/blue]")
                single_agent_mode = (agents == 1)
                success = run_voice_conversation(topic, mode="friendly", livekit_mode=mode, single_agent=single_agent_mode)
                if not success:
                    console.print("[red]Voice conversation failed to start[/red]")
            else:
                console.print("[yellow]Voice disabled. No fallback text conversation available.[/yellow]")
                console.print("[dim]Tip: Use --voice to enable voice conversation[/dim]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Conversation stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@app.command()
def interview(
    topic: str = typer.Option(..., "-t", "--topic", help="Interview topic"),
    turns: int = typer.Option(10, "-n", "--turns", help="Max conversation turns"),
    voice: bool = typer.Option(True, "--voice/--no-voice", help="Enable voice synthesis"),
    interviewer: str = typer.Option("journalist", "--interviewer", help="Interviewer persona"),
    interviewee: str = typer.Option("expert", "--interviewee", help="Interviewee persona"),
    mode: str = typer.Option("console", "--mode", help="LiveKit mode: console, dev, or start")
):
    """Start an interview conversation."""
    show_banner("interview", topic, 2)
    
    try:
        if _enhanced_available:
            runner = quick_interview(topic, interviewer=interviewer, interviewee=interviewee, max_turns=turns, voice=voice)
            if voice:
                console.print("🎙️ Starting voice conversation...")
            sync_run(runner)
        else:
            # Use the existing voice system
            if voice:
                console.print("[blue]🎙️ Using built-in voice system...[/blue]")
                success = run_voice_conversation(topic, mode="friendly", livekit_mode=mode)
                if not success:
                    console.print("[red]Voice conversation failed to start[/red]")
            else:
                console.print("[yellow]Voice disabled. No fallback text conversation available.[/yellow]")
                console.print("[dim]Tip: Use --voice to enable voice conversation[/dim]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Conversation stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@app.command()
def panel(
    topic: str = typer.Option(..., "-t", "--topic", help="Panel discussion topic"),
    agents: int = typer.Option(4, "-a", "--agents", help="Number of experts (default: 4)"),
    turns: int = typer.Option(15, "-n", "--turns", help="Max conversation turns"),
    voice: bool = typer.Option(True, "--voice/--no-voice", help="Enable voice synthesis"),
    personas: Optional[str] = typer.Option(None, "-p", "--personas", help="Comma-separated personas")
):
    """Start an expert panel discussion."""
    show_banner("expert panel", topic, agents)
    
    try:
        if _enhanced_available:
            if personas:
                selected_personas = personas.split(",")[:agents]
            else:
                # Default expert personas for panels
                expert_personas = ["educator", "analyst", "scientist", "entrepreneur", "theorist"]
                selected_personas = expert_personas[:agents]
            
            runner = quick_panel(topic, agents=selected_personas, max_turns=turns, voice=voice)
            if voice:
                console.print("🎙️ Starting voice conversation...")
            sync_run(runner)
        else:
            console.print("[red]Enhanced features required for this command. Please check your installation.[/red]")
            console.print("[dim]Tip: Try running 'pip install duotalk[enhanced]' or similar[/dim]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Conversation stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def speak_summary_with_tts(summary_text: str) -> bool:
    """Speak the summary using TTS without the interactive agent system"""
    try:
        # Try to use simple TTS approach
        import asyncio
        import tempfile
        import os
        
        # Try using edge-tts for simple text-to-speech
        try:
            import edge_tts
            
            async def speak_text():
                voice = "en-US-AriaNeural"  # Female voice
                communicate = edge_tts.Communicate(summary_text, voice)
                
                # Save to temporary file and play
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    await communicate.save(tmp_file.name)
                    
                    # Try to play the audio file
                    if os.name == 'nt':  # Windows
                        os.system(f'start "" "{tmp_file.name}"')
                    else:  # Unix-like
                        os.system(f'afplay "{tmp_file.name}" || aplay "{tmp_file.name}" || play "{tmp_file.name}"')
                    
                    # Wait for playback (estimate based on text length)
                    estimated_duration = len(summary_text) * 0.05  # ~20 words per second
                    await asyncio.sleep(min(estimated_duration, 30))  # Max 30 seconds
                    
                    # Clean up
                    try:
                        os.unlink(tmp_file.name)
                    except:
                        pass
            
            asyncio.run(speak_text())
            return True
            
        except ImportError:
            console.print("[yellow]edge-tts not available. Install with: pip install edge-tts[/yellow]")
            return False
            
    except Exception as e:
        console.print(f"[red]TTS Error: {e}[/red]")
        return False

@app.command()
def summarize(
    url: str = typer.Option(..., "-u", "--url", help="YouTube video URL to summarize"),
    voice: bool = typer.Option(True, "--voice/--no-voice", help="Enable voice synthesis"),
    mode: str = typer.Option("console", "--mode", help="LiveKit mode: console, dev, or start"),
    summary_mode: str = typer.Option("detailed", "--summary-mode", "-s", help="Summary length: 'short' or 'detailed'"),
    tts_engine: str = typer.Option("edge", "--tts-engine", "-t", help="TTS engine: 'edge', 'google', 'deepgram', 'cartesia'")
):
    """Summarize a YouTube video with voice synthesis."""
    try:
        # Import YouTube summarizer
        from duotalk.core.youtube_summarizer import validate_youtube_url, summarize_youtube_video
        
        # Validate URL
        if not validate_youtube_url(url):
            console.print("[red]❌ Invalid YouTube URL. Please provide a valid YouTube video URL.[/red]")
            console.print("[dim]Examples: https://youtube.com/watch?v=... or https://youtu.be/...[/dim]")
            return
        
        # Validate summary mode
        if summary_mode not in ["short", "detailed"]:
            console.print(f"[red]❌ Invalid summary mode: {summary_mode}. Please use 'short' or 'detailed'.[/red]")
            return
        
        # Validate TTS engine
        if tts_engine not in ["edge", "google", "deepgram", "cartesia"]:
            console.print(f"[red]❌ Invalid TTS engine: {tts_engine}. Please use 'edge', 'google', 'deepgram', or 'cartesia'.[/red]")
            return
        
        console.print(f"\n[bold blue]🎥 YouTube Video Summarizer[/bold blue]")
        console.print(f"[cyan]URL:[/cyan] {url}")
        console.print(f"[cyan]Voice:[/cyan] {'Enabled' if voice else 'Disabled'}")
        console.print(f"[cyan]Summary Mode:[/cyan] {summary_mode.title()}")
        if voice:
            console.print(f"[cyan]TTS Engine:[/cyan] {tts_engine.title()}")
        console.print()
        
        if voice:
            console.print("[blue]🎙️ Starting YouTube summarization with voice...[/blue]")
            console.print("[dim]Extracting transcript and generating spoken summary...[/dim]")
            
            # Generate the summary first
            import asyncio
            try:
                result = asyncio.run(summarize_youtube_video(url, use_voice=False, summary_mode=summary_mode))
                
                if result["success"]:
                    console.print(f"[green]✓ Successfully extracted transcript ({result['transcript_length']} characters)[/green]")
                    console.print(f"[green]✓ Generated {result['summary_mode']} summary[/green]")
                    console.print("\n[bold]Summary:[/bold]")
                    console.print(f"[white]{result['summary']}[/white]")
                    
                    # Now speak the summary using TTS
                    console.print(f"\n[blue]🎙️ Speaking summary using {tts_engine.title()} TTS...[/blue]")
                    
                    # Use the new TTS handler
                    from duotalk.core.tts_handler import speak_text_sync
                    success = speak_text_sync(result['summary'], engine=tts_engine)
                    
                    if success:
                        console.print(f"[green]✓ Voice summary completed with {tts_engine.title()} TTS[/green]")
                    else:
                        console.print(f"[yellow]⚠️ {tts_engine.title()} TTS failed, but text summary was successful[/yellow]")
                else:
                    console.print(f"[red]❌ Error: {result['error']}[/red]")
                    voice = False
                    
            except Exception as e:
                console.print(f"[red]Error during summarization: {e}[/red]")
                voice = False
        
        if not voice:
            console.print("[blue]📝 Generating text summary...[/blue]")
            
            # Run async summarization
            import asyncio
            try:
                result = asyncio.run(summarize_youtube_video(url, use_voice=False, summary_mode=summary_mode))
                
                if result["success"]:
                    console.print(f"[green]✓ Successfully extracted transcript ({result['transcript_length']} characters)[/green]")
                    console.print(f"[green]✓ Generated {result['summary_mode']} summary[/green]")
                    console.print("\n[bold]Summary:[/bold]")
                    console.print(f"[white]{result['summary']}[/white]")
                else:
                    console.print(f"[red]❌ Error: {result['error']}[/red]")
                    
            except Exception as e:
                console.print(f"[red]Error during summarization: {e}[/red]")
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Summarization stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def run_youtube_voice_summary(url: str, livekit_mode: str = "console", summary_mode: str = "detailed") -> bool:
    """Run YouTube summarization with voice using the existing voice system"""
    try:
        console.print(f"[green]🎙️ Starting voice summarization for YouTube video[/green]")
        console.print(f"[dim]LiveKit mode: {livekit_mode}[/dim]")
        console.print("[dim]Setting up voice synthesis session...[/dim]")
        
        # Set environment variables for the voice script
        env = os.environ.copy()
        env['DUOTALK_YOUTUBE_URL'] = url
        env['DUOTALK_MODE'] = 'youtube_summary'
        env['DUOTALK_SUMMARY_MODE'] = summary_mode
        
        # Find the youtube_summary_agent.py script
        package_dir = Path(__file__).parent.parent
        summary_script = package_dir / "youtube_summary_agent.py"
        
        # If not found in package, try current directory
        if not summary_script.exists():
            summary_script = Path.cwd() / "youtube_summary_agent.py"
        
        # If still not found, try the directory where this script is located
        if not summary_script.exists():
            summary_script = Path(__file__).parent / "youtube_summary_agent.py"
        
        # Check if we have the original youtube_summary_agent.py
        if not summary_script.exists():
            # Create a temporary script that uses our new module
            summary_script = package_dir / "temp_youtube_agent.py"
            create_temp_youtube_agent(summary_script, url, summary_mode)
        
        if not summary_script.exists():
            console.print(f"[red]Error: YouTube summary agent not found.[/red]")
            return False
        
        # Run the YouTube summary agent
        result = subprocess.run([
            sys.executable, str(summary_script), livekit_mode
        ], env=env)
        
        return result.returncode == 0
                
    except Exception as e:
        console.print(f"[red]Error starting voice summarization: {e}[/red]")
        return False

def create_temp_youtube_agent(script_path: Path, youtube_url: str, summary_mode: str = "detailed"):
    """Create a temporary YouTube agent script for voice synthesis"""
    script_content = f'''#!/usr/bin/env python3
import asyncio
import os
import logging
from livekit.agents import JobContext, WorkerOptions, cli, AgentSession
from livekit.plugins import google, cartesia
from duotalk.core.youtube_summarizer import YouTubeSummarizerAgent, YouTubeSummarizer

logger = logging.getLogger(__name__)

async def entrypoint(ctx: JobContext):
    """Main entrypoint for YouTube summarization with voice"""
    await ctx.connect()
    
    # Get parameters from environment
    youtube_url = os.getenv('DUOTALK_YOUTUBE_URL', '{youtube_url}')
    summary_mode = os.getenv('DUOTALK_SUMMARY_MODE', '{summary_mode}')
    
    logger.info(f"Starting YouTube voice summarization for: {{youtube_url}}")
    logger.info(f"Summary mode: {{summary_mode}}")
    
    try:
        # Create summarizer and get the summary first
        summarizer = YouTubeSummarizer()
        result = await summarizer.summarize_video(youtube_url, use_voice=False, summary_mode=summary_mode)
        
        if not result["success"]:
            logger.error(f"Failed to generate summary: {{result['error']}}")
            return
        
        summary_text = result["summary"]
        logger.info(f"Generated {{summary_mode}} summary, length: {{len(summary_text)}} characters")
        
        # Initialize the YouTube summarizer agent
        agent = YouTubeSummarizerAgent()
        
        # Create session with voice synthesis
        session = AgentSession(
            llm=google.LLM(model="gemini-2.5-flash-lite"),
            tts=cartesia.TTS(
                model="sonic-english",
                voice="a0e99841-438c-4a64-b679-ae501e7d6091",
            ),
        )
        
        # Start the session and immediately speak the summary
        await session.start(agent=agent, room=ctx.room)
        
        # Send the summary directly to TTS
        logger.info("Starting TTS playback of summary...")
        await session.send_message(summary_text)
        
        # Keep the session alive for a bit to let the audio play
        await asyncio.sleep(30)  # Adjust based on summary length
        
    except Exception as e:
        logger.error(f"Error in YouTube voice summarization: {{e}}")
        
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
'''
    
    with open(script_path, 'w') as f:
        f.write(script_content)

@app.command()
def personas():
    """List all available personas."""
    if _enhanced_available:
        try:
            available = get_available_personas()
            console.print("[bold]Available Personas:[/bold]")
            for persona in available:
                console.print(f"  • [cyan]{persona}[/cyan]")
        except Exception as e:
            console.print(f"[red]Error getting personas: {e}[/red]")
    else:
        console.print("[bold]Default Personas:[/bold]")
        default_personas = [
            "optimist", "skeptic", "analyst", "creative", "enthusiast",
            "expert", "journalist", "educator", "scientist", "entrepreneur",
            "theorist", "researcher", "strategist", "philosopher"
        ]
        for persona in default_personas:
            console.print(f"  • [cyan]{persona}[/cyan]")

def main():
    """Main entry point for the CLI"""
    # Show banner first if no arguments provided or help requested
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h']):
        show_duotalk_banner()
    app()

if __name__ == "__main__":
    main()
