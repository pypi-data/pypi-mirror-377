from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Tuple

import pytest
from telegram.error import RetryAfter, TimedOut, NetworkError, BadRequest, TelegramError

from select_notifier.base import Message, PermanentNotifierError, TransientNotifierError
from select_notifier.services.telegram import (
    TelegramConfig,
    TelegramNotifier,
    TelegramAsyncNotifier,
)


# --------------------------------
# Dummy async Bot to monkeypatch
# --------------------------------
class DummyBot:
    def __init__(self, record: Dict[str, Any], outcomes: List[Tuple[Any, ...]]) -> None:
        self._record = record
        self._outcomes = list(outcomes)
        self.token = "DUMMY"
        self.request = None
        self.base_url = "https://api.telegram.org/bot"

    async def send_message(self, *, chat_id: str | int, text: str, **kwargs: Any) -> Any:
        self._record["calls"] = int(self._record.get("calls", 0)) + 1
        self._record["last_chat_id"] = chat_id
        self._record["last_text"] = text
        self._record["last_kwargs"] = kwargs

        if not self._outcomes:
            return {"ok": True, "result": "default"}

        kind = self._outcomes.pop(0)
        if kind[0] == "ok":
            return {"ok": True, "result": "sent"}
        if kind[0] == "raise":
            raise kind[1]
        raise AssertionError("unknown outcome kind")


# ---------------------------
# Fixtures & helpers
# ---------------------------
@pytest.fixture
def cfg_ok() -> TelegramConfig:
    return TelegramConfig(
        bot_token="TEST_TOKEN",
        api_base="https://api.telegram.org",
        timeout=5.0,
        proxy_url=None,
    )


def monkeypatch_bot(monkeypatch: pytest.MonkeyPatch, record: Dict[str, Any], outcomes: List[Tuple[Any, ...]]) -> None:
    import select_notifier.services.telegram as tmod

    def _dummy_ctor(*args: Any, **kwargs: Any) -> DummyBot:
        return DummyBot(record=record, outcomes=outcomes)

    monkeypatch.setattr(tmod, "Bot", _dummy_ctor)


