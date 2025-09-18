from dataclasses import dataclass

@dataclass
class SMTPConfig:
    host: str | None
    port: int | None
    password: str | None
    sender_email: str | None
    use_tls: bool = True
    use_ssl: bool = False
