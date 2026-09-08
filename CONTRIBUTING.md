# Contributing to Si Sebel

## Before you start

1. Open an issue for a substantial feature or behavior change.
2. Do not include real student data, phone numbers, credentials, WhatsApp
   session files, databases, or logs in commits.
3. Do not add school facts unless they have a documented, verifiable source.

## Development workflow

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m pip install pytest pytest-cov black flake8 mypy
python -m compileall src scripts
python -m pytest tests -q --cov=src --cov-fail-under=30
```

Format changed Python files with Black and run Flake8 before opening a pull
request. Keep changes focused and update documentation when behavior changes.

## Pull requests

Pull requests should describe:

- the problem and the proposed change;
- security, privacy, and data-source impact;
- tests run and their actual results;
- deployment or migration considerations.

The CI workflow must pass. Changes affecting WhatsApp transport, database
schema, or production configuration require explicit rollout and rollback
notes.

