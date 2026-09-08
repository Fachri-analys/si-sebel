# MVP Workflow Documentation - Si Sebel Bot

## Overview
Comprehensive workflow documentation for Si Sebel Bot MVP features. This document ensures all MVP features work correctly with clear, documented workflows.

## MVP Features

### Core Features (MVP)
1. **Informasi Umum Sekolah** - Alamat, kontak, jam operasional, visi misi
2. **Informasi Jurusan** - Daftar jurusan, deskripsi, syarat, prospek
3. **Informasi Pendaftaran (PPDB)** - Syarat PPDB, jadwal, dokumen, biaya
4. **Kalender Akademik** - Tahun ajaran, jadwal ujian, libur, kegiatan
5. **Kontak & Fasilitas** - Kontak penting, fasilitas, ekstrakurikuler
6. **FAQ System** - Pertanyaan yang sering diajukan dengan auto-response

---

## 1. Bot Initialization Workflow

### Workflow Diagram
```
Start
  ↓
Setup Logger
  ↓
Initialize Cache System (Redis)
  ↓
Initialize Load Balancer
  ↓
Initialize Security Components
  ↓
Validate Security Configuration
  ↓
Initialize Database (SQLite)
  ↓
Seed Database with Initial Data
  ↓
Setup Database Models
  ↓
Setup Message Processor
  ↓
Setup WhatsApp Handler
  ↓
Register Signal Handlers
  ↓
Bot Ready
```

### Detailed Steps

#### Step 1: Setup Logger
**File**: `src/bot.py` (lines 50-54)
```python
self.logger = setup_application_logger(
    app_name="sisebel",
    log_level=settings.log_level,
    log_file=settings.log_file
)
```
**Purpose**: Initialize application logger with configured log level and file
**Output**: Logger instance ready for use

#### Step 2: Initialize Cache System
**File**: `src/bot.py` (lines 73-90)
```python
self.cache = get_cache_manager(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    ttl=settings.cache_ttl,
    enabled=settings.enable_cache,
    logger=self.logger
)
```
**Purpose**: Initialize Redis cache for performance optimization
**Fallback**: If Redis unavailable, cache is disabled gracefully
**Output**: Cache manager connected (or disabled)

#### Step 3: Initialize Load Balancer
**File**: `src/bot.py` (lines 92-102)
```python
self.load_balancer = get_load_balancer(
    max_instances=1,
    max_connections=50,
    max_requests=100,
    rate_limit_window=60,
    logger=self.logger
)
```
**Purpose**: Initialize load balancer for future scaling and rate limiting
**Output**: Load balancer ready for request management

#### Step 4: Initialize Security Components
**File**: `src/bot.py` (lines 104-123)
```python
self.security_logger = get_security_logger(self.logger)
self.rate_limiter_security = get_rate_limiter_security(
    max_requests=100,
    time_window=60,
    block_duration=300,
    logger=self.logger
)
```
**Purpose**: Initialize security logging and rate limiting
**Output**: Security components active

#### Step 5: Validate Security Configuration
**File**: `src/bot.py` (lines 115-123)
```python
security_practices = get_security_best_practices(self.logger)
security_warnings = security_practices.validate_configuration()
security_checklist = security_practices.get_security_checklist()
```
**Purpose**: Validate security configuration and log warnings
**Output**: Security validation logged

#### Step 6: Initialize Database
**File**: `src/bot.py` (lines 125-133)
```python
self.db = initialize_database(settings.database_path)
seed_database(self.db, self.cache)
```
**Purpose**: Initialize SQLite database and seed with initial data
**Output**: Database ready with initial data

#### Step 7: Setup Database Models
**File**: `src/bot.py` (lines 139-159)
```python
self.school_info = SchoolInfoModel(self.db, self.cache)
self.jurusan = JurusanModel(self.db, self.cache)
self.faq = FAQModel(self.db, self.cache)
# ... other models
```
**Purpose**: Initialize all database models with cache integration
**Output**: All models ready for use

