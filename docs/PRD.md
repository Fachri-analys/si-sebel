# PRD - Si Sebel (Chatbot WhatsApp SMKN 11 Jakarta)

## 1. Overview

### 1.1 Nama Project
Si Sebel - Chatbot Informasi SMKN 11 Jakarta

### 1.2 Deskripsi
Chatbot WhatsApp yang menyediakan informasi lengkap mengenai SMKN 11 Jakarta untuk membantu siswa, guru, orang tua, dan masyarakat yang membutuhkan informasi sekolah secara cepat dan mudah.

### 1.3 Tujuan
- Memudahkan akses informasi SMKN 11 Jakarta melalui WhatsApp
- Mengurangi beban admin sekolah dalam menjawab pertanyaan berulang
- Memberikan layanan informasi 24/7
- Mendukung program digitalisasi sekolah

### 1.4 Target Pengguna
- Siswa baru/potensial siswa
- Siswa aktif SMKN 11 Jakarta
- Guru dan staf sekolah
- Orang tua siswa
- Masyarakat umum

## 2. Problem Statement

### 2.1 Masalah yang Diatasi
- Informasi sekolah tersebar di berbagai platform (website, sosial media, brosur)
- Pertanyaan berulang sering masuk ke admin sekolah
- Respon admin tidak selalu tersedia 24/7
- Informasi sering tidak up-to-date
- Proses mencari informasi kurang efisien

### 2.2 Dampak Masalah
- Waktu admin terbuang untuk menjawab pertanyaan yang sama
- Informasi yang diterima masyarakat kadang tidak akurat
- Kesulitan bagi calon siswa mendapatkan informasi lengkap

## 3. Solution

### 3.1 Fitur Utama (MVP)

#### 3.1.1 Informasi Umum Sekolah
- Alamat lengkap dan peta
- Nomor telepon dan email
- Jam operasional sekolah
- Visi dan misi
- Sejarah singkat sekolah

#### 3.1.2 Informasi Jurusan
- Daftar jurusan yang tersedia
- Deskripsi setiap jurusan
- Syarat masuk setiap jurusan
- Prospek karir setiap jurusan

#### 3.1.3 Informasi Pendaftaran
- Syarat pendaftaran PPDB
- Jadwal pendaftaran
- Dokumen yang dibutuhkan
- Alur pendaftaran
- Biaya pendidikan

#### 3.1.4 Kalender Akademik
- Tahun ajaran berjalan
- Jadwal ujian
- Hari libur nasional
- Kegiatan sekolah penting

#### 3.1.5 Kontak & Fasilitas
- Nomor kontak penting (TU, BK, Humas)
- Fasilitas yang tersedia
- Ekstrakurikuler
- Lokasi dan transportasi

#### 3.1.6 FAQ (Frequently Asked Questions)
- Pertanyaan yang sering diajukan
- Jawaban otomatis berdasarkan keyword

### 3.2 Fitur Tambahan (Future)
- Integrasi dengan sistem absensi
- Pengumuman otomatis
- Jadwal pelajaran per kelas
- Form pengaduan/saran
- Analytics penggunaan

## 4. User Stories

### 4.1 Siswa Baru
- Sebagai calon siswa, saya ingin melihat jurusan yang tersedia
- Sebagai calon siswa, saya ingin tahu syarat pendaftaran
- Sebagai calon siswa, saya ingin tahu biaya pendidikan

### 4.2 Siswa Aktif
- Sebagai siswa aktif, saya ingin cek jadwal ujian
- Sebagai siswa aktif, saya ingin tahu jadwal libur
- Sebagai siswa aktif, saya ingin kontak admin jika darurat

### 4.3 Orang Tua
- Sebagai orang tua, saya ingin tahu kegiatan sekolah anak
- Sebagai orang tua, saya ingin kontak guru/BK
- Sebagai orang tua, saya ingin tahu informasi pembayaran

### 4.4 Admin Sekolah
- Sebagai admin, saya ingin update informasi dengan mudah
- Sebagai admin, saya ingin melihat statistik penggunaan
- Sebagai admin, saya ingin menambah FAQ baru

## 5. User Flow

