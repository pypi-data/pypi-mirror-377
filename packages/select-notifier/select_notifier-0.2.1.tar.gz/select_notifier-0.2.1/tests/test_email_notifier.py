from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage
from smtplib import SMTPAuthenticationError
from typing import Any, Callable, ContextManager, Literal, MutableMapping, Optional, cast

import pytest

from select_notifier.base import Message, PermanentNotifierError, TransientNotifierError
from select_notifier.services.email import EmailNotifier, SMTPConfig


# ---------- Helpers: Dummy SMTP contexts ----------
def make_dummy_smtp(
    *,
    success_after: int = 0,
    auth_error: bool = False,
    record: Optional[MutableMapping[str, Any]] = None,
) -> Callable[[str, int, Optional[float]], ContextManager[smtplib.SMTP]]:
    attempts: MutableMapping[str, int] = {"count": 0}
    rec: MutableMapping[str, Any] = record if record is not None else {}

    class DummySMTP:
        # --- context manager methods ---
        def __enter__(self) -> smtplib.SMTP:
            return cast(smtplib.SMTP, self)

        def __exit__(self, exc_type, exc, tb) -> Literal[False]:
            return False

        # --- methods used by EmailNotifier ---
        def ehlo(self) -> None:
            rec["ehlo"] = int(cast(Any, rec.get("ehlo", 0))) + 1

        def starttls(self, context: Optional[ssl.SSLContext] = None) -> None:
            assert isinstance(context, ssl.SSLContext)
            rec["starttls"] = int(cast(Any, rec.get("starttls", 0))) + 1

        def login(self, user: str, pwd: str) -> None:
            rec["login"] = (user, pwd)
            if auth_error:
                raise SMTPAuthenticationError(535, b"5.7.8 Authentication failed")

        def send_message(self, msg: EmailMessage) -> None:
            attempts["count"] = int(cast(Any, attempts.get("count", 0))) + 1
            rec["last_msg"] = msg
            if int(cast(Any, attempts["count"])) <= success_after:
                raise smtplib.SMTPException("transient failure")

    def factory(host: str, port: int, timeout: Optional[float]) -> ContextManager[smtplib.SMTP]:
        rec["factory_args"] = (host, port, timeout)
        return cast(ContextManager[smtplib.SMTP], DummySMTP())

    return factory


# ---------- Fixtures ----------
@pytest.fixture
def cfg_valid() -> SMTPConfig:
    return SMTPConfig(
        server="smtp.test.local",
        port=587,
        sender="from@example.com",
        password=" ap۱۲۳ 4 ",  # -> "ap1234"
        use_tls=True,
        use_ssl=False,
        timeout=5.0,
    )


