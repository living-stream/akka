English | [简体中文](README.md)

# 🍊 Akka - AI-Powered Social Media Operation Tool

<p align="center">
  <img src="akka.png" alt="Akka" width="600">
</p>

<p align="center">
  <strong>Complete the full loop from topic selection to publishing with a single sentence</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Node.js-18+-green.svg" alt="Node.js">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/AI-Agent-orange.svg" alt="AI Agent">
</p>

---

## 📖 Table of Contents

- [🍊 Akka - AI-Powered Social Media Operation Tool](#-akka---ai-powered-social-media-operation-tool)
  - [🎯 Core Capabilities](#-core-capabilities)
  - [🚀 Quick Start](#-quick-start)
  - [✨ Features](#-features)
  - [📖 User Guide](#-user-guide)
  - [📂 Project Structure](#-project-structure)
  - [🔌 API Endpoints](#-api-endpoints)
  - [🙏 Acknowledgments](#-acknowledgments)
  - [📄 License](#-license)

---

## 🎯 Core Capabilities

Akka (**A**utomated **K**nowledge & **K**ontent **A**ssistant) is an open-source **AI Social Media Operation Assistant** that achieves a complete loop from topic selection to publishing through **browser automation**, **material search**, **content generation**, and **content publishing**.

Just one instruction, Akka automatically completes:

| Capability | Description |
|------------|-------------|
| 🤖 **Automated Browser Operations** | Search competitors, collect materials, view data |
| 🔍 **Automated Material Search** | Intelligently search and organize relevant materials |
| 🎨 **Automated Content Generation** | Outline planning, copywriting creation, image generation |
| 📤 **Automated Publishing** | Automatically publish content |

**From topic planning to scheduled publishing, let AI Agent boost your social media operation efficiency by 10x, truly achieving "what you think is what you get".**

## 🚀 Quick Start

### 3-Step Launch

```bash
# 1. Clone the project
git clone https://github.com/living-stream/akka.git
cd akka

# 2. Configure API Key
cp config.example.yaml config/config.yaml
# Edit config/config.yaml and fill in your OpenAI API Key

# 3. Start
./start.sh
```

Visit http://localhost:3000 to get started!

### Prerequisites

- Python 3.10+
- Node.js 18+
- Chrome Browser

### Configuration

**Option 1: Environment Variables (Recommended)**
```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # optional
```

**Option 2: Configuration File**
```yaml
llm:
  provider: "openai"
  api_key: "your-api-key"
  model: "gpt-4o"
```

## ✨ Features

### 🖥️ Web Interface

| Feature | Description |
|---------|-------------|
| 💬 Smart Chat | Streaming conversation experience with thinking process display |
| 📝 Workspace | Note card display, image thumbnail preview, click to expand details |
| ⏰ Scheduled Tasks | Create and manage scheduled tasks with real-time status tracking |
| ⚙️ Settings | User persona and memory configuration |

### 🤖 Intelligent Content Generation

- **Fully Automated Creation**: Automatically generate complete Xiaohongshu (Little Red Book) image-text notes from a single instruction
- **Three-stage Generation Flow**: Outline planning → Copywriting creation → Image generation
- **Image Generation**: Automatically generate supporting images, supporting multiple images

### 📊 Skill System

| Skill | Function |
|-------|----------|
| competitor-benchmarking | Competitor benchmarking analysis |
| content-creation | Content generation (including browser information collection) |
| content-review | Content review analysis |
| inspiration-hunting | Inspiration collection |
| scheduled-task | Scheduled task management |

### 🌐 Browser Automation

- **Information Collection**: Search competitors, collect store information, view account data
- **Platform Operations**: Support for Xiaohongshu, Dianping and other platforms

### 🧠 Intelligent Control

- **User Isolation**: Each user has independent soul.md, memory.md, workspace
- **Conversation Memory**: Automatically save conversation history, auto-compress when exceeding 20 entries
- **Task Lock**: Ensure only one task executes at a time for the same user

## 📖 User Guide

### Web Interface

1. **Chat Page** - Chat with AI assistant, give task instructions
2. **Workspace** - View generated note content, click cards to expand details
3. **Tasks Page** - Manage scheduled tasks, view task status
4. **Settings Page** - Configure user persona and memory

### Command Line Client

**Execute Task**:
```bash
python master/client.py --uid test_user run "Help me analyze competitors in the coffee sector"
```

**More Examples**:
```bash
# Create scheduled task
python master/client.py --uid test_user run "Help me create a task to publish a coffee post tomorrow at 12pm"

# Generate note
python master/client.py --uid test_user run "Write a note about pour-over coffee"

# Competitor analysis
python master/client.py --uid test_user run "Search for viral notes in the coffee sector on Xiaohongshu, analyze their titles and cover characteristics"
```

**Health Check**:
```bash
python master/client.py health
```

## 📂 Project Structure

```
auto_ven/
├── master/                    # Backend core
│   ├── server.py              # FastAPI server
│   ├── client.py              # Command line client
│   ├── controller.py          # CoreController core logic
│   ├── scheduler.py           # Scheduled task scheduler
│   └── skills/
│       └── definitions/       # Skill definitions directory
├── web/                       # Next.js frontend
│   ├── app/                   # Page routes
│   │   ├── chat/              # Chat page
│   │   ├── workspace/         # Workspace page
│   │   ├── tasks/             # Tasks page
│   │   └── settings/          # Settings page
│   ├── components/            # UI components
│   │   ├── ui/                # Basic components
│   │   ├── chat/              # Chat components
│   │   ├── workspace/         # Workspace components
│   │   └── tasks/             # Task components
│   ├── hooks/                 # React Hooks
│   ├── store/                 # Zustand state management
│   └── lib/                   # Utility functions
├── users/                     # User data directory
│   └── {uid}/                 # User-specific directory
│       ├── soul.md            # User persona
│       ├── memory.md          # Long-term memory
│       ├── conversation.json  # Conversation history
│       ├── tasks.json         # Scheduled tasks
│       └── workspace/         # Workspace directory
│           └── {note_folder}/
│               ├── copywriting.md  # Note copywriting
│               ├── outline.md      # Outline
│               └── images/         # Images
├── agentic_tool/              # Agent tools
│   ├── browser_use_agent/     # Browser automation
│   └── note_generate_agent/   # Content generation
├── llm/                       # LLM model factory
├── config/                    # Configuration files
└── start.sh                   # One-click startup script
```

## 🔌 API Endpoints

### Conversation

| Method | Path | Description |
|--------|------|-------------|
| POST | `/run` | Execute task (streaming response) |
| GET | `/conversation/{uid}` | Get conversation history |
| DELETE | `/conversation/{uid}` | Clear conversation history |

### Workspace

| Method | Path | Description |
|--------|------|-------------|
| GET | `/workspace/{uid}` | Get note list |
| GET | `/workspace/{uid}/notes/{path}` | Get note content |
| GET | `/workspace/{uid}/images/{folder}/{name}` | Get note images |

### Scheduled Tasks

| Method | Path | Description |
|--------|------|-------------|
| POST | `/schedule` | Create scheduled task |
| GET | `/tasks/{uid}` | Get task list |
| DELETE | `/tasks/{uid}/{task_id}` | Cancel task |

### User

| Method | Path | Description |
|--------|------|-------------|
| GET | `/user/{uid}/profile` | Get user profile |
| PUT | `/user/{uid}/soul` | Update user persona |
| PUT | `/user/{uid}/memory` | Update user memory |

## 🙏 Acknowledgments

Akka is built on the following excellent open-source projects:

- **[browser-use](https://github.com/browser-use/browser-use)** - Browser automation framework
- **[LangChain](https://github.com/langchain-ai/langchain)** - LLM application development framework
- **[LangGraph](https://github.com/langchain-ai/langgraph)** - Multi-agent orchestration framework
- **[FastAPI](https://github.com/tiangolo/fastapi)** - Modern Python web framework
- **[Next.js](https://github.com/vercel/next.js)** - React full-stack framework

Thanks to the developers and communities behind these projects!

## 📄 License

MIT License
