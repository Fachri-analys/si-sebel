import sqlite3
from pathlib import Path

from database.connection import DatabaseConnection
from database.migration import run_migrations
from database.models import FAQModel
from handlers.message_processor import IntentType, MessageProcessor


def test_migration_adds_knowledge_base_metadata(tmp_path: Path):
    db_path = tmp_path / "legacy.db"
    connection = sqlite3.connect(db_path)
    connection.execute(
        "CREATE TABLE school_info (id INTEGER PRIMARY KEY, key TEXT, value TEXT)"
    )
    connection.execute("INSERT INTO school_info(key, value) VALUES ('nama', 'Sekolah')")
    connection.commit()
    connection.close()

    db = DatabaseConnection(str(db_path))
    run_migrations(db)

    columns = {
        row["name"]
        for row in db.execute_query("PRAGMA table_info(school_info)", fetch_all=True)
    }
    assert {"is_active", "source", "verified_at", "updated_at"} <= columns
    row = db.execute_query(
        "SELECT is_active, source FROM school_info WHERE key = ?", ("nama",), fetch=True
    )
    assert row == {"is_active": 1, "source": "Belum terverifikasi"}
    db.close()


def test_faq_search_scores_matching_terms(tmp_path: Path):
    db = DatabaseConnection(str(tmp_path / "faq.db"))
    db.initialize_database()
    model = FAQModel(db)
    model.add_faq(
        "Bagaimana cara daftar?", "Daftar melalui PPDB.", "daftar ppdb", priority=1
    )
    model.add_faq("Fasilitas sekolah", "Ada perpustakaan.", "fasilitas", priority=1)

    results = model.search_faq("cara daftar ppdb")
    assert results
    assert results[0]["question"] == "Bagaimana cara daftar?"
    db.close()


def test_message_id_claim_is_persistent_and_backup_is_valid(tmp_path: Path):
    db = DatabaseConnection(str(tmp_path / "messages.db"))
    db.initialize_database()

    assert db.claim_message_id("message-1") is True
    assert db.claim_message_id("message-1") is False

    backup = tmp_path / "backups" / "messages.db"
    db.backup_database(str(backup))
    db.close()

    backup_db = sqlite3.connect(backup)
    assert backup_db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert (
        backup_db.execute("SELECT message_id FROM processed_messages").fetchone()[0]
        == "message-1"
    )
    backup_db.close()


def test_intent_router_prioritizes_specific_domains():
    processor = MessageProcessor.__new__(MessageProcessor)
    processor._init_intent_patterns()
    assert processor._detect_intent("jadwal ujian") == IntentType.CALENDAR
    assert processor._detect_intent("kontak sekolah") == IntentType.CONTACT
    assert processor._detect_intent("2") == IntentType.JURUSAN
    assert processor._detect_intent("pesan tidak dikenali") == IntentType.UNKNOWN


def test_intent_router_supports_flexible_menu_inputs():
    processor = MessageProcessor.__new__(MessageProcessor)
    processor._init_intent_patterns()
    assert processor._detect_intent("1.") == IntentType.SCHOOL_INFO
    assert processor._detect_intent("no 2") == IntentType.JURUSAN
    assert processor._detect_intent("nomor 3") == IntentType.PPDB
    assert processor._detect_intent("menu 4") == IntentType.CALENDAR
    assert processor._detect_intent("pilihan 5") == IntentType.CONTACT
    assert processor._detect_intent("6.") == IntentType.FAQ


def test_intent_router_detects_facilities_and_extracurricular():
    processor = MessageProcessor.__new__(MessageProcessor)
    processor._init_intent_patterns()
    assert processor._detect_intent("fasilitas perpustakaan") == IntentType.FACILITIES
    assert processor._detect_intent("ekskul pramuka") == IntentType.EXTRACURRICULAR


