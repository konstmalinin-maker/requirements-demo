import pytest

from src.cli import main


@pytest.mark.req("FR-001", "UR-001", "NFR-004")
def test_fr001_add_cli(manager, capsys):
    code = main(
        ["--storage", str(manager.storage.path), "add", "--title", "Пример", "--body", "Текст"]
    )
    assert code == 0
    assert "Заметка создана. ID:" in capsys.readouterr().out
    assert manager.list_notes()[0].title == "Пример"


@pytest.mark.req("FR-002", "UR-002")
def test_fr002_list_cli(manager, capsys):
    args = ["--storage", str(manager.storage.path), "list"]
    assert main(args) == 0
    assert "Заметок пока нет" in capsys.readouterr().out
    note = manager.add_note("Список", "Текст")
    assert main(args) == 0
    output = capsys.readouterr().out
    assert "ID | Заголовок | Дата создания" in output and note.id in output


@pytest.mark.req("FR-003", "UR-003", "FR-004", "UR-004")
def test_cli_search_and_edit(manager, capsys):
    note = manager.add_note("Название", "Тело")
    base = ["--storage", str(manager.storage.path)]
    assert main(base + ["edit", note.id, "--title", "Изменено", "--body", "Другой текст"]) == 0
    assert "Заметка обновлена" in capsys.readouterr().out
    assert main(base + ["search", "--query", "ИЗМЕНЕНО"]) == 0
    assert "Изменено" in capsys.readouterr().out


@pytest.mark.req("FR-005", "UR-005")
@pytest.mark.parametrize(
    "answer,deleted", [("нет", False), ("", False), ("да", True), ("yes", True)]
)
def test_fr005_ur005_delete_confirmation(manager, capsys, answer, deleted):
    note = manager.add_note("Удаление", "Текст")
    assert (
        main(["--storage", str(manager.storage.path), "delete", note.id], input_fn=lambda _: answer)
        == 0
    )
    assert (manager.list_notes() == []) == deleted
    output = capsys.readouterr().out
    assert ("Заметка удалена" if deleted else "Удаление отменено") in output


@pytest.mark.req("FR-005", "UR-005")
def test_fr005_eof_does_not_delete(manager, capsys):
    note = manager.add_note("Оставить", "Текст")

    def eof(_):
        raise EOFError

    assert main(["--storage", str(manager.storage.path), "delete", note.id], input_fn=eof) == 0
    assert len(manager.list_notes()) == 1
    assert "Удаление отменено" in capsys.readouterr().out


@pytest.mark.req("NFR-004")
@pytest.mark.parametrize(
    "arguments", [["unknown"], ["add"], ["search"], ["edit", "x"], ["delete", "missing"]]
)
def test_nfr004_russian_errors(manager, capsys, arguments):
    assert main(["--storage", str(manager.storage.path)] + arguments, input_fn=lambda _: "да") == 2
    error = capsys.readouterr().err
    assert "Ошибка:" in error and "Traceback" not in error
    assert any(hint in error for hint in ["Укажите", "Проверьте"])


@pytest.mark.req("NFR-004")
def test_cli_io_error(manager, monkeypatch, capsys):
    def denied(_):
        raise PermissionError("injected")

    monkeypatch.setattr(type(manager.storage), "load", denied)
    assert main(["--storage", str(manager.storage.path), "list"]) == 2
    assert "права доступа" in capsys.readouterr().err


@pytest.mark.req("BR-003")
def test_cli_export_and_unknown_format(manager, capsys):
    manager.add_note("Экспорт", "Текст")
    base = ["--storage", str(manager.storage.path), "export"]
    assert main(base) == 0 and "Экспорт" in capsys.readouterr().out
    assert main(base + ["--format", "missing"]) == 2
    assert "неизвестный формат" in capsys.readouterr().err
