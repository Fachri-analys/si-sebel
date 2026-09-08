"""
Database models for Si Sebel Bot.
Provides ORM-like interface for database operations with Redis caching and metadata support.
Includes metadata: source, verified_at, updated_at, is_active.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import sqlite3
import re

from .connection import DatabaseConnection
from utils import CacheManager, CacheKey
from utils.security import InputValidator


class BaseModel:
    """Base model with common database operations and caching."""

    def __init__(self, db: DatabaseConnection, cache: Optional[CacheManager] = None):
        """
        Initialize base model.

        Args:
            db: Database connection
            cache: Optional cache manager
        """
        self.db = db
        self.cache = cache

    def _hash_phone(self, phone_number: str) -> str:
        """
        Pseudonymize phone number for privacy using a secret HMAC key.

        Args:
            phone_number: Phone number to hash

        Returns:
            Hashed phone number
        """
        return InputValidator().hash_phone_number(phone_number)


class SchoolInfoModel(BaseModel):
    """Model for school information operations."""

    def get_info(self, key: Optional[str] = None) -> Any:
        """
        Get school information with caching.

        Args:
            key: Specific key to retrieve, or None for all info

        Returns:
            School information value or dictionary of all info
        """
        cache_key = CacheKey.school_info(key)
        if self.cache:
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                return cached_value

        if key:
            query = "SELECT value FROM school_info WHERE key = ? AND is_active = 1"
            result = self.db.execute_query(query, (key,), fetch=True)
            value = result["value"] if result else None
        else:
            query = "SELECT key, value, category, source, verified_at FROM school_info WHERE is_active = 1"
            results = self.db.execute_query(query, fetch_all=True) or []
            value = {row["key"]: row["value"] for row in results}

        if self.cache and value is not None:
            self.cache.set(cache_key, value)

        return value

    def get_detailed_info(self, key: Optional[str] = None) -> Any:
        """Get full record including metadata."""
        if key:
            query = "SELECT * FROM school_info WHERE key = ? AND is_active = 1"
            return self.db.execute_query(query, (key,), fetch=True)
        else:
            query = "SELECT * FROM school_info WHERE is_active = 1 ORDER BY category, key"
            return self.db.execute_query(query, fetch_all=True) or []

    def set_info(
        self,
        key: str,
        value: str,
        category: str = None,
        description: str = None,
        is_active: bool = True,
        source: str = "Belum terverifikasi",
        verified_at: Optional[str] = None
    ) -> bool:
        """
        Set or update school information with cache invalidation (idempotent).
        """
        query = """
            INSERT INTO school_info (key, value, category, description, is_active, source, verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                category = excluded.category,
                description = excluded.description,
                is_active = excluded.is_active,
                source = excluded.source,
                verified_at = excluded.verified_at,
                updated_at = CURRENT_TIMESTAMP
        """
        try:
            self.db.execute_query(
                query,
                (key, value, category, description, 1 if is_active else 0, source, verified_at)
            )

            if self.cache:
                self.cache.delete(CacheKey.school_info(key))
                self.cache.delete(CacheKey.school_info())

            return True
        except sqlite3.Error:
            raise

    def get_by_category(self, category: str) -> Dict[str, str]:
        """Get school information by category."""
        query = "SELECT key, value FROM school_info WHERE category = ? AND is_active = 1"
        results = self.db.execute_query(query, (category,), fetch_all=True) or []
        return {row["key"]: row["value"] for row in results}


class JurusanModel(BaseModel):
    """Model for jurusan (major) operations."""

    def get_all_jurusan(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all jurusan with caching."""
        cache_key = f"jurusan:all:active_{active_only}"
        if self.cache:
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                return cached_value

        if active_only:
            query = "SELECT * FROM jurusan WHERE is_active = 1 ORDER BY nama"
        else:
            query = "SELECT * FROM jurusan ORDER BY nama"

        value = self.db.execute_query(query, fetch_all=True) or []

        if self.cache:
            self.cache.set(cache_key, value)

        return value

    def get_jurusan_by_id(self, jurusan_id: int) -> Optional[Dict[str, Any]]:
        """Get jurusan by ID."""
        query = "SELECT * FROM jurusan WHERE id = ?"
        return self.db.execute_query(query, (jurusan_id,), fetch=True)

    def get_jurusan_by_name(self, nama: str) -> Optional[Dict[str, Any]]:
        """Get jurusan by name or code."""
        query = """
            SELECT * FROM jurusan 
            WHERE (LOWER(nama) = LOWER(?) OR LOWER(kode) = LOWER(?)) 
            AND is_active = 1
        """
        return self.db.execute_query(query, (nama, nama), fetch=True)

    def add_jurusan(
        self,
        nama: str,
        deskripsi: str = None,
        syarat: str = None,
        prospek: str = None,
        kuota: int = 0,
        kode: str = None,
        is_active: bool = True,
        source: str = "Belum terverifikasi",
        verified_at: Optional[str] = None
    ) -> bool:
        """Add or update a jurusan idempotently."""
        query = """
            INSERT INTO jurusan (nama, kode, deskripsi, syarat, prospek, kuota, is_active, source, verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(nama) DO UPDATE SET
                kode = excluded.kode,
                deskripsi = excluded.deskripsi,
                syarat = excluded.syarat,
                prospek = excluded.prospek,
                kuota = excluded.kuota,
                is_active = excluded.is_active,
                source = excluded.source,
                verified_at = excluded.verified_at,
                updated_at = CURRENT_TIMESTAMP
        """
        try:
            self.db.execute_query(
                query,
                (nama, kode, deskripsi, syarat, prospek, kuota, 1 if is_active else 0, source, verified_at)
            )
            if self.cache:
                self.cache.delete(CacheKey.jurusan())
            return True
        except Exception:
            return False


class FAQModel(BaseModel):
    """Model for FAQ operations."""

    # Common Indonesian stopwords to filter out from keyword matching
    STOPWORDS = {
        "apa", "apakah", "siapa", "kapan", "dimana", "kemana", "mengapa",
        "bagaimana", "kenapa", "ada", "adakah", "bisa", "dapat", "yang", "dan",
        "di", "ke", "dari", "untuk", "pada", "dengan", "ini", "itu", "atau",
        "saya", "kami", "kamu", "anda", "mau", "ingin", "tanya", "mohon",
        "tolong", "halo", "hai", "si", "sebel", "sekolah"
    }

    def search_faq(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search FAQ with flexible keyword matching and caching."""
        cache_key = f"faq:search:{query}:{limit}"
        if self.cache:
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                return cached_value

        all_words = re.findall(r"[a-z0-9]+", query.lower())
        meaningful_terms = [w for w in all_words if w not in self.STOPWORDS and len(w) > 2]

        # If all words were stopwords, fallback to using all words
        search_terms = meaningful_terms if meaningful_terms else all_words

        if not search_terms:
            return []

        value = self.db.execute_query(
            "SELECT * FROM faq WHERE is_active = 1",
            fetch_all=True,
        ) or []

        def score(row: Dict[str, Any]) -> tuple:
            haystack = " ".join(
                str(row.get(field) or "").lower()
                for field in ("question", "keywords", "answer")
            )
            matches = sum(term in haystack for term in search_terms)
            return (matches, row.get("priority", 0), row.get("hit_count", 0))

        value = [row for row in value if score(row)[0] > 0]
        value.sort(key=score, reverse=True)
        value = value[:limit]

        if self.cache:
            self.cache.set(cache_key, value, ttl=1800)

        return value

    def get_faq_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get FAQ by category."""
        query = """
            SELECT * FROM faq 
            WHERE category = ? AND is_active = 1
            ORDER BY priority DESC, hit_count DESC
            LIMIT ?
        """
        return self.db.execute_query(query, (category, limit), fetch_all=True) or []

    def get_popular_faq(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most popular FAQs by hit count."""
        query = """
            SELECT * FROM faq 
            WHERE is_active = 1
            ORDER BY hit_count DESC, priority DESC
            LIMIT ?
        """
        return self.db.execute_query(query, (limit,), fetch_all=True) or []

    def add_faq(
        self,
        question: str,
        answer: str,
        keywords: str = None,
        category: str = None,
        priority: int = 0,
        is_active: bool = True,
        source: str = "Belum terverifikasi",
        verified_at: Optional[str] = None
    ) -> bool:
        """Add or update FAQ idempotently."""
        query = """
            INSERT INTO faq (question, answer, keywords, category, priority, is_active, source, verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(question) DO UPDATE SET
                answer = excluded.answer,
                keywords = excluded.keywords,
                category = excluded.category,
                priority = excluded.priority,
                is_active = excluded.is_active,
                source = excluded.source,
                verified_at = excluded.verified_at,
                updated_at = CURRENT_TIMESTAMP
        """
        try:
            self.db.execute_query(
                query,
                (question, answer, keywords, category, priority, 1 if is_active else 0, source, verified_at)
            )
            return True
        except Exception:
            return False

    def increment_hit_count(self, faq_id: int) -> bool:
        """Increment FAQ hit count."""
        query = "UPDATE faq SET hit_count = hit_count + 1 WHERE id = ?"
        try:
            self.db.execute_query(query, (faq_id,))
            return True
        except Exception:
            return False


class ConversationLogModel(BaseModel):
    """Model for conversation logging operations."""

    def log_conversation(
        self,
        phone_number: str,
        message: str,
        response: str = None,
        intent_detected: str = None,
        response_time_ms: int = None
    ) -> bool:
        """Log a conversation."""
        phone_hash = self._hash_phone(phone_number)

        query = """
            INSERT INTO conversation_log 
            (phone_number_hash, message, response, intent_detected, response_time_ms)
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            self.db.execute_query(
                query,
                (phone_hash, message, response, intent_detected, response_time_ms)
            )
            return True
        except Exception:
            return False

    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        queries = {
            "total_conversations": "SELECT COUNT(*) as count FROM conversation_log",
            "unique_users": "SELECT COUNT(DISTINCT phone_number_hash) as count FROM conversation_log",
            "avg_response_time": "SELECT AVG(response_time_ms) as avg FROM conversation_log WHERE response_time_ms IS NOT NULL",
            "total_intents": "SELECT COUNT(DISTINCT intent_detected) as count FROM conversation_log WHERE intent_detected IS NOT NULL"
        }

        stats = {}
        for key, query in queries.items():
            result = self.db.execute_query(query, fetch=True)
            stats[key] = result["count"] if result and "count" in result else (result["avg"] if result and "avg" in result else 0)

        return stats


class CalendarModel(BaseModel):
    """Model for calendar/academic events operations."""

    def get_events(
        self,
        event_type: str = None,
        tahun_ajaran: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get calendar events with caching."""
        cache_key = CacheKey.calendar(event_type, tahun_ajaran)
        if self.cache:
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                return cached_value

        conditions = ["is_active = 1"]
        params = []

        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)

        if tahun_ajaran:
            conditions.append("tahun_ajaran = ?")
            params.append(tahun_ajaran)

        where_clause = " AND ".join(conditions)
        params.append(limit)

        query = f"""
            SELECT * FROM calendar 
            WHERE {where_clause}
            ORDER BY event_date ASC
            LIMIT ?
        """

        value = self.db.execute_query(query, tuple(params), fetch_all=True) or []

        if self.cache:
            self.cache.set(cache_key, value)

        return value

    def get_upcoming_events(self, days: int = 60, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get upcoming events. Fallback to active calendar events if none found in window.
        """
        # Try finding events >= today
        query = """
            SELECT * FROM calendar 
            WHERE is_active = 1 
            AND event_date >= date('now') 
            ORDER BY event_date ASC
            LIMIT ?
        """
        events = self.db.execute_query(query, (limit,), fetch_all=True) or []

        # Fallback: if no future events, return active events for current semester/year
        if not events:
            fallback_query = """
                SELECT * FROM calendar 
                WHERE is_active = 1 
                ORDER BY event_date DESC
                LIMIT ?
            """
            events = self.db.execute_query(fallback_query, (limit,), fetch_all=True) or []

        return events

    def add_event(
        self,
        event_name: str,
        event_date: str,
        event_type: str,
        description: str = None,
        tahun_ajaran: str = "2025/2026",
        is_active: bool = True,
        source: str = "Belum terverifikasi",
        verified_at: Optional[str] = None
    ) -> bool:
        """Add or update event idempotently."""
        query = """
            INSERT INTO calendar (event_name, event_date, event_type, description, tahun_ajaran, is_active, source, verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(event_name, tahun_ajaran) DO UPDATE SET
                event_date = excluded.event_date,
                event_type = excluded.event_type,
                description = excluded.description,
                is_active = excluded.is_active,
                source = excluded.source,
                verified_at = excluded.verified_at,
                updated_at = CURRENT_TIMESTAMP
        """
        try:
            self.db.execute_query(
                query,
                (event_name, event_date, event_type, description, tahun_ajaran, 1 if is_active else 0, source, verified_at)
            )
            return True
        except Exception:
            return False


class ContactModel(BaseModel):
    """Model for contact information operations."""

    def get_contacts(self, role: str = None, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get contact information with caching."""
        cache_key = f"contact:role_{role}:active_{active_only}"
        if self.cache:
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                return cached_value

        conditions = []
        params = []

        if role:
            conditions.append("role = ?")
            params.append(role)

        if active_only:
            conditions.append("is_active = 1")

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM contact WHERE {where_clause} ORDER BY role, name"

        value = self.db.execute_query(query, tuple(params), fetch_all=True) or []

        if self.cache:
            self.cache.set(cache_key, value)

        return value

    def add_contact(
        self,
        name: str,
        role: str,
        phone_number: str = None,
        email: str = None,
        description: str = None,
        is_active: bool = True,
        source: str = "Belum terverifikasi",
        verified_at: Optional[str] = None
    ) -> bool:
        """Add or update contact idempotently."""
        query = """
            INSERT INTO contact (name, role, phone_number, email, description, is_active, source, verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name, role) DO UPDATE SET
                phone_number = excluded.phone_number,
                email = excluded.email,
                description = excluded.description,
                is_active = excluded.is_active,
                source = excluded.source,
                verified_at = excluded.verified_at,
                updated_at = CURRENT_TIMESTAMP
        """
        try:
            self.db.execute_query(
                query,
                (name, role, phone_number, email, description, 1 if is_active else 0, source, verified_at)
            )
            return True
        except Exception:
            return False


class FacilitiesModel(BaseModel):
    """Model for facilities operations."""

    def get_facilities(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all facilities with caching."""
        cache_key = f"facilities:active_{active_only}"
        if self.cache:
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                return cached_value

        if active_only:
            query = "SELECT * FROM facilities WHERE is_active = 1 ORDER BY name"
        else:
            query = "SELECT * FROM facilities ORDER BY name"

        value = self.db.execute_query(query, fetch_all=True) or []

        if self.cache:
            self.cache.set(cache_key, value)

        return value

    def add_facility(
        self,
        name: str,
        description: str = None,
        location: str = None,
        capacity: int = None,
        is_active: bool = True,
        source: str = "Belum terverifikasi",
        verified_at: Optional[str] = None
    ) -> bool:
        """Add or update facility idempotently."""
        query = """
            INSERT INTO facilities (name, description, location, capacity, is_active, source, verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                description = excluded.description,
                location = excluded.location,
                capacity = excluded.capacity,
                is_active = excluded.is_active,
                source = excluded.source,
                verified_at = excluded.verified_at,
                updated_at = CURRENT_TIMESTAMP
        """
        try:
            self.db.execute_query(
                query,
                (name, description, location, capacity, 1 if is_active else 0, source, verified_at)
            )
            return True
        except Exception:
            return False


class ExtracurricularModel(BaseModel):
    """Model for extracurricular activities operations."""

    def get_extracurriculars(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all extracurricular activities with caching."""
        cache_key = f"extracurricular:active_{active_only}"
        if self.cache:
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                return cached_value

        if active_only:
            query = "SELECT * FROM extracurricular WHERE is_active = 1 ORDER BY name"
        else:
            query = "SELECT * FROM extracurricular ORDER BY name"

        value = self.db.execute_query(query, fetch_all=True) or []

        if self.cache:
            self.cache.set(cache_key, value)

        return value

    def add_extracurricular(
        self,
        name: str,
        description: str = None,
        schedule: str = None,
        requirements: str = None,
        contact_person: str = None,
        is_active: bool = True,
        source: str = "Belum terverifikasi",
        verified_at: Optional[str] = None
    ) -> bool:
        """Add or update extracurricular idempotently."""
        query = """
            INSERT INTO extracurricular (name, description, schedule, requirements, contact_person, is_active, source, verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                description = excluded.description,
                schedule = excluded.schedule,
                requirements = excluded.requirements,
                contact_person = excluded.contact_person,
                is_active = excluded.is_active,
                source = excluded.source,
                verified_at = excluded.verified_at,
                updated_at = CURRENT_TIMESTAMP
        """
        try:
            self.db.execute_query(
                query,
                (name, description, schedule, requirements, contact_person, 1 if is_active else 0, source, verified_at)
            )
            return True
        except Exception:
            return False


class PPDBInfoModel(BaseModel):
    """Model for PPDB information operations."""

    def get_ppdb_info(self, key: str = None, tahun_ajaran: str = None) -> Any:
        """Get PPDB information with caching."""
        cache_key = CacheKey.ppdb_info(key, tahun_ajaran)
        if self.cache:
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                return cached_value

        conditions = ["is_active = 1"]
        params = []

        if key:
            conditions.append("key = ?")
            params.append(key)

        if tahun_ajaran:
            conditions.append("tahun_ajaran = ?")
            params.append(tahun_ajaran)

        where_clause = " AND ".join(conditions)

        if key:
            query = f"SELECT value FROM ppdb_info WHERE {where_clause}"
            result = self.db.execute_query(query, tuple(params), fetch=True)
            value = result["value"] if result else None
        else:
            query = f"SELECT key, value, category, source, verified_at FROM ppdb_info WHERE {where_clause}"
            results = self.db.execute_query(query, tuple(params), fetch_all=True) or []
            value = {row["key"]: row["value"] for row in results}

        if self.cache and value is not None:
            self.cache.set(cache_key, value)

        return value

    def set_ppdb_info(
        self,
        key: str,
        value: str,
        category: str = None,
        tahun_ajaran: str = "2025/2026",
        is_active: bool = True,
        source: str = "Belum terverifikasi",
        verified_at: Optional[str] = None
    ) -> bool:
        """Set or update PPDB info idempotently."""
        query = """
            INSERT INTO ppdb_info (key, value, category, tahun_ajaran, is_active, source, verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                category = excluded.category,
                tahun_ajaran = excluded.tahun_ajaran,
                is_active = excluded.is_active,
                source = excluded.source,
                verified_at = excluded.verified_at,
                updated_at = CURRENT_TIMESTAMP
        """
        try:
            self.db.execute_query(
                query,
                (key, value, category, tahun_ajaran, 1 if is_active else 0, source, verified_at)
            )
            return True
        except Exception:
            return False