"""
Enhanced CLI interface for DuoTalk with comprehensive features.
"""

import asyncio
import typer
import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree

# Optional YAML support
try:
    import yaml
    _yaml_available = True
except ImportError:
    _yaml_available = False

from ..core.config import ConversationConfig
from ..core.demo import run_demo_conversation
from ..core.convenience import (
    create_debate, create_roundtable, create_friendly_chat,
    create_interview, create_panel, create_socratic,
    create_business_discussion, create_academic_debate,
    create_creative_brainstorm, create_policy_discussion
)
from ..personas import ALL_PERSONA_NAMES, get_persona_by_name, ALL_PERSONAS
from ..modes import ALL_MODES, get_mode

# Optional enhanced features
try:
    from ..config.enhanced_config import DuoTalkConfig
    from ..quick import (
        quick_debate, quick_roundtable, quick_friendly, quick_interview, 
        quick_panel, quick_socratic, quick_start, sync_run
    )
    _enhanced_features = True
except ImportError:
    _enhanced_features = False

app = typer.Typer(name="duotalk", help="Advanced multi-agent voice conversation system")
console = Console()

# Conversation presets - now include debate and more options
CONVERSATION_PRESETS = {
    "business": create_business_discussion,
    "academic": create_academic_debate,
    "creative": create_creative_brainstorm,
    "policy": create_policy_discussion,
    "debate": lambda topic: create_debate(topic, ["optimist", "skeptic"]),
    "roundtable": lambda topic: create_roundtable(topic),
    "interview": lambda topic: create_interview(topic),
    "panel": lambda topic: create_panel(topic),
}


@app.command()
def start(
    topic: str = typer.Argument(..., help="Conversation topic"),
    mode: str = typer.Option("roundtable", help="Conversation mode"),
    personas: List[str] = typer.Option([], help="Persona names to use"),
    max_turns: int = typer.Option(10, help="Maximum conversation turns"),
    demo: bool = typer.Option(True, help="Run in demo mode (simulation)"),
    fast: bool = typer.Option(False, help="Fast mode (no typing animation)"),
):
    """Start a conversation with specified parameters."""
    try:
        if mode == "debate":
            config = create_debate(topic, personas or None, max_turns)
        elif mode == "roundtable":
            config = create_roundtable(topic, personas or None, max_turns)
        elif mode == "friendly":
            config = create_friendly_chat(topic, personas or None, max_turns)
        elif mode == "interview":
            config = create_interview(topic, personas[0] if personas else None, personas[1:] if len(personas) > 1 else None, max_turns)
        elif mode == "panel":
            config = create_panel(topic, personas[0] if personas else None, personas[1:] if len(personas) > 1 else None, max_turns)
        elif mode == "socratic":
            config = create_socratic(topic, personas or None, max_turns)
        else:
            console.print(f"❌ Unknown mode: {mode}. Available modes: {', '.join(ALL_MODES)}")
            raise typer.Exit(1)
        
        if demo:
            console.print("🎬 Running conversation in demo mode...")
            run_demo_conversation(
                config, 
                show_typing=not fast, 
                delay_between_turns=0.5 if fast else 2.0
            )
        else:
            console.print(f"🎭 Created {mode} conversation: '{topic}'")
            console.print(f"👥 Participants: {', '.join([agent.name for agent in config.agents])}")
            console.print("📝 Configuration created successfully!")
            console.print("🔧 To run with actual voice, set up LiveKit credentials and use --no-demo")
        
    except Exception as e:
        console.print(f"❌ Error creating conversation: {e}")
        raise typer.Exit(1)


