# MVP Testing Guide - Si Sebel Bot

## Overview
Comprehensive testing guide for Si Sebel Bot MVP features. This guide ensures all core functionality works correctly before production deployment.

## Pre-Testing Checklist

### Environment Setup
- [ ] Python 3.12+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Redis running (if using cache) or cache disabled
- [ ] Configuration file (.env) configured
- [ ] Logs directory created
- [ ] Database directory accessible

### Configuration Validation
- [ ] WhatsApp phone number configured
- [ ] Bot name configured
- [ ] Database path configured
- [ ] Redis configuration correct (if using cache)
- [ ] Security settings configured
- [ ] Log level set appropriately

---

## Test 1: Bot Initialization

### Objective
Verify bot initializes correctly without errors.

### Steps
```bash
cd "C:\Project 1\si-sebel"
python run_bot.py
```

### Expected Output
```
Initializing Si Sebel Bot...
Environment: development
Bot Name: Si Sebel
Initializing cache system...
Cache system initialized: {...}
Initializing load balancer...
Load balancer initialized: {...}
Initializing security components...
Security components initialized
Security configuration warnings: [...]
Security checklist status: {...}
Initializing database...
Database initialized successfully at sisebel.db
Seeding database with initial data...
Database seeded successfully
Setting up database models...
Database models setup successfully
Setting up message processor...
Message processor setup successfully
Setting up WhatsApp handler...
WhatsApp handler setup successfully
Starting bot...
Waiting for QR code...
```

### Success Criteria
- ✅ No errors during initialization
- ✅ Cache connected (or gracefully disabled)
- ✅ Database initialized
- ✅ All models setup successfully
- ✅ Message processor ready
- ✅ WhatsApp handler ready
- ✅ QR code displayed

### Failure Scenarios
**Error**: "Failed to connect to Redis"
**Solution**: Start Redis or set `ENABLE_CACHE=false`

**Error**: "Failed to initialize database"
**Solution**: Check database path permissions

**Error**: "piwapp library not available"
**Solution**: Install with `pip install piwapp`

---

## Test 2: WhatsApp Connection

### Objective
Verify WhatsApp connection works correctly.

### Steps
1. Start bot (if not already running)
2. Scan QR code with WhatsApp
3. Wait for connection confirmation

### Expected Output
```
QR Code displayed...
[QR Code ASCII Art]
Scan QR code with WhatsApp to connect
Connected! ✓ Online as 628xxxxxxxxxx
```

### Success Criteria
- ✅ QR code displayed correctly
- ✅ QR code scannable
- ✅ Connection established
- ✅ Phone number displayed
- ✅ No connection errors

### Failure Scenarios
**Error**: "QR code not displaying"
**Solution**: Use different terminal (Git Bash, PowerShell)

**Error**: "Connection timeout"
**Solution**: Check internet connection, retry connection

**Error**: "Auth failed"
**Solution**: Delete `piwapp_auth` folder, rescan QR

---

## Test 3: Menu Command

### Objective
Verify menu command works and displays all options.

### Steps
1. Send message: `menu`
2. Wait for response

### Expected Response
```
📚 MENU SI SEBEL

Silakan pilih topik yang ingin Anda tanyakan:

1. 🏫 Info Sekolah - Informasi umum SMKN 11 Jakarta
2. 📚 Jurusan - Daftar program keahlian
3. 📝 PPDB - Informasi pendaftaran
4. 📅 Kalender - Kalender akademik
5. 📞 Kontak - Kontak penting
6. 🏟️ Fasilitas - Fasilitas sekolah
7. ⚽ Ekstrakurikuler - Kegiatan ekstrakurikuler
8. ❓ FAQ - Pertanyaan yang sering diajukan

Ketik nama topik atau angka untuk informasi lebih lanjut.
```

### Success Criteria
- ✅ Response received within 5 seconds
- ✅ All menu items displayed
- ✅ Formatting correct
- ✅ No errors in response

### Failure Scenarios
**Issue**: No response
**Solution**: Check WhatsApp connection, check logs

**Issue**: Incomplete menu
**Solution**: Check database seeding, check models

---

## Test 4: School Info Query

### Objective
Verify school information retrieval works correctly.

### Steps
1. Send message: `info sekolah`
2. Wait for response