def test_jurusan_response_resolves_common_keywords(tmp_path: Path):
    import asyncio
    from database.models import JurusanModel

    db = DatabaseConnection(str(tmp_path / "jurusan.db"))
    db.initialize_database()
    model = JurusanModel(db)
    model.add_jurusan(
        nama="Akuntansi dan Keuangan Lembaga",
        kode="AKL",
        deskripsi="Belajar akuntansi dan pembukuan.",
        syarat="Teliti",
        prospek="Staf Akuntansi",
        kuota=72,
    )
    model.add_jurusan(
        nama="Manajemen Perkantoran dan Layanan Bisnis",
        kode="MPLB",
        deskripsi="Administrasi perkantoran digital.",
        syarat="Komunikatif",
        prospek="Sekretaris",
        kuota=72,
    )
    model.add_jurusan(
        nama="Pemasaran",
        kode="BR",
        deskripsi="Digital marketing dan bisnis ritel.",
        syarat="Kreatif",
        prospek="Digital Marketer",
        kuota=72,
    )

    processor = MessageProcessor.__new__(MessageProcessor)
    processor.jurusan = model
    processor.logger = None

    # Searching with keyword "akuntansi" should return AKL detail, not general list
    akl_res = asyncio.run(processor._get_jurusan_response("akuntansi"))
    assert "AKUNTANSI DAN KEUANGAN LEMBAGA" in akl_res
    assert "Belajar akuntansi" in akl_res

    # Searching with "perkantoran" should return MPLB detail
    mplb_res = asyncio.run(processor._get_jurusan_response("info jurusan perkantoran"))
    assert "MANAJEMEN PERKANTORAN DAN LAYANAN BISNIS" in mplb_res

    # Searching with "pemasaran" should return Pemasaran detail
    br_res = asyncio.run(processor._get_jurusan_response("pemasaran"))
    assert "PEMASARAN" in br_res

    # Generic request returns full list
    list_res = asyncio.run(processor._get_jurusan_response("jurusan"))
    assert "1. Akuntansi dan Keuangan Lembaga" in list_res
    db.close()


def test_cache_invalidation_on_data_mutation(tmp_path: Path):
    from database.models import (
        JurusanModel,
        ContactModel,
        FacilitiesModel,
        ExtracurricularModel,
        PPDBInfoModel,
    )

    class DummyCache:
        def __init__(self):
            self.deleted_keys = []
            self.deleted_patterns = []
            self.enabled = True

        def get(self, key):
            return None

        def set(self, key, val, ttl=None):
            pass

        def delete(self, key):
            self.deleted_keys.append(key)
            return True

        def delete_pattern(self, pattern):
            self.deleted_patterns.append(pattern)
            return 1

    cache = DummyCache()
    db = DatabaseConnection(str(tmp_path / "cache_test.db"))
    db.initialize_database()

    jurusan_m = JurusanModel(db, cache)
    jurusan_m.add_jurusan("RPL", "RPL", "Rekayasa Perangkat Lunak")
    assert "jurusan:*" in cache.deleted_patterns

    contact_m = ContactModel(db, cache)
    contact_m.add_contact("Pak Budi", "TU", "08123456789")
    assert "contact:*" in cache.deleted_patterns

    facility_m = FacilitiesModel(db, cache)
    facility_m.add_facility("Lab Komputer", "Lab praktikum")
    assert "facilities:*" in cache.deleted_patterns

    ekskul_m = ExtracurricularModel(db, cache)
    ekskul_m.add_extracurricular("Futsal", "Olahraga futsal")
    assert "extracurricular:*" in cache.deleted_patterns

    ppdb_m = PPDBInfoModel(db, cache)
    ppdb_m.set_ppdb_info("jalur", "Prestasi")
    assert "ppdb:*" in cache.deleted_patterns

    db.close()


def test_database_connection_pooling_and_reset(tmp_path: Path):
    from database import get_database, reset_database_instances

    path_a = str(tmp_path / "a.db")
    path_b = str(tmp_path / "b.db")

    db_a1 = get_database(path_a)
    db_a2 = get_database(path_a)
    db_b = get_database(path_b)

    assert db_a1 is db_a2
    assert db_a1 is not db_b
    assert str(db_a1.db_path) == path_a
    assert str(db_b.db_path) == path_b

    reset_database_instances()