@app.command()
def summarize(
    url: str = typer.Argument(..., help="YouTube video URL to summarize"),
    voice: bool = typer.Option(True, "--voice/--no-voice", help="Enable voice synthesis"),
    max_length: int = typer.Option(8000, help="Maximum transcript length to process"),
    save_output: bool = typer.Option(False, "--save", help="Save summary to file"),
):
    """Summarize a YouTube video with optional voice synthesis."""
    try:
        # Import YouTube functionality
        from ..core.convenience import create_youtube_summary
        from ..core.youtube_summarizer import validate_youtube_url
        
        console.print(Panel(
            "[bold blue]🎥 YouTube Video Summarizer[/bold blue]",
            title="DuoTalk YouTube Summary",
            border_style="blue"
        ))
        
        # Validate URL
        if not validate_youtube_url(url):
            console.print("[red]❌ Invalid YouTube URL provided[/red]")
            console.print("[dim]Please provide a valid YouTube URL (youtube.com or youtu.be)[/dim]")
            raise typer.Exit(1)
        
        console.print(f"[cyan]🔗 URL:[/cyan] {url}")
        console.print(f"[cyan]🎙️ Voice:[/cyan] {'Enabled' if voice else 'Disabled'}")
        console.print(f"[cyan]📏 Max Length:[/cyan] {max_length} characters")
        console.print()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Extract transcript
            task = progress.add_task("Extracting transcript...", total=None)
            
            try:
                result = create_youtube_summary(url, voice)
                progress.remove_task(task)
                
                if result["success"]:
                    console.print(f"[green]✅ Successfully processed video[/green]")
                    console.print(f"[dim]Transcript length: {result.get('transcript_length', 'Unknown')} characters[/dim]")
                    console.print()
                    
                    # Display summary
                    console.print(Panel(
                        result["summary"],
                        title="[bold]Video Summary[/bold]",
                        border_style="green"
                    ))
                    
                    # Save if requested
                    if save_output:
                        from pathlib import Path
                        import json
                        from datetime import datetime
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"youtube_summary_{timestamp}.json"
                        
                        output_data = {
                            "url": url,
                            "summary": result["summary"],
                            "transcript_length": result.get("transcript_length"),
                            "timestamp": timestamp,
                            "voice_enabled": voice
                        }
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(output_data, f, indent=2, ensure_ascii=False)
                        
                        console.print(f"\n[green]💾 Summary saved to: {filename}[/green]")
                    
                    # Voice synthesis notification
                    if voice and result.get("voice_ready"):
                        console.print("\n[blue]🎙️ Voice synthesis would be handled by LiveKit session[/blue]")
                        console.print("[dim]Set up LiveKit credentials for full voice functionality[/dim]")
                    
                else:
                    progress.remove_task(task)
                    console.print(f"[red]❌ Error: {result['error']}[/red]")
                    
                    # Provide helpful suggestions
                    if "transcript" in result["error"].lower():
                        console.print("\n[yellow]💡 Possible solutions:[/yellow]")
                        console.print("• Check if the video has captions/subtitles")
                        console.print("• Try a different video")
                        console.print("• Ensure the video is public and accessible")
                    
                    raise typer.Exit(1)
                
            except ImportError as e:
                progress.remove_task(task)
                console.print(f"[red]❌ Missing dependencies: {e}[/red]")
                console.print("\n[yellow]💡 Install required packages:[/yellow]")
                console.print("pip install yt-dlp requests")
                raise typer.Exit(1)
            
            except Exception as e:
                progress.remove_task(task)
                console.print(f"[red]❌ Unexpected error: {e}[/red]")
                raise typer.Exit(1)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️ Summarization cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def preset(
    preset_name: str = typer.Argument(..., help="Preset name"),
    topic: str = typer.Argument(..., help="Conversation topic"),
    max_turns: int = typer.Option(10, help="Maximum conversation turns"),
    demo: bool = typer.Option(True, help="Run in demo mode (simulation)"),
    fast: bool = typer.Option(False, help="Fast mode (no typing animation)"),
):
    """Start a conversation using a preset configuration."""
    if preset_name not in CONVERSATION_PRESETS:
        console.print(f"❌ Unknown preset: {preset_name}")
        console.print(f"Available presets: {', '.join(CONVERSATION_PRESETS.keys())}")
        raise typer.Exit(1)
    
    try:
        config = CONVERSATION_PRESETS[preset_name](topic)
        # Update max_turns if specified
        config.max_turns = max_turns
        
        if demo:
            console.print(f"🎬 Running {preset_name} conversation in demo mode...")
            run_demo_conversation(
                config, 
                show_typing=not fast, 
                delay_between_turns=0.5 if fast else 2.0
            )
        else:
            console.print(f"🎭 Created {preset_name} conversation: '{topic}'")
            console.print(f"👥 Participants: {', '.join([agent.name for agent in config.agents])}")
            console.print("📝 Configuration created successfully!")
            console.print("🔧 To run with actual voice, set up LiveKit credentials and use --no-demo")
        
    except Exception as e:
        console.print(f"❌ Error creating conversation: {e}")
        raise typer.Exit(1)