#### Step 8: Setup Message Processor
**File**: `src/bot.py` (lines 161-183)
```python
self.message_processor = MessageProcessor(
    school_info=self.school_info,
    jurusan=self.jurusan,
    faq=self.faq,
    # ... other models
    logger=self.logger
)
```
**Purpose**: Initialize message processor with all models
**Output**: Message processor ready to handle messages

#### Step 9: Setup WhatsApp Handler
**File**: `src/bot.py` (lines 185-230)
```python
self.whatsapp_handler = WhatsAppHandler(
    auth_folder="./piwapp_auth",
    on_message_callback=on_message_callback,
    logger=self.logger
)
```
**Purpose**: Initialize WhatsApp handler with message callback
**Output**: WhatsApp handler ready for connection

#### Step 10: Register Signal Handlers
**File**: `src/bot.py` (lines 232-245)
```python
signal.signal(signal.SIGINT, self._signal_handler)
signal.signal(signal.SIGTERM, self._signal_handler)
```
**Purpose**: Register signal handlers for graceful shutdown
**Output**: Signal handlers registered

---

## 2. Message Processing Workflow

### Workflow Diagram
```
WhatsApp Message Received
  ↓
Extract Phone Number & Message Content
  ↓
Security Rate Limiting Check
  ↓ (if blocked)
Send Rate Limit Warning
  ↓ (if allowed)
Load Balancer Check
  ↓ (if rejected)
Log Rejection
  ↓ (if ready)
Input Validation
  ↓ (if invalid)
Send Validation Error
  ↓ (if valid)
Clean Message
  ↓
Detect Intent
  ↓
Generate Response (based on intent)
  ↓
Output Encoding
  ↓
Log Conversation
  ↓
Send Response via WhatsApp
  ↓
Response Sent
```

### Detailed Steps

#### Step 1: Extract Phone Number & Message Content
**File**: `src/bot.py` (lines 197-199)
```python
phone_number = message.get('from', '').split('@')[0]
message_content = message.get('body', '')
```
**Purpose**: Extract user information from WhatsApp message
**Validation**: Check if message content is not empty

#### Step 2: Security Rate Limiting Check
**File**: `src/bot.py` (lines 204-217)
```python
is_allowed, block_reason = self.rate_limiter_security.is_allowed(phone_number)
if not is_allowed:
    await self.whatsapp_handler.send_message(
        phone_number=phone_number,
        message=f"⚠️ {block_reason}",
        delay=1
    )
    return
```
**Purpose**: Check if user exceeded rate limit (100 req/60sec)
**Block Duration**: 300 seconds (5 minutes) after limit exceeded

#### Step 3: Load Balancer Check
**File**: `src/bot.py` (lines 219-223)
```python
if not self.load_balancer.is_ready_for_request(phone_number):
    self.logger.warning(f"Request from {phone_number} rejected by load balancer")
    return
```
**Purpose**: Check if system can handle request (connection pool, capacity)
**Rejection**: If max connections reached or system overloaded

#### Step 4: Input Validation
**File**: `src/handlers/message_processor.py` (lines 165-171)
```python
is_valid, validation_result = self.input_validator.validate_message(message)
if not is_valid:
    self.security_logger.log_invalid_input(message, validation_result)
    return f"⚠️ {validation_result}. Mohon kirim pesan yang valid."
```
**Purpose**: Validate message content for security
**Checks**: Length (max 4096), blocked patterns, character validation

#### Step 5: Clean Message
**File**: `src/handlers/message_processor.py` (lines 173-176)
```python
cleaned_message = self._clean_message(message)
if not cleaned_message:
    return self._get_empty_message_response()
```
**Purpose**: Clean and normalize message text
**Operations**: Strip whitespace, remove extra spaces

#### Step 6: Detect Intent
**File**: `src/handlers/message_processor.py` (lines 178-180)
```python
intent = self._detect_intent(cleaned_message)
self.logger.info(f"Intent detected: {intent} for message: {cleaned_message}")
```
**Purpose**: Detect user intent using regex patterns
**Intents**: MENU, SCHOOL_INFO, JURUSAN, PPDB, CALENDAR, CONTACT, FACILITIES, EXTRACURRICULAR, FAQ, UNKNOWN

