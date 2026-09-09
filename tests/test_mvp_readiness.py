import asyncio
from pathlib import Path
import pytest

from database.connection import DatabaseConnection, reset_database_instances
from database.seeder import seed_database
from database.models import (
    SchoolInfoModel,
    JurusanModel,
    FAQModel,
    CalendarModel,
    ContactModel,
    FacilitiesModel,
    ExtracurricularModel,
    PPDBInfoModel,
    ConversationLogModel,
)
from handlers.message_processor import MessageProcessor, IntentType
from utils.security import reset_security_instances


@pytest.fixture
def mvp_setup(tmp_path: Path):
    reset_database_instances()
    reset_security_instances()
    db_file = str(tmp_path / "mvp_test.db")
    db = DatabaseConnection(db_file)
    db.initialize_database()
    seed_database(db, cache=None)

    school_info = SchoolInfoModel(db)
    jurusan = JurusanModel(db)
    faq = FAQModel(db)
    calendar = CalendarModel(db)
    contact = ContactModel(db)
    facilities = FacilitiesModel(db)
    extracurricular = ExtracurricularModel(db)
    ppdb = PPDBInfoModel(db)
    conv_log = ConversationLogModel(db)

    processor = MessageProcessor(
        school_info=school_info,
        jurusan=jurusan,
        faq=faq,
        calendar=calendar,
        contact=contact,
        facilities=facilities,
        extracurricular=extracurricular,
        ppdb=ppdb,
        conversation_log=conv_log,
    )
    yield processor, db
    db.close()
    reset_database_instances()
    reset_security_instances()


def test_mvp_menu_workflow(mvp_setup):
    processor, _ = mvp_setup
    for cmd in ["menu", "help", "?", "halo", "hai", "selamat pagi"]:
        res = asyncio.run(processor.process_message("6281200000001", cmd))
        assert "SI SEBEL - SMKN 11 Jakarta" in res
        assert "1. 📋 Informasi Umum Sekolah" in res
        assert "6. ❓ FAQ" in res


def test_mvp_feature_1_school_info(mvp_setup):
    processor, _ = mvp_setup
    for query in ["1", "1.", "no 1", "info sekolah", "alamat smkn 11", "visi misi"]:
        res = asyncio.run(processor.process_message("6281200000002", query))
        assert "INFORMASI SEKOLAH" in res
        assert "SMK Negeri 11 Jakarta" in res
        assert "Pinangsia" in res
        assert "Visi:" in res
        assert "Misi:" in res


def test_mvp_feature_2_jurusan(mvp_setup):
    processor, _ = mvp_setup
    # List query
    list_res = asyncio.run(processor.process_message("6281200000003", "2"))
    assert "JURUSAN & PROGRAM KEAHLIAN" in list_res
    assert "Akuntansi" in list_res
    assert "Manajemen Perkantoran" in list_res
    assert "Pemasaran" in list_res

    # Detail AKL
    akl_res = asyncio.run(processor.process_message("6281200000003", "akuntansi"))
    assert "AKUNTANSI DAN KEUANGAN LEMBAGA" in akl_res
    assert "Kuota: 72" in akl_res

    # Detail MPLB
    mplb_res = asyncio.run(
        processor.process_message("6281200000003", "info perkantoran")
    )
    assert "MANAJEMEN PERKANTORAN DAN LAYANAN BISNIS" in mplb_res

    # Detail Pemasaran
    pm_res = asyncio.run(processor.process_message("6281200000003", "pemasaran"))
    assert "PEMASARAN" in pm_res


def test_mvp_feature_3_ppdb(mvp_setup):
    processor, _ = mvp_setup
    for query in ["3", "ppdb", "pendaftaran", "syarat masuk", "biaya pendaftaran"]:
        res = asyncio.run(processor.process_message("6281200000004", query))
        assert "INFORMASI PPDB" in res
        assert "ppdb.jakarta.go.id" in res
        assert "Gratis" in res


def test_mvp_feature_4_calendar(mvp_setup):
    processor, _ = mvp_setup
    for query in ["4", "kalender akademik", "jadwal ujian"]:
        res = asyncio.run(processor.process_message("6281200000005", query))
        assert "KALENDER AKADEMIK" in res


def test_mvp_feature_5_contact_facilities_ekskul(mvp_setup):
    processor, _ = mvp_setup
    # Contact query via Menu 5
    contact_res = asyncio.run(processor.process_message("6281200000006", "5"))
    assert "KONTAK SEKOLAH" in contact_res
    assert "Tata Usaha" in contact_res or "smkn11jakarta@gmail.com" in contact_res
    assert "Fasilitas" in contact_res

    # Facilities direct query
    fac_res = asyncio.run(
        processor.process_message("6281200000006", "fasilitas sekolah")
    )
    assert "FASILITAS SEKOLAH" in fac_res

    # Extracurricular direct query
    ekskul_res = asyncio.run(processor.process_message("6281200000006", "ekskul"))
    assert "EKSTRAKURIKULER" in ekskul_res


def test_mvp_feature_6_faq(mvp_setup):
    processor, _ = mvp_setup
    # FAQ search with natural question
    faq_res = asyncio.run(
        processor.process_message("6281200000007", "apakah ada beasiswa kjp plus?")
    )
    assert "FAQ - PERTANYAAN UMUM" in faq_res
    assert "KJP" in faq_res or "beasiswa" in faq_res


def test_mvp_security_and_fallback(mvp_setup):
    processor, _ = mvp_setup
    # SQL injection attempt blocked
    sqli_res = asyncio.run(
        processor.process_message("6281200000008", "admin' UNION SELECT 1,2,3--")
    )
    assert "⚠️" in sqli_res
    assert "Mohon kirim pesan yang valid" in sqli_res

    # Everyday conversational text with double hyphens allowed
    normal_res = asyncio.run(
        processor.process_message(
            "6281200000008", "pagi min -- mau tanya jurusan akuntansi"
        )
    )
    assert "AKUNTANSI" in normal_res

    # Unknown query returns polite fallback
    unknown_res = asyncio.run(
        processor.process_message("6281200000008", "xyz123randomteks")
    )
    assert "Maaf, saya tidak mengerti" in unknown_res
    assert "Ketik 'menu'" in unknown_res