### Expected Response
```
🏫 INFORMASI SEKOLAH

Nama: SMKN 11 Jakarta
Alamat: Jl. Bumi No.21, RT.7/RW.2, Petamburan, Kec. Tanah Abang
Kota: Jakarta Pusat
Provinsi: DKI Jakarta
Kode Pos: 10260

📞 Kontak:
Telepon: (021) 3145905
Email: info@smkn11jkt.sch.id

⏰ Jam Operasional:
Senin - Jumat: 07:00 - 16:00
Sabtu: 07:00 - 12:00
Minggu: Tutup

🎯 Visi:
Menjadi SMK unggulan yang menghasilkan lulusan kompeten dan berkarakter.

🎯 Misi:
1. Menyelenggarakan pendidikan vokasi berkualitas
2. Mengembangkan potensi peserta didik
3. Membangun kemitraan dengan dunia industri
```

### Success Criteria
- ✅ Response received within 5 seconds
- ✅ All school information displayed
- ✅ Address, contact, hours correct
- ✅ Vision and mission displayed
- ✅ No errors

### Failure Scenarios
**Issue**: No data returned
**Solution**: Check database seeding, check school_info table

**Issue**: Incomplete information
**Solution**: Verify database data完整性

---

## Test 5: Jurusan Query

### Objective
Verify jurusan information retrieval works correctly.

### Steps
1. Send message: `jurusan`
2. Wait for response
3. Send message: `jurusan tkj`
4. Wait for response

### Expected Response (List)
```
📚 DAFTAR JURUSAN

1. TKJ - Teknik Komputer dan Jaringan
2. TKR - Teknik Kendaraan Ringan
3. RPL - Rekayasa Perangkat Lunak
4. Akuntansi - Akuntansi dan Keuangan
5. Perkantoran - Otomatisasi dan Tata Kelola Perkantoran
6. Multimedia - Multimedia dan Desain Grafis

Ketik nama jurusan untuk detail lebih lanjut.
```

### Expected Response (Detail)
```
📚 JURUSAN: TKJ

Nama: Teknik Komputer dan Jaringan
Deskripsi: Mempelajari jaringan komputer, server, dan keamanan jaringan.

📋 Syarat Pendaftaran:
- Minimal lulusan SMP/MTs
- Nilai rata-rata ≥ 75
- Sehat jasmani dan rohani

🎯 Prospek Karir:
- Network Administrator
- System Administrator
- Security Specialist
- IT Support
- Server Technician

⏰ Durasi: 3 Tahun
📈 Kompetensi Keahlian: 4 SKK
```

### Success Criteria
- ✅ Jurusan list displayed correctly
- ✅ Jurusan details displayed correctly
- ✅ All information complete
- ✅ No errors

### Failure Scenarios
**Issue**: No jurusan data
**Solution**: Check database seeding, check jurusan table

**Issue**: Detail query not working
**Solution**: Check intent detection for specific jurusan

---

## Test 6: PPDB Query

### Objective
Verify PPDB information retrieval works correctly.

### Steps
1. Send message: `ppdb`
2. Wait for response

### Expected Response
```
📝 INFORMASI PPDB

📅 Jadwal Pendaftaran:
Gelombang 1: 1 Maret - 30 April
Gelombang 2: 1 Mei - 30 Juni
Gelombang 3: 1 Juli - 15 Agustus

📋 Syarat Pendaftaran:
1. Fotokopi Ijazah/SKL SMP/MTs
2. Fotokopi Kartu Keluarga
3. Fotokopi Akta Kelahiran
4. Pas foto 3x4 (4 lembar)
5. Surat Keterangan Sehat
6. Nilai Rapor SMP/MTs

💰 Biaya Pendaftaran:
- Formulir: Rp 200.000
- Tes Seleksi: Rp 150.000
- Total: Rp 350.000

📍 Lokasi Pendaftaran:
SMKN 11 Jakarta
Jl. Bumi No.21, Jakarta Pusat
Jam: 08:00 - 15:00

📞 Kontak:
Telp: (021) 3145905
WA: 628xxxxxxxxxx
```

### Success Criteria
- ✅ PPDB information complete
- ✅ Schedule, requirements, costs displayed
- ✅ Contact information included
- ✅ No errors

### Failure Scenarios
**Issue**: No PPDB data
**Solution**: Check database seeding, check ppdb_info table

---

## Test 7: Calendar Query

### Objective
Verify calendar information retrieval works correctly.

### Steps
1. Send message: `kalender`
2. Wait for response