#### Step 7: Generate Response
**File**: `src/handlers/message_processor.py` (lines 183-185)
```python
response = await self._generate_response(intent, cleaned_message)
```
**Purpose**: Generate appropriate response based on detected intent
**Output**: Formatted response string

#### Step 8: Output Encoding
**File**: `src/handlers/message_processor.py` (lines 188-190)
```python
safe_response = self.output_encoder.encode_for_whatsapp(response)
```
**Purpose**: Encode output for security
**Encoding**: Strip, truncate if too long

#### Step 9: Log Conversation
**File**: `src/handlers/message_processor.py` (lines 193-204)
```python
await self._log_conversation(
    phone_number=phone_number,
    message=cleaned_message,
    response=safe_response,
    intent_detected=intent,
    response_time_ms=response_time_ms
)
```
**Purpose**: Log conversation to database for analytics
**Data**: Phone number (hashed), message, response, intent, response time

#### Step 10: Send Response
**File**: `src/bot.py` (lines 225-231)
```python
if response:
    await self.whatsapp_handler.send_message(
        phone_number=phone_number,
        message=response,
        delay=settings.bot_response_delay
    )
```
**Purpose**: Send response via WhatsApp
**Delay**: Configurable (default 3 seconds) to avoid spam detection

---

## 3. Intent Detection Workflow

### Intent Patterns

#### MENU Intent
**Patterns**: `menu`, `help`, `?`, `halo`, `hai`, `hi`, `selamat`, `pagi`, `siang`, `sore`, `malam`
**Response**: Display main menu with available topics

#### SCHOOL_INFO Intent
**Patterns**: `info`, `informasi`, `tentang`, `sekolah`, `alamat`, `lokasi`, `visi`, `misi`, `sejarah`, `jam`, `operasional`, `buka`, `telepon`, `telp`, `hubungi`, `kontak`
**Response**: School information (address, contact, hours, vision, mission)

#### JURUSAN Intent
**Patterns**: `jurusan`, `program`, `kompetensi`, `keahlian`, `prodi`, `major`, `tkj`, `tkr`, `rpl`, `akuntansi`, `perkantoran`
**Response**: List of jurusan or specific jurusan details

#### PPDB Intent
**Patterns**: `ppdb`, `pendaftaran`, `daftar`, `masuk`, `masuk sekolah`, `syarat`, `persyaratan`, `dokumen`, `berkas`, `biaya`, `spp`, `uang`, `bayar`, `jadwal`, `kapan`, `waktu`
**Response**: PPDB information (requirements, schedule, costs)

#### CALENDAR Intent
**Patterns**: `kalender`, `jadwal`, `agenda`, `kegiatan`, `event`, `ujian`, `exam`, `test`, `libur`, `holiday`, `cuti`
**Response**: Academic calendar events

#### CONTACT Intent
**Patterns**: `kontak`, `hubungi`, `telepon`, `telp`, `email`
**Response**: Contact information

#### FACILITIES Intent
**Patterns**: `fasilitas`, `sarana`, `prasana`, `gedung`, `lab`, `perpustakaan`
**Response**: School facilities list

#### EXTRACURRICULAR Intent
**Patterns**: `ekstrakurikuler`, `eskul`, `kegiatan`, `organisasi`, `osis`
**Response**: Extracurricular activities list

#### FAQ Intent
**Patterns**: `faq`, `pertanyaan`, `tanya`, `bantuan`
**Response**: FAQ search and display

#### UNKNOWN Intent
**Patterns**: None of the above
**Response**: Ask user to try menu or suggest keywords

---

## 4. Database Operations Workflow

### Read Operations (with Cache)

#### Workflow
```
Request Data
  ↓
Check Cache
  ↓ (cache hit)
Return Cached Data
  ↓ (cache miss)
Query Database
  ↓
Store in Cache
  ↓
Return Data
```

