# SRS - Si Sebel (Software Requirements Specification)

## 1. Introduction

### 1.1 Purpose
Dokumen ini mendefinisikan persyaratan teknis dan fungsional untuk pengembangan chatbot WhatsApp "Si Sebel" untuk SMKN 11 Jakarta.

### 1.2 Scope
Chatbot WhatsApp yang dapat menjawab pertanyaan seputar informasi SMKN 11 Jakarta secara otomatis melalui WhatsApp.

### 1.3 Definitions
- **Bot**: Program otomatis yang merespon pesan WhatsApp
- **User**: Pengguna yang mengirim pesan ke bot
- **Intent**: Tujuan atau maksud dari pesan user
- **Knowledge Base**: Database informasi SMKN 11 Jakarta

## 2. Overall Description

### 2.1 Product Perspective
Standalone WhatsApp bot yang berjalan di server lokal/PC dan terhubung ke WhatsApp melalui library open source.

### 2.2 Product Functions
- Menerima pesan masuk dari WhatsApp
- Memproses dan memahami intent pesan
- Mencari jawaban dari knowledge base
- Mengirim respon ke user
- Menyimpan log percakapan (opsional)

### 2.3 User Characteristics
- Tidak perlu install aplikasi tambahan
- Cukup punya WhatsApp
- Beragam latar belakang teknis (siswa, guru, orang tua)

### 2.4 Constraints
- Menggunakan library open source (bukan official API)
- Berjalan di PC/server lokal (MVP)
- Terbatas pada fitur text-based
- Respon tergantung koneksi internet

## 3. Functional Requirements

### 3.1 FR-001: Koneksi WhatsApp
Bot harus dapat:
- Menghubungkan ke WhatsApp menggunakan nomor khusus
- Menampilkan QR code untuk pairing pertama kali
- Menjaga koneksi tetap aktif
- Auto-reconnect jika koneksi terputus

### 3.2 FR-002: Penerimaan Pesan
Bot harus dapat:
- Menerima pesan text dari user
- Menerima pesan dari user baru (belum pernah chat)
- Menerima pesan dari user yang sudah pernah chat
- Handle pesan kosong atau tidak valid

### 3.3 FR-003: Processing Pesan
Bot harus dapat:
- Mendeteksi command menu (misal: "menu", "help", "?")
- Mendeteksi keyword dalam pesan
- Mengirim pesan default jika keyword tidak dikenali
- Handle multiple language (bahasa Indonesia)

### 3.4 FR-004: Menu Utama
Bot harus menampilkan menu utama dengan opsi:
1. Informasi Umum Sekolah
2. Jurusan
3. Pendaftaran
4. Kalender Akademik
5. Kontak & Fasilitas
6. FAQ

### 3.5 FR-005: Informasi Umum Sekolah
Bot harus dapat memberikan:
- Alamat lengkap SMKN 11 Jakarta
- Nomor telepon dan email
- Jam operasional
- Visi dan misi
- Sejarah singkat

### 3.6 FR-006: Informasi Jurusan
Bot harus dapat:
- Menampilkan daftar jurusan yang tersedia
- Memberikan detail jurusan saat user memilih salah satu
- Menampilkan syarat masuk jurusan
- Menampilkan prospek karir jurusan

### 3.7 FR-007: Informasi Pendaftaran
Bot harus dapat:
- Menampilkan syarat pendaftaran PPDB
- Menampilkan jadwal pendaftaran
- Menampilkan dokumen yang dibutuhkan
- Menampilkan alur pendaftaran
- Menampilkan informasi biaya

### 3.8 FR-008: Kalender Akademik
Bot harus dapat:
- Menampilkan tahun ajaran berjalan
- Menampilkan jadwal ujian
- Menampilkan hari libur nasional
- Menampilkan kegiatan sekolah penting

