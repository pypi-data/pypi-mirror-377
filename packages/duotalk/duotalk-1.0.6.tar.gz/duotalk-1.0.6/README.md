# DuoTalk 🎭

**Advanced Multi-Agent Voice Conversation System**

DuoTalk is a comprehensive Python package for creating engaging multi-agent voice conversations with customizable personas, conversation modes, and easy integration capabilities. Built on top of LiveKit and Google Gemini, it provides a powerful yet simple API for generating dynamic conversations between AI agents with distinct personalities.

## 🌟 Features

- **🎭 Rich Persona Library**: 14+ pre-defined personas (Optimist, Skeptic, Pragmatist, etc.)
- **🗣️ Multiple Conversation Modes**: Debate, Roundtable, Interview, Panel, Socratic, and more
- **🎙️ Voice Integration**: Full voice synthesis using Google Gemini's native audio
- **⚡ Easy Setup**: Simple pip installation and intuitive API
- **🔧 Highly Customizable**: Create custom personas, modes, and conversation flows
- **📊 Analytics**: Built-in conversation metrics and performance tracking
- **🖥️ CLI Interface**: Command-line tool for quick conversations
- **📝 Conversation Logging**: Automatic conversation transcription and analysis
- **🎯 Multiple Use Cases**: Education, brainstorming, testing, entertainment

## 🚀 Quick Start

### Installation

```bash
pip install duotalk
```

Or using uv:
```bash
uv add duotalk
```
# DuoTalk 🎭

Advanced Multi‑Agent Voice Conversation System

DuoTalk lets you create engaging conversations between AI agents with distinct personas across multiple modes (debate, roundtable, interview, and more). Use the Python API for full control or the CLI to get started in seconds. Optional YouTube summarization turns any video into a spoken, natural summary.

## 🌟 Highlights

- 🎭 Personas library: 14+ ready-to-use personas (optimist, skeptic, pragmatist, theorist, educator, scientist, artist, and more)
- 💬 Conversation modes: friendly, debate, roundtable, interview, panel, socratic
- 🧪 Quick start helpers: one‑liners like `quick_debate()` and `quick_roundtable()`
- 🧱 Builder API: fluent, composable setup with `ConversationBuilder`
- 🖥️ CLI: start demos, list personas/modes, summarize YouTube videos
- 🎬 YouTube summarizer: AI‑powered short or detailed summaries, optional voice
- 🔊 Voice ready: integrates with DuoTalk’s voice runner (LiveKit optional)
- 🧩 Typed APIs: shipped with `py.typed` for great editor/IDE support

## 🚀 Installation

```bash
pip install duotalk
```

Optional extras for YouTube summaries:

```bash
pip install yt-dlp requests google-generativeai
```

## 🔑 Environment

Create a `.env` (or export env vars) for optional features:

```env
# For YouTube summarization with Google Gemini
GOOGLE_API_KEY=your_google_api_key   # or GEMINI_API_KEY

# For real-time voice via LiveKit (optional)
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
```

## 🧭 Quick Start (Python)

Use quick helpers for the fastest path:

```python
import asyncio
from duotalk import quick_debate, quick_roundtable

async def main():
    # Debate mode (optimist vs skeptic by default)
    runner = quick_debate("Should AI replace human creativity?", max_turns=12, voice=False)
    await runner.start()

    # Roundtable with four personas
    runner = quick_roundtable("Future of renewable energy", max_turns=10, voice=False)
    await runner.start()

asyncio.run(main())
```

Prefer a fluent Builder:

```python
from duotalk import conversation

runner = (conversation()
    .with_topic("Climate change solutions")
    .with_mode("roundtable")
    .with_personas("pragmatist", "theorist", "skeptic")
    .with_max_turns(10)
    .with_voice_enabled(False)  # set True when LiveKit voice is configured
    .build_and_start())

# Start the conversation
import asyncio
asyncio.run(runner.start())
```

## 🖥️ CLI Usage

The CLI bundles common workflows. Run `duotalk --help` for all options.

