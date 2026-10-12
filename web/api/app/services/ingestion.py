"""CSV ingestion through the deterministic core adapters."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from claude_ads_core.adapters import GenericCSVExportAdapter
from claude_ads_core.adapters.native_export import NativeCSVExportAdapter
from claude_ads_core.models import AccountSnapshot

SOURCE_KINDS = ("csv", "native_csv", "api")
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def safe_filename(name: str) -> str:
    cleaned = _SAFE_NAME.sub("-", Path(name).name).strip("-.") or "upload.csv"
    return cleaned[:120]


def store_upload(run_dir: Path, filename: str, data: bytes, *, max_bytes: int) -> tuple[Path, str]:
    if len(data) > max_bytes:
        raise ValueError("upload exceeds the configured size limit")
    if not data.strip():
        raise ValueError("upload is empty")
    inputs = run_dir / "inputs"
    inputs.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = inputs / safe_filename(filename)
    target.write_bytes(data)
    return target, hashlib.sha256(data).hexdigest()


def read_csv_snapshot(platform: str, path: Path, *, source_kind: str, currency: str) -> AccountSnapshot:
    if source_kind == "csv":
        return GenericCSVExportAdapter(platform).read_snapshot(path)
    if source_kind == "native_csv":
        return NativeCSVExportAdapter(platform, {"currency": currency}).read_snapshot(path)
    raise ValueError(f"unsupported CSV source kind {source_kind}")


def adapter_mode(source_kind: str) -> str:
    return "live_read" if source_kind == "api" else "export"


def snapshot_summary(snapshot: AccountSnapshot) -> dict[str, Any]:
    return {
        "account_id": snapshot["account"]["account_id"],
        "window": snapshot["window"],
        "currency": snapshot["currency"],
        "spend": snapshot.get("spend"),
        "campaign_rows": len(snapshot["campaigns"]),
        "creative_rows": len(snapshot["creatives"]),
        "conversion_rows": len(snapshot["conversions"]),
        "budget_rows": len(snapshot["budgets"]),
    }
