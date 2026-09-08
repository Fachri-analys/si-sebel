import sqlite3
from pathlib import Path

from database.connection import DatabaseConnection
from database.migration import run_migrations
from database.models import FAQModel
from handlers.message_processor import IntentType, MessageProcessor


def test_migration_adds_knowledge_base_metadata(tmp_path: Path):
    db_path = tmp_path / "legacy.db"
    connection = sqlite3.connect(db_path)
    connection.execute("CREATE TABLE school_info (id INTEGER PRIMARY KEY, key TEXT, value TEXT)")
    connection.execute("INSERT INTO school_info(key, value) VALUES ('nama', 'Sekolah')")
    connection.commit()
    connection.close()

    db = DatabaseConnection(str(db_path))
    run_migrations(db)

    columns = {row["name"] for row in db.execute_query("PRAGMA table_info(school_info)", fetch_all=True)}
    assert {"is_active", "source", "verified_at", "updated_at"} <= columns
    row = db.execute_query("SELECT is_active, source FROM school_info WHERE key = ?", ("nama",), fetch=True)
    assert row == {"is_active": 1, "source": "Belum terverifikasi"}
    db.close()


def test_faq_search_scores_matching_terms(tmp_path: Path):
    db = DatabaseConnection(str(tmp_path / "faq.db"))
    db.initialize_database()
    model = FAQModel(db)
    model.add_faq("Bagaimana cara daftar?", "Daftar melalui PPDB.", "daftar ppdb", priority=1)
    model.add_faq("Fasilitas sekolah", "Ada perpustakaan.", "fasilitas", priority=1)

    results = model.search_faq("cara daftar ppdb")
    assert results
    assert results[0]["question"] == "Bagaimana cara daftar?"
    db.close()


def test_intent_router_prioritizes_specific_domains():
    processor = MessageProcessor.__new__(MessageProcessor)
    processor._init_intent_patterns()
    assert processor._detect_intent("jadwal ujian") == IntentType.CALENDAR
    assert processor._detect_intent("kontak sekolah") == IntentType.CONTACT
    assert processor._detect_intent("2") == IntentType.JURUSAN
    assert processor._detect_intent("pesan tidak dikenali") == IntentType.UNKNOWN
