"""Provider-neutral contract used by the chatbot WhatsApp integration."""

from typing import Awaitable, Callable, Mapping, Protocol

MessageCallback = Callable[[Mapping[str, object]], Awaitable[None]]


class WhatsAppAdapter(Protocol):
    """Minimal transport contract required by the business layer."""

    is_connected: bool

    async def connect(self) -> None: ...

    async def send_message(
        self, phone_number: str, text: str, delay: float = 1.0
    ) -> bool: ...

    async def disconnect(self) -> None: ...