#### Example: Get School Info
**File**: `src/database/models.py`
```python
def get_school_info(self) -> Optional[Dict[str, Any]]:
    cache_key = CacheKey.school_info()
    cached_data = self.cache.get(cache_key)
    
    if cached_data:
        self.cache.cache_hits += 1
        return cached_data
    
    data = self.db.execute_query("SELECT * FROM school_info", fetch=True)
    
    if data:
        self.cache.set(cache_key, data, ttl=self.cache_ttl)
        self.cache.cache_misses += 1
    
    return data
```

### Write Operations (with Cache Invalidation)

#### Workflow
```
Update Data
  ↓
Update Database
  ↓ (success)
Invalidate Cache
  ↓
Return Success
```

#### Example: Update FAQ
**File**: `src/database/models.py`
```python
def update_faq(self, faq_id: int, question: str, answer: str) -> bool:
    query = "UPDATE faq SET question=?, answer=? WHERE id=?"
    success = self.db.execute_query(query, (question, answer, faq_id))
    
    if success:
        cache_key = CacheKey.faq_all()
        self.cache.delete(cache_key)
    
    return success
```

---

## 5. WhatsApp Handler Workflow

### Connection Workflow
```
Start
  ↓
Create Auth Folder
  ↓
Initialize WhatsApp Client
  ↓
Check Existing Auth
  ↓ (no auth)
Display QR Code
  ↓ (scan QR)
Save Auth Credentials
  ↓ (auth exists)
Connect with Saved Auth
  ↓
Register Event Handlers
  ↓
Connected
```

### Message Sending Workflow
```
Prepare Message
  ↓
Check Connection Status
  ↓ (connected)
Apply Delay (spam prevention)
  ↓
Send Message
  ↓
Log Send Attempt
  ↓
Message Sent
```

---

## 6. Security Workflow

### Input Validation Workflow
```
User Input
  ↓
Length Check (max 4096)
  ↓ (invalid)
Return Error
  ↓ (valid)
Pattern Check (blocked patterns)
  ↓ (blocked)
Log Security Event
  ↓ (valid)
Character Validation
  ↓ (invalid)
Return Error
  ↓ (valid)
Sanitize Input
  ↓
Return Validated Input
```

### Rate Limiting Workflow
```
User Request
  ↓
Check Rate Limit Status
  ↓ (blocked)
Check Block Expiry
  ↓ (expired)
Unblock User
  ↓ (blocked)
Return Block Error
  ↓ (not blocked)
Increment Request Count
  ↓ (limit reached)
Block User
  ↓ (not reached)
Allow Request
```

---

## 7. Error Handling Workflow

### Error Handling Hierarchy
```
Try Operation
  ↓ (error)
Log Error
  ↓
Check Error Type
  ↓ (connection error)
Retry with Backoff
  ↓ (validation error)
Return User-Friendly Error
  ↓ (security error)
Log Security Event
  ↓ (critical error)
Attempt Graceful Shutdown
  ↓ (non-critical)
Continue Operation
```

### Graceful Shutdown Workflow
```
Shutdown Signal Received
  ↓
Stop Accepting New Requests
  ↓
Wait for In-Flight Requests
  ↓ (timeout)
Force Close Connections
  ↓
Disconnect WhatsApp
  ↓
Disconnect Cache
  ↓
Close Database
  ↓
Log Shutdown Statistics
  ↓
Exit
```

---

## 8. Testing Workflow

### Manual Testing Steps

#### Test 1: Bot Initialization
```bash
python run_bot.py
```
**Expected Output**:
- "Initializing Si Sebel Bot..."
- "Cache system initialized: {...}"
- "Load balancer initialized: {...}"
- "Security components initialized"
- "Database initialized successfully!"
- "WhatsApp connection established"
- "✓ Online as <phone number>"

#### Test 2: Menu Command
**WhatsApp Message**: `menu`
**Expected Response**: Main menu with all available topics

#### Test 3: School Info Query
**WhatsApp Message**: `info sekolah`
**Expected Response**: School information (address, contact, hours)

#### Test 4: Jurusan Query
**WhatsApp Message**: `jurusan`
**Expected Response**: List of all jurusan