### 3.9 FR-009: Kontak & Fasilitas
Bot harus dapat:
- Menampilkan nomor kontak penting (TU, BK, Humas)
- Menampilkan fasilitas yang tersedia
- Menampilkan ekstrakurikuler
- Menampilkan informasi lokasi dan transportasi

### 3.10 FR-010: FAQ System
Bot harus dapat:
- Menyimpan pertanyaan dan jawaban FAQ
- Mencocokkan pertanyaan user dengan FAQ
- Memberikan jawaban yang relevan
- Menampilkan FAQ terpopuler

### 3.11 FR-011: Pengiriman Respon
Bot harus dapat:
- Mengirim pesan text ke user
- Mengirim pesan dengan format (bold, list, dll)
- Mengirim pesan panjang (terpisah jika perlu)
- Handle gagal kirim pesan

### 3.12 FR-012: Logging (Opsional)
Bot harus dapat:
- Menyimpan log percakapan (user, pesan, respon, timestamp)
- Menyimpan log error
- Menyimpan statistik penggunaan

## 4. Non-Functional Requirements

### 4.1 Performance
- NFR-001: Response time maksimal 5 detik untuk pertanyaan sederhana
- NFR-002: Dapat menangani minimal 50 percakapan simultan (MVP)
- NFR-003: Memory usage maksimal 500MB (MVP)

### 4.2 Reliability
- NFR-004: Uptime minimal 90% (MVP)
- NFR-005: Auto-restart jika bot crash
- NFR-006: Auto-reconnect jika koneksi WhatsApp terputus

### 4.3 Usability
- NFR-007: Menu mudah dinavigasi
- NFR-008: Bahasa Indonesia yang jelas dan mudah dipahami
- NFR-009: Pesan error yang informatif

### 4.4 Maintainability
- NFR-010: Code terstruktur dan mudah dipahami
- NFR-011: Knowledge base mudah di-update tanpa mengubah code
- NFR-012: Dokumentasi lengkap

### 4.5 Security
- NFR-013: Data user tidak disimpan tanpa izin
- NFR-014: Tidak menampilkan informasi sensitif
- NFR-015: Log tidak berisi data pribadi

## 5. System Architecture

### 5.1 High-Level Architecture
```
User (WhatsApp)
    ↓
WhatsApp Network
    ↓
Si Sebel Bot (Python)
    ↓
Knowledge Base (SQLite/JSON)
```

### 5.2 Component Description

#### 5.2.1 WhatsApp Handler
- Menghandle koneksi ke WhatsApp
- Menerima dan mengirim pesan
- Handle events (message received, connection lost, dll)

#### 5.2.2 Message Processor
- Parse pesan dari user
- Deteksi intent/command
- Routing ke handler yang sesuai

#### 5.2.3 Intent Handler
- Handler untuk setiap intent (info sekolah, jurusan, dll)
- Query knowledge base
- Format respon

#### 5.2.4 Knowledge Base Manager
- Manage data sekolah
- CRUD operations untuk FAQ
- Search functionality

#### 5.2.5 Logger (Opsional)
- Log percakapan
- Log error
- Log statistik

## 6. Data Requirements

### 6.1 Knowledge Base Structure

#### 6.1.1 Informasi Sekolah
```json
{
  "nama": "SMKN 11 Jakarta",
  "alamat": "Jl. Bumi No.21, RT.13/RW.2, Gunung, Kec. Kby. Baru, Kota Jakarta Selatan",
  "telepon": "(021) 7221234",
  "email": "info@smkn11jkt.sch.id",
  "jam_operasional": "Senin - Jumat: 07.00 - 16.00",
  "visi": "...",
  "misi": "...",
  "sejarah": "..."
}
```

#### 6.1.2 Jurusan
```json
{
  "jurusan": [
    {
      "id": 1,
      "nama": "Teknik Komputer dan Jaringan",
      "deskripsi": "...",
      "syarat": "...",
      "prospek": "..."
    },
    ...
  ]
}
```

