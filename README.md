# Si Sebel

> Chatbot WhatsApp informasi SMKN 11 Jakarta untuk siswa, orang tua, guru, dan masyarakat.

[![CI](https://github.com/Fachri-analys/si-sebel/actions/workflows/ci.yml/badge.svg)](https://github.com/Fachri-analys/si-sebel/actions/workflows/ci.yml)
[![Docker Build](https://github.com/Fachri-analys/si-sebel/actions/workflows/docker-build.yml/badge.svg)](https://github.com/Fachri-analys/si-sebel/actions/workflows/docker-build.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-not%20specified-lightgrey)](https://github.com/Fachri-analys/si-sebel)

## Project status

**Controlled pilot — not yet an unconditional production-ready release.**

The core database, intent routing, validation, rate limiting, persistent
message idempotency, backup verification, healthcheck, and CI checks are
implemented. Provider staging credentials, real webhook testing, monitoring,
dependency locking, and scheduled restore drills are still required before
general production rollout.

Latest local validation:

| Check | Result |
| --- | --- |
| Python compile check | Passed |
| Automated tests | 9 passed |
| Coverage gate | 32.05% (minimum 32%) |
| Docker build | Not run locally; Docker unavailable |
| WhatsApp provider E2E | Pending staging credentials |

## Capabilities

- School information, study programs, PPDB, academic calendar, contacts,
  facilities, extracurricular activities, and FAQ.
- Numeric menu: `1` information umum, `2` jurusan, `3` PPDB, `4` kalender,
  `5` kontak/fasilitas, `6` FAQ.
- Intent routing with domain priority, study-program aliases, FAQ scoring,
  unknown-intent fallback, and lightweight conversation context.
- SQLite migrations with knowledge-base metadata and persistent message
  deduplication.
- Privacy-aware logging, HMAC phone pseudonymization, input validation, rate
  limiting, JSON-only cache payloads, and non-root Docker runtime.
- Atomic database backups with integrity verification and operational
  healthcheck.

## Architecture

```text
WhatsApp provider
        │
        ▼
WhatsApp adapter ──► message processor ──► intent router
        │                                      │
        └──────── response sender ◄────────────┤
                                               ▼
                                      SQLite knowledge base
                                      optional Redis cache
```

The provider adapter is isolated from the chatbot business logic so transport
changes do not require rewriting intent and knowledge-base code.

## Quick start

### Requirements

- Python 3.12+
- A WhatsApp provider account and pairing/session credentials
- SQLite (included with Python)
- Redis 7+ (optional; disable with `ENABLE_CACHE=false`)
- Docker and Docker Compose (optional)

### Local setup

```bash
git clone https://github.com/Fachri-analys/si-sebel.git
cd si-sebel

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.lock
copy config\.env.example config\.env
# Edit config/.env before starting the bot.
python run_bot.py
```

Never commit `config/.env`, provider credentials, WhatsApp auth data, database
files, or logs.

### Docker

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f bot
```

The image runs as a non-root user and exposes a database-backed healthcheck.
Provider readiness still requires a successful staging connection.

## Testing and operations

```bash
python -m compileall src scripts
python -m pytest tests -q --cov=src --cov-report=term-missing
python -m black --check src tests scripts
python -m flake8 src tests scripts --ignore=C901,E402,E501,E704,F401,F811,W291,W503
python scripts/healthcheck.py --database sisebel.db --auth-folder piwapp_auth
```

Database administration:

```bash
python scripts/db_admin.py backup --path sisebel.db --output backups/sisebel.db
python scripts/db_admin.py verify --path backups/sisebel.db
python scripts/db_admin.py prune --path sisebel.db --retention-days 30
```

Read the [operations runbook](docs/OPERATIONS.md) before deploying or
restoring a database.

## Repository layout

```text
.
├── .github/workflows/   # CI and deployment workflows
├── config/              # Environment template and configuration
├── docs/                # Product, architecture, security, and operations docs
├── scripts/             # Healthcheck and database administration commands
├── src/
│   ├── config/          # Typed settings and environment validation
│   ├── database/        # Schema, migrations, models, and seed data
│   ├── handlers/        # Provider adapter and message processing
│   └── utils/           # Security, cache, logging, and reliability utilities
├── tests/               # Automated test suite
├── Dockerfile
├── docker-compose.yml
└── run_bot.py
```

## Documentation

- [Installation guide](docs/INSTALLATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Operations runbook](docs/OPERATIONS.md)
- [Product requirements](docs/PRD.md)
- [Software requirements](docs/SRS.md)
- [CI/CD](docs/CI_CD.md)
- [Security audit](docs/SECURITY_AUDIT.md)
- [Security policy](SECURITY.md)
- [Contributing guide](CONTRIBUTING.md)

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.
All changes should preserve privacy-aware logging, keep tests passing, and
avoid introducing unverified school information.

## License

No open-source license has been declared yet. Until a license is added, all
rights remain with the repository owner.
