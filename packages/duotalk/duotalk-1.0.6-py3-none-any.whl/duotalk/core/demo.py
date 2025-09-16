"""
Demo conversation runner that simulates conversations without requiring LiveKit.
Perfect for testing and demonstration purposes.
"""

import asyncio
import random
import time
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.table import Table

from .config import ConversationConfig, AgentConfig
from ..modes import get_mode


class DemoConversationRunner:
    """
    Demo conversation runner that simulates conversations.
    Shows how conversations would work without requiring LiveKit setup.
    """
    
    def __init__(self, config: ConversationConfig):
        self.config = config
        self.console = Console()
        self.mode = get_mode(config.mode)
        self.turn_count = 0
        self.conversation_history = []
        
    async def run_demo(self, show_typing: bool = True, delay_between_turns: float = 2.0):
        """Run a demo conversation simulation."""
        self.console.print(Panel(
            f"🎭 Demo Conversation: {self.config.topic}",
            title="DuoTalk Demo Mode",
            title_align="center"
        ))
        
        # Show participants
        participants_table = Table(title="Participants")
        participants_table.add_column("Agent", style="cyan")
        participants_table.add_column("Persona", style="magenta")
        participants_table.add_column("Role", style="green")
        
        for agent in self.config.agents:
            participants_table.add_row(agent.name, agent.persona, agent.role)
        
        self.console.print(participants_table)
        self.console.print()
        
        # Start conversation
        self.console.print("🚀 Starting conversation simulation...\n")
        
        for turn in range(self.config.max_turns):
            if not self.mode.should_continue(turn, {"max_turns": self.config.max_turns}):
                break
                
            # Determine speaking agent
            agent_index = self.mode.get_turn_order(self.config.agents, turn)
            agent = self.config.agents[agent_index]
            
            # Generate response
            response = self._generate_demo_response(agent, turn)
            
            # Show typing effect
            if show_typing:
                with Live(refresh_per_second=10) as live:
                    typing_text = Text()
                    typing_text.append(f"{agent.name}: ", style="bold cyan")
                    
                    for i, char in enumerate(response):
                        typing_text.append(char)
                        live.update(Panel(typing_text, title=f"Turn {turn + 1}"))
                        await asyncio.sleep(0.05)  # Typing speed
                    
                    await asyncio.sleep(0.5)  # Pause after finishing
            else:
                self.console.print(Panel(
                    f"[bold cyan]{agent.name}:[/bold cyan] {response}",
                    title=f"Turn {turn + 1}"
                ))
            
            self.conversation_history.append({
                "turn": turn + 1,
                "agent": agent.name,
                "persona": agent.persona,
                "response": response
            })
            
            # Delay between turns
            await asyncio.sleep(delay_between_turns)
        
        # Show conversation summary
        self._show_summary()
    
    def _generate_demo_response(self, agent: AgentConfig, turn: int) -> str:
        """Generate a demo response based on agent persona and conversation context."""
        
        # Get mode-specific instructions
        instructions = self.mode.get_agent_instructions(
            agent_index=self.config.agents.index(agent),
            total_agents=len(self.config.agents),
            context={"topic": self.config.topic, "turn": turn}
        )
        
        # Persona-specific response patterns
        persona_responses = {
            "optimist": [
                f"I'm really excited about {self.config.topic}! The possibilities are endless.",
                f"Looking at {self.config.topic}, I see so many opportunities for positive change.",
                f"This is fascinating! {self.config.topic} could really transform how we think about things.",
                f"I believe {self.config.topic} will lead to amazing breakthroughs!",
                f"The future looks bright when it comes to {self.config.topic}."
            ],
            "skeptic": [
                f"I have some serious concerns about {self.config.topic}. We need to be careful.",
                f"Hold on, let's think critically about {self.config.topic}. What are the risks?",
                f"I'm not convinced that {self.config.topic} is as straightforward as it seems.",
                f"We should question our assumptions about {self.config.topic}.",
                f"What evidence do we have that {self.config.topic} will actually work?"
            ],
            "pragmatist": [
                f"Looking at {self.config.topic} practically, here's what we need to consider...",
                f"For {self.config.topic} to work, we need concrete steps and realistic timelines.",
                f"Let's focus on actionable solutions for {self.config.topic}.",
                f"The real question is: how do we implement {self.config.topic} effectively?",
                f"I think we need a balanced approach to {self.config.topic} that considers all stakeholders."
            ],
            "theorist": [
                f"From a theoretical perspective, {self.config.topic} raises fascinating questions.",
                f"If we consider the underlying principles of {self.config.topic}...",
                f"The conceptual framework around {self.config.topic} is quite complex.",
                f"I'd like to explore the philosophical implications of {self.config.topic}.",
                f"There's an interesting paradigm shift happening with {self.config.topic}."
            ],
            "scientist": [
                f"Based on current research, {self.config.topic} shows promising indicators.",
                f"The data suggests that {self.config.topic} has significant potential.",
                f"We need more empirical evidence to fully understand {self.config.topic}.",
                f"My analysis of {self.config.topic} indicates several key variables to consider.",
                f"From a scientific standpoint, {self.config.topic} requires rigorous testing."
            ],
            "entrepreneur": [
                f"I see huge market opportunities in {self.config.topic}!",
                f"The business model for {self.config.topic} could be revolutionary.",
                f"How can we scale {self.config.topic} and make it profitable?",
                f"Investors would be very interested in {self.config.topic} right now.",
                f"The competitive landscape for {self.config.topic} is wide open."
            ],
            "creative": [
                f"Imagine if we approached {self.config.topic} from a completely different angle...",
                f"What if {self.config.topic} could inspire entirely new forms of expression?",
                f"I envision {self.config.topic} as a canvas for innovation and creativity.",
                f"The artistic possibilities with {self.config.topic} are limitless!",
                f"Let's think outside the box about {self.config.topic}."
            ],
            "educator": [
                f"From an educational perspective, {self.config.topic} could transform learning.",
                f"We need to consider how {self.config.topic} impacts students and teachers.",
                f"The pedagogical implications of {self.config.topic} are significant.",
                f"How can we use {self.config.topic} to improve educational outcomes?",
                f"I think {self.config.topic} requires careful curriculum integration."
            ]
        }
        
        # Get responses for this persona, with fallback
        responses = persona_responses.get(agent.persona, [
            f"That's an interesting point about {self.config.topic}.",
            f"I have some thoughts on {self.config.topic} to share.",
            f"Let me add my perspective on {self.config.topic}.",
            f"Here's how I see {self.config.topic}...",
            f"I'd like to contribute to this discussion about {self.config.topic}."
        ])
        
        # Add some contextual variation based on turn
        if turn == 0:
            # Opening statements
            return f"Hello everyone! {random.choice(responses)}"
        elif turn >= self.config.max_turns - 2:
            # Closing thoughts
            return f"To wrap up my thoughts on {self.config.topic}: {random.choice(responses)}"
        else:
            # Build on previous conversation
            if self.conversation_history:
                last_speaker = self.conversation_history[-1]["agent"]
                return f"Building on what {last_speaker} said, {random.choice(responses)}"
            else:
                return random.choice(responses)
    
    def _show_summary(self):
        """Show conversation summary."""
        self.console.print("\n" + "="*60)
        self.console.print(Panel(
            "🎯 Conversation Complete!",
            title="Demo Summary",
            title_align="center"
        ))
        
        # Statistics
        stats_table = Table(title="Conversation Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Total Turns", str(len(self.conversation_history)))
        stats_table.add_row("Topic", self.config.topic)
        stats_table.add_row("Mode", self.config.mode)
        stats_table.add_row("Participants", str(len(self.config.agents)))
        
        self.console.print(stats_table)
        
        # Participation breakdown
        participation = {}
        for entry in self.conversation_history:
            agent = entry["agent"]
            participation[agent] = participation.get(agent, 0) + 1
        
        part_table = Table(title="Participation")
        part_table.add_column("Agent", style="cyan")
        part_table.add_column("Turns", style="green")
        part_table.add_column("Percentage", style="yellow")
        
        total_turns = len(self.conversation_history)
        for agent, turns in participation.items():
            percentage = (turns / total_turns * 100) if total_turns > 0 else 0
            part_table.add_row(agent, str(turns), f"{percentage:.1f}%")
        
        self.console.print(part_table)
        
        self.console.print("\n💡 This was a demo simulation. To run actual voice conversations,")
        self.console.print("   configure LiveKit credentials and use ConversationRunner!")


def run_demo_conversation(config: ConversationConfig, **kwargs):
    """Run a demo conversation synchronously."""
    runner = DemoConversationRunner(config)
    asyncio.run(runner.run_demo(**kwargs))
