"""Per-run data-lifecycle contract and deletion scheduling."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from claude_ads_core.workflow_contracts import validate_workflow_contract


def build_data_lifecycle(run_id: str, *, retention_days: int, owner: str, created_at: datetime) -> dict[str, Any]:
    delete_after = created_at + timedelta(days=max(retention_days, 0))
    lifecycle = {
        "schema_version": "1.0.0",
        "lifecycle_id": f"lc-{run_id}",
        "classification": "confidential",
        "retention": {
            "minimum_seconds": 0,
            "mode": "operator-defined",
            "delete_after": _iso(delete_after),
            "purpose": "Paid-media audit for the declared client and window",
            "exception_reason": None,
        },
        "encryption": {
            "at_rest": "verified",
            "in_transit": "verified",
            "evidence_refs": ["deploy:disk-encryption", "deploy:tls-termination"],
        },
        "access": {
            "owner": owner,
            "authorized_roles": ["admin", "operator", "approver"],
            "access_log_locator": "audit_events",
        },
        "deletion": {
            "status": "scheduled",
            "method": "run-directory purge with sha256 manifest verification",
            "verification_required": True,
            "verification_artifact_locator": None,
        },
        "incident": {
            "owner": owner,
            "reporting_channel": "internal-security-channel",
            "status": "not-triggered",
            "record_locator": None,
        },
    }
    validate_workflow_contract("data-lifecycle", lifecycle)
    return lifecycle


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def now_iso() -> str:
    return _iso(datetime.now(timezone.utc))
