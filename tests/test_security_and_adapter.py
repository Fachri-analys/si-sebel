from handlers.whatsapp_handler import WhatsAppHandler
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


def test_whatsapp_phone_normalization():
    handler = WhatsAppHandler.__new__(WhatsAppHandler)
    assert handler._format_phone("0812-3456-7890") == "6281234567890"
