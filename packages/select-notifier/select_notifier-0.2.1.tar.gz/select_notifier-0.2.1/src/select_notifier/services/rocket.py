from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Iterable, Optional

import httpx

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
logger = logging.getLogger("select_notifier.rocket")


# =================================
# REST API (chat.postMessage)
# =================================
@dataclass(frozen=True)
class RocketConfig:
    """
    Config for Rocket.Chat REST API (chat.postMessage).
    """

    domain: str
    user_id: str
    auth_token: str
    timeout: Optional[float] = None


class RocketNotifier(Notifier):
    """
    Send messages using Rocket.Chat REST API (chat.postMessage).
    """

    provider_name = "rocket"

    def __init__(
        self,
        config: RocketConfig,
        *,
        retries: Optional[int] = None,
        backoff: Optional[float] = None,
        http: Optional[httpx.Client] = None,
    ) -> None:
        """Initialize the rocket notifier.
        - retries: if None => treated as 0
        - backoff: required only when retries > 0 and must be > 0
        """
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
        self._http = http

        if self._cfg.timeout is not None and self._cfg.timeout <= 0:
            raise PermanentNotifierError("timeout must be > 0 when provided")

    # -------- Public: Notifier API --------
    def send(self, message: Message) -> SendResult:
        """Send a rocket message."""
        if not message.body.strip():
            raise PermanentNotifierError("body is required")

        channel = self._pick_target(message.to)
        if not channel:
            raise PermanentNotifierError("channel/@user is required for RocketNotifier (API mode)")

        payload = self._build_payload(subject=message.subject, body=message.body, channel=channel)

        attempt = 0
        last_err: Optional[Exception] = None

        while attempt <= self._retries:
            attempt += 1
            try:
                logger.info(
                    "Rocket(API) send (attempt %d/%d) to %s",
                    attempt,
                    self._retries + 1,
                    channel,
                )

                if self._http is None:
                    if self._cfg.timeout is not None:
                        with httpx.Client(timeout=self._cfg.timeout) as client:
                            self._post_api(client, payload)
                    else:
                        with httpx.Client() as client:
                            self._post_api(client, payload)
                else:
                    self._post_api(self._http, payload)

                logger.info("Rocket(API) message sent successfully to %s", channel)
                return SendResult.success(provider=self.provider_name)

            except TransientNotifierError as e:
                last_err = e
                if attempt > self._retries:
                    raise
                if self._backoff > 0:
                    time.sleep(self._backoff**attempt)

            except PermanentNotifierError:
                raise

        raise TransientNotifierError(
            f"Failed to send rocket (api) message to {channel} after {attempt} attempts."
        ) from last_err

    # -------- Convenience wrapper --------
    def send_text(
        self,
        *,
        subject: Optional[str] = None,
        body: str,
        to: Iterable[str] | None = None,
    ) -> SendResult:
        """Send a text rocket message (subject is optional)."""
        msg = normalize_message(subject=subject, body=body, to=to)
        return self.send(msg)

    # -------- Internals (API) --------
    def _post_api(self, client: httpx.Client, payload: dict) -> None:
        """Post a rocket message to the API."""
        url = f"{self._cfg.domain.rstrip('/')}/api/v1/chat.postMessage"
        headers = {
            "X-Auth-Token": self._cfg.auth_token,
            "X-User-Id": self._cfg.user_id,
        }
        try:
            resp = client.post(url, headers=headers, json=payload)
        except httpx.HTTPError as e:
            raise TransientNotifierError(str(e)) from e

        if resp.status_code == 200:
            try:
                data = resp.json()
            except ValueError as e:
                raise TransientNotifierError(f"invalid json from rocket api: {e}") from e
            if data.get("success"):
                return
            raise PermanentNotifierError(f"rocket api error: {str(data)[:200]}")

        if resp.status_code in (408, 429) or 500 <= resp.status_code < 600:
            raise TransientNotifierError(
                f"rocket api transient http {resp.status_code}: {resp.text[:200]}"
            )

        raise PermanentNotifierError(
            f"rocket api permanent http {resp.status_code}: {resp.text[:200]}"
        )

    @staticmethod
    def _pick_target(to: tuple[str, ...]) -> Optional[str]:
        """Pick a rocket target."""
        if not to:
            return None
        if len(to) > 1:
            logger.warning("Rocket API uses a single target; using the first one: %r", to[0])
        target = to[0].strip()
        if not target:
            return None
        if not (target.startswith("#") or target.startswith("@")):
            target = f"#{target}"
        return target

    @staticmethod
    def _build_payload(*, subject: Optional[str], body: str, channel: str) -> dict:
        """Build a rocket payload (subject optional)."""
        subj = (subject or "").strip()
        text = f"*{subj}*\n{body}" if subj else body
        return {"channel": channel, "text": text}

    # -------- Factory (API) --------
    @classmethod
    def create(
        cls,
        *,
        domain: str,
        user_id: str,
        auth_token: str,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        backoff: Optional[float] = None,
    ) -> "RocketNotifier":
        """Create a rocket notifier.
        - timeout: None => use httpx defaults
        - retries: None => treated as 0
        - backoff: required only when retries > 0
        """
        return cls(
            RocketConfig(domain=domain, user_id=user_id, auth_token=auth_token, timeout=timeout),
            retries=retries,
            backoff=backoff,
        )