# ---------- Tests ----------
def test_send_success(cfg_valid: SMTPConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    rec: MutableMapping[str, Any] = {}
    smtp_factory = make_dummy_smtp(success_after=0, record=rec)
    notifier = EmailNotifier(cfg_valid, retries=0, backoff=None, smtp_factory=smtp_factory)

    res = notifier.send_text(subject="OK", body="hello", to=["rcpt@example.com"])
    assert res.ok is True
    assert res.provider == "email"
    lm = cast(EmailMessage, rec.get("last_msg"))
    assert isinstance(lm, EmailMessage)
    assert lm["From"] == cfg_valid.sender
    assert lm["To"] == "rcpt@example.com"
    assert lm["Subject"] == "OK"


def test_missing_to_raises(cfg_valid: SMTPConfig) -> None:
    notifier = EmailNotifier(cfg_valid, smtp_factory=make_dummy_smtp())
    msg = Message.create(subject="s", body="b", to=[])
    with pytest.raises(PermanentNotifierError, match="'to' is required"):
        notifier.send(msg)


@pytest.mark.parametrize("bad_sender", ["", "foo", "foo@", "foo@bar", "a@b", "no-at-symbol.com"])
def test_invalid_sender_raises(bad_sender: str, cfg_valid: SMTPConfig) -> None:
    bad_cfg = SMTPConfig(
        server=cfg_valid.server,
        port=cfg_valid.port,
        sender=bad_sender,
        password=cfg_valid.password,
        use_tls=True,
        use_ssl=False,
        timeout=cfg_valid.timeout,
    )
    notifier = EmailNotifier(bad_cfg, smtp_factory=make_dummy_smtp())
    with pytest.raises(PermanentNotifierError, match="Invalid sender"):
        notifier.send_text(subject="s", body="b", to=["rcpt@example.com"])


@pytest.mark.parametrize("bad_rcpt", ["", "x@", "x@z", "no-at"])
def test_invalid_recipient_raises(bad_rcpt: str, cfg_valid: SMTPConfig) -> None:
    notifier = EmailNotifier(cfg_valid, smtp_factory=make_dummy_smtp())
    with pytest.raises(PermanentNotifierError, match="Invalid recipient"):
        notifier.send_text(subject="s", body="b", to=[bad_rcpt])


def test_auth_error_eventually_permanent(
    monkeypatch: pytest.MonkeyPatch, cfg_valid: SMTPConfig
) -> None:
    monkeypatch.setattr("time.sleep", lambda s: None)
    smtp_factory = make_dummy_smtp(auth_error=True)
    notifier = EmailNotifier(cfg_valid, retries=1, backoff=1.1, smtp_factory=smtp_factory)
    with pytest.raises(PermanentNotifierError, match="Authentication"):
        notifier.send_text(subject="s", body="b", to=["rcpt@example.com"])


def test_transient_failure_then_success(
    monkeypatch: pytest.MonkeyPatch, cfg_valid: SMTPConfig
) -> None:
    monkeypatch.setattr("time.sleep", lambda s: None)
    rec: MutableMapping[str, Any] = {}
    smtp_factory = make_dummy_smtp(success_after=1, record=rec)
    notifier = EmailNotifier(cfg_valid, retries=2, backoff=1.1, smtp_factory=smtp_factory)
    res = notifier.send_text(subject="retry", body="will pass on 2nd", to=["rcpt@example.com"])
    assert res.ok is True
    assert int(cast(Any, rec.get("starttls", 0))) >= 1


def test_transient_failure_exhausts_retries(
    monkeypatch: pytest.MonkeyPatch, cfg_valid: SMTPConfig
) -> None:
    monkeypatch.setattr("time.sleep", lambda s: None)
    smtp_factory = make_dummy_smtp(success_after=99)
    notifier = EmailNotifier(cfg_valid, retries=1, backoff=1.1, smtp_factory=smtp_factory)
    with pytest.raises(TransientNotifierError):
        notifier.send_text(subject="retry", body="never", to=["rcpt@example.com"])


def test_password_normalization_applied(cfg_valid: SMTPConfig) -> None:
    n = EmailNotifier(cfg_valid, smtp_factory=make_dummy_smtp())
    assert n._cfg.password == "ap1234"


def test_starttls_used_when_tls_true(cfg_valid: SMTPConfig) -> None:
    rec: MutableMapping[str, Any] = {}
    smtp_factory = make_dummy_smtp(record=rec)
    notifier = EmailNotifier(cfg_valid, smtp_factory=smtp_factory)
    notifier.send_text(subject="s", body="b", to=["rcpt@example.com"])
    assert int(cast(Any, rec.get("starttls", 0))) >= 1


def test_no_starttls_when_tls_false() -> None:
    cfg = SMTPConfig(
        server="smtp.test.local",
        port=587,
        sender="from@example.com",
        password="x",
        use_tls=False,
        use_ssl=False,
        timeout=5.0,
    )
    rec: MutableMapping[str, Any] = {}
    smtp_factory = make_dummy_smtp(record=rec)
    notifier = EmailNotifier(cfg, smtp_factory=smtp_factory)
    notifier.send_text(subject="s", body="b", to=["rcpt@example.com"])
    assert int(cast(Any, rec.get("starttls", 0))) == 0
