# System Architecture - Si Sebel

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER                                 │
│                    (WhatsApp App)                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ WhatsApp Message
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    WHATSAPP NETWORK                         │
│                   (WhatsApp Server)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ WhatsApp Protocol
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   SI SEBEL BOT SERVER                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           WhatsApp Handler (Library)                 │  │
│  │  - Connection Management                             │  │
│  │  - Message Receiver                                  │  │
│  │  - Message Sender                                   │  │
│  │  - QR Code Generation                               │  │
│  └──────────────────────────┬───────────────────────────┘  │
│                             │                               │
│                             │ Message Event                 │
│                             │                               │
│  ┌──────────────────────────▼───────────────────────────┐  │
│  │           Message Processor                           │  │
│  │  - Parse Message                                     │  │
│  │  - Detect Intent/Command                             │  │
│  │  - Route to Handler                                  │  │
│  └──────────────────────────┬───────────────────────────┘  │
│                             │                               │
│                             │ Intent                        │
│                             │                               │
│  ┌──────────────────────────▼───────────────────────────┐  │
│  │           Intent Handlers                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │ School Info  │  │  Jurusan     │  │ Pendaftaran│  │  │
│  │  │   Handler    │  │  Handler     │  │  Handler   │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │  Kalender    │  │   Kontak     │  │    FAQ     │  │  │
│  │  │  Handler     │  │  Handler     │  │  Handler   │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘  │  │
│  └──────────────────────────┬───────────────────────────┘  │
│                             │                               │
│                             │ Query                         │
│                             │                               │
│  ┌──────────────────────────▼───────────────────────────┐  │
│  │           Knowledge Base Manager                     │  │
│  │  - Search Information                                │  │
│  │  - Format Response                                   │  │
│  │  - Cache Management (Optional)                       │  │
│  └──────────────────────────┬───────────────────────────┘  │
│                             │                               │
│                             │ Data Request                  │
│                             │                               │
│  ┌──────────────────────────▼───────────────────────────┐  │
│  │           Knowledge Base                             │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  SQLite Database / JSON Files                  │  │  │
│  │  │  - School Information                          │  │  │
│  │  │  - Jurusan Data                                │  │  │
│  │  │  - Pendaftaran Info                            │  │  │
│  │  │  - Kalender Akademik                           │  │  │
│  │  │  - Kontak & Fasilitas                          │  │  │
│  │  │  - FAQ Data                                    │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Logger (Optional)                          │  │
│  │  - Conversation Logs                                 │  │
│  │  - Error Logs                                        │  │
│  │  - Usage Statistics                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. WhatsApp Handler
**Responsibility**: Menghandle semua komunikasi dengan WhatsApp

**Functions**:
- `connect()`: Establish connection ke WhatsApp
- `disconnect()`: Close connection
- `send_message(phone, message)`: Kirim pesan
- `on_message_received(callback)`: Event handler untuk pesan masuk
- `on_connection_lost(callback)`: Event handler untuk lost connection
- `generate_qr()`: Generate QR code untuk pairing

**Technology**: 
- PyWhatsApp (wrapper untuk whatsapp-web.js)
- Atau library Python lain seperti pywhatkit, whatsapp-python

**Key Considerations**:
- Auto-reconnect jika connection lost
- Handle rate limiting
- Error handling untuk failed sends

---

### 2. Message Processor
**Responsibility**: Memproses pesan user dan menentukan intent

**Functions**:
- `parse_message(message)`: Parse pesan dari user
- `detect_intent(message)`: Deteksi intent/command
- `route_to_handler(intent)`: Route ke handler yang sesuai
- `validate_message(message)`: Validasi format pesan

**Logic Flow**:
```python
def process_message(message):
    # 1. Check if empty
    if not message or message.strip() == "":
        return "Mohon ketik pesan yang valid"
    
    # 2. Check for menu command
    if message.lower() in ["menu", "help", "?"]:
        return show_main_menu()
    
    # 3. Check for specific commands
    if message.isdigit():
        return handle_menu_selection(int(message))
    
    # 4. Check for keywords
    intent = detect_intent_from_keywords(message)
    if intent:
        return route_to_handler(intent, message)
    
    # 5. Default: search FAQ
    faq_result = search_faq(message)
    if faq_result:
        return faq_result
    
    # 6. Fallback
    return default_response()
```