@app.command()
def list_personas():
    """List all available personas."""
    table = Table(title="Available Personas")
    table.add_column("Name", style="cyan")
    table.add_column("Persona", style="magenta")
    table.add_column("Role", style="green")
    table.add_column("Perspective", style="yellow")
    
    from ..personas import ALL_PERSONAS
    for persona in ALL_PERSONAS:
        table.add_row(
            persona.name,
            persona.persona,
            persona.role,
            persona.perspective
        )
    
    console.print(table)


@app.command()
def list_modes():
    """List all available conversation modes."""
    console.print(Panel("Available Conversation Modes", title_align="center"))
    
    mode_descriptions = {
        "friendly": "Collaborative discussion where agents build on each other's ideas",
        "debate": "Structured debate with opposing viewpoints and rebuttals",
        "roundtable": "Multi-participant discussion with diverse perspectives",
        "interview": "Interview format with one interviewer and multiple interviewees",
        "panel": "Expert panel with moderator and specialists",
        "socratic": "Question-driven exploration using Socratic method"
    }
    
    for mode, description in mode_descriptions.items():
        console.print(f"[bold cyan]{mode}[/bold cyan]: {description}")


@app.command()
def demo(
    topic: str = typer.Argument(..., help="Conversation topic"),
    mode: str = typer.Option("debate", help="Conversation mode"),
    personas: List[str] = typer.Option([], help="Persona names to use"),
    max_turns: int = typer.Option(6, help="Maximum conversation turns"),
    fast: bool = typer.Option(False, help="Fast mode (no typing animation)"),
):
    """Run a demo conversation simulation."""
    try:
        if mode == "debate":
            config = create_debate(topic, personas or None, max_turns)
        elif mode == "roundtable":
            config = create_roundtable(topic, personas or None, max_turns)
        elif mode == "friendly":
            config = create_friendly_chat(topic, personas or None, max_turns)
        elif mode == "interview":
            config = create_interview(topic, personas[0] if personas else None, personas[1:] if len(personas) > 1 else None, max_turns)
        elif mode == "panel":
            config = create_panel(topic, personas[0] if personas else None, personas[1:] if len(personas) > 1 else None, max_turns)
        elif mode == "socratic":
            config = create_socratic(topic, personas or None, max_turns)
        else:
            console.print(f"❌ Unknown mode: {mode}. Available modes: {', '.join(ALL_MODES)}")
            raise typer.Exit(1)
        
        console.print("🎬 Starting conversation demo...")
        run_demo_conversation(
            config, 
            show_typing=not fast, 
            delay_between_turns=0.5 if fast else 1.5
        )
        
    except Exception as e:
        console.print(f"❌ Error running demo: {e}")
        raise typer.Exit(1)


@app.command()
def test():
    """Run a quick test conversation."""
    try:
        config = create_debate("Is pineapple on pizza acceptable?", ["optimist", "skeptic"])
        console.print("🧪 Test conversation created successfully!")
        console.print(f"Topic: {config.topic}")
        console.print(f"Mode: {config.mode}")
        console.print(f"Agents: {', '.join([agent.name for agent in config.agents])}")
        console.print("✅ DuoTalk is working correctly!")
        
    except Exception as e:
        console.print(f"❌ Test failed: {e}")
        raise typer.Exit(1)


