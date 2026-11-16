"""BR-001, NFR-002, NFR-003: автономное атомарное JSON-хранилище."""

import json
import os
import tempfile
from pathlib import Path

from src.messages import UserError, message


class JsonStorage:
    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError) as exc:
            raise UserError(message("invalid_storage")) from exc
        if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
            raise UserError(message("invalid_storage"))
        return data

    def save(self, rows: list[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, temporary = tempfile.mkstemp(prefix=".notes-", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                if os.name == "posix":
                    os.fchmod(stream.fileno(), 0o600)
                json.dump(rows, stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
            if os.name == "posix":
                directory = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