### Expected Response
```
📅 KALENDER AKADEMIK 2024/2025

📅 Tahun Ajaran: 2024/2025

🗓️ Semester 1:
- 15 Juli: Awal tahun ajaran
- 17 Agustus: Upacara Kemerdekaan
- 20-25 Oktober: Ujian Tengah Semester
- 20 Desember - 5 Januari: Libur Natal & Tahun Baru
- 10-20 Desember: Ujian Akhir Semester
- 21 Desember: Libur semester 1

🗓️ Semester 2:
- 6 Januari: Awal semester 2
- 15-20 Maret: Ujian Tengah Semester
- 1-15 April: Libur Ramadhan
- 20-25 Mei: Ujian Akhir Semester
- 1-30 Juni: Libur semester 2
- 15 Juli: Awal tahun ajaran baru
```

### Success Criteria
- ✅ Calendar events displayed
- ✅ Dates and events correct
- ✅ Semester information included
- ✅ No errors

### Failure Scenarios
**Issue**: No calendar data
**Solution**: Check database seeding, check calendar table

---

## Test 8: Contact Query

### Objective
Verify contact information retrieval works correctly.

### Steps
1. Send message: `kontak`
2. Wait for response

### Expected Response
```
📞 KONTAK PENTING

🏫 Sekolah:
Telepon: (021) 3145905
Email: info@smkn11jkt.sch.id
WhatsApp: 628xxxxxxxxxx

👨‍💼 Kepala Sekolah:
Nama: [Nama Kepala Sekolah]
Telepon: (021) 3145906

📚 Pustakawan:
Telepon: (021) 3145907

🏥 UKS:
Telepon: (021) 3145908

📡 Humas:
Telepon: (021) 3145909
Email: humas@smkn11jkt.sch.id

📍 Alamat:
Jl. Bumi No.21, RT.7/RW.2, Petamburan
Jakarta Pusat, DKI Jakarta 10260
```

### Success Criteria
- ✅ All contacts displayed
- ✅ Phone numbers correct
- ✅ Email addresses correct
- ✅ No errors

### Failure Scenarios
**Issue**: No contact data
**Solution**: Check database seeding, check contact table

---

## Test 9: Facilities Query

### Objective
Verify facilities information retrieval works correctly.

### Steps
1. Send message: `fasilitas`
2. Wait for response

### Expected Response
```
🏟️ FASILITAS SEKOLAH

📚 Fasilitas Akademik:
- Ruang Kelas (30 ruang)
- Laboratorium Komputer (5 lab)
- Laboratorium Bahasa (2 lab)
- Perpustakaan
- Ruang Guru
- Ruang Kepala Sekolah

🏟️ Fasilitas Penunjang:
- Lapangan Olahraga
- Musholla
- Kantin
- UKS (Unit Kesehatan Sekolah)
- Toilet
- Parkir Kendaraan

🔧 Fasilitas Praktik:
- Bengkel TKJ
- Bengkel TKR
- Lab RPL
- Lab Akuntansi
- Lab Perkantoran
- Lab Multimedia
```

### Success Criteria
- ✅ All facilities listed
- ✅ Categories correct
- ✅ No errors

### Failure Scenarios
**Issue**: No facilities data
**Solution**: Check database seeding, check facilities table

---

## Test 10: Extracurricular Query

### Objective
Verify extracurricular information retrieval works correctly.

### Steps
1. Send message: `ekstrakurikuler`
2. Wait for response

### Expected Response
```
⚽ EKSTRAKURIKULER

🏅 OSIS (Organisasi Siswa Intra Sekolah)
Deskripsi: Organisasi pengurus kesiswaan
Jadwal: Jumat, 14:00 - 16:00

🏓 Paskibra
Deskripsi: Pasukan pengibar bendera
Jadwal: Selasa & Kamis, 15:00 - 17:00

🎭 Pramuka
Deskripsi: Kegiatan kepramukaan
Jadwal: Sabtu, 08:00 - 12:00

🎵 Rohis
Deskripsi: Kerohanian Islam
Jadwal: Rabu, 14:00 - 16:00

🏀 Basket
Deskripsi: Basket putra dan putri
Jadwal: Senin & Kamis, 15:00 - 17:00

⚽ Futsal
Deskripsi: Futsal putra dan putri
Jadwal: Selasa & Jumat, 15:00 - 17:00
```

### Success Criteria
- ✅ All extracurricular activities listed
- ✅ Schedules included
- ✅ No errors

### Failure Scenarios
**Issue**: No extracurricular data
**Solution**: Check database seeding, check extracurricular table

---

## Test 11: FAQ Query

