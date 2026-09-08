"""
Handlers package for Si Sebel Bot.
"""

from .message_processor import MessageProcessor

try:
    from .whatsapp_handler import WhatsAppHandler, WhatsAppManager
except Exception as e:
    print(f"❌ ERROR saat import whatsapp_handler: {type(e).__name__}: {e}")
    raise  # tetap naikkan error agar terlihat

__all__ = [
    'MessageProcessor',
    'WhatsAppHandler',
    'WhatsAppManager'
]