# Mochi Coco 🍡

```bash
.-===-.
|[:::]|
`-----´
```

A beautiful, feature-rich CLI chat application for interacting with LLMs via Ollama with streaming responses, session persistence, and markdown rendering.

## Installation

```bash
pip install mochi-coco
```

## Quick Start

1. Make sure you have [Ollama](https://ollama.com) running locally
2. Pull a model: `ollama pull gpt-oss:20b`
3. Start chatting:

```bash
mochi-coco
```

## Features

- 🚀 **Streaming responses** - Real-time chat with immediate feedback
- 💾 **Session persistence** - Your conversations are automatically saved in the terminal's directory and resumable
- 🎨 **Rich markdown rendering** - Beautiful formatting with syntax highlighting and toggle rendering mid session
- 🔄 **Model switching** - Change models mid-conversation
- ✏️ **Message editing** - Edit previous messages and start from there
- 🧠 **Thinking blocks** - Toggle display of model reasoning (when supported by model + only in markdown mode)
- 📋 **Session management** - Switch between different chat sessions
- 🎛️ **Interactive menus** - Easy-to-use command interface with clear instructions
- ⚡ **Background summarization** - Automatic conversation summaries
- 📝 **System Prompts** - Drop `*.md` or `*.txt` files into the `system_prompts` folder in the root directory of the terminal to use as system prompts.

## Commands

While chatting, you can use these commands:

- `/menu` - Open the main menu with all options
  - `/chats` - Switch between existing sessions or create new ones
  - `/models` - Change the current model
  - `/markdown` - Toggle markdown rendering on/off
  - `/thinking` - Toggle thinking blocks display
  - `/system` - Change system prompt during chat session
- `/edit` - Edit a previous message and continue from there
- `/exit` or `/quit` - Exit the application

## Usage

### Basic Chat
```bash
mochi-coco
```

### Custom Ollama Host
```bash
mochi-coco --host http://localhost:11434
```

### Example Session
```bash
$ mochi-coco
╭──────────────────────────────────────── 🍡 Welcome to Mochi-Coco! ─────────────────────────────────────────╮
│                                                                                                            │
│  🤖 AI Chat with Style                                                                                     │
│                                                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─────────────────────────────────────────── 💬 Previous Sessions ───────────────────────────────────────────╮
│                                                                                                            │
│ ┏━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓             │
│ ┃ #   ┃ Session ID   ┃ Model                ┃ Preview                             ┃ Messages ┃             │
│ ┡━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩             │
│ │ 1   │ 241d72d985   │ gpt-oss:20b          │ Who was the first Avenger in the    │    2     │             │
│ │     │              │                      │ MCU?                                │          │             │
│ │ 2   │ c1def24fa7   │ gpt-oss:20b          │ Hi                                  │    2     │             │
│ └─────┴──────────────┴──────────────────────┴─────────────────────────────────────┴──────────┘             │
│                                                                                                            │
│ 💡 Options:                                                                                                │
│ • 📝 Select session (1-2)                                                                                  │
│ • 🆕 Type 'new' for new chat                                                                               │
│ • 🗑️ Type '/delete <number>' to delete session                                                             │
│ • 👋 Type 'q' to quit                                                                                      │
│                                                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice: new
╭─ 🤖 Available Models ──────────────────────────────────────────────────────────────────────────────────────╮
│ ╭─────┬───────────────────────────┬──────────────┬─────────────────┬──────────┬───────╮                    │
│ │ #   │ Model Name                │    Size (MB) │ Family          │ Max. Cxt │ Tools │                    │
│ ├─────┼───────────────────────────┼──────────────┼─────────────────┼──────────┼───────┤                    │
│ │ 1   │ gpt-oss:20b               │      13141.8 │ gptoss          │   131072 │  Yes  │                    │
│ │ 2   │ qwen3:14b                 │       8846.5 │ qwen3           │    40960 │  Yes  │                    │
│ │ 3   │ qwen3:latest              │       4983.3 │ qwen3           │    40960 │  Yes  │                    │
│ │ 4   │ qwen3:30b                 │      17697.0 │ qwen3moe        │   262144 │  Yes  │                    │
│ │ 5   │ llama3.2:latest           │       1925.8 │ llama           │   131072 │  Yes  │                    │
│ │ 6   │ qwen3-coder:latest        │      17697.0 │ qwen3moe        │   262144 │  No   │                    │
│ │ 7   │ mistral-small3.2:latest   │      14474.3 │ mistral3        │   131072 │  Yes  │                    │
│ ╰─────┴───────────────────────────┴──────────────┴─────────────────┴──────────┴───────╯                    │
│                                                                                                            │
│ 💡 Options:                                                                                                │
│ • 🔢 Select model (1-7)                                                                                    │
│ • 👋 Type 'q' to quit                                                                                      │
│                                                                                                            │
│ ⚠️ ATTENTION: Max. Cxt. is only supported context length not set.                                          │
│ 💡 Open Ollama application to set default context length!                                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice: 1
╭──────────────────────────────────────────── Markdown Rendering ────────────────────────────────────────────╮
│ 📝 Enable markdown formatting for responses?                                                               │
│ This will format code blocks, headers, tables, etc.                                                        │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Enable markdown? [y/n] (y): y
╭────────────────────────────────────────── Thinking Block Display ──────────────────────────────────────────╮
│ 🤔 Show model's thinking process in responses?                                                             │
│ This will display thinking blocks as formatted quotes.                                                     │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Show thinking blocks? [y/n] (n): y
╭─ 🔧 System Prompts ────────────────────────────────────────────────────────────────────────────────────────╮
│ ╭─────┬───────────────────┬────────────────────────────────────────┬────────────╮                          │
│ │ #   │ Filename          │ Preview                                │ Word Count │                          │
│ ├─────┼───────────────────┼────────────────────────────────────────┼────────────┤                          │
│ │ 1   │ AGENT.md          │ # Persona You are a 00-agent of the... │         58 │                          │
│ │ 2   │ system_prompt.txt │ You are a helpful assistant.           │          5 │                          │
│ ╰─────┴───────────────────┴────────────────────────────────────────┴────────────╯                          │
│                                                                                                            │
│ 💡 Options:                                                                                                │
│ • 📝 Select system prompt (1-2)                                                                            │
│ • 🆕 Type 'no' for no system prompt                                                                        │
│ • 🗑️ Type '/delete <number>' to delete a system prompt                                                     │
│ • 👋 Type 'q' to quit                                                                                      │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice: no
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 💡 Continuing without system prompt...                                                                     │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Info ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ The current model 'gpt-oss:20b' doesn't support structured summarization. Please select a compatible model │
│ to use for generating conversation summaries.                                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ 🤖 Available Models ──────────────────────────────────────────────────────────────────────────────────────╮
│ ╭─────┬───────────────────────────┬──────────────┬─────────────────┬──────────┬───────╮                    │
│ │ #   │ Model Name                │    Size (MB) │ Family          │ Max. Cxt │ Tools │                    │
│ ├─────┼───────────────────────────┼──────────────┼─────────────────┼──────────┼───────┤                    │
│ │ 1   │ qwen3:latest              │       4983.3 │ qwen3           │    40960 │  Yes  │                    │
│ │ 2   │ llama3.2:latest           │       1925.8 │ llama           │   131072 │  Yes  │                    │
│ │ 3   │ qwen3-coder:latest        │      17697.0 │ qwen3moe        │   262144 │  No   │                    │
│ │ 4   │ mistral-small3.2:latest   │      14474.3 │ mistral3        │   131072 │  Yes  │                    │
│ ╰─────┴───────────────────────────┴──────────────┴─────────────────┴──────────┴───────╯                    │
│                                                                                                            │
│ 💡 Options:                                                                                                │
│ • 🔢 Select model (1-4)                                                                                    │
│ • 👋 Type 'q' to quit                                                                                      │
│                                                                                                            │
│ ⚠️ ATTENTION: Max. Cxt. is only supported context length not set.                                          │
│ 💡 Open Ollama application to set default context length!                                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice: 2
╭─ Success ──────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Summary model set to 'llama3.2:latest' for this session                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ 💬 Chat Session ──────────────────────────────────────────────────────────────────────────────────────────╮
│ Session ID: b61cafc23e                                                                                     │
│ Model: gpt-oss:20b                                                                                         │
│ Markdown: Enabled                                                                                          │
│ Thinking Blocks: Enabled                                                                                   │
│                                                                                                            │
│ 💡 Available Commands:                                                                                     │
│ • /menu - Open the main menu                                                                               │
│ • /edit - Edit a previous message                                                                          │
│ • /exit or /quit - Exit the application                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭────────╮
│ 🧑 You │
╰────────╯
```


### Chat Session Menu
```bash
╭────────╮
│ 🧑 You │
╰────────╯
/menu
╭─ ⚙️  Chat Menu ────────────────────────────────────────────────────────────────────────────────────────────╮
│ ╭─────┬──────────────────────┬───────────────────────────────────╮                                         │
│ │ #   │ Command              │ Description                       │                                         │
│ ├─────┼──────────────────────┼───────────────────────────────────┤                                         │
│ │ 1   │ 💬 Switch Sessions   │ Change to different chat session  │                                         │
│ │ 2   │ 🤖 Change Model      │ Select a different AI model       │                                         │
│ │ 3   │ 📝 Toggle Markdown   │ Enable/disable markdown rendering │                                         │
│ │ 4   │ 🤔 Toggle Thinking   │ Show/hide thinking blocks         │                                         │
│ │ 5   │ 🔧 Change System     │ Select different system prompt    │                                         │
│ │     │ Prompt               │                                   │                                         │
│ ╰─────┴──────────────────────┴───────────────────────────────────╯                                         │
│                                                                                                            │
│ 💡 Options:                                                                                                │
│ • Select an option (1-5)                                                                                   │
│ • Type 'q' to cancel                                                                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice:
```

### Edit Menu
```bash
╭────────╮
│ 🧑 You │
╰────────╯
/edit

✏️ Edit Message
╭─ ✏️  Edit Messages ────────────────────────────────────────────────────────────────────────────────────────╮
│ ╭─────┬──────────────┬───────────────────────────────────────────────────────────────────────────╮         │
│ │ #   │ Role         │ Preview                                                                   │         │
│ ├─────┼──────────────┼───────────────────────────────────────────────────────────────────────────┤         │
│ │ 1   │ 🧑 User      │ Who was the first Avenger in the MCU?                                     │         │
│ │ -   │ 🤖 Assistant │ **Captain America (Steve Rogers)** is widely considered the first Aven... │         │
│ ╰─────┴──────────────┴───────────────────────────────────────────────────────────────────────────╯         │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Select a user message (1-1) or 'q' to cancel                                                               │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```