# ---------------------------
# Tests: TelegramNotifier (sync wrapper)
# ---------------------------
def test_send_success_first_try(cfg_ok: TelegramConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    rec: Dict[str, Any] = {}
    monkeypatch_bot(monkeypatch, rec, outcomes=[("ok",)])

    n = TelegramNotifier.create(
        bot_token=cfg_ok.bot_token,
        api_base=cfg_ok.api_base,
        timeout=cfg_ok.timeout,
    )

    msg = Message.create(subject="Deploy", body="✅ shipped", to=["fake_chat"])
    res = n.send(msg)

    assert res.ok is True
    assert res.provider == "telegram"
    assert rec["calls"] == 1
    assert rec["last_text"].startswith("Deploy\n✅ shipped")
    assert rec["last_chat_id"] == "fake_chat"


def test_subject_optional(cfg_ok: TelegramConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    rec: Dict[str, Any] = {}
    monkeypatch_bot(monkeypatch, rec, outcomes=[("ok",)])

    n = TelegramNotifier.create(bot_token=cfg_ok.bot_token, api_base=cfg_ok.api_base)
    msg = Message.create(subject="", body="Body only", to=["fake_chat"])
    res = n.send(msg)

    assert res.ok is True
    assert rec["last_text"] == "Body only"


def test_missing_body_raises(cfg_ok: TelegramConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    rec: Dict[str, Any] = {}
    monkeypatch_bot(monkeypatch, rec, outcomes=[("ok",)])

    n = TelegramNotifier.create(bot_token=cfg_ok.bot_token, api_base=cfg_ok.api_base)
    msg = Message.create(subject="S", body="   ", to=["fake_chat"])
    with pytest.raises(PermanentNotifierError, match="body is required"):
        n.send(msg)


def test_missing_to_raises(cfg_ok: TelegramConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    rec: Dict[str, Any] = {}
    monkeypatch_bot(monkeypatch, rec, outcomes=[("ok",)])

    n = TelegramNotifier.create(bot_token=cfg_ok.bot_token, api_base=cfg_ok.api_base)
    msg = Message.create(subject="S", body="B", to=[])
    with pytest.raises(PermanentNotifierError, match="'to'"):
        n.send(msg)


def test_retry_after_then_success(monkeypatch: pytest.MonkeyPatch, cfg_ok: TelegramConfig) -> None:
    monkeypatch.setattr("time.sleep", lambda s: None)

    rec: Dict[str, Any] = {}
    monkeypatch_bot(
        monkeypatch,
        rec,
        outcomes=[
            ("raise", RetryAfter("wait", retry_after=1)),
            ("ok",),
        ],
    )

    n = TelegramNotifier.create(
        bot_token=cfg_ok.bot_token,
        api_base=cfg_ok.api_base,
        retries=2,
        backoff=1.2,
    )
    msg = Message.create(subject="", body="B", to=["fake_chat"])
    res = n.send(msg)

    assert res.ok is True
    assert rec["calls"] == 2


def test_network_timeout_then_success(monkeypatch: pytest.MonkeyPatch, cfg_ok: TelegramConfig) -> None:
    monkeypatch.setattr("time.sleep", lambda s: None)

    rec: Dict[str, Any] = {}
    monkeypatch_bot(
        monkeypatch,
        rec,
        outcomes=[
            ("raise", TimedOut("t")),
            ("ok",),
        ],
    )

    n = TelegramNotifier.create(
        bot_token=cfg_ok.bot_token,
        api_base=cfg_ok.api_base,
        retries=1,
        backoff=1.1,
    )
    msg = Message.create(subject="S", body="B", to=["fake_chat"])
    res = n.send(msg)

    assert res.ok is True
    assert rec["calls"] == 2


def test_network_error_exhausts(monkeypatch: pytest.MonkeyPatch, cfg_ok: TelegramConfig) -> None:
    monkeypatch.setattr("time.sleep", lambda s: None)

    rec: Dict[str, Any] = {}
    monkeypatch_bot(
        monkeypatch,
        rec,
        outcomes=[
            ("raise", NetworkError("down")),
            ("raise", NetworkError("down")),
        ],
    )

    n = TelegramNotifier.create(
        bot_token=cfg_ok.bot_token,
        api_base=cfg_ok.api_base,
        retries=1,
        backoff=1.1,
    )
    msg = Message.create(subject="S", body="B", to=["fake_chat"])

    with pytest.raises(TransientNotifierError):
        n.send(msg)
    assert rec["calls"] == 2


def test_bad_request_is_permanent(cfg_ok: TelegramConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    rec: Dict[str, Any] = {}
    monkeypatch_bot(monkeypatch, rec, outcomes=[("raise", BadRequest("bad chat id"))])

    n = TelegramNotifier.create(bot_token=cfg_ok.bot_token, api_base=cfg_ok.api_base)
    msg = Message.create(subject="S", body="B", to=["bad"])

    with pytest.raises(PermanentNotifierError, match="bad chat id"):
        n.send(msg)
    assert rec["calls"] == 1


def test_telegram_error_transient(monkeypatch: pytest.MonkeyPatch, cfg_ok: TelegramConfig) -> None:
    monkeypatch.setattr("time.sleep", lambda s: None)

    rec: Dict[str, Any] = {}
    monkeypatch_bot(
        monkeypatch,
        rec,
        outcomes=[
            ("raise", TelegramError("oops")),
            ("ok",),
        ],
    )

    n = TelegramNotifier.create(
        bot_token=cfg_ok.bot_token,
        api_base=cfg_ok.api_base,
        retries=1,
        backoff=1.1,
    )
    msg = Message.create(subject="S", body="B", to=["fake_chat"])
    res = n.send(msg)
    assert res.ok is True
    assert rec["calls"] == 2


def test_constructor_requires_backoff_when_retries_positive(cfg_ok: TelegramConfig) -> None:
    with pytest.raises(PermanentNotifierError, match="backoff must be > 0"):
        TelegramNotifier.create(bot_token=cfg_ok.bot_token, api_base=cfg_ok.api_base, retries=1)


def test_invalid_timeout_raises() -> None:
    with pytest.raises(PermanentNotifierError, match="timeout must be > 0"):
        TelegramNotifier.create(bot_token="T", api_base="https://api.telegram.org", timeout=0)


# ---------------------------
# Tests: TelegramAsyncNotifier
# ---------------------------
@pytest.mark.asyncio
async def test_async_send_success(cfg_ok: TelegramConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    rec: Dict[str, Any] = {}
    import select_notifier.services.telegram as tmod

    def _dummy_ctor(*args: Any, **kwargs: Any) -> DummyBot:
        return DummyBot(record=rec, outcomes=[("ok",)])

    monkeypatch.setattr(tmod, "Bot", _dummy_ctor)

    n = TelegramAsyncNotifier.create(
        bot_token=cfg_ok.bot_token,
        api_base=cfg_ok.api_base,
        timeout=cfg_ok.timeout,
    )
    msg = Message.create(subject="", body="hi", to=["1207551180"])
    res = await n.send_async(msg)

    assert res.ok is True
    assert rec["calls"] == 1
    assert rec["last_text"] == "hi"


@pytest.mark.asyncio
async def test_async_bad_request(cfg_ok: TelegramConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    rec: Dict[str, Any] = {}
    import select_notifier.services.telegram as tmod

    def _dummy_ctor(*args: Any, **kwargs: Any) -> DummyBot:
        return DummyBot(record=rec, outcomes=[("raise", BadRequest("bad"))])

    monkeypatch.setattr(tmod, "Bot", _dummy_ctor)

    n = TelegramAsyncNotifier.create(bot_token=cfg_ok.bot_token, api_base=cfg_ok.api_base)
    msg = Message.create(subject="x", body="y", to=["-1"])
    with pytest.raises(PermanentNotifierError, match="bad"):
        await n.send_async(msg)
    assert rec["calls"] == 1


# ---------------------------
# Guard: sync wrapper must not run under a running loop
# ---------------------------
def test_sync_wrapper_errors_if_loop_running(cfg_ok: TelegramConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    rec: Dict[str, Any] = {}
    monkeypatch_bot(monkeypatch, rec, outcomes=[("ok",)])

    n = TelegramNotifier.create(bot_token=cfg_ok.bot_token, api_base=cfg_ok.api_base)

    async def _call_send_in_loop() -> None:
        msg = Message.create(subject="", body="B", to=["1207551180"])
        with pytest.raises(PermanentNotifierError, match="event loop is running"):
            await asyncio.to_thread(n.send, msg)

    asyncio.run(_call_send_in_loop())
