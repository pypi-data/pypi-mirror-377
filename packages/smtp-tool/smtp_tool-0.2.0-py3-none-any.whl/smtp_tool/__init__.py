from .smtp_config import SMTPConfig
from .email_sender import send_email

__all__ = [
    "SMTPConfig",
    "send_email",
]

__version__ = "0.1.0"