### Objective
Verify FAQ system works correctly.

### Steps
1. Send message: `faq`
2. Wait for response
3. Send message: `cara daftar`
4. Wait for response

### Expected Response (List)
```
❓ FAQ (Pertanyaan yang Sering Diajukan)

Topik Populer:
- Cara daftar
- Syarat masuk
- Biaya sekolah
- Jurusan apa saja
- Jadwal sekolah

Ketik kata kunci untuk mencari jawaban.
```

### Expected Response (Search)
```
❓ FAQ

Q: Bagaimana cara mendaftar di SMKN 11 Jakarta?
A: Pendaftaran dilakukan secara online melalui website PPDB DKI Jakarta atau langsung ke sekolah dengan membawa berkas yang diperlukan.

Q: Apa syarat untuk masuk?
A: Syaratnya adalah lulusan SMP/MTs dengan nilai rata-rata minimal 75, fotokopi ijazah/SKL, kartu keluarga, akta kelahiran, pas foto, dan surat keterangan sehat.
```

### Success Criteria
- ✅ FAQ list displayed
- ✅ FAQ search works
- ✅ Answers displayed correctly
- ✅ No errors

### Failure Scenarios
**Issue**: No FAQ data
**Solution**: Check database seeding, check faq table

**Issue**: Search not working
**Solution**: Check FAQ search logic in message processor

---

## Test 12: Input Validation

### Objective
Verify input validation blocks malicious inputs.

### Steps
1. Send message: `[DELETE FROM users;]`
2. Wait for response
3. Send message: `[__import__('os').system('rm -rf /')]`
4. Wait for response
5. Send message: `<script>alert('xss')</script>`
6. Wait for response

### Expected Response
```
⚠️ Message contains blocked content. Mohon kirim pesan yang valid.
```

### Success Criteria
- ✅ SQL injection blocked
- ✅ Command injection blocked
- ✅ XSS blocked
- ✅ Security event logged
- ✅ No errors

### Failure Scenarios
**Issue**: Malicious input not blocked
**Solution**: Check input validation logic, check blocked patterns

---

## Test 13: Rate Limiting

### Objective
Verify rate limiting works correctly.

### Steps
1. Send 101 messages within 60 seconds
2. Wait for response after 101st message

### Expected Response
```
⚠️ Rate limit exceeded. Try again in 300s
```

### Success Criteria
- ✅ First 100 messages processed
- ✅ 101st message blocked
- ✅ Block message received
- ✅ Security event logged
- ✅ No errors

### Failure Scenarios
**Issue**: Rate limiting not working
**Solution**: Check rate limiter configuration, check security logger

---

## Test 14: Cache Performance

### Objective
Verify cache improves performance.

### Steps
1. Send message: `info sekolah` (first time)
2. Note response time
3. Send message: `info sekolah` (second time)
4. Note response time
5. Check cache statistics in logs

### Expected Results
- First query: Slower (database hit)
- Second query: Faster (cache hit)
- Cache hit rate: >80%
- Cache hits: >0
- Cache misses: >0

### Success Criteria
- ✅ Cache hit on second query
- ✅ Response time improved
- ✅ Cache statistics logged
- ✅ No errors

### Failure Scenarios
**Issue**: Cache not working
**Solution**: Check Redis connection, check cache manager

---

## Test 15: Graceful Shutdown

### Objective
Verify bot shuts down gracefully.

### Steps
1. Start bot (if not running)
2. Press Ctrl+C
3. Wait for shutdown

### Expected Output
```
Stopping Si Sebel Bot...
Final cache statistics: {...}
Final load balancer statistics: {...}
Si Sebel Bot stopped successfully
```

### Success Criteria
- ✅ Shutdown initiated
- ✅ Resources released
- ✅ Statistics logged
- ✅ No errors
- ✅ Clean exit

### Failure Scenarios
**Issue**: Shutdown hangs
**Solution**: Check signal handlers, check resource cleanup

---

## Test 16: Database Operations

### Objective
Verify database operations work correctly.

### Steps
1. Check database file exists: `ls -lh sisebel.db`
2. Check database tables: Use SQLite browser or `sqlite3 sisebel.db ".tables"`
3. Verify data exists in tables

### Expected Results
- Database file exists
- All tables created
- Data seeded correctly
- No corruption

### Success Criteria
- ✅ Database file present
- ✅ All tables exist
- ✅ Data populated
- ✅ No errors

### Failure Scenarios
**Issue**: Database not created
**Solution**: Check database initialization, check permissions

