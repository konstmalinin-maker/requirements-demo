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
