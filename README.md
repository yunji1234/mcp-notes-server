# mcp-notes-server

🎥 Watch the demo: _[https://www.loom.com/share/7bc47e4a05234e2c91ae89212b587653]_

A custom [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that gives Claude the ability to manage local notes stored in a `notes.json` file — create, read, list, search, and delete notes, all through natural conversation.

## What this server does

`mcp-notes-server` runs locally and exposes five tools to Claude over the MCP protocol:

| Tool | Description |
|---|---|
| `create_note(title, content)` | Saves a new note. If a note with the same title already exists, the new content is appended to it instead of overwriting. |
| `read_note(title)` | Returns the full content of a note by title. |
| `list_notes()` | Lists the titles of all saved notes. |
| `search_notes(query)` | Finds notes whose title or content contains the given text (case-insensitive). |
| `delete_note(title)` | Deletes a note by title. |

All notes are stored as a simple JSON list of `{title, content}` objects in `notes.json`, right alongside the server — no database or external service required.

## Installation

### 1. Clone or download this repository

```powershell
git clone <your-repo-url> mcp-notes-server
cd mcp-notes-server
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## Using with Claude Code

### 1. Verify the server starts (optional but recommended)

With the venv activated, run:

```powershell
python server.py
```

You should see it start and hang — that's expected, it waits for input over stdio. Press `Ctrl+C` to stop it. You do **not** need to keep it running; Claude Code starts and stops it automatically.

### 2. Register the server

Run this once from any terminal, replacing the paths with your own project location:

```powershell
claude mcp add notes-server "C:\your\path\to\mcp-notes-server\venv\Scripts\python.exe" "C:\your\path\to\mcp-notes-server\server.py"
```

Confirm it was registered:

```powershell
claude mcp list
```

You should see `notes-server` in the output.

### 3. Use it from any project

The server is registered globally, so the notes tools are available in every Claude Code session regardless of which project directory you're working in. All notes are always stored in one place: `notes.json` in this repo's folder.

Just open Claude Code and type a note-related prompt — no need to start anything manually first.

## Using with Claude Desktop

### 1. Locate your config file

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

If the file doesn't exist yet, create it.

### 2. Add the config snippet

See the [Configuration](#configuration) section below. Update the paths to point to your local clone of this repo.

### 3. Restart Claude Desktop

Quit and reopen Claude Desktop. The notes tools should now be available — look for the tools icon in the chat input to confirm `notes-server` is connected.

## Configuration

Add this block to `claude_desktop_config.json`, replacing the paths with your own project location. On Windows, use double backslashes (`\\`) in JSON paths:

```json
{
  "mcpServers": {
    "notes-server": {
      "command": "C:\\your\\path\\to\\mcp-notes-server\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\your\\path\\to\\mcp-notes-server\\server.py"
      ]
    }
  }
}
```

> If you already have other servers registered, just add `"notes-server": { ... }` as another entry inside your existing `mcpServers` object — don't replace the whole file.

## Troubleshooting

**Server not showing up** — run `claude mcp list` to verify registration. If missing, re-run the `claude mcp add` command.

**"module not found" errors** — make sure the path in the `claude mcp add` command points to the venv's Python (`venv\Scripts\python.exe`), not the system Python.

**Changes to server.py not taking effect** — Claude Code starts the server fresh per session, so just start a new session after editing.

## Example prompts

Once the server is connected, try asking Claude things like:

- "Create a note titled 'Groceries' with the content 'milk, eggs, bread, coffee'."
- "What does my 'Groceries' note say?"
- "List all my notes."
- "Search my notes for anything about 'meeting'."
- "Delete the note titled 'Old Ideas'."
- "Add 'and orange juice' to my Groceries note." *(this appends, since the note already exists)*

Claude will automatically pick the right tool based on your request — no special syntax needed.