@app.command()
def interactive():
    """Start an interactive conversation builder."""
    console.print(Panel("🎭 Interactive Conversation Builder", title_align="center"))
    
    # Get topic
    topic = typer.prompt("Enter conversation topic")
    
    # Get mode
    console.print(f"Available modes: {', '.join(ALL_MODES)}")
    mode = typer.prompt("Choose conversation mode", default="roundtable")
    
    if mode not in ALL_MODES:
        console.print(f"❌ Invalid mode. Using 'roundtable' instead.")
        mode = "roundtable"
    
    # Get personas
    console.print(f"Available personas: {', '.join(ALL_PERSONA_NAMES)}")
    personas_input = typer.prompt("Enter persona names (comma-separated)", default="")
    
    if personas_input:
        personas = [p.strip() for p in personas_input.split(",")]
    else:
        personas = None
    
    # Get max turns
    max_turns = typer.prompt("Maximum turns", default=10, type=int)
    
    # Create conversation
    try:
        if mode == "debate":
            config = create_debate(topic, personas, max_turns)
        elif mode == "roundtable":
            config = create_roundtable(topic, personas, max_turns)
        elif mode == "friendly":
            config = create_friendly_chat(topic, personas, max_turns)
        elif mode == "interview":
            config = create_interview(topic, personas[0] if personas else None, personas[1:] if personas and len(personas) > 1 else None, max_turns)
        elif mode == "panel":
            config = create_panel(topic, personas[0] if personas else None, personas[1:] if personas and len(personas) > 1 else None, max_turns)
        elif mode == "socratic":
            config = create_socratic(topic, personas, max_turns)
        else:
            config = create_roundtable(topic, personas, max_turns)
        
        console.print("\n🎉 Conversation created successfully!")
        console.print(f"Topic: {config.topic}")
        console.print(f"Mode: {config.mode}")
        console.print(f"Agents: {', '.join([agent.name for agent in config.agents])}")
        console.print(f"Max turns: {config.max_turns}")
        
    except Exception as e:
        console.print(f"❌ Error creating conversation: {e}")
        raise typer.Exit(1)


@app.command()
def voice(
    topic: str = typer.Argument(..., help="Conversation topic"),
    mode: str = typer.Option("debate", help="Conversation mode"),
    personas: List[str] = typer.Option([], help="Persona names to use"),
    max_turns: int = typer.Option(6, help="Maximum conversation turns"),
):
    """Start a REAL voice conversation using enhanced features or fallback to existing voice runner."""
    
    console.print(Panel(
        "[bold blue]🎙️ Voice Conversation Mode[/bold blue]\n\n"
        "This will start a real voice conversation where AI agents actually speak!\n"
        "Make sure you have:\n"
        "• Google API key in .env file\n"
        "• LiveKit credentials (optional)\n"
        "• Microphone/speakers connected\n\n"
        "Press Ctrl+C to stop the conversation.",
        title="Voice Mode",
        border_style="blue"
    ))
    
    console.print(f"🎙️ Starting voice conversation: {topic}")
    console.print(f"📊 Mode: {mode}")
    
    # Try enhanced features first
    if _enhanced_features:
        try:
            if not personas:
                # Auto-select based on mode
                if mode == "debate":
                    personas = ["optimist", "skeptic"]
                elif mode == "roundtable":
                    personas = ["optimist", "skeptic", "pragmatist", "theorist"]
                else:
                    personas = ["optimist", "skeptic"]
            
            console.print(f"👥 Agents: {personas}")
            console.print(f"🔄 Max turns: {max_turns}")
            console.print("\n🚀 Launching enhanced voice session...")
            
            runner = quick_start(topic, mode=mode, agents=personas, max_turns=max_turns, voice=True)
            sync_run(runner)
            return
            
        except Exception as e:
            console.print(f"[yellow]Enhanced voice features failed: {e}[/yellow]")
            console.print("[yellow]Falling back to basic voice runner...[/yellow]")
    
    # Fallback to existing voice runner
    try:
        from .voice_cli import run_voice_conversation
        
        if not personas:
            if mode == "debate":
                personas = ["Alex Bright", "Quinn Question"]
            else:
                personas = ["Alex Bright", "Sam Skeptic"]
        
        console.print(f"👥 Agents: {personas}")
        console.print(f"🔄 Max turns: {max_turns}")
        console.print("\n🚀 Launching LiveKit voice session...")
        
        success = run_voice_conversation(topic, mode, personas, max_turns)
        if not success:
            raise typer.Exit(1)
            
    except ImportError:
        console.print("[red]❌ Voice functionality not available.[/red]")
        console.print("Make sure LiveKit and voice dependencies are installed.")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Voice conversation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def voice_preset(
    preset: str = typer.Argument(..., help="Preset name"),
    topic: str = typer.Argument(..., help="Conversation topic"),
    max_turns: int = typer.Option(10, help="Maximum conversation turns"),
):
    """Start a voice conversation using a preset configuration."""
    from .voice_cli import run_voice_conversation
    
    # Map presets to modes and personas
    preset_configs = {
        "business": ("roundtable", ["entrepreneur", "analyst", "pragmatist"]),
        "academic": ("debate", ["educator", "scientist"]),
        "creative": ("roundtable", ["creative", "artist", "theorist"]),
        "policy": ("panel", ["analyst", "pragmatist", "theorist"]),
        "debate": ("debate", ["optimist", "skeptic"]),
        "roundtable": ("roundtable", ["optimist", "skeptic", "pragmatist", "theorist"]),
    }
    
    if preset not in preset_configs:
        console.print(f"❌ Unknown preset: {preset}")
        console.print(f"Available presets: {list(preset_configs.keys())}")
        raise typer.Exit(1)
    
    mode, personas = preset_configs[preset]
    
    console.print(Panel(
        f"[bold green]🎙️ Voice {preset.title()} Conversation[/bold green]\n\n"
        f"Topic: {topic}\n"
        f"Mode: {mode}\n"
        f"Personas: {', '.join(personas)}",
        title="Voice Preset",
        border_style="green"
    ))
    
    success = run_voice_conversation(topic, mode, personas, max_turns)
    if not success:
        raise typer.Exit(1)


