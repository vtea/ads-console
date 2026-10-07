"""Redaction helpers so tokens never reach logs, errors, or artifacts."""

from __future__ import annotations

import re
from typing import Any

_SENSITIVE = re.compile(
    r"\b(api[_-]?key|access[_-]?token|refresh[_-]?token|authorization|auth|token|secret|password|code|signature)"
    r"\s*[=:]\s*[\"']?(?:Bearer\s+)?[^\s&,;\"']+|\bBearer\s+[^\s,;]+",
    re.IGNORECASE,
)
_TOKEN_SHAPES = re.compile(r"\b(?:EAA[A-Za-z0-9]{20,}|sk-ant-[A-Za-z0-9_-]{10,}|sk-[A-Za-z0-9_-]{16,})\b")
_SENSITIVE_KEYS = re.compile(r"(?i)(access[_-]?token|refresh[_-]?token|api[_-]?key|secret|password|authorization)")


def redact_text(value: Any) -> str:
    text = str(value)
    text = _SENSITIVE.sub(lambda m: m.group(0).split("=")[0].split(":")[0] + "=[REDACTED]" if ("=" in m.group(0) or ":" in m.group(0)) else "Bearer [REDACTED]", text)
    return _TOKEN_SHAPES.sub("[REDACTED]", text)


def redact_mapping(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: ("[REDACTED]" if _SENSITIVE_KEYS.search(str(k)) else redact_mapping(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_mapping(item) for item in value]
    if isinstance(value, str):
        return redact_text(value)
    return value


def sanitize_error(exc: BaseException) -> str:
    return redact_text(f"{type(exc).__name__}: {exc}")
