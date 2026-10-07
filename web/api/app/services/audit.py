from __future__ import annotations

from sqlalchemy.orm import Session

from ..db.models import AuditEvent
from ..security.redact import redact_text


def record(db: Session, *, actor_id: int | None, action: str, target_type: str = "", target_id: str = "", detail: str = "") -> AuditEvent:
    event = AuditEvent(actor_id=actor_id, action=action, target_type=target_type, target_id=str(target_id), detail=redact_text(detail)[:4000])
    db.add(event)
    db.flush()
    return event
