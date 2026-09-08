import asyncio

import pytest

from handlers.whatsapp_handler import WhatsAppHandler
from utils.metrics import Metrics
from utils.security import InputValidator, RateLimiterSecurity


def test_input_validator_rejects_malicious_payload():
    valid, reason = InputValidator().validate_message("<script>alert(1)</script>")
    assert not valid
    assert "blocked" in reason.lower()


def test_rate_limiter_blocks_after_limit():
    limiter = RateLimiterSecurity(max_requests=1, time_window=60, block_duration=60)
    assert limiter.is_allowed("sender")[0]
    allowed, reason = limiter.is_allowed("sender")
    assert not allowed
    assert reason


def test_phone_formatting_normalizes_indonesian_numbers():
    handler = WhatsAppHandler.__new__(WhatsAppHandler)
    assert handler._format_phone("0812-3456-7890") == "6281234567890"
    assert handler._format_phone("6281234567890") == "6281234567890"


def test_send_message_returns_false_when_disconnected():
    handler = WhatsAppHandler.__new__(WhatsAppHandler)
    handler.is_connected = False
    assert asyncio.run(handler.send_message("081234567890", "test")) is False


def test_metrics_snapshot_is_copy_and_rejects_invalid_values():
    registry = Metrics()
    registry.increment("messages.received", 2)
    snapshot = registry.snapshot()
    snapshot["messages.received"] = 99
    assert registry.snapshot()["messages.received"] == 2
    with pytest.raises(ValueError):
        registry.increment("", 1)


def test_input_validator_allows_normal_double_hyphen_text():
    validator = InputValidator()
    # Everyday Indonesian phrases with double hyphens or dashes should NOT be blocked
    valid, sanitized = validator.validate_message("Halo pak -- mau tanya info jurusan")
    assert valid
    assert "info jurusan" in sanitized

    valid2, sanitized2 = validator.validate_message("jadwal ujian - - terima kasih")
    assert valid2

    # Actual SQL injection comment with query must still be blocked
    is_valid, reason = validator.validate_message("admin'-- DROP TABLE users")
    assert not is_valid
    assert "blocked" in reason.lower()


def test_rate_limiter_memory_cleanup():
    limiter = RateLimiterSecurity(max_requests=10, time_window=1, block_duration=2)
    # Simulate past request
    limiter.requests["old_user"] = [(100.0, False)]
    limiter.blocked_until["expired_user"] = 100.0

    limiter.cleanup_expired(current_time=200.0)

    assert "old_user" not in limiter.requests
    assert "expired_user" not in limiter.blocked_until


def test_reset_security_instances():
    from utils.security import get_input_validator, reset_security_instances

    v1 = get_input_validator()
    v2 = get_input_validator()
    assert v1 is v2

    reset_security_instances()
    v3 = get_input_validator()
    assert v3 is not v1