#### 6.1.3 FAQ
```json
{
  "faq": [
    {
      "pertanyaan": "Bagaimana cara mendaftar?",
      "jawaban": "...",
      "keyword": ["daftar", "pendaftaran", "ppdb"]
    },
    ...
  ]
}
```

### 6.2 Database Schema (SQLite)

#### Tabel: conversations_log (opsional)
```sql
CREATE TABLE conversations_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT,
    message TEXT,
    response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabel: faq
```sql
CREATE TABLE faq (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT,
    keywords TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 7. Interface Requirements

### 7.1 User Interface (WhatsApp)
- Text-based conversation
- Menu dengan angka/emoji
- Format pesan yang jelas

### 7.2 Admin Interface (Optional)
- CLI untuk update knowledge base
- Simple web dashboard (future)

## 8. API Specifications

### 8.1 Internal Functions

#### 8.1.1 send_message(phone_number, message)
```python
def send_message(phone_number: str, message: str) -> bool:
    """
    Mengirim pesan ke nomor WhatsApp
    Returns: True jika berhasil, False jika gagal
    """
```

#### 8.1.2 process_message(message)
```python
def process_message(message: str) -> str:
    """
    Memproses pesan user dan mengembalikan respon
    Returns: String respon
    """
```

#### 8.1.3 get_school_info(category)
```python
def get_school_info(category: str) -> dict:
    """
    Mengambil informasi sekolah berdasarkan kategori
    Returns: Dictionary informasi
    """
```

#### 8.1.4 search_faq(query)
```python
def search_faq(query: str) -> list:
    """
    Mencari FAQ berdasarkan query
    Returns: List FAQ yang relevan
    """
```

## 9. Testing Requirements

### 9.1 Unit Testing
- Test setiap fungsi secara terpisah
- Test edge cases (pesan kosong, keyword tidak dikenali, dll)
- Test database operations

### 9.2 Integration Testing
- Test koneksi WhatsApp
- Test flow percakapan lengkap
- Test auto-reconnect

### 9.3 User Acceptance Testing
- Test dengan real user (siswa/guru)
- Kumpulkan feedback
- Perbaiki berdasarkan feedback

## 10. Deployment Requirements

### 10.1 Development Environment
- Python 3.8+
- Library WhatsApp untuk Python
- SQLite3
- Git

### 10.2 Production Environment (Optional)
- VPS dengan OS Linux/Windows
- Python environment
- Database backup
- Monitoring tool

## 11. Documentation Requirements

### 11.1 Technical Documentation
- Architecture diagram
- API documentation
- Setup guide
- Troubleshooting guide

### 11.2 User Documentation
- Cara menggunakan bot
- Panduan menu
- FAQ pengguna

### 11.3 Admin Documentation
- Cara update knowledge base
- Cara restart bot
- Cara monitoring

## 12. Compliance & Standards

### 12.1 WhatsApp Terms of Service
- Menggunakan library open source dengan risiko banned
- Tidak melakukan spam
- Tidak mengirim pesan tanpa request

### 12.2 Data Privacy
- Tidak menyimpan data pribadi user
- Tidak sharing data ke pihak ketiga
- Transparent tentang data collection

## 13. Assumptions & Dependencies

### 13.1 Assumptions
- Nomor WhatsApp khusus tersedia
- Data sekolah dapat diperoleh dari pihak sekolah
- PC/server dengan internet tersedia
- Tim memiliki basic knowledge Python

### 13.2 Dependencies
- Library WhatsApp Python
- Python 3.x
- Internet connection
- WhatsApp service available

## 14. Appendix

### 14.1 Glossary
- **MVP**: Minimum Viable Product
- **PPDB**: Penerimaan Peserta Didik Baru
- **TU**: Tata Usaha
- **BK**: Bimbingan Konseling

### 14.2 References
- WhatsApp Library Documentation
- SMKN 11 Jakarta Website
- Python Documentation