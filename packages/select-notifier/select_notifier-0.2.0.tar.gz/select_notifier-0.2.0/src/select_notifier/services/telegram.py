from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Optional, Iterable

from telegram import Bot
from telegram.error import RetryAfter, TimedOut, NetworkError, BadRequest, TelegramError
from telegram.request import HTTPXRequest

from select_notifier.base import (
    Message,
    SendResult,
    Notifier,
    AsyncNotifier,
    normalize_message,
    TransientNotifierError,
    PermanentNotifierError,
)


# =============================
# Logging (no forced handlers; user controls logging config)
# =============================
logger = logging.getLogger("select_notifier.telegram")

# =============================
# Config
# =============================
@dataclass(frozen=True)
class TelegramConfig:
    """
    Minimal config for a PTB Bot client (sender-only).
    - bot_token: (Required) BotFather token
    - api_base:  (Required) Base URL of Bot API, e.g. "https://api.telegram.org" or your self-hosted server
                 NOTE: will be normalized to end with '/bot'
    - timeout:   (Optional) I/O timeout seconds for HTTPXRequest (connect/read)
    - proxy_url: (Optional) HTTP/SOCKS proxy URL ('http://', 'socks5://', ...)
    """
    bot_token: str
    api_base: str
    timeout: Optional[float] = None
    proxy_url: Optional[str] = None


# =============================
# Telegram Notifiers
# =============================
class TelegramNotifier(Notifier):
    """
    Synchronous wrapper over PTB's async Bot for send-only use cases.
    - Maps transient errors (RetryAfter/TimedOut/NetworkError/5xx-like) to TransientNotifierError with retry loop.
    - Maps permanent errors (BadRequest/auth issues) to PermanentNotifierError.
    - If an event loop is already running in this thread, raises PermanentNotifierError
      (use TelegramAsyncNotifier in async contexts).
    """
    provider_name = "telegram"
    def __init__(
        self,
        config: TelegramConfig,
        *,
        retries: Optional[int] = None,
        backoff: Optional[float] = None,
    ) -> None:
        if not config.bot_token or not config.bot_token.strip():
            raise PermanentNotifierError("bot_token is required")
        if not config.api_base or not config.api_base.strip():
            raise PermanentNotifierError("api_base is required")

        base = config.api_base.rstrip("/")
        if not base.endswith("/bot"):
            base = f"{base}/bot"

        if config.timeout is not None and config.timeout <= 0:
            raise PermanentNotifierError("timeout must be > 0 when provided")

        req_kwargs: dict = {}
        if config.timeout is not None:
            req_kwargs.update({"read_timeout": config.timeout, "connect_timeout": config.timeout})
        if config.proxy_url:
            req_kwargs["proxy_url"] = config.proxy_url

        request = HTTPXRequest(**req_kwargs)
        self._bot = Bot(token=config.bot_token, base_url=base, request=request)

        self._retries = int(retries) if retries is not None else 0
        if self._retries < 0:
            raise PermanentNotifierError("retries must be >= 0")
        if self._retries > 0:
            if backoff is None or backoff <= 0:
                raise PermanentNotifierError("backoff must be > 0 when retries > 0")
            self._backoff = float(backoff)
        else:
            self._backoff = 0.0

    # ------------- Public (Notifier API) -------------
    def send(self, message: Message) -> SendResult:
        if not message.body.strip():
            raise PermanentNotifierError("body is required")

        chat = self._pick_target(message.to)
        if not chat:
            raise PermanentNotifierError("'to' (chat_id or @channel) is required")

        text = self._compose_text(message)
        kwargs: dict = {"chat_id": chat, "text": text}

        if "parse_mode" in message.meta:
            kwargs["parse_mode"] = str(message.meta["parse_mode"])
        if "disable_web_page_preview" in message.meta:
            kwargs["disable_web_page_preview"] = bool(message.meta["disable_web_page_preview"])
        if "disable_notification" in message.meta:
            kwargs["disable_notification"] = bool(message.meta["disable_notification"])

        attempt = 0
        last_err: Optional[Exception] = None

        while attempt <= self._retries:
            attempt += 1
            try:
                logger.debug("Telegram send attempt %d/%d to %s", attempt, self._retries + 1, chat)
                coro = self._bot.send_message(**kwargs)
                result = self._run_coro(coro)
                logger.info("Telegram message sent to %s", chat)
                return SendResult.success(provider=self.provider_name, raw={"result": str(result)})

            except RetryAfter as e:
                last_err = e
                sleep_s = float(getattr(e, "retry_after", 1))
                logger.warning("Telegram RetryAfter: sleeping %s sec", sleep_s)
                time.sleep(max(0.0, sleep_s))

            except (TimedOut, NetworkError) as e:
                last_err = e
                if attempt > self._retries:
                    raise TransientNotifierError(str(e)) from e
                if self._backoff > 0:
                    time.sleep(self._backoff ** attempt)

            except BadRequest as e:
                raise PermanentNotifierError(str(e)) from e

            except TelegramError as e:
                last_err = e
                if attempt > self._retries:
                    raise TransientNotifierError(str(e)) from e
                if self._backoff > 0:
                    time.sleep(self._backoff ** attempt)

        raise TransientNotifierError(
            f"Failed to send telegram message to {chat} after {attempt} attempts."
        ) from last_err

    # ------------- Internals -------------
    @staticmethod
    def _pick_target(to: tuple[str, ...]) -> Optional[str]:
        if not to:
            return None
        target = (to[0] or "").strip()
        return target or None

    @staticmethod
    def _compose_text(message: Message) -> str:
        subj = (message.subject or "").strip()
        return f"{subj}\n{message.body}" if subj else message.body

    @staticmethod
    def _loop_running() -> bool:
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    def _run_coro(self, coro):
        if self._loop_running():
            raise PermanentNotifierError(
                "An asyncio event loop is running in this thread. "
                "Use TelegramAsyncNotifier in async contexts."
            )
        return asyncio.run(coro)

    # ------------- Factory -------------
    @classmethod
    def create(
        cls,
        *,
        bot_token: str,
        api_base: str,
        timeout: Optional[float] = None,
        proxy_url: Optional[str] = None,
        retries: Optional[int] = None,
        backoff: Optional[float] = None,
    ) -> "TelegramNotifier":
        cfg = TelegramConfig(
            bot_token=bot_token,
            api_base=api_base,
            timeout=timeout,
            proxy_url=proxy_url,
        )
        return cls(cfg, retries=retries, backoff=backoff)


