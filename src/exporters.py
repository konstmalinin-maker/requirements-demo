"""BR-003: формат экспорта расширяется реестром без изменения ядра."""

import json
from collections.abc import Callable
from dataclasses import asdict

from src.messages import UserError, message
from src.note_manager import Note


class ExportRegistry:
    def __init__(self):
        self.handlers: dict[str, Callable[[list[Note]], str]] = {
            "json": lambda notes: json.dumps(
                [asdict(n) for n in notes], ensure_ascii=False, indent=2
            )
        }

    def register(self, name: str, handler: Callable[[list[Note]], str]) -> None:
        self.handlers[name] = handler

    def export(self, notes: list[Note], format_name: str) -> str:
        if format_name not in self.handlers:
            raise UserError(message("unknown_format"))
        return self.handlers[format_name](notes)
