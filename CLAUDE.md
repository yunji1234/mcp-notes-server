# mcp-notes-server

MCP server that exposes note management tools to Claude Code. Notes are stored locally in `notes.json`.

## Stack

- **Python 3.11+**
- **`mcp` (FastMCP)** — MCP server framework; tools are registered with `@mcp.tool()`
- **`pytest`** — test runner
- No database, no external services

## Architecture

Everything lives in a single file: `server.py`.

```
server.py          # FastMCP server + all 5 tools
notes.json         # data store — a JSON list of {title, content} objects
tests/
  test_server.py   # pytest tests, one per tool behaviour
requirements.txt   # mcp, pytest
```

The three private helpers at the top of `server.py` own all I/O:
- `_load_notes()` — reads `notes.json`, returns `[]` on missing or corrupt file
- `_save_notes(notes)` — writes the full list back to `notes.json`
- `_find_note(notes, title)` — case-insensitive title lookup, returns `None` if not found

Every tool calls `_load_notes()` at the start and `_save_notes()` after any mutation. There is no in-memory state between calls.

`NOTES_FILE` is resolved relative to `server.py`'s own directory (not the working directory), so notes always land in this folder regardless of where Claude Code is running from.

## Running the server

You never run the server manually in normal use — Claude Code starts and stops it automatically once registered.

To verify it starts cleanly:

```powershell
.\venv\Scripts\Activate.ps1
python server.py
# should hang waiting for input — Ctrl+C to stop
```

To register with Claude Code (one-time, user-scoped):

```powershell
claude mcp add --scope user notes-server "C:\your\path\to\mcp-notes-server\venv\Scripts\python.exe" "C:\your\path\to\mcp-notes-server\server.py"
```

## Running tests

```powershell
.\venv\Scripts\Activate.ps1
python -m pytest tests/ -v --basetemp=.pytest_tmp
```

Tests monkeypatch `server.NOTES_FILE` to a `tmp_path` file, so they never touch the real `notes.json`.

## Conventions

**Adding a new tool**
- Decorate with `@mcp.tool()`
- Write a clear docstring — FastMCP uses it to tell Claude when to call the tool
- Call `_load_notes()` at the top; call `_save_notes()` after any mutation
- Return a plain string confirming what was done (or a "not found" message on failure)
- Add a test in `tests/test_server.py` covering at least the happy path and the not-found case

**Changing the data format**
- Notes are stored as `{"title": str, "content": str}` — keep it flat
- `_find_note` matches by lowercase title; keep lookups case-insensitive

**Duplicate titles**
- `create_note` appends to existing content (joined with `\n`) — it does not overwrite
- This is intentional; do not change it to overwrite without updating the tests and README

**Do not add**
- In-memory caching between tool calls — the file is the source of truth
- A database or external dependency — the whole point is zero-infrastructure
- Overwrite behaviour to `create_note` without updating tests and README
