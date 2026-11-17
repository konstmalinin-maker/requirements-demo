# Скриншоты практики №5

Все изображения сняты 16.11.2026 с реальных страниц GitHub и окна терминала.

- [10-repository-tree.png](10-repository-tree.png) — Структура реального репозитория в терминале, tree -a -L 2.
- [03-srs-functional.png](03-srs-functional.png) — SRS в Markdown: FR-001, приоритет, связь с UR-001 и критерий приёмки.
- [04-issues-labels.png](04-issues-labels.png) — Все 19 закрытых Issues по требованиям, метки типа, приоритета и REQ-ID.
- [11-git-log-req.png](11-git-log-req.png) — История коммитов с REQ-ID и отдельным автокоммитом RTM.
- [01-pr-open.png](01-pr-open.png) — PR #20 в открытом состоянии, до слияния.
- [02-pr-merged.png](02-pr-merged.png) — PR #20 после слияния, связанные Issues закрыты.
- [06-generated-rtm.png](06-generated-rtm.png) — Автоматически созданная RTM в GitHub; автор последнего изменения — github-actions[bot].
- [07-actions-success.png](07-actions-success.png) — Успешный workflow: проверка, автогенерация RTM и артефакт.
- [12-traceability-pass.png](12-traceability-pass.png) — Результат реального локального запуска check_traceability.py: PASS.
- [16-coverage-and-performance.png](16-coverage-and-performance.png) — Покрытие 98,50%, 54 passed и измерение list: 111,100 мс при 10000 заметок.
- [08-actions-coverage-failure.png](08-actions-coverage-failure.png) — Намеренно неуспешный workflow проверки покрытия.
- [17-ci-coverage-threshold-log.png](17-ci-coverage-threshold-log.png) — Настоящий журнал CI: порог 80% не достигнут, покрытие 49,25%, exit code 1.
- [13-commitlint-rejected-accepted.png](13-commitlint-rejected-accepted.png) — Сохранённые журналы реального отклонённого и принятого коммитов.
- [05-automatic-label-and-project-events.png](05-automatic-label-and-project-events.png) — Автоматическая req-метка, комментарий со ссылкой на SRS и переход карточки в Done.
- [14-reverse-traceability-failures.png](14-reverse-traceability-failures.png) — Обнаружены осиротевший тест и ложный статус реализации без коммита.
- [15-requirement-version-checks.png](15-requirement-version-checks.png) — Изменение без новой версии отклонено; согласованная редакция успешно проверена.
- [09-requirement-v2.png](09-requirement-v2.png) — Фактическое определение FR-003@v2 с правилом удаления пробелов запроса.
- [18-kanban-board.png](18-kanban-board.png) — GitHub Kanban: четыре колонки и карточки с REQ-ID.
- [19-kanban-req-id-verification.png](19-kanban-req-id-verification.png) — Проверка GitHub API: все 19 REQ-ID точно совпадают с ID требований.
