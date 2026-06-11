import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import server


@pytest.fixture
def notes_file(tmp_path, monkeypatch):
    """Point the server at a throwaway notes.json so tests never touch the real file."""
    path = tmp_path / "notes.json"
    path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(server, "NOTES_FILE", str(path))
    return path


def test_create_and_read_note(notes_file):
    create_result = server.create_note("Groceries", "milk, eggs, bread")
    assert "created" in create_result.lower()
    assert "Groceries" in create_result

    read_result = server.read_note("Groceries")
    assert "Groceries" in read_result
    assert "milk, eggs, bread" in read_result


def test_list_notes_returns_correct_titles(notes_file):
    server.create_note("Note A", "first note")
    server.create_note("Note B", "second note")

    result = server.list_notes()
    assert "Note A" in result
    assert "Note B" in result
    assert "2" in result


def test_search_notes_finds_matching_content(notes_file):
    server.create_note("Meeting Notes", "Discuss roadmap and budget")
    server.create_note("Groceries", "milk, eggs, bread")

    result = server.search_notes("roadmap")
    assert "Meeting Notes" in result
    assert "Groceries" not in result


def test_delete_note_removes_it(notes_file):
    server.create_note("Temp Note", "to be deleted")

    delete_result = server.delete_note("Temp Note")
    assert "deleted" in delete_result.lower()
    assert "Temp Note" in delete_result

    assert "Temp Note" not in server.list_notes()
    assert "No note titled" in server.read_note("Temp Note")


def test_read_nonexistent_note_returns_helpful_message(notes_file):
    result = server.read_note("Does Not Exist")
    assert "No note titled" in result
    assert "Does Not Exist" in result


def test_create_duplicate_note_appends_gracefully(notes_file):
    server.create_note("Groceries", "milk, eggs")
    second_result = server.create_note("Groceries", "and orange juice")

    assert "already existed" in second_result.lower()
    assert "appended" in second_result.lower()

    read_result = server.read_note("Groceries")
    assert "milk, eggs" in read_result
    assert "and orange juice" in read_result

    # Only one note should exist for that title, not two separate entries.
    assert server.list_notes().count("Groceries") == 1
