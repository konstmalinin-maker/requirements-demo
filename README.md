# Requirements Demo

[![Traceability Check](https://github.com/konstmalinin-maker/requirements-demo/actions/workflows/traceability.yml/badge.svg)](https://github.com/konstmalinin-maker/requirements-demo/actions/workflows/traceability.yml)

Практическая работа №5 — requirements-as-code. Локальный консольный менеджер заметок: создание, список, поиск, редактирование, подтверждаемое удаление. Python 3.12+.

## Документация

- [SRS](docs/srs.md), [BR](docs/requirements/business.md), [UR](docs/requirements/user.md), [FR](docs/requirements/functional.md), [NFR](docs/requirements/non-functional.md).
- [RTM](docs/traceability.md), [проверка трассируемости](docs/traceability-report.md), [глоссарий](docs/glossary.md).
- [Версионирование требований](docs/requirements/changelog.md).

## Быстрый старт

```sh
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
note --storage ./demo-notes.json add --title "Практика" --body "Проверить требования"
note --storage ./demo-notes.json list
note --storage ./demo-notes.json search --query "ПРАКТИКА"
python -m pytest --cov=src --cov-fail-under=80
python scripts/generate_rtm.py
python scripts/check_traceability.py
```

## Коммиты

```sh
npm ci
npm run prepare
```

Для feat/fix/test требуется стабильный REQ-ID в скобках, например `feat(notes): add search (FR-003)`. Husky проверяет commit-msg локально, commitlint — диапазон PR в CI. CI также проверяет версии требований и обратные связи тестов.

## Структура

- docs/ — спецификация, RTM, журнал и отчёт.
- src/ — ядро, CLI и локализация.
- tests/ — поведенческие и интеграционные тесты с REQ-маркерами.
- scripts/ — генерация RTM, проверка трассируемости и версий.
- .github/ — Issue template и workflows.

## Результаты практики №5

- [Отчёт с ответами и скриншотами](PR5_Отчёт_Малинин.md).
- [Скриншоты](docs/pr5-images/README.md).
- [GitHub Project / Kanban](https://github.com/users/konstmalinin-maker/projects/2).
- [Успешный CI с автокоммитом RTM](https://github.com/konstmalinin-maker/requirements-demo/actions/runs/43864521678).
- [Контрольный отказ при покрытии 49,25%](https://github.com/konstmalinin-maker/requirements-demo/actions/runs/43864264093).

54 теста; покрытие 98,5% при пороге 80%; полная команда list на 10000 заметок — 111,1 мс в локальной среде Python 3.12.14/Linux. Проверка трассируемости: 19 требований, 54 собранных теста, PASS. FR-003 обновлён до @v2 вместе с кодом, тестом и changelog.

Дополнительные задания: A — генератор RTM; B — обязательный порог покрытия; C — commitlint/Husky; D — автоматические метки и ссылки в Issues; E — GitHub Project; F — обратная трассируемость; G — проверка версий требований. Фактический статус каждого пункта и ограничения доступа приведены в отчёте.

Файл JSON локальный. Несогласованная параллельная запись не поддерживается. Индивидуальная проверка BR-002 не заменяет исследование удобства с новыми независимыми пользователями.
