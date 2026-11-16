"""Extra A: generate the actual RTM from git history and collected tests."""

from traceability_lib import REPO, ROOT, commits, definitions, registry, source_commits, test_links


def generate(root=ROOT):
    specs = definitions(root)
    meta = registry(root)
    history = commits(root)
    links = test_links(root)
    lines = [
        "# Матрица трассируемости (RTM)",
        "",
        "Автоматически создано `scripts/generate_rtm.py` из определений SRS, реестра, git log и собранных pytest-тестов. Ссылки на коммиты соответствуют реальной истории. Наличие тестовой связи не заменяет успешный запуск тестов.",
        "",
        "| REQ | Тип | Приоритет | Issue | Коммиты реализации / проверки | Тесты | Статус |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for rid, spec in sorted(specs.items()):
        item = meta[rid]
        rows = source_commits(history, rid)
        tests = [node for node, ids in links.items() if rid in ids]
        issue = f"[#{item['issue']}]({REPO}/issues/{item['issue']})" if item.get("issue") else "—"
        refs = "<br>".join(f"[{r['sha'][:7]}]({REPO}/commit/{r['sha']})" for r in rows) or "—"
        test_refs = "<br>".join(f"`{n}`" for n in tests) or "—"
        status = "Трассировано" if rows and tests and item.get("issue") else "Неполная связь"
        lines.append(
            f"| [{rid}@v{spec['version']}]({spec['path'].removeprefix('docs/')}) | {rid.split('-')[0]} | {spec['priority']} | {issue} | {refs} | {test_refs} | {status} |"
        )
    lines += [
        "",
        "## Методика",
        "",
        "Коммиты связываются по REQ-ID в сообщении и реальным изменениям исходников, тестов, скриптов или настроек CI. Чисто документальный коммит не считается достаточным свидетельством реализации. Автокоммиты `chore(rtm):` исключены, чтобы избежать самоссылки и бесконечного изменения RTM.",
        "",
        "Состояние прохождения тестов, измеренное покрытие и проверка критериев публикуются в GitHub Actions и отчёте практики. BR-002 имеет ограничение индивидуальной проверки удобства, указанное в SRS.",
        "",
    ]
    path = root / "docs/traceability.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(
        f"RTM generated: {len(specs)} requirements, {len(links)} collected tests -> {path.relative_to(root)}"
    )
    return path


if __name__ == "__main__":
    generate()