---

### 3. Intent Handlers
**Responsibility**: Menangani setiap intent/fitur spesifik

#### 3.1 School Info Handler
**Functions**:
- `get_general_info()`: Info umum sekolah
- `get_address()`: Alamat lengkap
- `get_contact_info()`: Nomor telepon, email
- `get_operating_hours()`: Jam operasional
- `get_vision_mission()`: Visi dan misi

#### 3.2 Jurusan Handler
**Functions**:
- `list_jurusan()`: Daftar semua jurusan
- `get_jurusan_detail(jurusan_id)`: Detail jurusan spesifik
- `get_jurusan_requirements(jurusan_id)`: Syarat masuk jurusan
- `get_jurusan_prospects(jurusan_id)`: Prospek karir

#### 3.3 Pendaftaran Handler
**Functions**:
- `get_ppdb_requirements()`: Syarat PPDB
- `get_ppdb_schedule()`: Jadwal pendaftaran
- `get_required_documents()`: Dokumen yang dibutuhkan
- `get_registration_flow()`: Alur pendaftaran
- `get_fee_info()`: Informasi biaya

#### 3.4 Kalender Handler
**Functions**:
- `get_academic_year()`: Tahun ajaran berjalan
- `get_exam_schedule()`: Jadwal ujian
- `get_holidays()`: Hari libur
- `get_events()`: Kegiatan sekolah

#### 3.5 Kontak Handler
**Functions**:
- `get_important_contacts()`: Kontak penting (TU, BK, Humas)
- `get_facilities()`: Fasilitas sekolah
- `get_extracurriculars()`: Ekstrakurikuler
- `get_location_info()`: Lokasi dan transportasi

#### 3.6 FAQ Handler
**Functions**:
- `search_faq(query)`: Cari FAQ berdasarkan query
- `get_popular_faqs()`: FAQ terpopuler
- `get_faq_by_category(category)`: FAQ per kategori

---

### 4. Knowledge Base Manager
**Responsibility**: Manage semua data sekolah

**Functions**:
- `get_school_info(category)`: Get info sekolah
- `get_jurusan_data()`: Get data jurusan
- `get_ppdb_info()`: Get info pendaftaran
- `get_calendar_data()`: Get data kalender
- `get_contact_data()`: Get data kontak
- `search_faqs(query)`: Search FAQ
- `update_data(data_type, data)`: Update data (admin only)

**Data Structure Example**:
```python
# knowledge_base.py
class KnowledgeBase:
    def __init__(self):
        self.school_info = self.load_school_info()
        self.jurusan_data = self.load_jurusan()
        self.ppdb_info = self.load_ppdb()
        self.calendar_data = self.load_calendar()
        self.contact_data = self.load_contact()
        self.faq_data = self.load_faq()
    
    def load_school_info(self):
        # Load from JSON/Database
        pass
    
    def get_school_info(self, category=None):
        if category:
            return self.school_info.get(category)
        return self.school_info
```

---

### 5. Knowledge Base
**Responsibility**: Menyimpan semua data sekolah

**Storage Options**:

#### Option 1: JSON Files (MVP - Recommended)
```
knowledge_base/
├── school_info.json
├── jurusan.json
├── ppdb.json
├── calendar.json
├── contact.json
└── faq.json
```

**Advantages**:
- Sederhana dan mudah di-edit
- Tidak perlu database server
- Mudah untuk version control
- Cepat untuk MVP

**Disadvantages**:
- Tidak scalable untuk data besar
- Tidak ada query complex
- Concurrent update issue

#### Option 2: SQLite Database
```sql
-- Table: school_info
CREATE TABLE school_info (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Table: jurusan
CREATE TABLE jurusan (
    id INTEGER PRIMARY KEY,
    nama TEXT,
    deskripsi TEXT,
    syarat TEXT,
    prospek TEXT
);

-- Table: faq
CREATE TABLE faq (
    id INTEGER PRIMARY KEY,
    pertanyaan TEXT,
    jawaban TEXT,
    keywords TEXT
);
```

