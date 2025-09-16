from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import httpx
import pytest

from select_notifier.base import Message, PermanentNotifierError, TransientNotifierError
from select_notifier.services.rocket import RocketConfig, RocketNotifier


# ---------------------------
# Dummy httpx.Client factory
# ---------------------------
class DummyResponse:
    def __init__(
        self,
        status_code: int = 200,
        text: str = "ok",
        json_data: Optional[dict] = None,
        json_raises: bool = False,
    ) -> None:
        self.status_code = status_code
        self.text = text
        self._json_data = {"success": True} if json_data is None else json_data
        self._json_raises = json_raises

    def json(self) -> dict:
        if self._json_raises:
            raise ValueError("invalid json")
        return self._json_data


class DummyHTTPClient:
    def __init__(self, outcomes: List[Tuple[Any, ...]], record: Dict[str, Any]) -> None:
        self._outcomes = list(outcomes)
        self.record = record

    def post(
        self, url: str, headers: Optional[dict] = None, json: Optional[dict] = None
    ) -> DummyResponse:
        self.record["last_url"] = url
        self.record["last_headers"] = headers or {}
        self.record["last_json"] = json or {}
        self.record["calls"] = int(self.record.get("calls", 0)) + 1

        if not self._outcomes:
            return DummyResponse()

        kind = self._outcomes.pop(0)
        if kind[0] == "raise":
            raise kind[1]
        if kind[0] == "status":
            _, code, text = kind
            return DummyResponse(status_code=code, text=text, json_data={"success": False})
        if kind[0] == "resp":
            return kind[1]
        raise AssertionError("unknown outcome kind")


# ---------------------------
# Fixtures
# ---------------------------
@pytest.fixture
def cfg() -> RocketConfig:
    return RocketConfig(
        domain="https://rocket.example",
        user_id="U123",
        auth_token="T456",
        timeout=5.0,
    )


# ---------------------------
# Tests
# ---------------------------
def test_send_success_first_try(cfg: RocketConfig) -> None:
    rec: Dict[str, Any] = {}
    client = DummyHTTPClient(
        outcomes=[("resp", DummyResponse(status_code=200, json_data={"success": True}))],
        record=rec,
    )
    n = RocketNotifier(cfg, http=client, retries=0)

    msg = Message.create(subject="S", body="B", to=["#ops"])
    res = n.send(msg)

    assert res.ok is True
    assert res.provider == "rocket"
    assert rec["last_url"] == "https://rocket.example/api/v1/chat.postMessage"
    assert rec["last_headers"]["X-Auth-Token"] == "T456"
    assert rec["last_headers"]["X-User-Id"] == "U123"
    assert rec["last_json"]["channel"] == "#ops"
    assert rec["last_json"]["text"].startswith("*S*\nB")


def test_send_adds_hash_if_missing(cfg: RocketConfig) -> None:
    rec: Dict[str, Any] = {}
    client = DummyHTTPClient(outcomes=[("resp", DummyResponse())], record=rec)
    n = RocketNotifier(cfg, http=client, retries=0)

    msg = Message.create(subject="S", body="B", to=["ops"])
    res = n.send(msg)
    assert res.ok is True
    assert rec["last_json"]["channel"] == "#ops"


def test_missing_body_raises_permanent(cfg: RocketConfig) -> None:
    n = RocketNotifier(cfg, http=DummyHTTPClient(outcomes=[], record={}))
    msg = Message.create(subject="s", body="   ", to=["#ops"])
    with pytest.raises(PermanentNotifierError, match="body is required"):
        n.send(msg)


def test_missing_channel_raises_permanent(cfg: RocketConfig) -> None:
    n = RocketNotifier(cfg, http=DummyHTTPClient(outcomes=[], record={}))
    msg = Message.create(subject="s", body="b", to=[])
    with pytest.raises(PermanentNotifierError, match="channel/@user is required"):
        n.send(msg)


def test_transient_http_error_then_success(
    monkeypatch: pytest.MonkeyPatch, cfg: RocketConfig
) -> None:
    monkeypatch.setattr("time.sleep", lambda s: None)

    rec: Dict[str, Any] = {}
    outcomes = [
        ("raise", httpx.HTTPError("network down")),
        ("resp", DummyResponse(status_code=200, json_data={"success": True})),
    ]
    client = DummyHTTPClient(outcomes=outcomes, record=rec)
    n = RocketNotifier(cfg, http=client, retries=2, backoff=1.1)

    msg = Message.create(subject="S", body="B", to=["#ops"])
    res = n.send(msg)
    assert res.ok is True
    assert rec["calls"] == 2


def test_5xx_then_success(monkeypatch: pytest.MonkeyPatch, cfg: RocketConfig) -> None:
    monkeypatch.setattr("time.sleep", lambda s: None)

    rec: Dict[str, Any] = {}
    outcomes = [
        ("status", 503, "service unavailable"),
        ("resp", DummyResponse(status_code=200, json_data={"success": True})),
    ]
    client = DummyHTTPClient(outcomes=outcomes, record=rec)
    n = RocketNotifier(cfg, http=client, retries=2, backoff=1.1)

    msg = Message.create(subject="S", body="B", to=["#ops"])
    res = n.send(msg)
    assert res.ok is True
    assert rec["calls"] == 2


def test_permanent_4xx_raises(cfg: RocketConfig) -> None:
    rec: Dict[str, Any] = {}
    outcomes = [("status", 400, "bad request")]
    client = DummyHTTPClient(outcomes=outcomes, record=rec)
    n = RocketNotifier(cfg, http=client, retries=1, backoff=1.1)

    msg = Message.create(subject="S", body="B", to=["#ops"])
    with pytest.raises(PermanentNotifierError, match="permanent http 400"):
        n.send(msg)
    assert rec["calls"] == 1


def test_invalid_json_transient(cfg: RocketConfig) -> None:
    rec: Dict[str, Any] = {}
    outcomes = [("resp", DummyResponse(status_code=200, json_raises=True))]
    client = DummyHTTPClient(outcomes=outcomes, record=rec)
    n = RocketNotifier(cfg, http=client, retries=0)

    msg = Message.create(subject="S", body="B", to=["#ops"])
    with pytest.raises(TransientNotifierError, match="invalid json"):
        n.send(msg)


def test_success_false_is_permanent(cfg: RocketConfig) -> None:
    rec: Dict[str, Any] = {}
    outcomes = [
        (
            "resp",
            DummyResponse(status_code=200, json_data={"success": False, "error": "room not found"}),
        ),
    ]
    client = DummyHTTPClient(outcomes=outcomes, record=rec)
    n = RocketNotifier(cfg, http=client, retries=0)

    msg = Message.create(subject="S", body="B", to=["#ops"])
    with pytest.raises(PermanentNotifierError, match="rocket api error"):
        n.send(msg)


def test_multiple_targets_uses_first_and_warns(
    cfg: RocketConfig, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.WARNING)
    rec: Dict[str, Any] = {}
    client = DummyHTTPClient(outcomes=[("resp", DummyResponse())], record=rec)
    n = RocketNotifier(cfg, http=client, retries=0)

    msg = Message.create(subject="S", body="B", to=["#ops", "#other"])
    res = n.send(msg)
    assert res.ok is True
    assert rec["last_json"]["channel"] == "#ops"
    assert any("uses a single target" in r.message for r in caplog.records)
