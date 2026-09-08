"""
Main bot application for Si Sebel.
Mencoba koneksi WhatsApp, jika gagal fallback ke console mode.
"""

import asyncio
import signal
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from config import settings
from utils import (
    setup_application_logger,
    WhatsAppConnectionError,
    get_cache_manager,
    get_load_balancer,
    get_security_logger,
    get_rate_limiter_security,
    get_security_best_practices,
)
from database import (
    initialize_database,
    SchoolInfoModel,
    JurusanModel,
    FAQModel,
    CalendarModel,
    ContactModel,
    FacilitiesModel,
    ExtracurricularModel,
    PPDBInfoModel,
    ConversationLogModel,
    seed_database,
)
from handlers import WhatsAppHandler, MessageProcessor


class SiSebelBot:
    def __init__(self):
        self.logger = setup_application_logger(
            app_name="sisebel", log_level=settings.log_level, log_file=settings.log_file
        )
        self.logger.info("Initializing Si Sebel Bot...")
        self.logger.info(f"Environment: {settings.environment}")
        self.logger.info(f"Bot Name: {settings.bot_name}")

        self.db = None
        self.cache = None
        self.load_balancer = None
        self.security_logger = None
        self.rate_limiter_security = None
        self.whatsapp_handler = None
        self.message_processor = None
        self.is_running = False
        self.use_whatsapp = False  # akan di-set saat koneksi berhasil

    def initialize(self):
        try:
            self.logger.info("Initializing cache...")
            self.cache = get_cache_manager(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                ttl=settings.cache_ttl,
                enabled=settings.enable_cache,
                logger=self.logger,
            )
            if self.cache.enabled:
                self.cache.connect()
                self.logger.info(f"Cache OK: {self.cache.get_stats()}")
            else:
                self.logger.info("Cache disabled")

            self.logger.info("Initializing load balancer...")
            self.load_balancer = get_load_balancer(
                max_instances=1,
                max_connections=50,
                max_requests=100,
                rate_limit_window=60,
                logger=self.logger,
            )
            self.logger.info("Load balancer OK")

            self.logger.info("Initializing security...")
            self.security_logger = get_security_logger(self.logger)
            self.rate_limiter_security = get_rate_limiter_security(
                max_requests=100, time_window=60, block_duration=300, logger=self.logger
            )
            get_security_best_practices(self.logger)
            self.logger.info("Security OK")

            self.logger.info("Initializing database...")
            self.db = initialize_database(settings.database_path)
            self.logger.info("Seeding database...")
            seed_database(self.db, self.cache)
            self.logger.info("Database seeded!")

        except Exception as e:
            self.logger.error(f"Init failed: {e}")
            raise

    def setup_models(self):
        try:
            self.logger.info("Setting up models...")
            self.school_info = SchoolInfoModel(self.db, self.cache)
            self.jurusan = JurusanModel(self.db, self.cache)
            self.faq = FAQModel(self.db, self.cache)
            self.calendar = CalendarModel(self.db, self.cache)
            self.contact = ContactModel(self.db, self.cache)
            self.facilities = FacilitiesModel(self.db, self.cache)
            self.extracurricular = ExtracurricularModel(self.db, self.cache)
            self.ppdb = PPDBInfoModel(self.db, self.cache)
            self.conversation_log = ConversationLogModel(self.db, self.cache)
            self.logger.info("Models OK")
        except Exception as e:
            self.logger.error(f"Models failed: {e}")
            raise

    def setup_message_processor(self):
        try:
            self.logger.info("Setting up message processor...")
            self.message_processor = MessageProcessor(
                school_info=self.school_info,
                jurusan=self.jurusan,
                faq=self.faq,
                calendar=self.calendar,
                contact=self.contact,
                facilities=self.facilities,
                extracurricular=self.extracurricular,
                ppdb=self.ppdb,
                conversation_log=self.conversation_log,
                logger=self.logger,
            )
            self.logger.info("Message processor ready")
        except Exception as e:
            self.logger.error(f"Processor failed: {e}")
            raise

    def setup_whatsapp_handler(self):
        try:
            self.logger.info("Setting up WhatsApp handler...")
            auth_folder = Path("./piwapp_auth")
            auth_folder.mkdir(parents=True, exist_ok=True)

            async def on_message_callback(message):
                resources_acquired = False
                try:
                    from_jid = message.get("from", "")
                    if not from_jid or "@broadcast" in from_jid or "status" in from_jid:
                        return
                    sender = from_jid.split("@")[0]
                    body = message.get("body", "")
                    message_id = message.get("id") or message.get("message_id")
                    if not body or not sender:
                        return
                    if message_id and not self.db.claim_message_id(str(message_id)):
                        self.logger.info("Duplicate message ignored")
                        return

                    is_allowed, block_reason = self.rate_limiter_security.is_allowed(
                        sender
                    )
                    if not is_allowed:
                        await self.whatsapp_handler.send_message(
                            phone_number=sender, text=f"⚠️ {block_reason}", delay=1
                        )
                        return

                    if not self.load_balancer.is_ready_for_request(sender):
                        self.logger.warning(f"Load balancer reject {sender}")
                        return
                    resources_acquired = True

                    response = await self.message_processor.process_message(
                        phone_number=sender, message=body
                    )
                    if response:
                        await self.whatsapp_handler.send_message(
                            phone_number=sender,
                            text=response,
                            delay=settings.bot_response_delay,
                        )
                except Exception as e:
                    self.logger.error("Callback failed: %s", e)
                finally:
                    if resources_acquired:
                        self.load_balancer.release_resources()

            self.whatsapp_handler = WhatsAppHandler(
                auth_folder=str(auth_folder),
                on_message_callback=on_message_callback,
                logger=self.logger,
            )
            self.logger.info("WhatsApp handler setup OK")
        except Exception as e:
            self.logger.error(f"Handler setup failed: {e}")
            raise

    async def start(self):
        try:
            self.initialize()
            self.setup_models()
            self.setup_message_processor()

            # Coba konek WhatsApp
            try:
                self.setup_whatsapp_handler()
                self.logger.info("Connecting to WhatsApp...")
                await self.whatsapp_handler.connect()
                self.use_whatsapp = True
                self.is_running = True
                self.logger.info("✓ Bot running with WhatsApp! Scan QR code.")
                await self.whatsapp_handler.keep_alive()
            except Exception as e:
                self.logger.warning(f"WhatsApp connection failed: {e}")
                if settings.environment == "development":
                    self.logger.info("Falling back to console mode...")
                    await self._run_console()
                else:
                    raise WhatsAppConnectionError(
                        "WhatsApp connection is required outside development"
                    ) from e

        except Exception as e:
            self.logger.error(f"Start error: {e}")
            raise

    async def _run_console(self):
        """Mode console sebagai fallback."""
        self.is_running = True
        self.logger.info("✓ Console mode active. Ketik pesan (exit untuk keluar).")
        while self.is_running:
            user_input = await asyncio.to_thread(input, ">> ")
            if user_input.lower() in ["exit", "quit", "q"]:
                self.is_running = False
                break
            response = await self.message_processor.process_message(
                phone_number="6281234567890", message=user_input
            )
            print(f"\n🤖 Bot: {response}\n")

    async def stop(self):
        self.logger.info("Stopping bot...")
        self.is_running = False
        if self.whatsapp_handler:
            self.whatsapp_handler.stop()
            await self.whatsapp_handler.disconnect()
        if self.cache and self.cache.enabled:
            self.cache.disconnect()
        if self.db:
            self.db.close()
        self.logger.info("Bot stopped.")

    def setup_signal_handlers(self):
        def signal_handler(signum, frame):
            self.logger.info(f"Signal {signum}, shutting down...")
            self.is_running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main():
    bot = SiSebelBot()
    bot.setup_signal_handlers()
    try:
        await bot.start()
    except KeyboardInterrupt:
        bot.logger.info("Keyboard interrupt.")
    except Exception as e:
        bot.logger.error(f"Fatal: {e}")
        sys.exit(1)
    finally:
        await bot.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
