"""NFR-006: централизованная локализация интерфейса."""

import json
from pathlib import Path

MESSAGES = json.loads(Path(__file__).with_name("messages_ru.json").read_text(encoding="utf-8"))


def message(key: str, **values) -> str:
    return MESSAGES[key].format(**values)


class UserError(ValueError):
    """Ожидаемая ошибка с готовым русскоязычным сообщением NFR-004."""
