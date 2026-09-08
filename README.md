# Si Sebel - Chatbot WhatsApp SMKN 11 Jakarta

Chatbot WhatsApp yang menyediakan informasi lengkap mengenai SMKN 11 Jakarta untuk siswa, guru, orang tua, dan masyarakat.

## Status Controlled Pilot

Database migration, intent routing, input validation, rate limiting, and WhatsApp
message deduplication are covered by automated tests. The current local run has
7 passing tests with 31% total coverage. This is not a production-ready claim:
provider/webhook integration, operational observability, and broader business
scenario coverage still require staging validation.

Run tests with:

```bash
python -m pytest tests -q --cov=src --cov-report=term-missing
```

## Database operations

Run these commands from the project root:

```bash
python scripts/db_admin.py backup --path sisebel.db --output backups/sisebel.db
python scripts/db_admin.py verify --path backups/sisebel.db
python scripts/db_admin.py prune --path sisebel.db --retention-days 30
```

The backup command performs an SQLite integrity check and prints a SHA-256
checksum. Store backups outside the application container and test restores
before relying on them for recovery.

## 📋 Overview

**Nama Project**: Si Sebel  
**Tujuan**: Memberikan informasi SMKN 11 Jakarta melalui WhatsApp 24/7  
**Target**: Siswa, guru, orang tua, masyarakat  
**Teknologi**: Python, WhatsApp Library (Open Source), SQLite, Redis Caching, CI/CD

## 🌟 Features

### Core Features (MVP)
- Informasi Umum Sekolah
- Informasi Jurusan (6 jurusan dengan detail)
- Informasi Pendaftaran (PPDB)
- Kalender Akademik
- Kontak & Fasilitas
- FAQ System dengan auto-response

### Advanced Features
- **Redis Caching**: Distributed caching untuk performance tinggi
- **Load Balancing**: Rate limiting dan connection pooling
- **CI/CD Pipeline**: Automated testing dan deployment dengan GitHub Actions
- **Docker Support**: Containerized deployment dengan Docker Compose
- **Monitoring**: Comprehensive logging dan cache statistics

## 🎯 Fitur Utama (MVP)

1. **Informasi Umum Sekolah** - Alamat, kontak, jam operasional, visi misi
2. **Informasi Jurusan** - Daftar jurusan, deskripsi, syarat, prospek
3. **Informasi Pendaftaran** - Syarat PPDB, jadwal, dokumen, biaya
4. **Kalender Akademik** - Tahun ajaran, jadwal ujian, libur, kegiatan
5. **Kontak & Fasilitas** - Kontak penting, fasilitas, ekstrakurikuler
6. **FAQ System** - Pertanyaan yang sering diajukan dengan auto-response

## 📁 Project Structure

```
si-sebel/
├── docs/                          # Dokumentasi project
│   ├── PRD.md                    # Product Requirements Document
│   ├── SRS.md                    # Software Requirements Specification
│   ├── ROADMAP.md                # Timeline dan phase development
│   ├── ARCHITECTURE.md           # System architecture
│   ├── INSTALLATION.md           # Installation guide
│   ├── CACHING.md                # Caching system documentation
│   └── CI_CD.md                  # CI/CD pipeline documentation
├── src/                           # Source code
│   ├── bot.py                    # Main bot application
│   ├── config/                   # Configuration management
│   │   ├── settings.py           # Application settings
│   │   └── __init__.py
│   ├── database/                 # Database layer
│   │   ├── connection.py         # Database connection
│   │   ├── schema.py             # Database schema
│   │   ├── models.py             # Database models with caching
│   │   ├── seeder.py             # Database seeder
│   │   └── __init__.py
│   ├── handlers/                 # Message handlers
│   │   ├── whatsapp_handler.py   # WhatsApp connection handler
│   │   ├── message_processor.py # Message processor
│   │   └── __init__.py
│   ├── utils/                    # Utility functions
│   │   ├── logger.py             # Logging utility
│   │   ├── exceptions.py         # Custom exceptions
│   │   ├── cache.py              # Redis caching system
│   │   ├── load_balancer.py      # Load balancing & rate limiting
│   │   └── __init__.py
│   └── models/                   # Data models
│       └── __init__.py
├── config/                        # Configuration files
│   ├── .env.example              # Environment variables template
│   └── .env                      # Environment variables (not in git)
├── .github/                       # GitHub Actions CI/CD
│   └── workflows/
│       ├── ci.yml                # Testing and linting workflow
│       ├── cd.yml                # Deployment workflow
│       └── docker-build.yml      # Docker build workflow
├── logs/                          # Log files directory
├── tests/                         # Test files
├── requirements.txt               # Python dependencies
├── run_bot.py                    # Bot run script
├── Dockerfile                     # Docker container definition
├── docker-compose.yml             # Docker Compose configuration
├── .gitignore                    # Git ignore file
└── README.md                     # File ini
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ (REQUIRED - piwapp library requires Python 3.12+)
- Pip (Python package manager)
- Git
- Redis Server (for caching) - or disable caching
- Nomor WhatsApp khusus untuk bot

### Installation

Detailed installation guide available in [docs/INSTALLATION.md](docs/INSTALLATION.md)

Quick steps:
1. Clone repository
```bash
git clone <repository-url>
cd si-sebel
```

2. Create virtual environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Setup Redis (for caching)
```bash
# Option 1: Docker (Recommended)
docker run -d -p 6379:6379 --name sisebel-redis redis:7-alpine

# Option 2: Docker Compose
docker-compose up -d redis