**Advantages**:
- Support query complex
- Better performance untuk data besar
- ACID compliance
- Support concurrent access

**Disadvantages**:
- Perlu database knowledge
- Lebih kompleks untuk setup

**Recommendation**: Mulai dengan JSON untuk MVP, upgrade ke SQLite jika perlu.

---

### 6. Logger (Optional)
**Responsibility**: Log aktivitas untuk monitoring dan debugging

**Functions**:
- `log_conversation(phone, message, response)`: Log percakapan
- `log_error(error)`: Log error
- `get_statistics()`: Get statistik penggunaan

**Data Logged**:
- Timestamp
- Phone number (hashed for privacy)
- Message
- Response
- Intent detected
- Response time

**Storage**: SQLite or JSON file

---

## Data Flow

### Normal Conversation Flow
```
1. User sends message
   ↓
2. WhatsApp Handler receives message
   ↓
3. Message Processor parses message
   ↓
4. Intent is detected
   ↓
5. Routed to appropriate Intent Handler
   ↓
6. Handler queries Knowledge Base
   ↓
7. Knowledge Base returns data
   ↓
8. Handler formats response
   ↓
9. WhatsApp Handler sends response
   ↓
10. User receives response
```

### Error Handling Flow
```
1. Error occurs at any stage
   ↓
2. Error is caught and logged
   ↓
3. User-friendly error message sent
   ↓
4. System attempts recovery (reconnect, retry)
   ↓
5. If unrecoverable, admin is notified
```

---

## Technology Stack

### Backend
- **Language**: Python 3.8+
- **WhatsApp Library**: PyWhatsApp atau whatsapp-python
- **Database**: SQLite3 atau JSON files
- **Framework**: Flask (optional, untuk web dashboard)

### Libraries
```python
# requirements.txt
pywhatkit>=0.6.1  # atau library WhatsApp lain
python-dotenv>=0.19.0
sqlite3  # built-in
json  # built-in
logging  # built-in
datetime  # built-in
```

### Development Tools
- Git untuk version control
- VS Code / PyCharm untuk development
- Postman untuk testing (jika ada API)

---

## Deployment Architecture

### Development (Local)
```
PC/Laptop
├── Python Environment
├── Si Sebel Bot
├── Knowledge Base (JSON/SQLite)
└── WhatsApp Connection
```

### Production (Optional - Future)
```
VPS Server
├── Docker Container
│   ├── Python Environment
│   ├── Si Sebel Bot
│   ├── Knowledge Base (SQLite)
│   └── WhatsApp Connection
├── Nginx (optional, untuk web dashboard)
└── SSL Certificate
```

---

## Security Considerations

### Data Privacy
- Hash phone numbers di logs
- Tidak simpan data pribadi user
- Transparent tentang data collection

### WhatsApp Security
- Gunakan nomor khusus, bukan nomor pribadi
- Avoid spam messages
- Follow WhatsApp terms of service
- Monitor untuk banned number

### Server Security
- Use environment variables untuk sensitive data
- Regular backup
- Monitor for suspicious activity

---

## Scalability Considerations

### Current Scale (MVP)
- 50-100 concurrent conversations
- Response time < 5 seconds
- Single server

### Future Scale
- Multiple bot instances
- Load balancer
- Redis untuk caching
- Message queue untuk async processing
- Official WhatsApp API untuk better reliability

---

## Monitoring & Maintenance

### Metrics to Monitor
- Response time
- Error rate
- Number of active conversations
- FAQ hit rate
- System uptime

### Maintenance Tasks
- Regular data updates
- Log rotation
- Backup database
- Update library dependencies
- Monitor WhatsApp connection status

---

## Development Phases

### Phase 1: Core Architecture
- WhatsApp Handler
- Message Processor
- Basic Intent Handlers
- JSON Knowledge Base

### Phase 2: Enhancement
- All Intent Handlers
- FAQ System
- Error Handling
- Logging

### Phase 3: Optimization
- Performance optimization
- Caching
- Better error recovery
- Admin tools

### Phase 4: Production (Optional)
- Cloud deployment
- Monitoring setup
- Backup automation
- Security hardening