```bash
# Demo a conversation in the terminal
duotalk demo "Pineapple on pizza" --mode debate --max-turns 6

# Start (create config) for any mode
duotalk start "AI ethics in hiring" --mode roundtable --personas optimist,skeptic,analyst

# Presets
duotalk preset business "Quarterly planning"
duotalk preset academic "The role of peer review"
duotalk preset creative "Designing for delight"
duotalk preset policy "AI regulation roadmap"

# Explore available options
duotalk list-personas
duotalk list-modes

# Interactive builder
duotalk interactive

# YouTube summarization (short or detailed via prompt)
duotalk summarize "https://www.youtube.com/watch?v=VIDEO_ID" --voice --save
```

Commands provided by the CLI:

- `start` – build a conversation config for a mode/personas
- `demo` – run a text‑mode demo in the terminal
- `preset` – business, academic, creative, policy, debate, roundtable, interview, panel
- `summarize` – summarize a YouTube video (optional voice)
- `list-personas` – list all persona names
- `list-modes` – list all conversation modes
- `interactive` – step‑by‑step guided setup

## 🎬 YouTube Summaries (Python)

Two options are available:

1) High‑level convenience

```python
import asyncio
from duotalk.core.youtube_summarizer import summarize_youtube_video

async def main():
    result = await summarize_youtube_video(
        url="https://www.youtube.com/watch?v=VIDEO_ID",
        use_voice=False,
        summary_mode="detailed"  # or "short"
    )
    if result["success"]:
        print(result["summary"])  # natural, speech‑friendly text

asyncio.run(main())
```

2) CLI

```bash
duotalk summarize "https://www.youtube.com/watch?v=VIDEO_ID" --voice --save
```

Notes:
- Requires `yt-dlp` and `requests` for transcript fetching.
- Provide `GOOGLE_API_KEY` (or `GEMINI_API_KEY`) to enable AI summaries.
- Voice playback is optional and depends on your voice setup.

## � Personas

Available persona names include:

`optimist`, `pessimist`, `pragmatist`, `theorist`, `skeptic`, `enthusiast`, `mediator`, `analyst`, `creative`, `logical thinker`, `educator`, `entrepreneur`, `scientist`, `artist`

Pick any by name in the Builder, quick helpers, or CLI.

## 🧩 Conversation Modes

- `friendly` – collaborative discussion
- `debate` – structured argument with opposing viewpoints
- `roundtable` – multi‑participant exchange
- `interview` – interviewer with one or more interviewees
- `panel` – moderator plus subject‑matter experts
- `socratic` – question‑driven exploration

## 🔊 Voice

The package supports voice‑enabled runs via DuoTalk’s voice runner. You can work in demo (text) mode without any voice setup. To enable voice, configure your audio stack (e.g., LiveKit credentials) and set `.with_voice_enabled(True)` or pass `voice=True` to quick helpers. The CLI will indicate when a voice session is required.

## � Python API Surface (at a glance)

- Quick helpers: `quick_debate`, `quick_roundtable`, `quick_friendly`, `quick_interview`, `quick_panel`, `quick_socratic`, `quick_start`
- Builder: `ConversationBuilder` and `conversation()`
- Convenience creators: `create_debate`, `create_roundtable`, `create_friendly_chat`, `create_interview`, `create_panel`, `create_socratic`, `create_random_conversation`, presets (business/academic/creative/policy)
- YouTube: `summarize_youtube_video`, `validate_youtube_url`, `extract_video_id`

## 🐍 Requirements

- Python 3.8+
- Optional: `yt-dlp`, `requests`, `google-generativeai` for YouTube summaries
- Optional: voice runtime (e.g., LiveKit) if you enable audio

## 📄 License

MIT – see `LICENSE`.

—

Build dynamic agent conversations, fast. If you have ideas for new personas or modes, PRs and issues are welcome.
- **Exponential backoff retry logic** for YouTube API rate limits (429 errors)
- **Progressive wait times** with intelligent retry strategies
- **Comprehensive logging** for debugging and monitoring
- **Graceful degradation** when services are temporarily unavailable

### 🐛 Bug Fixes
- **Fixed single agent chat mode** - no more unwanted multi-agent conversations
- **Improved error handling** across all conversation types
- **Enhanced session management** for better stability

