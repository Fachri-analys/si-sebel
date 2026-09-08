"""
Message processor for Si Sebel Bot.
Handles message parsing, intent detection, and response generation.
"""

import re
from typing import Any, Dict, Optional
from datetime import datetime

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
from utils.logger import Logger
from utils.exceptions import MessageProcessingError
from utils.metrics import metrics
from utils.security import (
    get_input_validator,
    get_output_encoder,
    get_security_logger,
)


class IntentType:
    """Intent types for message classification."""

    MENU = "menu"
    SCHOOL_INFO = "school_info"
    JURUSAN = "jurusan"
    PPDB = "ppdb"
    CALENDAR = "calendar"
    CONTACT = "contact"
    FACILITIES = "facilities"
    EXTRACURRICULAR = "extracurricular"
    FAQ = "faq"
    UNKNOWN = "unknown"


class MessageProcessor:
    """Processor for incoming messages and response generation."""

    def __init__(
        self,
        school_info: SchoolInfoModel,
        jurusan: JurusanModel,
        faq: FAQModel,
        calendar: CalendarModel,
        contact: ContactModel,
        facilities: FacilitiesModel,
        extracurricular: ExtracurricularModel,
        ppdb: PPDBInfoModel,
        conversation_log: ConversationLogModel,
        logger: Optional[Logger] = None,
    ):
        """
        Initialize message processor.

        Args:
            school_info: School info model
            jurusan: Jurusan model
            faq: FAQ model
            calendar: Calendar model
            contact: Contact model
            facilities: Facilities model
            extracurricular: Extracurricular model
            ppdb: PPDB info model
            conversation_log: Conversation log model
            logger: Logger instance
        """
        self.school_info = school_info
        self.jurusan = jurusan
        self.faq = faq
        self.calendar = calendar
        self.contact = contact
        self.facilities = facilities
        self.extracurricular = extracurricular
        self.ppdb = ppdb
        self.conversation_log = conversation_log

        self.logger = logger or Logger.get_logger("message_processor")

        # Initialize security components
        self.input_validator = get_input_validator(self.logger)
        self.output_encoder = get_output_encoder()
        self.security_logger = get_security_logger(self.logger)
        self.context: Dict[str, Dict[str, Any]] = {}

        # Initialize intent patterns
        self._init_intent_patterns()

    def _init_intent_patterns(self) -> None:
        """Initialize regex patterns for intent detection."""
        self.intent_patterns = {
            IntentType.MENU: [
                r"^(menu|help|\?|halo|hai|hi|selamat|pagi|siang|sore|malam)",
                r"^menu$",
                r"^help$",
                r"^\?$",
            ],
            IntentType.SCHOOL_INFO: [
                r"(info|informasi|tentang|sekolah|alamat|lokasi|visi|misi|sejarah)",
                r"(jam|operasional|buka)",
                r"(telepon|telp|hubungi|kontak)",
            ],
            IntentType.JURUSAN: [
                r"(jurusan|program|kompetensi|keahlian|prodi|major)",
                r"(tkj|tkr|rpl|akuntansi|perkantoran)",
            ],
            IntentType.PPDB: [
                r"(ppdb|pendaftaran|daftar|masuk|masuk sekolah)",
                r"(syarat|persyaratan|dokumen|berkas)",
                r"(biaya|spp|uang|bayar)",
                r"(jadwal|kapan|waktu)",
            ],
            IntentType.CALENDAR: [
                r"(kalender|jadwal|agenda|kegiatan|event)",
                r"(ujian|exam|test)",
                r"(libur|holiday|cuti)",
            ],
            IntentType.CONTACT: [
                r"(kontak|hubungi|telepon|telp|email)",
                r"(tu|tata usaha)",
                r"(bk|bimbingan konseling)",
                r"(humas|kesiswaan)",
            ],
            IntentType.FACILITIES: [
                r"(fasilitas|sarana|prasarana|lab|laboratorium)",
                r"(kantin|perpustakaan|masjid|lapangan)",
            ],
            IntentType.EXTRACURRICULAR: [
                r"(ekskul|ekstrakurikuler|organisasi|osis)",
                r"(pramuka|paskibra|basket|futsal|kir)",
            ],
        }
        self.intent_patterns[IntentType.FACILITIES].append(
            r"(fasilitas|sarana|prasarana)"
        )

    async def process_message(self, phone_number: str, message: str) -> str:
        """
        Process incoming message and generate response.

        Args:
            phone_number: User's phone number
            message: User's message

        Returns:
            Bot response

        Raises:
            MessageProcessingError: If processing fails
        """
        start_time = datetime.now()

        try:
            metrics.increment("messages.received")
            # Validate input (security check)
            is_valid, validation_result = self.input_validator.validate_message(message)
            if not is_valid:
                metrics.increment("messages.rejected")
                self.security_logger.log_invalid_input(message, validation_result)
                self.logger.warning(
                    f"Invalid input from {phone_number}: {validation_result}"
                )
                return f"⚠️ {validation_result}. Mohon kirim pesan yang valid."

            # Clean message
            cleaned_message = self._clean_message(message)

            if not cleaned_message:
                metrics.increment("messages.empty")
                return self._get_empty_message_response()

            # Detect intent
            intent = self._detect_intent(cleaned_message)

            sender_hash = self.input_validator.hash_phone_number(phone_number)
            self.logger.info(
                "Intent detected intent=%s sender_hash=%s message_length=%d",
                intent,
                sender_hash,
                len(cleaned_message),
            )

            # Generate response based on intent
            response = await self._generate_response(intent, cleaned_message)
            if len(self.context) > 1000:
                self.context.pop(next(iter(self.context)), None)
            self.context.setdefault(phone_number, {})["intent"] = intent
            if intent == IntentType.JURUSAN:
                self.context[phone_number]["last_jurusan_query"] = cleaned_message

            # Encode output for security
            safe_response = self.output_encoder.encode_for_whatsapp(response)

            # Calculate response time
            response_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Log conversation
            await self._log_conversation(
                phone_number=phone_number,
                message=cleaned_message,
                response=safe_response,
                intent_detected=intent,
                response_time_ms=response_time_ms,
            )
            metrics.increment("messages.processed")

            return safe_response

        except Exception as e:
            metrics.increment("messages.errors")
            self.logger.error(f"Error processing message: {e}")
            raise MessageProcessingError(f"Failed to process message: {e}")

    def _clean_message(self, message: str) -> str:
        """
        Clean and normalize message.

        Args:
            message: Raw message

        Returns:
            Cleaned message
        """
        if not message:
            return ""

        # Remove extra whitespace
        cleaned = " ".join(message.split())

        # Convert to lowercase for processing
        return cleaned.lower().strip()

    def _detect_intent(self, message: str) -> str:
        """
        Detect intent from message using pattern matching.

        Args:
            message: Cleaned message

        Returns:
            Detected intent
        """
        menu_intent = {
            "1": IntentType.SCHOOL_INFO,
            "2": IntentType.JURUSAN,
            "3": IntentType.PPDB,
            "4": IntentType.CALENDAR,
            "5": IntentType.CONTACT,
            "6": IntentType.FAQ,
        }
        # Support single digits and common menu command formats (e.g., '1', '1.', 'no 1', 'menu 1')
        normalized_choice = message.strip()
        menu_number_match = re.match(
            r"^(?:(?:no|nomor|menu|pilihan)\s*\.?\s*)?([1-6])[\.\)]?$",
            normalized_choice,
            re.IGNORECASE,
        )
        if menu_number_match:
            choice = menu_number_match.group(1)
            return menu_intent[choice]

        if normalized_choice in menu_intent:
            return menu_intent[normalized_choice]

        # Check for menu commands first
        for pattern in self.intent_patterns.get(IntentType.MENU, []):
            if re.search(pattern, message, re.IGNORECASE):
                return IntentType.MENU

        # Specific domains must win over broad PPDB/school patterns.
        priority = (
            IntentType.CONTACT,
            IntentType.CALENDAR,
            IntentType.JURUSAN,
            IntentType.PPDB,
            IntentType.FACILITIES,
            IntentType.EXTRACURRICULAR,
            IntentType.SCHOOL_INFO,
            IntentType.FAQ,
        )
        for intent in priority:
            if any(
                re.search(pattern, message, re.IGNORECASE)
                for pattern in self.intent_patterns.get(intent, [])
            ):
                return intent
        if "?" in message or any(
            word in message.split()
            for word in ("tanya", "berapa", "apakah", "bagaimana")
        ):
            return IntentType.FAQ
        return IntentType.UNKNOWN

    async def _generate_response(self, intent: str, message: str) -> str:
        """
        Generate response based on intent.

        Args:
            intent: Detected intent
            message: User's message

        Returns:
            Bot response
        """
        if intent == IntentType.MENU:
            return self._get_menu_response()

        elif intent == IntentType.SCHOOL_INFO:
            return await self._get_school_info_response(message)

        elif intent == IntentType.JURUSAN:
            return await self._get_jurusan_response(message)

        elif intent == IntentType.PPDB:
            return await self._get_ppdb_response(message)

        elif intent == IntentType.CALENDAR:
            return await self._get_calendar_response(message)

        elif intent == IntentType.CONTACT:
            return await self._get_contact_response(message)

        elif intent == IntentType.FACILITIES:
            return await self._get_facilities_response()

        elif intent == IntentType.EXTRACURRICULAR:
            return await self._get_extracurricular_response()

        elif intent == IntentType.FAQ:
            return await self._get_faq_response(message)

        else:
            return self._get_unknown_response()

    def _get_menu_response(self) -> str:
        """Generate main menu response."""
        menu = (
            "🏫 *SI SEBEL - SMKN 11 Jakarta*\n\n"
            "Silakan pilih informasi yang Anda butuhkan:\n\n"
            "1. 📋 Informasi Umum Sekolah\n"
            "2. 📚 Jurusan & Program Keahlian\n"
            "3. 📝 Pendaftaran (PPDB)\n"
            "4. 📅 Kalender Akademik\n"
            "5. 📞 Kontak & Fasilitas\n"
            "6. ❓ FAQ (Pertanyaan Umum)\n\n"
            "Ketik angka atau kata kunci untuk informasi lebih lanjut.\n"
            "Ketik 'menu' kapan saja untuk kembali ke menu utama."
        )
        return menu

    async def _get_school_info_response(self, message: str) -> str:
        """Generate school info response."""
        try:
            # Get general school info
            info = self.school_info.get_info()

            if not info:
                return "Maaf, informasi sekolah belum tersedia."

            response = (
                "🏫 *INFORMASI SEKOLAH*\n\n"
                f"Nama: {info.get('nama', 'N/A')}\n"
                f"Alamat: {info.get('alamat', 'N/A')}\n"
                f"Telepon: {info.get('telepon', 'N/A')}\n"
                f"Email: {info.get('email', 'N/A')}\n"
                f"Jam Operasional: {info.get('jam_operasional', 'N/A')}\n\n"
                f"*Visi:*\n{info.get('visi', 'N/A')}\n\n"
                f"*Misi:*\n{info.get('misi', 'N/A')}\n\n"
                f"*Sejarah:*\n{info.get('sejarah', 'N/A')}"
            )

            return response

        except Exception as e:
            self.logger.error(f"Error getting school info: {e}")
            return "Maaf, terjadi kesalahan saat mengambil informasi sekolah."

    async def _get_jurusan_response(self, message: str) -> str:
        """Generate jurusan response."""
        try:
            # Check if user is asking for specific jurusan
            jurusan_list = self.jurusan.get_all_jurusan()

            if not jurusan_list:
                return "Maaf, informasi jurusan belum tersedia."

            # Comprehensive keyword and alias map for SMKN 11 Jakarta majors
            jurusan_alias_map = {
                "akl": {
                    "akl",
                    "akuntansi",
                    "keuangan",
                    "akuntansi dan keuangan lembaga",
                    "pembukuan",
                },
                "mplb": {
                    "mplb",
                    "perkantoran",
                    "manajemen perkantoran",
                    "layanan bisnis",
                    "administrasi perkantoran",
                    "administrasi kantor",
                    "otkp",
                    "manajemen perkantoran dan layanan bisnis",
                },
                "br": {
                    "br",
                    "pemasaran",
                    "bisnis ritel",
                    "bisnis retail",
                    "bdp",
                    "ritel",
                    "retail",
                },
            }

            message_lower = message.lower()
            message_words = set(re.findall(r"[a-z0-9]+", message_lower))

            # If message matches a specific jurusan alias or keyword
            for jurusan in jurusan_list:
                kode = str(jurusan.get("kode") or "").lower()
                nama = str(jurusan.get("nama") or "").lower()
                aliases = set(jurusan_alias_map.get(kode, set()))
                if nama:
                    aliases.add(nama)
                if kode:
                    aliases.add(kode)

                # Match if alias is substring in message OR any alias matches individual message word
                matched = any(
                    alias in message_lower for alias in aliases if len(alias) > 2
                ) or any(w in aliases for w in message_words if len(w) >= 2)

                if matched:
                    return self._format_jurusan_detail(jurusan)

            # Otherwise, show list
            response = "📚 *JURUSAN & PROGRAM KEAHLIAN*\n\n"

            for idx, jurusan in enumerate(jurusan_list, 1):
                response += f"{idx}. {jurusan['nama']}\n"
                response += f"   {jurusan['deskripsi'][:100]}...\n\n"

            response += "Ketik nama jurusan untuk detail lebih lanjut."

            return response

        except Exception as e:
            self.logger.error(f"Error getting jurusan info: {e}")
            return "Maaf, terjadi kesalahan saat mengambil informasi jurusan."

    def _format_jurusan_detail(self, jurusan: Dict[str, Any]) -> str:
        """Format jurusan detail response."""
        return (
            f"📚 *{jurusan['nama'].upper()}*\n\n"
            f"*Deskripsi:*\n{jurusan['deskripsi']}\n\n"
            f"*Syarat:*\n{jurusan['syarat']}\n\n"
            f"*Prospek Karir:*\n{jurusan['prospek']}\n\n"
            f"Kuota: {jurusan['kuota']} siswa"
        )

    async def _get_ppdb_response(self, message: str) -> str:
        """Generate PPDB response."""
        try:
            ppdb_info = self.ppdb.get_ppdb_info()

            if not ppdb_info:
                return "Maaf, informasi PPDB belum tersedia."

            response = (
                "📝 *INFORMASI PPDB*\n\n"
                f"Tahun Ajaran: {ppdb_info.get('tahun_ajaran', 'N/A')}\n"
                f"Jalur Pendaftaran: {ppdb_info.get('jalur_pendaftaran', 'N/A')}\n"
                f"Tanggal Pendaftaran: {ppdb_info.get('tanggal_pendaftaran', 'N/A')}\n"
                f"Website: {ppdb_info.get('website_ppdb', 'N/A')}\n\n"
                f"*Syarat Umum:*\n{ppdb_info.get('syarat_umum', 'N/A')}\n\n"
                f"*Dokumen yang Dibutuhkan:*\n{ppdb_info.get('dokumen_dibutuhkan', 'N/A')}\n\n"
                f"*Biaya:*\n{ppdb_info.get('biaya_pendaftaran', 'N/A')}\n"
                f"{ppdb_info.get('biaya_operasional', 'N/A')}\n"
                f"{ppdb_info.get('biaya_spp', 'N/A')}"
            )

            return response

        except Exception as e:
            self.logger.error(f"Error getting PPDB info: {e}")
            return "Maaf, terjadi kesalahan saat mengambil informasi PPDB."

    async def _get_calendar_response(self, message: str) -> str:
        """Generate calendar response."""
        try:
            events = self.calendar.get_upcoming_events(days=30, limit=10)

            if not events:
                return "Maaf, tidak ada kegiatan yang akan datang."

            response = "📅 *KALENDER AKADEMIK*\n\n"

            for event in events:
                response += f"📌 {event['event_name']}\n"
                response += f"   📅 {event['event_date']}\n"
                response += f"   📝 {event['description']}\n\n"

            return response

        except Exception as e:
            self.logger.error(f"Error getting calendar info: {e}")
            return "Maaf, terjadi kesalahan saat mengambil kalender."

    async def _get_contact_response(self, message: str) -> str:
        """Generate contact response."""
        try:
            contacts = self.contact.get_contacts()

            if not contacts:
                return "Maaf, informasi kontak belum tersedia."

            response = "📞 *KONTAK SEKOLAH*\n\n"

            for contact in contacts:
                response += f"👤 {contact['name']} ({contact['role']})\n"
                response += f"   📱 {contact['phone_number']}\n"
                if contact["email"]:
                    response += f"   📧 {contact['email']}\n"
                if contact.get("description"):
                    response += f"   📝 {contact['description']}\n"
                response += "\n"

            response += (
                "🏢 *Fasilitas & Ekstrakurikuler:*\n"
                "- Ketik *fasilitas* untuk melihat sarana & prasarana sekolah.\n"
                "- Ketik *ekskul* untuk melihat kegiatan ekstrakurikuler."
            )

            return response

        except Exception as e:
            self.logger.error(f"Error getting contact info: {e}")
            return "Maaf, terjadi kesalahan saat mengambil informasi kontak."

    async def _get_facilities_response(self) -> str:
        """Generate facilities response."""
        try:
            facilities = self.facilities.get_facilities()

            if not facilities:
                return "Maaf, informasi fasilitas belum tersedia."

            response = "🏢 *FASILITAS SEKOLAH*\n\n"

            for facility in facilities:
                response += f"🏗️ {facility['name']}\n"
                response += f"   📍 {facility['location']}\n"
                response += f"   👥 Kapasitas: {facility['capacity']}\n"
                response += f"   📝 {facility['description']}\n\n"

            return response

        except Exception as e:
            self.logger.error(f"Error getting facilities info: {e}")
            return "Maaf, terjadi kesalahan saat mengambil informasi fasilitas."

    async def _get_extracurricular_response(self) -> str:
        """Generate extracurricular response."""
        try:
            ekskul = self.extracurricular.get_extracurriculars()

            if not ekskul:
                return "Maaf, informasi ekstrakurikuler belum tersedia."

            response = "⚽ *EKSTRAKURIKULER*\n\n"

            for activity in ekskul:
                response += f"🎯 {activity['name']}\n"
                response += f"   ⏰ {activity['schedule']}\n"
                response += f"   👤 Contact: {activity['contact_person']}\n"
                response += f"   📝 {activity['description']}\n\n"

            return response

        except Exception as e:
            self.logger.error(f"Error getting extracurricular info: {e}")
            return "Maaf, terjadi kesalahan saat mengambil informasi ekstrakurikuler."

    async def _get_faq_response(self, message: str) -> str:
        """Generate FAQ response."""
        try:
            faqs = self.faq.search_faq(message, limit=3)

            if not faqs:
                return (
                    "❓ Maaf, saya tidak menemukan jawaban untuk pertanyaan Anda.\n\n"
                    "Ketik 'menu' untuk melihat topik yang tersedia, "
                    "atau coba kata kunci lain."
                )

            response = "❓ *FAQ - PERTANYAAN UMUM*\n\n"

            for idx, faq in enumerate(faqs, 1):
                response += f"Q{idx}: {faq['question']}\n"
                response += f"A{idx}: {faq['answer']}\n\n"

                # Increment hit count
                self.faq.increment_hit_count(faq["id"])

            return response

        except Exception as e:
            self.logger.error(f"Error searching FAQ: {e}")
            return "Maaf, terjadi kesalahan saat mencari FAQ."

    def _get_empty_message_response(self) -> str:
        """Generate response for empty message."""
        return "Mohon ketik pesan yang valid. Ketik 'menu' untuk melihat topik yang tersedia."

    def _get_unknown_response(self) -> str:
        """Generate response for unknown intent."""
        return (
            "Maaf, saya tidak mengerti pesan Anda.\n\n"
            "Ketik 'menu' untuk melihat topik yang tersedia, "
            "atau coba kata kunci lain seperti: jurusan, ppdb, kontak, dll."
        )

    async def _log_conversation(
        self,
        phone_number: str,
        message: str,
        response: str,
        intent_detected: str,
        response_time_ms: int,
    ) -> None:
        """
        Log conversation to database.

        Args:
            phone_number: User's phone number
            message: User's message
            response: Bot's response
            intent_detected: Detected intent
            response_time_ms: Response time in milliseconds
        """
        try:
            # Sanitize message for logging (security)
            safe_message = "[redacted]"
            safe_response = self.output_encoder.encode_for_log(response)

            self.conversation_log.log_conversation(
                phone_number=phone_number,
                message=safe_message,
                response=safe_response,
                intent_detected=intent_detected,
                response_time_ms=response_time_ms,
            )
        except Exception as e:
            self.logger.error(f"Error logging conversation: {e}")
