from __future__ import annotations

import logging
import re
import smtplib
import ssl
import time
import unicodedata
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from smtplib import SMTPAuthenticationError
from typing import Callable, ContextManager, Optional, Protocol

from select_notifier.base import (
    Message,
    Notifier,
    PermanentNotifierError,
    SendResult,
    TransientNotifierError,
    normalize_message,
)

# ---------------------------------
# Logging (no forced handlers; user controls logging config)
# ---------------------------------
logger = logging.getLogger("select_notifier.email")


# ---------------------------------
# Config
# ---------------------------------
@dataclass(frozen=True)
class SMTPConfig:
    """SMTP configuration."""

    server: str
    port: int
    sender: str
    password: str
    use_tls: bool = True  # STARTTLS (587)
    use_ssl: bool = False  # SMTPS (465)
    timeout: Optional[float] = None  # None => use smtplib default


# ---------------------------------
# SMTP factory protocol (DIP)
# ---------------------------------
class SMTPContextFactory(Protocol):
    """SMTP context factory protocol."""

    def __call__(
        self, server: str, port: int, timeout: Optional[float]
    ) -> ContextManager[smtplib.SMTP]: ...


def _default_smtp_factory(
    server: str,
    port: int,
    timeout: Optional[float],
    *,
    use_ssl: bool,
) -> ContextManager[smtplib.SMTP]:
    """Default SMTP factory."""
    if use_ssl:
        if timeout is None:
            return smtplib.SMTP_SSL(server, port)  # type: ignore[return-value]
        return smtplib.SMTP_SSL(server, port, timeout=timeout)  # type: ignore[return-value]
    else:
        if timeout is None:
            return smtplib.SMTP(server, port)  # type: ignore[return-value]
        return smtplib.SMTP(server, port, timeout=timeout)  # type: ignore[return-value]


# ---------------------------------
# EmailNotifier (implements Notifier)
# ---------------------------------
class EmailNotifier(Notifier):
    """Email notifier."""

    provider_name = "email"
    _EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(
        self,
        config: SMTPConfig,
        *,
        retries: Optional[int] = None,
        backoff: Optional[float] = None,
        smtp_factory: (
            Callable[[str, int, Optional[float]], ContextManager[smtplib.SMTP]] | None
        ) = None,
    ) -> None:
        """Initialize the email notifier.
        - retries: if None => treated as 0
        - backoff: required only when retries > 0 and must be > 0
        - timeout: if provided, must be > 0
        """
        norm_pwd = self._normalize_secret(config.password)
        object.__setattr__(config, "password", norm_pwd)

        if config.timeout is not None and config.timeout <= 0:
            raise PermanentNotifierError("timeout must be > 0 when provided")

        self._cfg = config

        self._retries = int(retries) if retries is not None else 0
        if self._retries < 0:
            raise PermanentNotifierError("retries must be >= 0")
        if self._retries > 0:
            if backoff is None or backoff <= 0:
                raise PermanentNotifierError("backoff must be > 0 when retries > 0")
            self._backoff = float(backoff)
        else:
            self._backoff = 0.0

        self._smtp_factory = smtp_factory or (
            lambda host, port, timeout: _default_smtp_factory(
                host, port, timeout, use_ssl=config.use_ssl
            )
        )

    # -------- Public: Notifier API --------
    def send(self, message: Message) -> SendResult:
        """Send an email."""
        if not message.to:
            raise PermanentNotifierError("'to' is required for EmailNotifier")
        self._validate_email(self._cfg.sender, "sender")
        for addr in message.to:
            self._validate_email(addr, "recipient")

        msg = self._build_text_message(
            sender=self._cfg.sender,
            to=", ".join(message.to),
            subject=message.subject,
            body_text=message.body,
        )

        attempt = 0
        last_err: Exception | None = None

        while attempt <= self._retries:
            attempt += 1
            try:
                logger.info(
                    "Email send (attempt %d/%d) to %s", attempt, self._retries + 1, message.to
                )

                context = ssl.create_default_context()
                with self._smtp_factory(
                    self._cfg.server, self._cfg.port, self._cfg.timeout
                ) as smtp:
                    smtp.ehlo()
                    if self._cfg.use_tls and not self._cfg.use_ssl:
                        smtp.starttls(context=context)
                        smtp.ehlo()
                    smtp.login(self._cfg.sender, self._cfg.password)
                    smtp.send_message(msg)

                logger.info("Email sent successfully to %s", message.to)
                return SendResult.success(provider=self.provider_name)

            except SMTPAuthenticationError as e:
                last_err = e
                logger.warning("SMTP auth failed (attempt %d): %s", attempt, e)
                if attempt > self._retries:
                    raise PermanentNotifierError(str(e)) from e
                if self._backoff > 0:
                    time.sleep(self._backoff**attempt)

            except (smtplib.SMTPException, OSError) as e:
                last_err = e
                logger.warning("SMTP send failed (attempt %d): %r", attempt, e)
                if attempt > self._retries:
                    raise TransientNotifierError(str(e)) from e
                if self._backoff > 0:
                    time.sleep(self._backoff**attempt)

        raise TransientNotifierError(
            f"Failed to send email to {message.to!r} via {self._cfg.server}:{self._cfg.port} "
            f"after {attempt} attempts."
        ) from last_err

    # -------- Convenience wrapper --------
    def send_text(
        self,
        *,
        subject: str,
        body: str,
        to: list[str] | tuple[str, ...],
    ) -> SendResult:
        """Send a text email (subject required for email)."""
        msg = normalize_message(subject=subject, body=body, to=to)
        return self.send(msg)

    # -------- Private helpers --------
    @staticmethod
    def _validate_email(addr: str, label: str) -> None:
        """Validate the email address."""
        if not addr or not EmailNotifier._EMAIL_RE.match(addr):
            raise PermanentNotifierError(f"Invalid {label} email address: {addr!r}")

    @staticmethod
    def _normalize_secret(secret: str) -> str:
        """Normalize the secret."""
        s = "".join(ch for ch in secret if not ch.isspace())
        s = "".join(
            str(unicodedata.digit(ch)) if ch.isdigit() and not ch.isascii() else ch for ch in s
        )
        return s

    @staticmethod
    def _build_text_message(*, sender: str, to: str, subject: str, body_text: str) -> EmailMessage:
        """Build a text email message."""
        if not subject or not subject.strip():
            raise PermanentNotifierError("subject is required for email")
        if not body_text.strip():
            raise PermanentNotifierError("body is required")

        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()
        msg.set_content(body_text)
        return msg

    # -------- Factory method --------
    @classmethod
    def create(
        cls,
        *,
        sender: str,
        password: str,
        server: str,
        port: int,
        use_tls: bool = True,
        use_ssl: bool = False,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        backoff: Optional[float] = None,
    ) -> "EmailNotifier":
        """Create an email notifier.
        - timeout: None => use smtplib default
        - retries: None => treated as 0
        - backoff: required only when retries > 0
        """
        cfg = SMTPConfig(
            server=server,
            port=port,
            sender=sender,
            password=password,
            use_tls=use_tls,
            use_ssl=use_ssl,
            timeout=timeout,
        )
        return cls(cfg, retries=retries, backoff=backoff)
