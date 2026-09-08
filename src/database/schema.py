"""
Database schema definitions for Si Sebel Bot.
Contains all SQL schema definitions for SQLite database.
Includes metadata tracking: is_active, source, verified_at, updated_at.
"""

# School Information Table
SCHOOL_INFO_SCHEMA = """
CREATE TABLE IF NOT EXISTS school_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    category TEXT,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    source TEXT DEFAULT 'Belum terverifikasi',
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_school_info_key ON school_info(key);
CREATE INDEX IF NOT EXISTS idx_school_info_category ON school_info(category);
CREATE INDEX IF NOT EXISTS idx_school_info_active ON school_info(is_active);
"""

# Jurusan Table
JURUSAN_SCHEMA = """
CREATE TABLE IF NOT EXISTS jurusan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT UNIQUE NOT NULL,
    kode TEXT,
    deskripsi TEXT,
    syarat TEXT,
    prospek TEXT,
    kuota INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    source TEXT DEFAULT 'Belum terverifikasi',
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_jurusan_nama ON jurusan(nama);
CREATE INDEX IF NOT EXISTS idx_jurusan_kode ON jurusan(kode);
CREATE INDEX IF NOT EXISTS idx_jurusan_active ON jurusan(is_active);
"""

# PPDB Information Table
PPDB_INFO_SCHEMA = """
CREATE TABLE IF NOT EXISTS ppdb_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    category TEXT,
    tahun_ajaran TEXT DEFAULT '2025/2026',
    is_active BOOLEAN DEFAULT 1,
    source TEXT DEFAULT 'Belum terverifikasi',
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(key)
);

CREATE INDEX IF NOT EXISTS idx_ppdb_key ON ppdb_info(key);
CREATE INDEX IF NOT EXISTS idx_ppdb_category ON ppdb_info(category);
CREATE INDEX IF NOT EXISTS idx_ppdb_active ON ppdb_info(is_active);
"""

# Calendar/Academic Events Table
CALENDAR_SCHEMA = """
CREATE TABLE IF NOT EXISTS calendar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL,
    event_date DATE NOT NULL,
    event_type TEXT NOT NULL,
    description TEXT,
    tahun_ajaran TEXT DEFAULT '2025/2026',
    is_active BOOLEAN DEFAULT 1,
    source TEXT DEFAULT 'Belum terverifikasi',
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_name, tahun_ajaran)
);

CREATE INDEX IF NOT EXISTS idx_calendar_date ON calendar(event_date);
CREATE INDEX IF NOT EXISTS idx_calendar_type ON calendar(event_type);
CREATE INDEX IF NOT EXISTS idx_calendar_active ON calendar(is_active);
"""

# Contact Information Table
CONTACT_SCHEMA = """
CREATE TABLE IF NOT EXISTS contact (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    phone_number TEXT,
    email TEXT,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    source TEXT DEFAULT 'Belum terverifikasi',
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, role)
);

CREATE INDEX IF NOT EXISTS idx_contact_role ON contact(role);
CREATE INDEX IF NOT EXISTS idx_contact_active ON contact(is_active);
"""

# Facilities Table
FACILITIES_SCHEMA = """
CREATE TABLE IF NOT EXISTS facilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    location TEXT,
    capacity INTEGER,
    is_active BOOLEAN DEFAULT 1,
    source TEXT DEFAULT 'Belum terverifikasi',
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_facilities_name ON facilities(name);
CREATE INDEX IF NOT EXISTS idx_facilities_active ON facilities(is_active);
"""

# Extracurricular Table
EXTRACURRICULAR_SCHEMA = """
CREATE TABLE IF NOT EXISTS extracurricular (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    schedule TEXT,
    requirements TEXT,
    contact_person TEXT,
    is_active BOOLEAN DEFAULT 1,
    source TEXT DEFAULT 'Belum terverifikasi',
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_extracurricular_name ON extracurricular(name);
CREATE INDEX IF NOT EXISTS idx_extracurricular_active ON extracurricular(is_active);
"""

# FAQ Table
FAQ_SCHEMA = """
CREATE TABLE IF NOT EXISTS faq (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT UNIQUE NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT,
    category TEXT,
    priority INTEGER DEFAULT 0,
    hit_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    source TEXT DEFAULT 'Belum terverifikasi',
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_faq_keywords ON faq(keywords);
CREATE INDEX IF NOT EXISTS idx_faq_category ON faq(category);
CREATE INDEX IF NOT EXISTS idx_faq_priority ON faq(priority DESC);
CREATE INDEX IF NOT EXISTS idx_faq_active ON faq(is_active);
"""

# Conversation Log Table (Optional)
CONVERSATION_LOG_SCHEMA = """
CREATE TABLE IF NOT EXISTS conversation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number_hash TEXT NOT NULL,
    message TEXT NOT NULL,
    response TEXT,
    intent_detected TEXT,
    response_time_ms INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversation_phone ON conversation_log(phone_number_hash);
CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON conversation_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_conversation_intent ON conversation_log(intent_detected);
"""

PROCESSED_MESSAGES_SCHEMA = """
CREATE TABLE IF NOT EXISTS processed_messages (
    message_id TEXT PRIMARY KEY,
    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_processed_messages_at
    ON processed_messages(processed_at);
"""

# Combined Schema
ALL_SCHEMAS = [
    SCHOOL_INFO_SCHEMA,
    JURUSAN_SCHEMA,
    PPDB_INFO_SCHEMA,
    CALENDAR_SCHEMA,
    CONTACT_SCHEMA,
    FACILITIES_SCHEMA,
    EXTRACURRICULAR_SCHEMA,
    FAQ_SCHEMA,
    CONVERSATION_LOG_SCHEMA,
    PROCESSED_MESSAGES_SCHEMA,
]

MIGRATION_SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""