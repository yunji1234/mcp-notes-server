import json
import os

from mcp.server.fastmcp import FastMCP

NOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes.json")

mcp = FastMCP("notes-server")


def _load_notes() -> list[dict]:
    if not os.path.exists(NOTES_FILE):
        return []
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def _save_notes(notes: list[dict]) -> None:
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)


def _find_note(notes: list[dict], title: str) -> dict | None:
    for note in notes:
        if note.get("title", "").lower() == title.lower():
            return note
    return None


@mcp.tool()
def create_note(title: str, content: str) -> str:
    """Create a new note with a title and content, saved to notes.json.
    If a note with the same title already exists, the new content is
    appended to that note's existing content rather than overwriting it.
    Use this whenever the user wants to save, jot down, or record information."""
    title = title.strip()
    if not title:
        return "Error: note title cannot be empty."
    if not content.strip():
        return "Error: note content cannot be empty."

    notes = _load_notes()
    existing = _find_note(notes, title)
    if existing is not None:
        existing["content"] = f"{existing['content']}\n{content}"
        _save_notes(notes)
        return f"A note titled '{title}' already existed, so the new content was appended to it."

    notes.append({"title": title, "content": content})
    _save_notes(notes)
    return f"Note '{title}' was created and saved."


@mcp.tool()
def read_note(title: str) -> str:
    """Return the full content of the note with the given title.
    Use this when the user wants to view, recall, or check what a specific note says."""
    title = title.strip()
    if not title:
        return "Error: note title cannot be empty."

    notes = _load_notes()
    note = _find_note(notes, title)
    if note is None:
        return f"No note titled '{title}' was found."
    return f"--- {note['title']} ---\n{note['content']}"


@mcp.tool()
def list_notes() -> str:
    """List the titles of every saved note.
    Use this when the user wants an overview of what notes exist."""
    notes = _load_notes()
    if not notes:
        return "There are no notes yet."

    lines = "\n".join(f"- {note.get('title', '(untitled)')}" for note in notes)
    return f"You have {len(notes)} note(s):\n{lines}"


@mcp.tool()
def search_notes(query: str) -> str:
    """Search all notes for a case-insensitive match of the query in either
    the title or the content, and return the titles of matching notes.
    Use this when the user wants to find notes related to a topic or keyword."""
    query = query.strip()
    if not query:
        return "Error: search query cannot be empty."

    notes = _load_notes()
    if not notes:
        return "There are no notes to search."

    needle = query.lower()
    matches = [
        note.get("title", "(untitled)")
        for note in notes
        if needle in note.get("title", "").lower() or needle in note.get("content", "").lower()
    ]
    if not matches:
        return f"No notes matched '{query}'."

    lines = "\n".join(f"- {title}" for title in matches)
    return f"Found {len(matches)} note(s) matching '{query}':\n{lines}"


@mcp.tool()
def delete_note(title: str) -> str:
    """Delete the note with the given title from notes.json.
    Use this when the user wants to remove or discard a saved note."""
    title = title.strip()
    if not title:
        return "Error: note title cannot be empty."

    notes = _load_notes()
    note = _find_note(notes, title)
    if note is None:
        return f"No note titled '{title}' was found, so nothing was deleted."

    notes.remove(note)
    _save_notes(notes)
    return f"Note '{title}' was deleted."


if __name__ == "__main__":
    mcp.run()
