import asyncio
from pathlib import Path

from database.connection import DatabaseConnection
from database.models import (
    CalendarModel,
    ContactModel,
    ConversationLogModel,
    ExtracurricularModel,
    FacilitiesModel,
    FAQModel,
    JurusanModel,
    PPDBInfoModel,
    SchoolInfoModel,
)
from database.seeder import seed_database
from handlers.message_processor import MessageProcessor


def _processor(db: DatabaseConnection) -> MessageProcessor:
    return MessageProcessor(
        school_info=SchoolInfoModel(db),
        jurusan=JurusanModel(db),
        faq=FAQModel(db),
        calendar=CalendarModel(db),
        contact=ContactModel(db),
        facilities=FacilitiesModel(db),
        extracurricular=ExtracurricularModel(db),
        ppdb=PPDBInfoModel(db),
        conversation_log=ConversationLogModel(db),
    )


def test_seeded_mvp_conversation_flow(tmp_path: Path):
    db = DatabaseConnection(str(tmp_path / "mvp.db"))
    db.initialize_database()
    seed_database(db)
    processor = _processor(db)

    cases = {
        "1": "SMK Negeri 11 Jakarta",
        "2": "Jurusan",
        "3": "PPDB",
        "4": "Kalender",
        "5": "Kontak",
        "6": "FAQ",
        "alamat sekolah": "Jl. Pinangsia",
        "jurusan TKJ": "Jurusan",
        "cara daftar PPDB?": "PPDB",
        "jadwal ujian": "Kalender",
        "kontak sekolah": "Kontak",
        "fasilitas sekolah": "Fasilitas",
        "ekskul": "Ekstrakurikuler",
        "pertanyaan yang tidak dikenali": "tidak mengerti",
    }

    for message, expected in cases.items():
        response = asyncio.run(processor.process_message("6281200000000", message))
        assert expected.lower() in response.lower(), message

    assert (
        "empty message"
        in asyncio.run(processor.process_message("6281200000000", "")).lower()
    )
    assert (
        "pesan yang valid"
        in asyncio.run(
            processor.process_message("6281200000000", "<script>alert(1)</script>")
        ).lower()
    )
    db.close()