## 🏗️ Code Architecture
![image](https://github.com/user-attachments/assets/e3a6fa09-b5da-45c5-b97d-5621f0255769)

## 📋 Requirements

> **Prerequisites for running DuoTalk**

- 🐍 **Python 3.8+**
- 🔗 **[LiveKit Agents SDK](https://github.com/livekit/agents)**
- 🧠 **[Google Gemini API](https://aistudio.google.com/)**

## 🚀 Quick Setup

### 1️⃣ Clone & Navigate
```bash
git clone https://github.com/AbhyudayPatel/DuoTalk.git
cd DuoTalk
```

### 2️⃣ Install Dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ Environment Configuration
Create a `.env` file in your project root:
```env
# Add your Google Gemini API key
GOOGLE_API_KEY=your_gemini_api_key_here
```

> 💡 **Tip:** Get your API key from [Google AI Studio](https://aistudio.google.com/)

## 🎮 Usage

### 🏃‍♂️ Starting DuoTalk
```bash
# For 2 agents (friendly/discussion/debate):
python dual_voice_agents.py console
# For 4 agents (roundtable/friendly/debate):
python four_agents_duotalk.py console
```

### 📝 Interactive Setup

#### Step 1: 🎯 Choose Your Topic
```
Enter the topic for the conversation: _
```
**Examples:**
- `The future of AI and robotics`
- `Climate change solutions`
- `Space exploration and Mars colonization`
- `The ethics of genetic engineering`

#### Step 2: 🎭 Select Conversation Mode
```
Select conversation mode:
1. Friendly discussion (2 agents)
2. Debate format (2 agents)
3. Roundtable discussion (4 agents)
Enter your choice (1, 2, or 3): _
```

| Mode | 🤝 Friendly Discussion | ⚔️ Debate Format | 🌀 Roundtable |
|------|------------------------|-------------------|-------------------|
| **Style** | Collaborative & supportive | Opposing viewpoints | Diverse perspectives |
| **Tone** | Encouraging dialogue | Direct & contrary | Dynamic & engaging |
| **Personas** | Agent1 & Agent2 | Optimist vs Skeptic | Optimist, Skeptic, Pragmatist, Theorist |
| **Voices** | Puck & Charon | Puck & Charon | Puck & Charon (multiple roles) |

## ⚙️ Configuration

<details>
<summary>🔧 <strong>Customization Options</strong></summary>

| Setting | Default | How to Change |
|---------|---------|---------------|
| 🔄 **Max Turns** | 12 turns | Modify `max_turns` in `ConversationState` |
| 🎤 **Agent Voices** | Puck & Charon | Update voice parameters in code |
| 🤖 **AI Model** | `gemini-2.5-flash-preview-native-audio-dialog` | Change model string |
| 💬 **Response Length** | One-line responses | Modify instructions in `DualPersonaAgent` |

</details>


### 🧩 Core Components

| Component | 🎯 Purpose |
|-----------|------------|
| `ConversationState` | 📊 Manages conversation state and settings |
| `DualPersonaAgent` | 🎭 Main agent class with dual persona support |
| `get_conversation_mode()` | 📝 Handles user input for conversation mode |
| `run_friendly_conversation()` | 🤝 Manages friendly discussion flow |
| `run_debate_conversation()` | ⚔️ Manages debate flow with optimist/skeptic roles |
| `safe_generate_reply()` | 🛡️ Handles responses with error handling and retries |

## 🛡️ Error Handling & Reliability

DuoTalk is built with **enterprise-grade reliability**:

<details>
<summary>🔍 <strong>Comprehensive Error Management</strong></summary>

| Feature | Description |
|---------|-------------|
| 📊 **Session Health Monitoring** | Real-time health checks |
| 🔄 **Automatic Retries** | Smart retry logic for failed responses |
| 🧹 **Graceful Cleanup** | Proper resource management |
| 📝 **Detailed Logging** | Comprehensive debugging information |
| ⏱️ **Timeout Protection** | Prevents hanging operations |
| 🔧 **Recovery Mechanisms** | Automatic error recovery |

</details>


## 📄 License

**MIT License** - See LICENSE file for details

*Experience the future of AI conversation today!*

</div>
