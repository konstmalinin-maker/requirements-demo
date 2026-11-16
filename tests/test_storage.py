import json
import os
import stat

import pytest

from src.messages import UserError
from src.storage import JsonStorage


@pytest.mark.req("NFR-002", "BR-001")
def test_nfr002_failed_replace_preserves_original(manager, monkeypatch):
    manager.add_note("Original", "Сохранить")
    original = manager.storage.path.read_bytes()

    def broken_replace(_source, _target):
        raise OSError("injected before atomic replace")

    monkeypatch.setattr(os, "replace", broken_replace)
    with pytest.raises(OSError):
        manager.add_note("Should not appear", "Не сохранять")
    assert manager.storage.path.read_bytes() == original
    assert not list(manager.storage.path.parent.glob(".notes-*.tmp"))
    assert len(json.loads(original)) == 1


@pytest.mark.req("NFR-002")
def test_serialization_failure_cleans_temporary(tmp_path):
    storage = JsonStorage(tmp_path / "notes.json")
    with pytest.raises(TypeError):
        storage.save([{"bad": object()}])
    assert not storage.path.exists()
    assert not list(tmp_path.glob(".notes-*.tmp"))


@pytest.mark.req("NFR-003")
@pytest.mark.skipif(os.name != "posix", reason="POSIX file permissions")
def test_nfr003_permissions_0600(manager):
    note = manager.add_note("Private", "Текст")
    assert stat.S_IMODE(manager.storage.path.stat().st_mode) == 0o600
    manager.storage.path.chmod(0o644)
    manager.edit_note(note.id, title="Still private")
    assert stat.S_IMODE(manager.storage.path.stat().st_mode) == 0o600


@pytest.mark.req("NFR-002", "NFR-004")
@pytest.mark.parametrize(
    "content",
    [
        "{broken",
        "{}",
        "[1]",
        '[{"id": "x"}]',
        '[{"id":1,"title":"a","body":"b","created_at":"c","updated_at":"d"}]',
    ],
)
def test_corrupted_storage_rejected(manager, content):
    manager.storage.path.write_text(content)
    with pytest.raises(UserError, match="повреждён"):
        manager.list_notes()
    assert manager.storage.path.read_text() == content


@pytest.mark.req("NFR-002", "NFR-004")
def test_non_utf8_storage_rejected(manager):
    manager.storage.path.write_bytes(b"\xff\xfe")
    with pytest.raises(UserError, match="повреждён"):
        manager.list_notes()
