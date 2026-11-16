import pytest

from src.messages import UserError
from src.note_manager import NoteManager


@pytest.mark.req("FR-001", "UR-001", "BR-001")
def test_fr001_ur001_add_persists(manager):
    note = manager.add_note("  Заголовок  ", "  Текст  ")
    saved = NoteManager(manager.storage).list_notes()[0]
    assert saved == note
    assert note.title == "Заголовок" and note.body == "Текст"
    assert len(note.id) == 32
    assert note.created_at == note.updated_at
    assert manager.add_note("Ещё", "Другая").id != note.id


@pytest.mark.req("FR-001", "NFR-004")
@pytest.mark.parametrize(
    "title,body,key",
    [
        ("", "Body", "заголовок обязателен"),
        (" \n", "Body", "заголовок обязателен"),
        ("x" * 101, "Body", "заголовок слишком длинный"),
        ("Title", "", "тело заметки обязательно"),
        ("Title", " \t", "тело заметки обязательно"),
        ("Title", "x" * 10001, "тело заметки слишком длинное"),
    ],
)
def test_fr001_rejects_invalid_without_write(manager, title, body, key):
    with pytest.raises(UserError, match=key):
        manager.add_note(title, body)
    assert not manager.storage.path.exists()


@pytest.mark.req("FR-001")
def test_fr001_exact_limits(manager):
    note = manager.add_note("x" * 100, "y" * 10000)
    assert len(note.title) == 100 and len(note.body) == 10000


@pytest.mark.req("FR-002", "UR-002")
def test_fr002_ur002_list(manager):
    assert manager.list_notes() == []
    a = manager.add_note("Один", "А")
    b = manager.add_note("Два", "Б")
    assert manager.list_notes() == [a, b]


@pytest.mark.req("FR-003", "UR-003")
@pytest.mark.parametrize(
    "query,expected",
    [("PYTHON", ["Python"]), ("ЗАМЕТКА", ["Другой"]), ("", []), ("  ", []), ("нетсовпадений", [])],
)
def test_fr003_ur003_search(manager, query, expected):
    manager.add_note("Python", "Язык")
    manager.add_note("Другой", "Заметка о практике")
    assert [n.title for n in manager.search_notes(query)] == expected


@pytest.mark.req("FR-004", "UR-004")
def test_fr004_ur004_edit(manager):
    old = manager.add_note("До", "Текст")
    changed = manager.edit_note(old.id, title="После")
    assert changed.id == old.id and changed.created_at == old.created_at
    assert changed.updated_at >= old.updated_at
    assert changed.title == "После" and changed.body == old.body
    changed = manager.edit_note(old.id, body="Новый текст")
    assert changed.title == "После" and changed.body == "Новый текст"


@pytest.mark.req("FR-004", "NFR-004")
@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"title": " "},
        {"body": ""},
        {"title": "x" * 101},
        {"body": "x" * 10001},
        {"title": "Valid", "body": ""},
    ],
)
def test_fr004_invalid_edit_is_atomic(manager, changes):
    note = manager.add_note("До", "Текст")
    original = manager.storage.path.read_bytes()
    with pytest.raises(UserError):
        manager.edit_note(note.id, **changes)
    assert manager.storage.path.read_bytes() == original


@pytest.mark.req("FR-004", "FR-005", "NFR-004")
def test_unknown_id_preserves_storage(manager):
    manager.add_note("До", "Текст")
    original = manager.storage.path.read_bytes()
    for operation in [
        lambda: manager.edit_note("missing", title="X"),
        lambda: manager.delete_note("missing"),
    ]:
        with pytest.raises(UserError, match="не найдена"):
            operation()
        assert manager.storage.path.read_bytes() == original
