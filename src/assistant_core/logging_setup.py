from __future__ import annotations

import json
import logging
import sys
from typing import TextIO

ALLOWED_EXTRA_KEYS = ("intent", "latency_ms", "session", "degraded")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data: dict[str, object] = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in ALLOWED_EXTRA_KEYS:
            if hasattr(record, key):
                data[key] = getattr(record, key)
        return json.dumps(data, ensure_ascii=False)


def setup_logging(
    level: str = "INFO",
    stream: TextIO | None = None,
    logger_name: str = "assistant_core",
) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    resolved_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(resolved_level)

    target_stream = sys.stderr if stream is None else stream
    handler = logging.StreamHandler(target_stream)
    handler.setFormatter(JsonFormatter())

    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger
