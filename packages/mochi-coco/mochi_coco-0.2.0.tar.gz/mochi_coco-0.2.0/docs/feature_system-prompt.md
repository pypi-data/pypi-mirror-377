# Feature: System Prompt

- Available system prompts are displayed in the `System Prompt`-Panel. The `System Prompt`-Panel is only shown when the folder `system_prompts` exists in the terminal directory and `*.md` or `*.txt` files are present. Otherwise, the `System Prompt`-Panel is not shown and the possibility of opening the `System Prompt`-Panel within the `Chat Menu`-Panel is disabled/not shown.
- When the user creates a new chat session, the user is prompted to select a system prompt. But only, if folder `system_prompts` exists in the terminal directory and `*.md` or `*.txt` files are present.
- During the session the user can open the chat session menu (command `/menu`) and within this menu the user can select a system prompt (would replace the current system prompt in the chat history json file).
- When the user selects a already existing chat session, the user is not prompted to select a system prompt, since the system prompt is already set (within the chat session json file).

**Possibility to open the `System Prompt`-Panel within the `Chat Menu`-Panel:**
```terminal
╭─ ⚙️ Chat Menu ──────────────────────────────────────────────────────────────────────────────────────╮
│ ╭─────┬──────────────────────┬───────────────────────────────────╮                                  │
│ │ #   │ Command              │ Description                       │                                  │
│ ├─────┼──────────────────────┼───────────────────────────────────┤                                  │
│ │ 1   │ 💬 Switch Sessions   │ Change to different chat session  │                                  │
│ │ 2   │ 🤖 Change Model      │ Select a different AI model       │                                  │
│ │ 3   │ 📝 Toggle Markdown   │ Enable/disable markdown rendering │                                  │
│ │ 4   │ 🤔 Toggle Thinking   │ Show/hide thinking blocks         │                                  │
│ │ 5   │ 🥸 System Prompt     │ Select custom system prompt       │                                  │
│ ╰─────┴──────────────────────┴───────────────────────────────────╯                                  │
│                                                                                                     │
│ 💡 Options:                                                                                         │
│ • Select an option (1-4)                                                                            │
│ • Type 'q' to cancel                                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
> The possible selection for a system prompt is only shown in case there is a `system_prompts` folder with at least one file (`*.md` or `*.txt`).

**Chat History with system prompt:**
```json
{
  "metadata": {
    "session_id": "dfbef86f0b",
    "model": "qwen3:30b",
    "created_at": "2025-09-12T13:42:59.586691",
    "updated_at": "2025-09-12T13:43:13.760347",
    "message_count": 2,
    "summary": null
  },
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant.",
      "message_id": "352a94b145",
      "timestamp": "2025-09-12T13:43:07.502463"
    },
    {
      "role": "user",
      "content": "Hi",
      "message_id": "352a94b1a8",
      "timestamp": "2025-09-12T13:43:08.502463"
    },
    {
      "role": "assistant",
      "content": "Hello! How can I assist you today? 😊",
      "model": "qwen3:30b",
      "message_id": "25181efdcb",
      "timestamp": "2025-09-12T13:43:13.760332",
      "eval_count": 91,
      "prompt_eval_count": 9
    }
  ]
}
```


**User flow displayed for system prompt selection:**
```terminal
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                                                                 ┃
┃                                    🍡 Welcome to Mochi-Coco!                                    ┃
┃                                                                                                 ┃
┃                                                                                                 ┃
┃                                            .-===-.                                              ┃
┃                                            |[:::]|                                              ┃
┃                                            `-----´                                              ┃
┃                                                                                                 ┃
┃                                    🤖 AI Chat with Style                                        ┃
┃                                                                                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
╭─ 💬 Previous Sessions ──────────────────────────────────────────────────────────────────────────╮
│ ╭─────┬──────────────┬──────────────────────┬─────────────────────────────────────┬──────────╮  │
│ │ #   │ Session ID   │ Model                │ Preview                             │ Messages │  │
│ ├─────┼──────────────┼──────────────────────┼─────────────────────────────────────┼──────────┤  │
│ │ 1   │ dfbef86f0b   │ qwen3:30b            │ Hi                                  │    2     │  │
│ ╰─────┴──────────────┴──────────────────────┴─────────────────────────────────────┴──────────╯  │
│                                                                                                 │
│ 💡 Options:                                                                                     │
│ • 📝 Select session (1-1)                                                                       │
│ • 🆕 Type 'new' for new chat                                                                    │
│ • 🗑️ Type '/delete <number>' to delete session                                                   │
│ • 👋 Type 'q' to quit                                                                           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice: new
╭─ System Prompts ────────────────────────────────────────────────────────────╮
│ ╭─────┬──────────────┬──────────────────────────────────────┬────────────╮  │
│ │ #   │ Filename     │ Preview                              │ Word Count │  │
│ ├─────┼──────────────┼──────────────────────────────────────┼────────────┤  │
│ │ 1   │ AGENT.md     │ # Persona                            │        345 │  │
│ │ 2   │ Assistant.md │ You are a helpful assistant          │       1221 │  │
│ ╰─────┴──────────────┴──────────────────────────────────────┴────────────╯  │
│                                                                             │
│ 💡 Options:                                                                 │
│ • 📝 Select system prompt (1-2)                                             │
│ • 🆕 Type 'no' for no system prompt                                         │
│ • 🗑️ Type '/delete <number>' to delete a system prompt                      │
│ • 👋 Type 'q' to quit                                                       │
╰─────────────────────────────────────────────────────────────────────────────╯
Enter your choice: 1
╭─────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 🤖 Select your AI model                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ 🤖 Available Models ───────────────────────────────────────────────────────────────────────────╮
│ ╭─────┬───────────────────────────┬──────────────┬─────────────────┬──────────┬───────╮         │
│ │ #   │ Model Name                │    Size (MB) │ Family          │ Max. Cxt │ Tools │         │
│ ├─────┼───────────────────────────┼──────────────┼─────────────────┼──────────┼───────┤         │
│ │ 1   │ gpt-oss:20b               │      13141.8 │ gptoss          │   131072 │   ☑️   │         │
│ │ 2   │ qwen3:14b                 │       8846.5 │ qwen3           │    40960 │   ☑️   │         │
│ │ 3   │ qwen3:latest              │       4983.3 │ qwen3           │    40960 │   ☑️   │         │
│ │ 4   │ qwen3:30b                 │      17697.0 │ qwen3moe        │   262144 │   ☑️   │         │
│ │ 5   │ llama3.2:latest           │       1925.8 │ llama           │   131072 │   ☑️   │         │
│ │ 6   │ qwen3-coder:latest        │      17697.0 │ qwen3moe        │   262144 │       │         │
│ │ 7   │ mistral-small3.2:latest   │      14474.3 │ mistral3        │   131072 │   ☑️   │         │
│ ╰─────┴───────────────────────────┴──────────────┴─────────────────┴──────────┴───────╯         │
│                                                                                                 │
│ 💡 Options:                                                                                     │
│ • 🔢 Select model (1-7)                                                                         │
│ • 👋 Type 'q' to quit                                                                           │
│                                                                                                 │
│ ⚠️  ATTENTION: The maximum context length is the supported length of the model but not the       │
│ actual length during chat sessions.                                                             │
│ 💡 Open Ollama application to set default context length!                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯
Enter your choice: 1
╭────────────────────────────────────── Markdown Rendering ───────────────────────────────────────╮
│ 📝 Enable markdown formatting for responses?                                                    │
│ This will format code blocks, headers, tables, etc.                                             │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯
Enable markdown? (Y/n): y
╭──────────────────────────────────── Thinking Block Display ─────────────────────────────────────╮
│ 🤔 Show model's thinking process in responses?                                                  │
│ This will display thinking blocks as formatted quotes.                                          │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯
Show thinking blocks? (y/N): y
╭─ 💬 Chat Session ───────────────────────────────────────────────────────────────────────────────╮
│ Session ID: 5e02ab1f62                                                                          │
│ Model: gpt-oss:20b                                                                              │
│ Markdown: Enabled                                                                               │
│ Thinking Blocks: Enabled                                                                        │
│                                                                                                 │
│ 💡 Available Commands:                                                                          │
│ • /menu - Open the main menu                                                                    │
│ • /edit - Edit a previous message                                                               │
│ • /exit or /quit - Exit the application                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯

╭────────╮
│ 🧑 You │
╰────────╯
```
