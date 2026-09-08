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