@app.command()
def interactive():
    """Start an interactive conversation builder session."""
    console.print(Panel(
        "[bold blue]🎙️ Interactive DuoTalk Builder[/bold blue]",
        title="Interactive Mode",
        border_style="blue"
    ))
    
    # Get topic
    topic = Prompt.ask("\n[bold]What would you like the agents to discuss?[/bold]")
    
    # Get mode
    console.print("\n[bold]Available conversation modes:[/bold]")
    for i, mode in enumerate(ALL_MODES, 1):
        mode_info = get_mode(mode)
        console.print(f"  {i}. [cyan]{mode}[/cyan] - {mode_info.description}")
    
    mode_choice = Prompt.ask(
        "\n[bold]Choose a mode[/bold]", 
        choices=[str(i) for i in range(1, len(ALL_MODES) + 1)],
        default="1"
    )
    mode = ALL_MODES[int(mode_choice) - 1]
    
    # Get agents
    console.print(f"\n[bold]Available personas:[/bold]")
    for i, persona in enumerate(ALL_PERSONA_NAMES, 1):
        console.print(f"  {i}. [cyan]{persona}[/cyan]")
    
    use_default = Confirm.ask(f"\nUse default personas for {mode} mode?", default=True)
    
    if use_default:
        personas = []  # Will auto-select based on mode
    else:
        persona_input = Prompt.ask("\nEnter persona numbers (comma-separated, e.g., 1,3,5)")
        persona_indices = [int(x.strip()) - 1 for x in persona_input.split(",")]
        personas = [ALL_PERSONA_NAMES[i] for i in persona_indices if 0 <= i < len(ALL_PERSONA_NAMES)]
    
    # Get settings
    max_turns = int(Prompt.ask("\nMaximum conversation turns", default="15"))
    voice_enabled = Confirm.ask("Enable voice synthesis?", default=True)
    
    # Create and start conversation
    console.print(f"\n[bold green]🚀 Starting {mode} conversation...[/bold green]")
    
    try:
        if voice_enabled and _enhanced_features:
            runner = quick_start(topic, mode=mode, agents=personas, max_turns=max_turns, voice=True)
            sync_run(runner)
        else:
            # Demo mode or fallback
            if mode == "debate":
                config = create_debate(topic, personas or ["optimist", "skeptic"])
            elif mode == "roundtable":
                config = create_roundtable(topic, personas)
            else:
                # Use basic config for other modes
                agents = [get_persona_by_name(p) for p in (personas or ["optimist", "skeptic"])]
                config = ConversationConfig(
                    topic=topic,
                    agents=agents,
                    mode=mode,
                    max_turns=max_turns
                )
            
            asyncio.run(run_demo_conversation(config))
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Conversation interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def info(
    component: Optional[str] = typer.Argument(None, help="Component to show info about (personas, modes, config)")
):
    """Show information about DuoTalk components."""
    
    if component == "personas" or component is None:
        console.print(Panel(
            "[bold blue]👤 Available Personas[/bold blue]",
            title="Personas",
            border_style="blue"
        ))
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Perspective", style="white")
        table.add_column("Role", style="yellow")
        
        for persona in ALL_PERSONAS:
            table.add_row(
                persona.name,
                persona.perspective[:50] + "..." if len(persona.perspective) > 50 else persona.perspective,
                persona.role
            )
        
        console.print(table)
        console.print()
    
    if component == "modes" or component is None:
        console.print(Panel(
            "[bold green]🎭 Available Modes[/bold green]",
            title="Conversation Modes",
            border_style="green"
        ))
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Mode", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Recommended Setup", style="yellow")
        
        for mode_name in ALL_MODES:
            mode_obj = get_mode(mode_name)
            table.add_row(
                mode_name,
                mode_obj.config.description[:60] + "..." if len(mode_obj.config.description) > 60 else mode_obj.config.description,
                f"{mode_obj.config.recommended_agents} agents recommended"
            )
        
        console.print(table)
        console.print()
    
    if component == "config" or component is None:
        console.print(Panel(
            "[bold yellow]⚙️ Configuration Options[/bold yellow]",
            title="Configuration",
            border_style="yellow"
        ))
        
        if _enhanced_features:
            config = DuoTalkConfig()
            
            tree = Tree("DuoTalk Configuration")
            
            # Basic settings
            basic = tree.add("Basic Settings")
            basic.add(f"Max Turns: {config.max_turns}")
            basic.add(f"Turn Timeout: {config.turn_timeout}s")
            basic.add(f"Conversation Delay: {config.conversation_delay}s")
            
            # Voice settings
            voice = tree.add("Voice Settings")
            voice.add(f"Voice Enabled: {config.voice_enabled}")
            voice.add(f"Voice Provider: {config.voice_provider}")
            voice.add(f"Voice Speed: {config.voice_speed}")
            
            # Advanced settings
            advanced = tree.add("Advanced Settings")
            advanced.add(f"Interruptions: {config.interruption_enabled}")
            advanced.add(f"Auto-save: {config.auto_save_conversations}")
            advanced.add(f"Stats Enabled: {config.enable_statistics}")
            
            console.print(tree)
        else:
            console.print("[yellow]Enhanced configuration features not available.[/yellow]")
            console.print("Basic configuration can be done through ConversationConfig parameters.")


