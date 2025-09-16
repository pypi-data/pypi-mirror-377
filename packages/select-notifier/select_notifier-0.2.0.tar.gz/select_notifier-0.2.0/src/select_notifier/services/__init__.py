from __future__ import annotations

__all__ = [
    "EmailNotifier",
    "SMTPConfig",
    "RocketNotifier",
    "RocketConfig",
    "TelegramNotifier",
    "TelegramConfig",
    "TelegramAsyncNotifier",
]


def __getattr__(name: str):
    if name in ("EmailNotifier", "SMTPConfig"):
        from .email import EmailNotifier, SMTPConfig

        return {"EmailNotifier": EmailNotifier, "SMTPConfig": SMTPConfig}[name]
    if name in ("RocketNotifier", "RocketConfig"):
        from .rocket import RocketConfig, RocketNotifier

        return {"RocketNotifier": RocketNotifier, "RocketConfig": RocketConfig}[name]
    if name in ("TelegramNotifier", "TelegramConfig", "TelegramAsyncNotifier"):
        from .telegram import TelegramAsyncNotifier, TelegramConfig, TelegramNotifier

        return {
            "TelegramNotifier": TelegramNotifier,
            "TelegramConfig": TelegramConfig,
            "TelegramAsyncNotifier": TelegramAsyncNotifier,
        }[name]

    raise AttributeError(name)
