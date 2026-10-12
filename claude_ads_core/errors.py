"""Message-ID exceptions that preserve existing public exception hierarchies."""

from __future__ import annotations

import re
from typing import Any

from .i18n import t


_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----", re.DOTALL)
_TOKEN = re.compile(r"\b(?:sk[_-](?:live[_-])?|gh[pousr]_|AIza)[A-Za-z0-9._-]{8,}\b", re.IGNORECASE)
_CREDENTIAL = re.compile(
    r"\b(api[_-]?key|access[_-]?token|refresh[_-]?token|authorization|auth|key|token|secret|password|code|signature)"
    r"\s*[=:]\s*[\"']?(?:Bearer\s+)?[^\s&,;\"']+|\bBearer\s+[^\s,;]+",
    re.IGNORECASE,
)
_OPTION_CREDENTIAL = re.compile(
    r"(--(?:api[-_]?key|access[-_]?token|refresh[-_]?token|token|secret|password|authorization))\s+\S+",
    re.IGNORECASE,
)
_URL_USERINFO = re.compile(r"(\b[a-z][a-z0-9+.-]*://)[^\s/<>]*@", re.IGNORECASE)


def safe_error_text(value: object) -> str:
    """Use existing report redaction plus CLI credential/URL safeguards."""
    # Lazy import keeps contracts usable while reporting imports their types.
    from .reporting import _redact_text

    text = _PRIVATE_KEY.sub("[REDACTED PRIVATE KEY]", str(value))
    text = _URL_USERINFO.sub(r"\1", text)
    text = _OPTION_CREDENTIAL.sub(r"\1 [REDACTED]", text)
    text = _CREDENTIAL.sub(
        lambda match: f"{match.group(1)}=[REDACTED]" if match.group(1) else "Bearer [REDACTED]",
        text,
    )
    return _redact_text(_TOKEN.sub("[REDACTED]", text))



class LocalizedError:
    """Mixin for first-party exceptions with stable IDs and interpolation data.

    Passing another localized error retains its ID and parameters. Plain text
    remains supported for third-party adapters; it is opaque data, not a lookup
    key. Localization happens at display time so a caller may choose its scope.
    """

    def __init__(self, message: object, **params: Any) -> None:
        if isinstance(message, LocalizedError):
            self.message_id = message.message_id
            self.params = dict(message.params)
            self.original_message = message.original_message
        else:
            text = str(message)
            self.message_id = text if text.startswith("core.") else None
            self.params = dict(params)
            self.original_message = text
        super().__init__(str(self))

    def __str__(self) -> str:
        if self.message_id is not None:
            return t(self.message_id, **self.params)
        return self.original_message