@app.command()
def preview(
    topic: str = typer.Argument(..., help="Conversation topic"),
    mode: str = typer.Option("friendly", help="Conversation mode"),
    personas: List[str] = typer.Option([], help="Persona names to use"),
    max_turns: int = typer.Option(15, help="Maximum conversation turns"),
):
    """Preview a conversation configuration without starting it."""
    
    try:
        if _enhanced_features:
            from ..core.builder import ConversationBuilder
            
            builder = ConversationBuilder()
            conversation = builder.with_topic(topic).with_mode(mode).with_max_turns(max_turns)
            
            if personas:
                conversation = conversation.with_personas(*personas)
            else:
                conversation = conversation.with_agents(2)
            
            preview_data = conversation.preview()
            
            console.print(Panel(
                "[bold blue]🔍 Conversation Preview[/bold blue]",
                title="Preview",
                border_style="blue"
            ))
            
            # Create preview table
            table = Table(show_header=False, box=None)
            table.add_column("Property", style="bold cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Topic", preview_data["topic"])
            table.add_row("Mode", preview_data["mode"])
            table.add_row("Agents", ", ".join(preview_data["agents"]))
            table.add_row("Max Turns", str(preview_data["max_turns"]))
            table.add_row("Voice Enabled", "Yes" if preview_data["voice_enabled"] else "No")
            table.add_row("Demo Mode", "Yes" if preview_data["demo_mode"] else "No")
            
            if preview_data["metadata"]:
                table.add_row("Metadata", str(preview_data["metadata"]))
            
            console.print(table)
            console.print()
            
            # Show agent details
            console.print("[bold]Agent Details:[/bold]")
            for agent_name in preview_data["agents"]:
                try:
                    agent = get_persona_by_name(agent_name)
                    console.print(f"  • [cyan]{agent.name}[/cyan]: {agent.perspective}")
                except:
                    console.print(f"  • [cyan]{agent_name}[/cyan]: Custom agent")
            
            console.print()
            start_now = Confirm.ask("Start this conversation now?", default=False)
            
            if start_now:
                voice_mode = Confirm.ask("Enable voice synthesis?", default=True)
                
                console.print(f"\n[bold green]🚀 Starting conversation...[/bold green]")
                
                try:
                    runner = quick_start(
                        topic, 
                        mode=mode, 
                        agents=personas if personas else None, 
                        max_turns=max_turns,
                        voice=voice_mode
                    )
                    sync_run(runner)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Conversation interrupted by user[/yellow]")
                except Exception as e:
                    console.print(f"\n[red]Error: {str(e)}[/red]")
        else:
            # Basic preview without enhanced features
            console.print(Panel(
                "[bold blue]🔍 Basic Conversation Preview[/bold blue]",
                title="Preview",
                border_style="blue"
            ))
            
            table = Table(show_header=False, box=None)
            table.add_column("Property", style="bold cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Topic", topic)
            table.add_row("Mode", mode)
            table.add_row("Personas", ", ".join(personas) if personas else "Default for mode")
            table.add_row("Max Turns", str(max_turns))
            
            console.print(table)
            console.print("\n[yellow]Enhanced preview features not available.[/yellow]")
                
    except Exception as e:
        console.print(f"[red]Error creating preview: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    reset: bool = typer.Option(False, "--reset", help="Reset to default configuration"),
    edit: bool = typer.Option(False, "--edit", help="Edit configuration interactively"),
):
    """Manage DuoTalk configuration."""
    
    if not _enhanced_features:
        console.print("[yellow]Enhanced configuration features not available.[/yellow]")
        console.print("Configuration can be done through ConversationConfig parameters in code.")
        return
    
    try:
        config_obj = DuoTalkConfig()
        
        if reset:
            if Confirm.ask("Reset configuration to defaults?"):
                config_obj.reset_to_defaults()
                console.print("[green]✅ Configuration reset to defaults[/green]")
            return
            
        if edit:
            console.print(Panel(
                "[bold blue]⚙️ Configuration Editor[/bold blue]",
                title="Edit Config",
                border_style="blue"
            ))
            
            # Edit basic settings
            config_obj.max_turns = int(Prompt.ask("Max turns", default=str(config_obj.max_turns)))
            config_obj.turn_timeout = float(Prompt.ask("Turn timeout (seconds)", default=str(config_obj.turn_timeout)))
            config_obj.voice_enabled = Confirm.ask("Enable voice", default=config_obj.voice_enabled)
            config_obj.voice_speed = float(Prompt.ask("Voice speed", default=str(config_obj.voice_speed)))
            config_obj.interruption_enabled = Confirm.ask("Allow interruptions", default=config_obj.interruption_enabled)
            
            config_obj.save()
            console.print("[green]✅ Configuration saved[/green]")
            return
        
        # Show configuration (default)
        console.print(Panel(
            "[bold blue]⚙️ Current Configuration[/bold blue]",
            title="Configuration",
            border_style="blue"
        ))
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Description", style="yellow")
        
        # Add configuration rows
        settings = [
            ("max_turns", config_obj.max_turns, "Maximum conversation turns"),
            ("turn_timeout", f"{config_obj.turn_timeout}s", "Timeout for each turn"),
            ("voice_enabled", config_obj.voice_enabled, "Voice synthesis enabled"),
            ("voice_provider", config_obj.voice_provider, "Voice synthesis provider"),
            ("voice_speed", config_obj.voice_speed, "Voice playback speed"),
            ("interruption_enabled", config_obj.interruption_enabled, "Allow interruptions"),
            ("conversation_delay", f"{config_obj.conversation_delay}s", "Delay between turns"),
            ("auto_save", config_obj.auto_save_conversations, "Auto-save conversations"),
            ("statistics", config_obj.enable_statistics, "Enable statistics tracking"),
        ]
        
        for setting, value, description in settings:
            table.add_row(setting, str(value), description)
        
        console.print(table)
        
        console.print(f"\n[dim]Config file: {config_obj.config_file}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
