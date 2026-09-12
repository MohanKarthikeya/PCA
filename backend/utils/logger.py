"""
Structured logging setup.
Outputs JSON-formatted logs. API keys are never logged.
"""

import logging
import sys
import time
from typing import Any

from config.settings import get_settings

settings = get_settings()


class _JsonFormatter(logging.Formatter):
    """Simple JSON-line formatter without third-party deps."""

    SENSITIVE_KEYS = {"api_key", "google_api_key", "openai_api_key",
                      "anthropic_api_key", "deepseek_api_key", "authorization"}

    def format(self, record: logging.LogRecord) -> str:
        import json

        payload: dict[str, Any] = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Attach any extra fields, scrubbing sensitive keys
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in {
                "name", "msg", "args", "levelname", "levelno",
                "pathname", "filename", "module", "exc_info",
                "exc_text", "stack_info", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread",
                "threadName", "processName", "process", "message",
                "taskName",
            }:
                continue
            if key.lower() in self.SENSITIVE_KEYS:
                payload[key] = "***REDACTED***"
            else:
                payload[key] = value

        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        return json.dumps(payload)


def setup_logging() -> None:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Quieten noisy libs
    for noisy in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class AILatencyLogger:
    """Context manager that logs AI provider call latency."""

    def __init__(self, provider: str, operation: str) -> None:
        self._provider = provider
        self._operation = operation
        self._start: float = 0.0
        self._log = get_logger("pca.ai")

    def __enter__(self) -> "AILatencyLogger":
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        elapsed_ms = round((time.perf_counter() - self._start) * 1000, 2)
        if exc_type:
            self._log.error(
                "AI call failed",
                extra={"provider": self._provider, "operation": self._operation,
                       "latency_ms": elapsed_ms, "error": str(exc_val)},
            )
        else:
            self._log.info(
                "AI call completed",
                extra={"provider": self._provider, "operation": self._operation,
                       "latency_ms": elapsed_ms},
            )
