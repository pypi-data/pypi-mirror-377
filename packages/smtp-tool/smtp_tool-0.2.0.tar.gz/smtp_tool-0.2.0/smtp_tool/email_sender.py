from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from typing import Literal

from .smtp_config import SMTPConfig


def send_email(
    to_list: list[str],
    subject: str,
    body: str,
    config: SMTPConfig,
    subtype: Literal["plain", "html"] = "plain",
    sender_name: str | None = None,
) -> str:
    """
    发送邮件.

    Args:
        to_list (list[str]): 收件人列表.
        subject (str): 邮件主题.
        body (str): 邮件正文.
        config (SMTPConfig): SMTP 配置.
        subtype (Literal["plain", "html"], optional): 邮件正文类型.
        sender_name (str | None, optional): 发件人名称.
    Returns:
        str: 发送的邮件 ID.
    Raises:
        ValueError: 如果缺少必要参数.
        smtplib.SMTPException: 如果发送邮件失败.
    """
    if not isinstance(config, SMTPConfig):
        raise TypeError("config must be an SMTPConfig instance")

    if not config.host:
        raise ValueError("SMTP host is required")
    if not config.port or config.port <= 0:
        raise ValueError("Valid SMTP port is required")
    if not config.password:
        raise ValueError("SMTP password is required")
    if not config.sender_email:
        raise ValueError("Sender email is required")

    if not to_list:
        raise ValueError("Recipient 'to' is required")

    sender_email = config.sender_email
    if not sender_email:
        raise ValueError("Sender email is required (sender_email or username)")

    msg = EmailMessage()
    msg["Subject"] = subject or ""
    msg["From"] = formataddr((sender_name or "", sender_email))
    msg["To"] = ", ".join(to_list)

    msg.set_content(body or "", subtype=subtype)

    message_id = make_msgid()
    msg["Message-ID"] = message_id

    recipients = to_list

    context = ssl.create_default_context()

    if config.use_ssl:
        server = smtplib.SMTP_SSL(config.host, config.port, context=context)
    else:
        server = smtplib.SMTP(config.host, config.port)

    try:
        server.ehlo()
        if config.use_tls:
            server.starttls(context=context)
            server.ehlo()

        if config.sender_email and config.password:
            server.login(config.sender_email, config.password)

        server.send_message(msg, from_addr=sender_email, to_addrs=recipients)
    finally:
        try:
            server.quit()
        except Exception:
            server.close()

    return message_id
