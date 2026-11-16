import json
import os
import socket
import subprocess
import sys
import time
from dataclasses import asdict

import pytest

from src.cli import main
from src.exporters import ExportRegistry
from src.messages import MESSAGES
from src.note_manager import Note


@pytest.mark.req("BR-001", "FR-001", "FR-002", "FR-003", "FR-004", "FR-005")
def test_br001_offline_cycle(manager, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("Network is forbidden")

    monkeypatch.setattr(socket, "socket", no_network)
    note = manager.add_note("Offline", "Текст")
    assert manager.search_notes("OFFLINE") == [note]
    manager.edit_note(note.id, body="Изменено")
    assert len(manager.list_notes()) == 1
    manager.delete_note(note.id)
    assert manager.list_notes() == []


@pytest.mark.req("BR-002", "NFR-004", "NFR-006")
def test_br002_help_and_basic_scenario(manager, capsys):
    start = time.perf_counter()
    with pytest.raises(SystemExit) as result:
        main(["--help"])
    assert result.value.code == 0
    help_text = capsys.readouterr().out
    assert "Локальный менеджер" in help_text and "создать заметку" in help_text
    base = ["--storage", str(manager.storage.path)]
    assert main(base + ["add", "--title", "Пример", "--body", "Текст"]) == 0
    assert main(base + ["list"]) == 0
    assert main(base + ["search", "--query", "ПРИМЕР"]) == 0
    assert time.perf_counter() - start < 300


@pytest.mark.req("BR-003")
def test_br003_export_plugin(manager):
    manager.add_note("Первый", "Текст")
    registry = ExportRegistry()
    registry.register("titles", lambda notes: "\n".join(n.title for n in notes))
    assert registry.export(manager.list_notes(), "titles") == "Первый"
    assert json.loads(registry.export(manager.list_notes(), "json"))[0]["title"] == "Первый"


@pytest.mark.req("NFR-001", "FR-002")
def test_nfr001_list_10000_under_500ms(tmp_path, record_property):
    path = tmp_path / "performance.json"
    rows = [
        asdict(
            Note(
                str(i),
                f"Заметка {i}",
                "Текст",
                "2026-11-16T00:00:00+00:00",
                "2026-11-16T00:00:00+00:00",
            )
        )
        for i in range(10000)
    ]
    path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    start = time.perf_counter()
    completed = subprocess.run(
        [sys.executable, "-m", "src.cli", "--storage", str(path), "list"],
        capture_output=True,
        text=True,
        check=True,
    )
    elapsed = (time.perf_counter() - start) * 1000
    assert len(completed.stdout.splitlines()) == 10001
    record_property("notes", 10000)
    record_property("list_ms", round(elapsed, 3))
    print(f"NFR-001: notes=10000, full CLI elapsed={elapsed:.3f} ms, budget=500 ms")
    assert elapsed < 500, f"list took {elapsed:.3f} ms"


@pytest.mark.req("NFR-005")
def test_nfr005_public_modules_importable():
    from src.note_manager import NoteManager
    from src.storage import JsonStorage

    assert callable(NoteManager) and callable(JsonStorage)


@pytest.mark.req("NFR-006")
def test_nfr006_messages_externalized():
    for key in [
        "created",
        "updated",
        "deleted",
        "confirm",
        "bad_arguments",
        "io_error",
        "description",
    ]:
        assert key in MESSAGES and isinstance(MESSAGES[key], str)
    assert "да/нет" in MESSAGES["confirm"]


@pytest.mark.req("FR-001", "NFR-006")
def test_cli_module_entrypoint_and_environment_path(tmp_path):
    path = tmp_path / "env.json"
    result = subprocess.run(
        [sys.executable, "-m", "src.cli", "add", "--title", "Среда", "--body", "Текст"],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "NOTES_FILE": str(path)},
    )
    assert result.returncode == 0 and path.exists()
    assert "Заметка создана" in result.stdout
