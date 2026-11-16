"""Forward/reverse traceability, real test collection and implemented-without-commit checks."""

import re
import sys

from traceability_lib import ID, ROOT, commits, definitions, registry, source_commits, test_links


def check(root=ROOT):
    findings = []
    try:
        specs = definitions(root)
        meta = registry(root)
        history = commits(root)
        tests = test_links(root)
        if not specs:
            findings.append(("SRS", "Нет требований", "Нужны определения ## ID@vN"))
        if set(specs) != set(meta):
            findings.append(
                ("Registry", "Набор ID отличается", str(sorted(set(specs) ^ set(meta))))
            )
        mentioned = {rid for row in history for rid in row["requirements"]}
        for rid, spec in sorted(specs.items()):
            item = meta.get(rid, {})
            if item.get("version") != spec["version"]:
                findings.append((rid, "Версии не совпадают", "SRS и registry.json"))
            if rid not in mentioned:
                findings.append((rid, "Нет коммита", "Добавить реальную связь с Git"))
            if item.get("status") == "implemented" and not source_commits(history, rid):
                findings.append(
                    (rid, "Реализовано без коммита", "Нет изменений кода/тестов/CI с этим ID")
                )
            if not item.get("issue"):
                findings.append((rid, "Нет Issue", "Заполнить registry.json"))
            if rid.startswith(("FR-", "UR-")) and not any(rid in ids for ids in tests.values()):
                findings.append(
                    (rid, "Нет собранного теста", "Добавить pytest.mark.req к реальному тесту")
                )
        for node, ids in tests.items():
            if not ids:
                findings.append((node, "Тест без REQ", "Нужен pytest.mark.req"))
            for rid in ids:
                if not ID.fullmatch(rid) or rid not in specs:
                    findings.append((node, "Осиротевший тест", f"Неизвестное требование {rid}"))
        path = root / "docs/traceability.md"
        if not path.exists():
            findings.append(("RTM", "Файл отсутствует", "Запустите generate_rtm.py"))
        else:
            text = path.read_text()
            for rid in re.findall(
                r"^\| \[?((?:BR|UR|FR|NFR)-\d{3})(?:@v\d+)?[^\n]*\| (?:Реализовано|Трассировано|Implemented|✅) \|",
                text,
                re.MULTILINE,
            ):
                if not source_commits(history, rid):
                    findings.append(
                        (
                            rid,
                            "RTM заявляет реализацию без коммита",
                            "Ложноположительный статус RTM",
                        )
                    )
        summary = f"Всего требований: {len(specs)}; REQ в коммитах: {len(set(specs) & mentioned)}; собрано тестов: {len(tests)}."
    except (ValueError, KeyError) as exc:
        findings.append(("Инструмент", "Ошибка проверки", str(exc).replace("\n", " ")))
        summary = "Проверка не завершена."
    lines = [
        "# Проверка трассируемости",
        "",
        summary,
        "",
        "| Объект | Результат | Подробности |",
        "| --- | --- | --- |",
    ]
    if not findings:
        lines.append("| Все требования | PASS | Прямые и обратные связи проверены |")
    else:
        for obj, result, detail in findings:
            lines.append(f"| {obj.replace('|', '/')} | {result} | {detail.replace('|', '/')} |")
    lines += [
        "",
        "Итог: **"
        + ("PASS — все требования трассированы" if not findings else "FAIL — обнаружены проблемы")
        + "**.",
        "",
    ]
    report = "\n".join(lines)
    (root / "docs/traceability-report.md").write_text(report, encoding="utf-8")
    print(report)
    return int(bool(findings))


if __name__ == "__main__":
    sys.exit(check())
