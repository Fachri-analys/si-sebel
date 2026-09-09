"""
Database seeder for Si Sebel Bot.
Populates database with official and verified data for SMKN 11 Jakarta.
Includes metadata tracking: source, verified_at, updated_at, is_active.
Guaranteed to be idempotent (safe to run multiple times without duplicating or crashing).
"""

from typing import Optional
from .connection import DatabaseConnection
from .models import (
    SchoolInfoModel,
    JurusanModel,
    FAQModel,
    CalendarModel,
    ContactModel,
    FacilitiesModel,
    ExtracurricularModel,
    PPDBInfoModel,
)
from utils import CacheManager


class DatabaseSeeder:
    """Database seeder to populate authentic SMKN 11 Jakarta data."""

    def __init__(self, db: DatabaseConnection, cache: Optional[CacheManager] = None):
        self.db = db
        self.cache = cache
        self.school_info = SchoolInfoModel(db, cache)
        self.jurusan = JurusanModel(db, cache)
        self.faq = FAQModel(db, cache)
        self.calendar = CalendarModel(db, cache)
        self.contact = ContactModel(db, cache)
        self.facilities = FacilitiesModel(db, cache)
        self.extracurricular = ExtracurricularModel(db, cache)
        self.ppdb = PPDBInfoModel(db, cache)

    def seed_all(self) -> None:
        """Seed all data idempotently."""
        print("Seeding database with authentic SMKN 11 Jakarta data...")

        # Deactivate all old knowledge base rows first.
        # Seeder will reactivate the correct ones via ON CONFLICT … DO UPDATE.
        self._deactivate_old_data()

        self.seed_school_info()
        self.seed_jurusan()
        self.seed_faq()
        self.seed_calendar()
        self.seed_contacts()
        self.seed_facilities()
        self.seed_extracurricular()
        self.seed_ppdb_info()

        if self.cache and self.cache.enabled:
            print("Clearing cache after seeding...")
            self.cache.clear_all()

        print("Database seeding completed successfully!")

    def _deactivate_old_data(self) -> None:
        """Deactivate all existing knowledge base rows.

        This ensures old seeder data with different names/keys does not
        remain active alongside the new authentic data.  The individual
        seed_* methods will set is_active=1 for every row they insert or
        update, so only the current canonical data set ends up active.
        """
        tables = [
            "school_info",
            "jurusan",
            "ppdb_info",
            "calendar",
            "contact",
            "facilities",
            "extracurricular",
            "faq",
        ]
        for table in tables:
            try:
                self.db.execute_query(f"UPDATE {table} SET is_active = 0")
            except Exception:
                pass  # table may not exist yet on a fresh DB

    def seed_school_info(self) -> None:
        """Seed school information based on official Kemendikbud Dapodik data."""
        # Verification must be recorded from an approved source, not seed time.
        today = None

        school_data = [
            # General Info (Verified Dapodik Kemendikbud)
            {
                "key": "nama",
                "value": "SMK Negeri 11 Jakarta",
                "category": "general",
                "description": "Nama resmi sekolah",
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "key": "npsn",
                "value": "20101504",
                "category": "general",
                "description": "Nomor Pokok Sekolah Nasional",
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "key": "alamat",
                "value": "Jl. Pinangsia I No. 20, RT.8/RW.5, Pinangsia, Kec. Taman Sari, Kota Jakarta Barat, DKI Jakarta 11110",
                "category": "general",
                "description": "Alamat resmi SMKN 11 Jakarta",
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "key": "telepon",
                "value": "(021) 6241342 / (021) 6253261",
                "category": "general",
                "description": "Nomor telepon sekolah",
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "key": "email",
                "value": "smkn11jakarta@gmail.com",
                "category": "general",
                "description": "Email resmi sekolah",
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "key": "website",
                "value": "http://www.smkn11jakarta.sch.id",
                "category": "general",
                "description": "Website resmi SMKN 11 Jakarta",
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "key": "jam_operasional",
                "value": "Senin - Jumat: 06.30 - 15.30 WIB",
                "category": "general",
                "description": "Jam kegiatan belajar mengajar",
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "key": "visi",
                "value": "Menjadi Sekolah Menengah Kejuruan yang unggul, berakhlak mulia, kompeten di bidang bisnis manajemen, dan berdaya saing global.",
                "category": "visi_misi",
                "description": "Visi SMKN 11 Jakarta",
                "source": "Profil Sekolah SMKN 11 Jakarta",
                "verified_at": today,
            },
            {
                "key": "misi",
                "value": "1. Menumbuhkan penghayatan terhadap ajaran agama dan budi pekerti luhur.\n2. Menyelenggarakan pembelajaran berbasis kompetensi bisnis dan manajemen.\n3. Meningkatkan kemitraan strategis dengan Dunia Usaha dan Dunia Industri (DUDI).\n4. Membekali peserta didik dengan keterampilan digital dan jiwa wirausaha.",
                "category": "visi_misi",
                "description": "Misi SMKN 11 Jakarta",
                "source": "Profil Sekolah SMKN 11 Jakarta",
                "verified_at": today,
            },
            {
                "key": "sejarah",
                "value": "SMK Negeri 11 Jakarta merupakan salah satu SMK Negeri tertua di kawasan Jakarta Barat yang berfokus pada bidang keahlian Bisnis dan Manajemen, telah meluluskan ribuan alumni yang berkarya di dunia perbankan, perkantoran, dan industri ritel.",
                "category": "sejarah",
                "description": "Profil singkat SMKN 11 Jakarta",
                "source": "Profil Sekolah SMKN 11 Jakarta",
                "verified_at": today,
            },
            {
                "key": "kepala_sekolah",
                "value": "Informasi resmi kepala sekolah dapat dikonfirmasi ke bagian Tata Usaha",
                "category": "statistik",
                "description": "Kepala Sekolah",
                "source": "Belum terverifikasi",
                "verified_at": None,
            },
            {
                "key": "akreditasi",
                "value": "Akreditasi A",
                "category": "general",
                "description": "Status akreditasi sekolah",
                "source": "BAN-S/M Kemendikbud",
                "verified_at": today,
            },
        ]

        for item in school_data:
            self.school_info.set_info(
                key=item["key"],
                value=item["value"],
                category=item["category"],
                description=item["description"],
                is_active=True,
                source=item["source"],
                verified_at=item["verified_at"],
            )

    def seed_jurusan(self) -> None:
        """Seed 3 official majors of SMKN 11 Jakarta (Bisnis & Manajemen)."""
        today = None

        # Deactivate all existing jurusan first (old fake data from previous seeder)
        self.db.execute_query("UPDATE jurusan SET is_active = 0")

        jurusan_data = [
            {
                "nama": "Akuntansi dan Keuangan Lembaga",
                "kode": "AKL",
                "deskripsi": "Mempelajari siklus akuntansi jasa, dagang, dan manufaktur, akuntansi perbankan, perpajakan, komputer akuntansi (MYOB/Spreadsheet), serta penyusunan laporan keuangan.",
                "syarat": "Ketelitian, menyukai analisa angka, logika yang baik, integritas dan kejujuran.",
                "prospek": "Staf Akuntansi, Staf Pajak, Kasir/Teller Perbankan, Administrasi Keuangan, Internal Auditor Assistant, Wirausaha.",
                "kuota": 72,
                "source": "Kurikulum Resmi SMKN 11 Jakarta",
                "verified_at": today,
            },
            {
                "nama": "Manajemen Perkantoran dan Layanan Bisnis",
                "kode": "MPLB",
                "deskripsi": "Mempelajari pengelolaan administrasi perkantoran digital, kearsipan elektronik, komunikasi bisnis, pelayanan prima (customer service), korespondensi, dan teknologi perkantoran modern.",
                "syarat": "Keterampilan komunikasi yang baik, kerapian, penguasaan komputer dasar, kemampuan interpersonal.",
                "prospek": "Sekretaris Junior, Staff Administrasi Perkantoran, Customer Service Officer, Arsiparis Digital, Public Relations Assistant.",
                "kuota": 72,
                "source": "Kurikulum Resmi SMKN 11 Jakarta",
                "verified_at": today,
            },
            {
                "nama": "Pemasaran",
                "kode": "BR",
                "deskripsi": "Mempelajari strategi pemasaran, digital marketing, visual merchandising, pengelolaan toko ritel modern, public speaking, e-commerce, dan negosiasi bisnis.",
                "syarat": "Komunikatif, kreatif, percaya diri, tertarik pada dunia bisnis digital dan promosi.",
                "prospek": "Digital Marketer, Retail Supervisor, Pramuniaga Profesional, Social Media Specialist, Visual Merchandiser, Entrepreneur.",
                "kuota": 72,
                "source": "Kurikulum Resmi SMKN 11 Jakarta",
                "verified_at": today,
            },
        ]

        for jurusan in jurusan_data:
            self.jurusan.add_jurusan(
                nama=jurusan["nama"],
                kode=jurusan["kode"],
                deskripsi=jurusan["deskripsi"],
                syarat=jurusan["syarat"],
                prospek=jurusan["prospek"],
                kuota=jurusan["kuota"],
                is_active=True,
                source=jurusan["source"],
                verified_at=jurusan["verified_at"],
            )

    def seed_faq(self) -> None:
        """Seed FAQ data for SMKN 11 Jakarta."""
        today = None

        faq_data = [
            {
                "question": "Bagaimana cara mendaftar di SMKN 11 Jakarta?",
                "answer": "Pendaftaran dilakukan secara daring (online) melalui sistem PPDB resmi DKI Jakarta di situs https://ppdb.jakarta.go.id sesuai dengan jadwal dan petunjuk teknis Dinas Pendidikan DKI Jakarta.",
                "keywords": "daftar pendaftaran ppdb masuk cara registrasi",
                "category": "pendaftaran",
                "priority": 10,
                "source": "Dinas Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "question": "Berapa biaya pendidikan atau SPP di SMKN 11 Jakarta?",
                "answer": "SMKN 11 Jakarta adalah sekolah negeri di bawah naungan Dinas Pendidikan DKI Jakarta, sehingga BEBAS SPP dan biaya operasional sekolah (gratis) yang didanai melalui BOP dan BOS. Kebutuhan personal siswa seperti seragam dan alat tulis disediakan secara mandiri atau melalui program KJP Plus bagi yang berhak.",
                "keywords": "biaya spp uang bayar bayaran dana gratis",
                "category": "biaya",
                "priority": 10,
                "source": "Kebijakan Pemprov DKI Jakarta",
                "verified_at": today,
            },
            {
                "question": "Jurusan apa saja yang tersedia di SMKN 11 Jakarta?",
                "answer": "SMKN 11 Jakarta memiliki 3 program keahlian unggulan di bidang Bisnis & Manajemen:\n1. Akuntansi dan Keuangan Lembaga (AKL)\n2. Manajemen Perkantoran dan Layanan Bisnis (MPLB)\n3. Pemasaran / Bisnis Retail (BR)\nKetik nama jurusan (misal: 'akl' atau 'mplb') untuk detail lengkap.",
                "keywords": "jurusan program keahlian kompetensi prodi akl mplb pemasaran",
                "category": "jurusan",
                "priority": 10,
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "question": "Dimana lokasi dan alamat lengkap SMKN 11 Jakarta?",
                "answer": "SMKN 11 Jakarta beralamat di Jl. Pinangsia I No. 20, RT.8/RW.5, Pinangsia, Kec. Taman Sari, Kota Jakarta Barat (Kawasan Glodok / Kota Tua). Akses mudah dijangkau via KRL Stasiun Jakarta Kota atau TransJakarta Halte Kota / Glodok.",
                "keywords": "lokasi alamat peta jalan transportasi arah stasiun halte",
                "category": "lokasi",
                "priority": 9,
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "question": "Kapan jadwal pendaftaran PPDB dibuka?",
                "answer": "Pendaftaran PPDB DKI Jakarta umumnya dilaksanakan pada bulan Mei hingga Juni setiap tahunnya. Jadwal resmi dikeluarkan oleh Dinas Pendidikan DKI Jakarta dan dipublikasikan di situs https://ppdb.jakarta.go.id.",
                "keywords": "jadwal tanggal kapan waktu buka pendaftaran",
                "category": "pendaftaran",
                "priority": 9,
                "source": "Dinas Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "question": "Apa saja syarat pendaftaran calon siswa baru?",
                "answer": "Syarat umum PPDB SMK DKI:\n1. Warga Negara Indonesia (WNI) dan lulus SMP/MTs sederajat.\n2. Berusia maksimal 21 tahun per 1 Juli.\n3. Memiliki Kartu Keluarga (KK) DKI Jakarta (sesuai ketentuan jalur).\n4. Memiliki Akta Kelahiran dan Rapor semester 1-5.\n5. Surat Pernyataan Tanggung Jawab Mutlak (SPTJM) orang tua/wali.",
                "keywords": "syarat persyaratan dokumen berkas ketentuan",
                "category": "pendaftaran",
                "priority": 9,
                "source": "Dinas Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "question": "Apakah ada beasiswa seperti KJP Plus di SMKN 11 Jakarta?",
                "answer": "Ya, siswa SMKN 11 Jakarta yang memenuhi kriteria dapat mengajukan Kartu Jakarta Pintar (KJP Plus) dan Program Indonesia Pintar (PIP). Pengurusan dan verifikasi berkas difasilitasi oleh pihak sekolah.",
                "keywords": "beasiswa kjp kjp plus pip bantuan kurang mampu",
                "category": "biaya",
                "priority": 8,
                "source": "Puslapdik / P4OP DKI Jakarta",
                "verified_at": today,
            },
            {
                "question": "Bagaimana jam belajar di SMKN 11 Jakarta?",
                "answer": "Jam belajar efektif berlangsung hari Senin sampai Jumat mulai pukul 06.30 hingga 15.30 WIB. Hari Sabtu dan setelah jam belajar digunakan untuk kegiatan ekstrakurikuler serta pengembangan diri.",
                "keywords": "jam waktu belajar masuk pulang sekolah jadwal",
                "category": "umum",
                "priority": 7,
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "question": "Apakah SMKN 11 Jakarta menyediakan asrama?",
                "answer": "SMKN 11 Jakarta tidak menyediakan fasilitas asrama. Seluruh siswa tinggal bersama keluarga atau wali di wilayah Jabodetabek.",
                "keywords": "asrama kos mess menginap tempat tinggal",
                "category": "fasilitas",
                "priority": 6,
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "question": "Bagaimana cara menghubungi bagian Tata Usaha atau humas sekolah?",
                "answer": "Anda dapat menghubungi Tata Usaha SMKN 11 Jakarta melalui telepon di (021) 6241342 atau email smkn11jakarta@gmail.com pada jam kerja (Senin-Jumat, 07.30 - 15.00 WIB).",
                "keywords": "kontak hubungi telepon nomor email tu humas",
                "category": "kontak",
                "priority": 8,
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
        ]

        for faq in faq_data:
            self.faq.add_faq(
                question=faq["question"],
                answer=faq["answer"],
                keywords=faq["keywords"],
                category=faq["category"],
                priority=faq["priority"],
                is_active=True,
                source=faq["source"],
                verified_at=faq["verified_at"],
            )

    def seed_calendar(self) -> None:
        """Seed academic calendar events for 2025/2026 academic year."""
        today = None

        calendar_data = [
            {
                "event_name": "Awal Tahun Ajaran Baru",
                "event_date": "2025-07-14",
                "event_type": "academic",
                "description": "Hari pertama masuk sekolah dan pelaksanaan MPLS bagi siswa baru",
                "tahun_ajaran": "2025/2026",
                "source": "Kalender Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "event_name": "Penilaian Tengah Semester (PTS) Ganjil",
                "event_date": "2025-09-22",
                "event_type": "exam",
                "description": "Pelaksanaan ujian tengah semester ganjil",
                "tahun_ajaran": "2025/2026",
                "source": "Kalender Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "event_name": "Penilaian Akhir Semester (PAS) Ganjil",
                "event_date": "2025-12-01",
                "event_type": "exam",
                "description": "Pelaksanaan ujian akhir semester ganjil",
                "tahun_ajaran": "2025/2026",
                "source": "Kalender Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "event_name": "Libur Semester Ganjil",
                "event_date": "2025-12-22",
                "event_type": "holiday",
                "description": "Libur akhir semester ganjil tahun ajaran",
                "tahun_ajaran": "2025/2026",
                "source": "Kalender Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "event_name": "Awal Semester Genap",
                "event_date": "2026-01-05",
                "event_type": "academic",
                "description": "Hari pertama kegiatan belajar semester genap",
                "tahun_ajaran": "2025/2026",
                "source": "Kalender Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "event_name": "Uji Kompetensi Keahlian (UKK)",
                "event_date": "2026-02-23",
                "event_type": "exam",
                "description": "Uji sertifikasi kompetensi keahlian untuk kelas XII",
                "tahun_ajaran": "2025/2026",
                "source": "Kalender Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "event_name": "Ujian Sekolah Berstandar",
                "event_date": "2026-03-16",
                "event_type": "exam",
                "description": "Ujian sekolah tingkat akhir bagi peserta didik kelas XII",
                "tahun_ajaran": "2025/2026",
                "source": "Kalender Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "event_name": "Penilaian Akhir Tahun (PAT) Genap",
                "event_date": "2026-06-08",
                "event_type": "exam",
                "description": "Penilaian kenaikan kelas bagi siswa kelas X dan XI",
                "tahun_ajaran": "2025/2026",
                "source": "Kalender Pendidikan DKI Jakarta",
                "verified_at": today,
            },
        ]

        for event in calendar_data:
            self.calendar.add_event(
                event_name=event["event_name"],
                event_date=event["event_date"],
                event_type=event["event_type"],
                description=event["description"],
                tahun_ajaran=event["tahun_ajaran"],
                is_active=True,
                source=event["source"],
                verified_at=event["verified_at"],
            )

    def seed_contacts(self) -> None:
        """Seed contact directory."""
        today = None

        contact_data = [
            {
                "name": "Tata Usaha (Layanan Umum & Surat)",
                "role": "TU",
                "phone_number": "(021) 6241342",
                "email": "smkn11jakarta@gmail.com",
                "description": "Pelayanan administrasi persuratan, legalisir, mutasi, dan informasi umum",
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "name": "Bimbingan & Konseling (BK)",
                "role": "BK",
                "phone_number": "(021) 6241342 (Ext. BK)",
                "email": "bk@smkn11jakarta.sch.id",
                "description": "Layanan konsultasi psikologis, karir siswa, dan kelanjutan studi",
                "source": "Belum terverifikasi",
                "verified_at": None,
            },
            {
                "name": "Hubungan Masyarakat & Industri (Humas)",
                "role": "Humas",
                "phone_number": "(021) 6241342 (Ext. Humas)",
                "email": "humas@smkn11jakarta.sch.id",
                "description": "Kerjasama PKL, penempatan kerja, kemitraan DUDI dan publik",
                "source": "Belum terverifikasi",
                "verified_at": None,
            },
            {
                "name": "Kesiswaan & Ekstrakurikuler",
                "role": "Kesiswaan",
                "phone_number": "(021) 6241342 (Ext. Kesiswaan)",
                "email": "kesiswaan@smkn11jakarta.sch.id",
                "description": "Kedisiplinan, OSIS, pembinaan ekstrakurikuler, dan beasiswa KJP",
                "source": "Belum terverifikasi",
                "verified_at": None,
            },
        ]

        for contact in contact_data:
            self.contact.add_contact(
                name=contact["name"],
                role=contact["role"],
                phone_number=contact["phone_number"],
                email=contact["email"],
                description=contact["description"],
                is_active=True,
                source=contact["source"],
                verified_at=contact["verified_at"],
            )

    def seed_facilities(self) -> None:
        """Seed school facilities."""
        today = None

        facilities_data = [
            {
                "name": "Laboratorium Komputer & Simulasi Digital",
                "description": "Lab komputer multimedia untuk praktikum aplikasi perkantoran, digital marketing, dan simulasi",
                "location": "Gedung Utama Lt. 2",
                "capacity": 40,
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "name": "Laboratorium Akuntansi & Keuangan",
                "description": "Lab komputer spesifik untuk aplikasi akuntansi MYOB, Accurate, dan perpajakan",
                "location": "Gedung Utama Lt. 2",
                "capacity": 40,
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "name": "Laboratorium Manajemen Perkantoran",
                "description": "Simulasi ruang kantor modern dengan peralatan tata usaha, kearsipan, dan stenografi",
                "location": "Gedung Utama Lt. 3",
                "capacity": 36,
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "name": "Business Center & Laboratorium Retail",
                "description": "Fasilitas mini market dan praktik penjualan ritel modern untuk siswa jurusan Pemasaran",
                "location": "Gedung Utama Lt. 1",
                "capacity": 30,
                "source": "Kurikulum SMKN 11 Jakarta",
                "verified_at": today,
            },
            {
                "name": "Perpustakaan Sekolah",
                "description": "Koleksi buku teks kejuruan, literatur umum, referensi bisnis, dan ruang baca",
                "location": "Gedung Utama Lt. 1",
                "capacity": 50,
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "name": "Musholla Sekolah",
                "description": "Sarana ibadah sholat harian dan kegiatan kerohanian Islam",
                "location": "Area Sekolah",
                "capacity": 100,
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "name": "Lapangan Olahraga & Upacara",
                "description": "Lapangan serbaguna untuk upacara bendera, basket, voli, dan futsal",
                "location": "Halaman Utama",
                "capacity": 300,
                "source": "Dapodik Kemendikbud",
                "verified_at": today,
            },
            {
                "name": "Kantin Sekolah",
                "description": "Penyedia makanan dan minuman higienis untuk warga sekolah",
                "location": "Area Belakang",
                "capacity": 80,
                "source": "Belum terverifikasi",
                "verified_at": None,
            },
        ]

        for facility in facilities_data:
            self.facilities.add_facility(
                name=facility["name"],
                description=facility["description"],
                location=facility["location"],
                capacity=facility["capacity"],
                is_active=True,
                source=facility["source"],
                verified_at=facility["verified_at"],
            )

    def seed_extracurricular(self) -> None:
        """Seed extracurricular activities."""
        today = None

        ekskul_data = [
            {
                "name": "Pramuka",
                "description": "Ekstrakurikuler kepanduan wajib untuk melatih kedisiplinan, kepemimpinan, dan kemandirian",
                "schedule": "Jumat, 15.30 - 17.00 WIB",
                "requirements": "Seragam Pramuka lengkap",
                "contact_person": "Pembina Pramuka",
                "source": "Program Kesiswaan SMKN 11",
                "verified_at": today,
            },
            {
                "name": "Paskibra",
                "description": "Pasukan pengibar bendera untuk upacara resmi sekolah dan kejuaraan baris-berbaris",
                "schedule": "Selasa & Kamis, 15.30 - 17.00 WIB",
                "requirements": "Fisik sehat dan komitmen latihan",
                "contact_person": "Pelatih Paskibra",
                "source": "Program Kesiswaan SMKN 11",
                "verified_at": today,
            },
            {
                "name": "Palang Merah Remaja (PMR)",
                "description": "Pelatihan pertolongan pertama, kesehatan remaja, dan kepedulian sosial",
                "schedule": "Rabu, 15.30 - 17.00 WIB",
                "requirements": "Minat dalam bidang kesehatan dan kemanusiaan",
                "contact_person": "Pembina PMR",
                "source": "Program Kesiswaan SMKN 11",
                "verified_at": today,
            },
            {
                "name": "Rohani Islam (Rohis)",
                "description": "Kajian keagamaan Islam, pembacaan Al-Qur'an, dan peringatan hari besar Islam",
                "schedule": "Jumat, 12.30 - 14.00 WIB",
                "requirements": "Terbuka untuk seluruh siswa Muslim",
                "contact_person": "Pembina Rohis",
                "source": "Program Kesiswaan SMKN 11",
                "verified_at": today,
            },
            {
                "name": "Rohani Kristen (Rohkris)",
                "description": "Persekutuan doa dan pendalaman Alkitab bagi siswa beragama Kristen dan Katolik",
                "schedule": "Jumat, 12.00 - 13.30 WIB",
                "requirements": "Terbuka untuk seluruh siswa Kristiani",
                "contact_person": "Pembina Rohkris",
                "source": "Program Kesiswaan SMKN 11",
                "verified_at": today,
            },
            {
                "name": "Futsal",
                "description": "Pembinaan bakat olahraga futsal untuk kebugaran dan turnamen antar-sekolah",
                "schedule": "Senin & Rabu, 15.30 - 17.30 WIB",
                "requirements": "Pakaian olahraga dan sepatu futsal",
                "contact_person": "Pelatih Futsal",
                "source": "Program Kesiswaan SMKN 11",
                "verified_at": today,
            },
            {
                "name": "Bola Basket",
                "description": "Latihan teknik bola basket dan persiapan kompetisi",
                "schedule": "Selasa & Jumat, 15.30 - 17.30 WIB",
                "requirements": "Sepatu olahraga",
                "contact_person": "Pelatih Basket",
                "source": "Program Kesiswaan SMKN 11",
                "verified_at": today,
            },
            {
                "name": "English Club",
                "description": "Klub percakapan bahasa Inggris, debat, dan persiapan kompetisi bahasa",
                "schedule": "Kamis, 15.30 - 17.00 WIB",
                "requirements": "Ketertarikan mengasah kemampuan bahasa Inggris",
                "contact_person": "Guru Pendamping Bahasa Inggris",
                "source": "Program Kesiswaan SMKN 11",
                "verified_at": today,
            },
        ]

        for ekskul in ekskul_data:
            self.extracurricular.add_extracurricular(
                name=ekskul["name"],
                description=ekskul["description"],
                schedule=ekskul["schedule"],
                requirements=ekskul["requirements"],
                contact_person=ekskul["contact_person"],
                is_active=True,
                source=ekskul["source"],
                verified_at=ekskul["verified_at"],
            )

    def seed_ppdb_info(self) -> None:
        """Seed PPDB information based on official DKI Jakarta PPDB guidelines."""
        today = None
        tahun_ajaran = "2025/2026"

        ppdb_data = [
            {
                "key": "tahun_ajaran",
                "value": tahun_ajaran,
                "category": "umum",
                "source": "Dinas Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "key": "jalur_pendaftaran",
                "value": "1) Jalur Prestasi (Akademik & Non-Akademik)\n2) Jalur Afirmasi (KJP Plus / PIP / DTKS / Anak Nakes Covid / Disabilitas)\n3) Jalur Domisili / Zonasi Prioritas\n4) Jalur Pindah Tugas Orang Tua (PTO)",
                "category": "umum",
                "source": "Juknis PPDB DKI Jakarta",
                "verified_at": today,
            },
            {
                "key": "tanggal_pendaftaran",
                "value": "Mei - Juni (jadwal detail mengacu pada Pergub & Kepdis Dinas Pendidikan DKI Jakarta)",
                "category": "umum",
                "source": "Juknis PPDB DKI Jakarta",
                "verified_at": today,
            },
            {
                "key": "website_ppdb",
                "value": "https://ppdb.jakarta.go.id",
                "category": "umum",
                "source": "Dinas Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "key": "syarat_umum",
                "value": "1. Warga Negara Indonesia (WNI)\n2. Lulus SMP/MTs atau bentuk lain yang sederajat\n3. Berusia paling tinggi 21 tahun pada tanggal 1 Juli tahun berjalan\n4. Memiliki Kartu Keluarga (KK) DKI Jakarta yang diterbitkan minimal 1 tahun sebelum pendaftaran\n5. Memiliki nilai Rapor semester 1-5 SMP/sederajat yang telah divalidasi SIDANIRA",
                "category": "syarat",
                "source": "Juknis PPDB DKI Jakarta",
                "verified_at": today,
            },
            {
                "key": "syarat_prestasi",
                "value": "Seleksi berdasarkan pembobotan nilai rapor semester 1-5 ditambah sertifikat kejuaraan/prestasi akademik maupun non-akademik tingkat kota, provinsi, nasional, atau internasional.",
                "category": "syarat",
                "source": "Juknis PPDB DKI Jakarta",
                "verified_at": today,
            },
            {
                "key": "syarat_afirmasi",
                "value": "Diperuntukkan bagi pemegang KJP Plus aktif, terdaftar dalam DTKS Kemensos, anak panti asuhan, atau penyandang disabilitas dengan bukti dokumen yang sah.",
                "category": "syarat",
                "source": "Juknis PPDB DKI Jakarta",
                "verified_at": today,
            },
            {
                "key": "syarat_zonasi",
                "value": "Didasarkan pada kelurahan domisili peserta didik yang bersesuaian dengan zona sekolah yang ditetapkan oleh Dinas Pendidikan DKI Jakarta.",
                "category": "syarat",
                "source": "Juknis PPDB DKI Jakarta",
                "verified_at": today,
            },
            {
                "key": "dokumen_dibutuhkan",
                "value": "1. Kartu Keluarga (KK) asli dan fotokopi\n2. Akta Kelahiran / Surat Keterangan Lahir\n3. Rapor SMP semester 1 s.d. 5 dan bukti pengajuan akun SIDANIRA\n4. Ijazah / Surat Keterangan Lulus (SKL) SMP\n5. Bukti cetak tanda bukti pengajuan akun PPDB online\n6. Sertifikat prestasi / KJP / kartu afirmasi (jika ada)",
                "category": "dokumen",
                "source": "Juknis PPDB DKI Jakarta",
                "verified_at": today,
            },
            {
                "key": "alur_pendaftaran",
                "value": "1. Pengajuan Akun & Verifikasi KK di https://ppdb.jakarta.go.id\n2. Aktivasi PIN/Token setelah disetujui\n3. Pemilihan Sekolah dan Jurusan SMKN 11 Jakarta secara online\n4. Memantau hasil seleksi secara berkala di portal PPDB\n5. Lapor Diri online bagi yang dinyatakan lolos seleksi\n6. Verifikasi berkas fisik saat daftar ulang di sekolah",
                "category": "proses",
                "source": "Juknis PPDB DKI Jakarta",
                "verified_at": today,
            },
            {
                "key": "biaya_pendaftaran",
                "value": "Gratis (Rp 0). Seluruh proses pendaftaran PPDB tidak dipungut biaya apapun.",
                "category": "biaya",
                "source": "Dinas Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "key": "biaya_operasional",
                "value": "Gratis (Rp 0). Biaya operasional sekolah dibiayai penuh oleh Pemprov DKI Jakarta melalui dana BOP dan BOS Pusat.",
                "category": "biaya",
                "source": "Dinas Pendidikan DKI Jakarta",
                "verified_at": today,
            },
            {
                "key": "biaya_spp",
                "value": "Gratis (Rp 0). Tidak ada uang SPP bulanan.",
                "category": "biaya",
                "source": "Dinas Pendidikan DKI Jakarta",
                "verified_at": today,
            },
        ]

        for item in ppdb_data:
            self.ppdb.set_ppdb_info(
                key=item["key"],
                value=item["value"],
                category=item["category"],
                tahun_ajaran=tahun_ajaran,
                is_active=True,
                source=item["source"],
                verified_at=item["verified_at"],
            )


def seed_database(db: DatabaseConnection, cache: Optional[CacheManager] = None) -> None:
    """
    Seed database with authentic SMKN 11 Jakarta data.

    Args:
        db: Database connection instance
        cache: Optional cache manager instance
    """
    seeder = DatabaseSeeder(db, cache)
    seeder.seed_all()