**Issue**: No data in tables
**Solution**: Check database seeding, check seeder script

---

## Test 17: Security Configuration

### Objective
Verify security configuration is valid.

### Steps
1. Check logs for security warnings
2. Check security checklist status in logs
3. Verify security components initialized

### Expected Results
- Security configuration validated
- Security checklist logged
- Security components active
- Warnings (if any) documented

### Success Criteria
- ✅ Security validation passed
- ✅ Security checklist complete
- ✅ No critical warnings
- ✅ Security components active

### Failure Scenarios
**Issue**: Security validation failed
**Solution**: Check security configuration, fix warnings

---

## Test 18: Logging

### Objective
Verify logging works correctly.

### Steps
1. Send several messages
2. Check log file: `tail -f logs/sisebel.log`
3. Verify logs contain expected information

### Expected Results
- Logs created
- All operations logged
- Security events logged
- Errors logged (if any)

### Success Criteria
- ✅ Log file created
- ✅ All events logged
- ✅ Logs readable
- ✅ No log errors

### Failure Scenarios
**Issue**: Logs not created
**Solution**: Check log directory permissions, check logger configuration

---

## Performance Testing

### Response Time Targets
- Cache hit: <50ms
- Cache miss: <200ms
- Database query: <100ms
- Overall response: <300ms

### Performance Test Steps
1. Send 100 messages (various intents)
2. Measure response times
3. Calculate average
4. Check against targets

### Success Criteria
- ✅ Average response time <300ms
- ✅ P95 response time <500ms
- ✅ P99 response time <1000ms
- ✅ No timeouts

---

## Load Testing

### Load Test Steps
1. Send 1000 messages over 10 minutes
2. Monitor system resources
3. Check for errors
4. Verify stability

### Success Criteria
- ✅ No crashes
- ✅ <1% error rate
- ✅ Response times acceptable
- ✅ System stable

---

## Regression Testing

### Regression Test Steps
1. Run all tests above
2. Document results
3. Fix any issues
4. Re-run tests
5. Verify fixes

### Success Criteria
- ✅ All tests pass
- ✅ No regressions
- ✅ Performance maintained
- ✅ Security maintained

---

## Final Acceptance Criteria

### Must Pass (Critical)
- [ ] Bot initializes without errors
- [ ] WhatsApp connection works
- [ ] All menu commands work
- [ ] All query commands work
- [ ] Input validation works
- [ ] Rate limiting works
- [ ] Graceful shutdown works
- [ ] Database operations work
- [ ] Cache works (if enabled)
- [ ] Security configuration valid

### Should Pass (Important)
- [ ] Response times acceptable
- [ ] Error handling comprehensive
- [ ] Logging comprehensive
- [ ] Performance acceptable
- [ ] No memory leaks
- [ ] No resource leaks

### Nice to Have (Enhancement)
- [ ] Cache hit rate >80%
- [ ] Zero errors in testing
- [ ] All documentation complete
- [ ] Monitoring dashboard

---

## Test Results Template

| Test Case | Status | Notes | Date |
|-----------|--------|-------|------|
| Bot Initialization | ⬜ | | |
| WhatsApp Connection | ⬜ | | |
| Menu Command | ⬜ | | |
| School Info Query | ⬜ | | |
| Jurusan Query | ⬜ | | |
| PPDB Query | ⬜ | | |
| Calendar Query | ⬜ | | |
| Contact Query | ⬜ | | |
| Facilities Query | ⬜ | | |
| Extracurricular Query | ⬜ | | |
| FAQ Query | ⬜ | | |
| Input Validation | ⬜ | | |
| Rate Limiting | ⬜ | | |
| Cache Performance | ⬜ | | |
| Graceful Shutdown | ⬜ | | |
| Database Operations | ⬜ | | |
| Security Configuration | ⬜ | | |
| Logging | ⬜ | | |
| Performance Testing | ⬜ | | |
| Load Testing | ⬜ | | |

---

## Conclusion

This testing guide ensures all MVP features work correctly before production deployment. Follow each test systematically and document results.

**Key Points**:
- Test in order from basic to advanced
- Document all results
- Fix issues before proceeding
- Re-test after fixes
- Maintain test documentation

**Success Criteria**:
- All critical tests pass
- Response times acceptable
- Security validated
- Performance acceptable
- No critical errors

**Next Steps**:
1. Complete all tests
2. Document results
3. Fix any issues
4. Re-test fixes
5. Prepare for production