# Option 3: Skip Redis (disable caching)
# Set ENABLE_CACHE=false in config/.env
```

5. Setup configuration
```bash
copy config\.env.example config\.env  # Windows
# or
cp config/.env.example config/.env  # Linux/Mac
# Edit .env dengan konfigurasi yang sesuai
```

6. Run bot
```bash
# Option 1: Direct Python
python run_bot.py

# Option 2: Docker Compose
docker-compose up -d bot
```

7. Scan QR code dengan WhatsApp untuk pairing

## 📖 Documentation

### User Documentation
- [MVP_WORKFLOW.md](docs/MVP_WORKFLOW.md) - Comprehensive workflow documentation for all MVP features
- [MVP_TESTING_GUIDE.md](docs/MVP_TESTING_GUIDE.md) - Complete testing guide with 18 test cases
- [INSTALLATION.md](docs/INSTALLATION.md) - Installation guide
- [PRD.md](docs/PRD.md) - Product Requirements Document
- [SRS.md](docs/SRS.md) - Software Requirements Specification
- [ROADMAP.md](docs/ROADMAP.md) - Timeline dan phase development

### Technical Documentation
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
- [CACHING.md](docs/CACHING.md) - Caching system documentation
- [CI_CD.md](docs/CI_CD.md) - CI/CD pipeline documentation

### Security Documentation
- [SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md) - OWASP Top 10 security audit
- [SECURITY_CHECKLIST.md](docs/SECURITY_CHECKLIST.md) - Security checklist
- [PROMPT_INJECTION_ANALYSIS.md](docs/PROMPT_INJECTION_ANALYSIS.md) - Injection attack analysis
- [LOGIC_VALIDATION.md](docs/LOGIC_VALIDATION.md) - Logic validation report
- [HIGH_MEDIUM_PRIORITY_STATUS.md](docs/HIGH_MEDIUM_PRIORITY_STATUS.md) - Security improvements status

## 🛠️ Technology Stack

- **Language**: Python 3.12+ (REQUIRED)
- **WhatsApp Library**: piwapp (Pure Python WhatsApp client)
- **Database**: SQLite
- **Caching**: Redis (distributed caching for performance)
- **Configuration**: pydantic-settings
- **Logging**: colorlog (colored console logs)
- **Async**: asyncio (for async operations)
- **CI/CD**: GitHub Actions (automated testing & deployment)
- **Containerization**: Docker & Docker Compose
- **Load Balancing**: Built-in rate limiting and connection pooling

## 👥 Team Roles

- **Project Manager**: Koordinasi, timeline, dokumentasi
- **Backend Developer**: Implementasi bot, logic, database
- **Data Collector**: Kumpulkan data SMKN 11 Jakarta
- **QA/Tester**: Testing fitur, user feedback

## 📅 Timeline

Total: 6-8 minggu untuk MVP

- **Week 1-2**: Setup & Basic Bot
- **Week 3-4**: Knowledge Base & Data Collection
- **Week 5-6**: Features Implementation
- **Week 7**: User Testing & Refinement
- **Week 8**: Documentation & Presentation

Detail timeline ada di [ROADMAP.md](docs/ROADMAP.md)

## 🎯 Success Metrics

- Akurasi jawaban > 80%
- Response time < 5 detik
- Minimal 50 pertanyaan terjawab selama testing
- Minimal 20 user testing
- User feedback positif > 70%

## ⚠️ Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Nomor WhatsApp di-banned | Gunakan nomor khusus, avoid spam |
| Data sekolah tidak lengkap | Koordinasi dengan pihak sekolah sejak awal |
| Library tidak stabil | Pilih library yang aktif, punya fallback |
| Timeline terlambat | Buffer time di setiap phase |

## 📝 Development Status

### Phase 1: Core Features ✅
- [x] Project Structure
- [x] PRD Documentation
- [x] SRS Documentation
- [x] Roadmap Documentation
- [x] Architecture Documentation
- [x] Installation Documentation
- [x] Environment Setup
- [x] Configuration Management
- [x] Database Schema & Models
- [x] WhatsApp Connection Handler
- [x] Message Processor
- [x] Basic Menu System
- [x] Main Bot Application
- [x] Database Seeder (Sample Data)

### Phase 2: Advanced Features ✅
- [x] Redis Caching System
- [x] Cache Integration to Database Models
- [x] Load Balancing Preparation
- [x] Rate Limiting System
- [x] Connection Pooling
- [x] Health Checking System

### Phase 3: DevOps ✅
- [x] GitHub Actions CI Pipeline
- [x] GitHub Actions CD Pipeline
- [x] Docker Containerization
- [x] Docker Compose Configuration
- [x] Automated Testing Workflow
- [x] Automated Linting Workflow
- [x] Security Scanning Workflow

### Phase 4: Documentation ✅
- [x] Caching System Documentation
- [x] CI/CD Pipeline Documentation
- [x] Updated Installation Guide
- [x] Updated README

### Phase 5: Testing & Deployment 🔄
- [ ] Unit Tests Implementation
- [ ] Integration Tests
- [ ] User Testing
- [ ] Performance Testing
- [ ] Production Deployment
- [ ] Monitoring Setup

## 🤝 Contributing

Ini adalah project untuk PKM, silakan ikuti roadmap yang sudah ditentukan dan komunikasi dengan team sebelum membuat changes.

## 📄 License

Project ini dibuat untuk keperluan PKM SMKN 11 Jakarta.

## 📞 Contact

Untuk pertanyaan mengenai project ini, silakan hubungi team pengembang.

---

**Dibuat untuk PKM SMKN 11 Jakarta**  
*Made with ❤️ by Si Sebel Team*