class TelegramAsyncNotifier(AsyncNotifier):
    """
    Async variant that fits async apps (FastAPI/Quart/…).
    Uses HTTPXRequest as PTB network layer.
    """
    provider_name = "telegram"

    def __init__(self, config: TelegramConfig) -> None:
        if not config.bot_token or not config.bot_token.strip():
            raise PermanentNotifierError("bot_token is required")
        if not config.api_base or not config.api_base.strip():
            raise PermanentNotifierError("api_base is required")

        base = config.api_base.rstrip("/")
        if not base.endswith("/bot"):
            base = f"{base}/bot"

        if config.timeout is not None and config.timeout <= 0:
            raise PermanentNotifierError("timeout must be > 0 when provided")

        req_kwargs: dict = {}
        if config.timeout is not None:
            req_kwargs.update({"read_timeout": config.timeout, "connect_timeout": config.timeout})
        if config.proxy_url:
            req_kwargs["proxy_url"] = config.proxy_url

        request = HTTPXRequest(**req_kwargs)
        self._bot = Bot(token=config.bot_token, base_url=base, request=request)

    async def send_async(self, message: Message) -> SendResult:
        if not message.body.strip():
            raise PermanentNotifierError("body is required")
        chat = TelegramNotifier._pick_target(message.to)
        if not chat:
            raise PermanentNotifierError("'to' (chat_id or @channel) is required")

        text = TelegramNotifier._compose_text(message)
        kwargs: dict = {"chat_id": chat, "text": text}
        if "parse_mode" in message.meta:
            kwargs["parse_mode"] = str(message.meta["parse_mode"])
        if "disable_web_page_preview" in message.meta:
            kwargs["disable_web_page_preview"] = bool(message.meta["disable_web_page_preview"])
        if "disable_notification" in message.meta:
            kwargs["disable_notification"] = bool(message.meta["disable_notification"])

        try:
            result = await self._bot.send_message(**kwargs)
            logger.info("Telegram message sent to %s", chat)
            return SendResult.success(provider=self.provider_name, raw={"result": str(result)})
        except RetryAfter as e:
            raise TransientNotifierError(str(e)) from e
        except (TimedOut, NetworkError) as e:
            raise TransientNotifierError(str(e)) from e
        except BadRequest as e:
            raise PermanentNotifierError(str(e)) from e
        except TelegramError as e:
            raise TransientNotifierError(str(e)) from e

    @classmethod
    def create(
        cls,
        *,
        bot_token: str,
        api_base: str,
        timeout: Optional[float] = None,
        proxy_url: Optional[str] = None,
    ) -> "TelegramAsyncNotifier":
        return cls(
            TelegramConfig(
                bot_token=bot_token,
                api_base=api_base,
                timeout=timeout,
                proxy_url=proxy_url,
            )
        )