### 5.1 Flow Pengguna Baru
1. User menambahkan nomor WhatsApp Si Sebel
2. User mengirim pesan "halo" atau "menu"
3. Bot menyapa dan menampilkan menu utama
4. User memilih topik informasi yang diinginkan
5. Bot memberikan informasi yang diminta
6. User bisa lanjut bertanya atau selesai

### 5.2 Flow Pengguna yang Kembali
1. User mengirim pertanyaan langsung
2. Bot mendeteksi intent dari pesan
3. Bot memberikan jawaban yang relevan
4. User bisa follow-up dengan pertanyaan lain

## 6. Non-Functional Requirements

### 6.1 Performance
- Respon bot dalam 3-5 detik
- Dapat menangani 100+ percakapan simultan (MVP)
- Uptime 90% (MVP)

### 6.2 Usability
- Interface sederhana dan intuitif
- Menu jelas dan mudah dinavigasi
- Bahasa Indonesia yang mudah dipahami

### 6.3 Reliability
- Bot tersedia 24/7
- Auto-restart jika crash
- Backup data berkala

### 6.4 Security
- Data pengguna tidak disimpan tanpa izin
- Log percakapan untuk monitoring saja
- Tidak menampilkan informasi sensitif

## 7. Technical Stack

### 7.1 Backend
- Python 3.x
- Framework: Flask/FastAPI (untuk web dashboard jika perlu)
- WhatsApp Library: PyWhatsApp (wrapper untuk whatsapp-web.js) atau library Python lain

### 7.2 Database
- SQLite (MVP) - sederhana, portable
- JSON file untuk knowledge base
- Excel/CSV untuk data management (opsional)

### 7.3 Deployment
- Local server/PC untuk MVP
- Cloud server (VPS) untuk production
- GitHub untuk version control

## 8. Success Metrics

### 8.1 Metrics untuk PKM
- Bot berhasil merespon pertanyaan dengan akurasi >80%
- Minimal 50 pertanyaan terjawab selama periode testing
- User feedback positif dari minimal 20 pengguna
- Dokumentasi lengkap dan reproducible

### 8.2 Metrics untuk Production
- Jumlah pengguna aktif per bulan
- Rasio pertanyaan yang berhasil dijawab
- Response time rata-rata
- User satisfaction score

## 9. Risks & Mitigation

### 9.1 Risks
- Nomor WhatsApp di-banned oleh WhatsApp
- Data informasi sekolah tidak up-to-date
- Bot tidak mengerti pertanyaan kompleks
- Server down/bot tidak aktif

### 9.2 Mitigation
- Gunakan nomor khusus, bukan nomor pribadi
- Buat sistem update data yang mudah untuk admin
- Implementasi FAQ yang komprehensif
- Auto-restart mechanism dan monitoring

## 10. Timeline (MVP)

### Phase 1: Setup & Basic Bot (1-2 minggu)
- Setup environment dan library
- WhatsApp bot basic connection
- Menu sederhana

### Phase 2: Knowledge Base (1-2 minggu)
- Kumpulkan data SMKN 11 Jakarta
- Strukturkan data dalam database/JSON
- Implementasi FAQ system

### Phase 3: Features Implementation (2-3 minggu)
- Implementasi semua fitur MVP
- Testing dan debugging
- User testing dengan siswa/guru

### Phase 4: Documentation & Presentation (1 minggu)
- Dokumentasi teknis
- Video demo
- Presentasi PKM

## 11. Budget Estimation

### Development
- Rp 0 (sudah ada komputer dan internet)
- Nomor WhatsApp khusus: Rp 50.000 (kartu perdana)

### Infrastructure (Optional untuk production)
- VPS: Rp 100.000-300.000/bulan (opsional)
- Domain: Rp 150.000/tahun (opsional)

### Total Estimasi: Rp 50.000 - Rp 500.000 (tergantung kebutuhan)

## 12. Team Roles

- **Project Manager**: Koordinasi, timeline, dokumentasi
- **Backend Developer**: Implementasi bot, logic, database
- **Content/Data Collector**: Kumpulkan data SMKN 11 Jakarta
- **QA/Tester**: Testing fitur, user feedback
- *(Bisa disesuaikan dengan jumlah anggota tim)*