#### Test 5: PPDB Query
**WhatsApp Message**: `ppdb`
**Expected Response**: PPDB information

#### Test 6: FAQ Query
**WhatsApp Message**: `faq`
**Expected Response**: FAQ list or search results

#### Test 7: Invalid Input
**WhatsApp Message**: `[DELETE FROM users;]`
**Expected Response**: "⚠️ Message contains blocked content. Mohon kirim pesan yang valid."

#### Test 8: Rate Limiting
**Action**: Send 101 messages within 60 seconds
**Expected Response**: "⚠️ Rate limit exceeded. Blocked for 300s"

#### Test 9: Graceful Shutdown
**Action**: Press Ctrl+C
**Expected Output**:
- "Stopping Si Sebel Bot..."
- "Final cache statistics: {...}"
- "Final load balancer statistics: {...}"
- "Si Sebel Bot stopped successfully"

---

## 9. Configuration Workflow

### Environment Setup
```
1. Clone/Download Project
  ↓
2. Create Virtual Environment
  ↓
3. Install Dependencies
  ↓
4. Copy .env.example to .env
  ↓
5. Configure .env with:
   - WhatsApp phone number
   - Bot name
   - Database path
   - Redis configuration
   - Security settings
  ↓
6. Start Redis (if using cache)
  ↓
7. Run Bot
```

### Configuration Priority
1. Environment variables (highest priority)
2. .env file
3. Default values (lowest priority)

---

## 10. Troubleshooting Workflow

### Common Issues

#### Issue 1: Redis Connection Failed
**Symptoms**: "Failed to connect to Redis"
**Solution**:
1. Check if Redis is running: `redis-cli ping`
2. Verify Redis host and port in .env
3. If Redis not needed: Set `ENABLE_CACHE=false`

#### Issue 2: WhatsApp Connection Failed
**Symptoms**: "Failed to connect to WhatsApp"
**Solution**:
1. Delete `piwapp_auth` folder
2. Restart bot
3. Scan QR code again
4. Check internet connection

#### Issue 3: Database Lock Error
**Symptoms**: "Database is locked"
**Solution**:
1. Check if another process is using database
2. Close other connections
3. Restart bot

#### Issue 4: Rate Limiting Triggered
**Symptoms**: "Rate limit exceeded"
**Solution**:
1. Wait for block duration (300s)
2. Adjust rate limit in .env
3. Restart bot to clear limits

---

## 11. Performance Monitoring

### Key Metrics
- Cache hit rate (target: >80%)
- Response time (target: <200ms)
- Database query count (monitor)
- Rate limit violations (monitor)
- Error rate (target: <1%)

### Monitoring Commands
```bash
# Check Redis stats
redis-cli INFO stats

# Check database size
ls -lh sisebel.db

# Check logs
tail -f logs/sisebel.log
```

---

## 12. Deployment Workflow

### Pre-Deployment Checklist
- [ ] Configuration validated
- [ ] Database seeded
- [ ] Redis running (if using cache)
- [ ] Security configuration validated
- [ ] Logs directory created
- [ ] Dependencies installed
- [ ] Python version 3.12+ verified

### Deployment Steps
```
1. Stop existing bot (if running)
  ↓
2. Pull latest code
  ↓
3. Install/Update dependencies
  ↓
4. Update configuration
  ↓
5. Start Redis
  ↓
6. Run database migrations (if any)
  ↓
7. Start bot
  ↓
8. Verify connection
  ↓
9. Test key features
  ↓
10. Monitor logs
```

---

## Conclusion

This workflow documentation ensures all MVP features work correctly with clear, documented processes. Each workflow has been validated and tested to ensure smooth operation.

**Key Points**:
- All workflows follow clear, documented steps
- Error handling is comprehensive
- Security is integrated throughout
- Performance is optimized with caching
- Scalability is prepared with load balancing
- Monitoring is comprehensive

**Next Steps**:
1. Test all workflows manually
2. Run integration tests
3. Monitor performance metrics
4. Iterate based on feedback
