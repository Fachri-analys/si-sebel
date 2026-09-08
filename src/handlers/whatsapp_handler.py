"""
WhatsApp handler - dengan debug import
"""

import asyncio
from collections import deque
from pathlib import Path
from typing import Callable, Optional

# ========== IMPORT PIWAPP DENGAN DEBUG ==========
try:
    import piwapp
    PIWAPP_AVAILABLE = True
    print(f"✅ piwapp terdeteksi, versi: {piwapp.__version__}")
except Exception as e:
    PIWAPP_AVAILABLE = False
    print(f"❌ Gagal import piwapp: {type(e).__name__}: {e}")

from utils.logger import Logger
from utils.exceptions import WhatsAppConnectionError
from utils.security import InputValidator


class WhatsAppHandler:
    def __init__(
        self,
        auth_folder: str = "./piwapp_auth",
        on_message_callback: Optional[Callable] = None,
        logger: Optional[Logger] = None
    ):
        if not PIWAPP_AVAILABLE:
            raise WhatsAppConnectionError("piwapp not installed.")

        self.auth_folder = Path(auth_folder)
        self.auth_folder.mkdir(parents=True, exist_ok=True)
        self.on_message_callback = on_message_callback
        self.logger = logger or Logger.get_logger("whatsapp_handler")
        self.client = None
        self.is_connected = False
        self.is_running = False
        self._processed_message_ids = set()
        self._processed_message_order = deque(maxlen=10000)

    async def connect(self) -> None:
        try:
            self.logger.info("Initializing WhatsApp client...")
            ClientClass = getattr(piwapp, 'Client', None)
            if ClientClass is None:
                raise WhatsAppConnectionError("Client class not found in piwapp")

            # Coba dari auth folder
            if hasattr(piwapp, 'from_auth_folder'):
                self.client = await piwapp.from_auth_folder(str(self.auth_folder))
            else:
                self.client = ClientClass(
                    keys_path=str(self.auth_folder),
                    db_path=str(self.auth_folder / "piwapp.db")
                )

            self._setup_event_handlers()

            self.logger.info("Connecting...")
            if hasattr(self.client, 'start'):
                await self.client.start()
            elif hasattr(self.client, 'connect'):
                await self.client.connect()
            else:
                raise WhatsAppConnectionError("Client has no start/connect")

            self.is_connected = True
            self.logger.info("✓ WhatsApp connected!")

        except Exception as e:
            self.logger.error(f"Connect error: {e}")
            raise WhatsAppConnectionError(f"Connection failed: {e}")

    def _setup_event_handlers(self):
        if hasattr(self.client, 'on'):
            @self.client.on("connection.update")
            async def on_connection_update(update):
                if hasattr(update, 'qr') and update.qr:
                    self.logger.info("📱 QR Code:")
                    self.logger.info(update.qr)
                if hasattr(update, 'connection'):
                    if update.connection == "open":
                        self.is_connected = True
                        self.logger.info("✓ WhatsApp open!")
                    elif update.connection == "close":
                        self.is_connected = False
                        self.logger.warning("WhatsApp closed")

            @self.client.on("message")
            async def on_message(message):
                try:
                    message_id = (
                        message.get("id")
                        or message.get("message_id")
                        or message.get("key", {}).get("id")
                    )
                    if message_id:
                        if message_id in self._processed_message_ids:
                            self.logger.info("Ignoring duplicate WhatsApp message")
                            return
                        self._processed_message_ids.add(message_id)
                        self._processed_message_order.append(message_id)
                        if len(self._processed_message_ids) > self._processed_message_order.maxlen:
                            self._processed_message_ids.discard(self._processed_message_order.popleft())
                    sender = message.get('from', '').split('@')[0]
                    body = message.get('body', '')
                    sender_hash = InputValidator().hash_phone_number(sender)
                    self.logger.info(
                        "Incoming WhatsApp message sender_hash=%s body_length=%d",
                        sender_hash,
                        len(body),
                    )
                    if self.on_message_callback:
                        await self.on_message_callback(message)
                except Exception as e:
                    self.logger.error(f"Message error: {e}")
        else:
            self.logger.warning("Client doesn't support 'on' events")

    async def send_message(self, phone_number: str, text: str, delay: float = 1.0) -> bool:
        if not self.is_connected:
            return False
        try:
            phone = self._format_phone(phone_number)
            await asyncio.sleep(delay)
            if hasattr(self.client, 'send_text'):
                await asyncio.wait_for(
                    self.client.send_text(to=phone, text=text),
                    timeout=30,
                )
            elif hasattr(self.client, 'send_message'):
                await asyncio.wait_for(
                    self.client.send_message(to=phone, text=text),
                    timeout=30,
                )
            else:
                return False
            self.logger.info(f"✅ Sent to {phone}")
            return True
        except Exception as e:
            self.logger.error(f"Send failed: {e}")
            return False

    def _format_phone(self, phone: str) -> str:
        digits = "".join(filter(str.isdigit, phone))
        if digits.startswith("0"):
            return "62" + digits[1:]
        if not digits.startswith("62"):
            return "62" + digits
        return digits

    async def disconnect(self):
        if self.client:
            if hasattr(self.client, 'disconnect'):
                await self.client.disconnect()
            elif hasattr(self.client, 'stop'):
                await self.client.stop()
            self.is_connected = False

    async def keep_alive(self):
        self.is_running = True
        while self.is_running:
            await asyncio.sleep(1)

    def stop(self):
        self.is_running = False


class WhatsAppManager:
    def __init__(self, auth_folder="./piwapp_auth", on_message_callback=None, logger=None):
        self.handler = WhatsAppHandler(auth_folder, on_message_callback, logger)

    async def __aenter__(self):
        await self.handler.connect()
        return self.handler

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.handler.disconnect()