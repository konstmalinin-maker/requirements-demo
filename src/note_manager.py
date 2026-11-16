"""FR-001…FR-005: управление заметками независимо от командного интерфейса."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from uuid import uuid4

from src.messages import UserError, message
from src.storage import JsonStorage


@dataclass
class Note:
    id: str
    title: str
    body: str
    created_at: str
    updated_at: str


def validate_text(value: str, field: str, limit: int) -> str:
    value = value.strip()
    if not value:
        raise UserError(message(f"{field}_required"))
    if len(value) > limit:
        raise UserError(message(f"{field}_long"))
    return value


class NoteManager:
    def __init__(self, storage: JsonStorage):
        self.storage = storage

    def list_notes(self) -> list[Note]:
        rows = self.storage.load()
        fields = {"id", "title", "body", "created_at", "updated_at"}
        if any(set(row) != fields or not all(isinstance(v, str) for v in row.values()) for row in rows):
            raise UserError(message("invalid_storage"))
        return [Note(**row) for row in rows]

    def add_note(self, title: str, body: str) -> Note:
        title = validate_text(title, "title", 100)
        body = validate_text(body, "body", 10_000)
        notes = self.list_notes()
        now = datetime.now(timezone.utc).isoformat()
        note = Note(uuid4().hex, title, body, now, now)
        notes.append(note)
        self.storage.save([asdict(n) for n in notes])
        return note

    def search_notes(self, query: str) -> list[Note]:
        if not query.strip():
            return []
        query = query.casefold()
        return [n for n in self.list_notes() if query in n.title.casefold() or query in n.body.casefold()]

    def edit_note(self, note_id: str, title: str | None = None, body: str | None = None) -> Note:
        if title is None and body is None:
            raise UserError(message("edit_empty"))
        new_title = validate_text(title, "title", 100) if title is not None else None
        new_body = validate_text(body, "body", 10_000) if body is not None else None
        notes = self.list_notes()
        for note in notes:
            if note.id == note_id:
                if new_title is not None:
                    note.title = new_title
                if new_body is not None:
                    note.body = new_body
                note.updated_at = datetime.now(timezone.utc).isoformat()
                self.storage.save([asdict(n) for n in notes])
                return note
        raise UserError(message("not_found", id=note_id))

    def delete_note(self, note_id: str) -> None:
        notes = self.list_notes()
        remaining = [n for n in notes if n.id != note_id]
        if len(remaining) == len(notes):
            raise UserError(message("not_found", id=note_id))
        self.storage.save([asdict(n) for n in remaining])
