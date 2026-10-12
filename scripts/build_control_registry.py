#!/usr/bin/env python3
"""Rebuild the checked-in typed registry from the canonical catalog/references."""

from __future__ import annotations

import json
import re
from pathlib import Path
import sys
from typing import Any

# Source checkouts and installed skills both keep core beside scripts/.
_CORE_PARENT = str(Path(__file__).resolve().parents[1])
if _CORE_PARENT not in sys.path:
    sys.path.insert(0, _CORE_PARENT)
from claude_ads_core.cli_support import LocaleArgumentParser, cli_locale
from claude_ads_core.i18n import locale_scope, t


ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$")

# Narrow mappings only: each listed catalog intent is directly within the
# corresponding verified claim's scope.  The mappings ground discovery; they do
# not assign severity or make a control scoreable.
CLAIM_SUPPORT: dict[tuple[str, str], tuple[tuple[str, ...], tuple[str, ...]]] = {
    ("google", "G42"): (("CLM-0007",), ("google-ads-conversion-goals-official",)),
    ("google", "G43"): (("CLM-0007",), ("google-ads-enhanced-conversions-official",)),
    ("google", "G96"): (("CLM-0211",), ("google-ads-dsa-ad-rank-official", "google-ads-keyword-prioritization-official")),
    ("google", "G97"): (("CLM-0210",), ("google-ads-keyword-prioritization-official",)),
    ("meta", "M01"): (("CLM-0008",), ("meta-conversions-api-official",)),
    ("meta", "M02"): (("CLM-0008",), ("meta-conversions-api-official",)),
    ("meta", "M03"): (("CLM-0008",), ("meta-conversions-api-official",)),
    ("linkedin", "L01"): (("CLM-0009",), ("linkedin-conversion-tracking-official",)),
    ("linkedin", "L02"): (("CLM-0009",), ("linkedin-conversions-api-official",)),
    ("tiktok", "T01"): (("CLM-0010",), ("tiktok-pixel-official",)),
    ("microsoft", "MS01"): (("CLM-0011",), ("microsoft-uet-official",)),
    ("microsoft", "MS03"): (("CLM-0011",), ("microsoft-google-import-official",)),
    ("reddit", "RD-M02"): (("CLM-0015",), ("reddit-business-help",)),
    ("reddit", "RD-M03"): (("CLM-0015",), ("reddit-business-help",)),
    ("pinterest", "PN-M01"): (("CLM-0016",), ("pinterest-conversions-api",)),
    ("pinterest", "PN-M02"): (("CLM-0016",), ("pinterest-conversions-api",)),
}

# Approved health decisions (owner-approved 2026-09-30): only controls listed
# here are scoreable, and only for platforms with an enabled profile.
APPROVED_HEALTH: dict[str, dict[str, Any]] = {
    "meta": {
        "category_weights": {"measurement": 100},
        "controls": {"M01": ("measurement", "high"), "M02": ("measurement", "high"), "M03": ("measurement", "high")},
    },
}


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(t('maintenance.build_control_registry.pyyaml_is_required_to_rebuild_the_control_registry')) from exc
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SystemExit(t("maintenance.build_control_registry.failed", error=exc)) from exc
    if not isinstance(payload, dict):
        raise SystemExit(t('maintenance.build_control_registry.must_contain_an_object', v0=path))
    return payload


def _reference_rows(path: Path) -> tuple[bool, dict[str, tuple[str, str]]]:
    text = path.read_text(encoding="utf-8")
    categorized = "| ID | Category |" in text
    rows: dict[str, tuple[str, str]] = {}
    for line in text.splitlines():
        match = ROW.match(line)
        if not match:
            continue
        first, second, third = (part.strip() for part in match.groups())
        if first == "ID" or set(first) == {"-"}:
            continue
        rows[first] = (second, third)
    return categorized, rows


def build(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    catalog = _load_yaml(root / "tests" / "fixtures" / "check-catalog.yaml")
    claim_payload = json.loads(
        (root / "control-plane" / "manifests" / "claim-ledger.json").read_text(encoding="utf-8")
    )
    claims = {claim["id"]: claim for claim in claim_payload["claims"]}
    controls: list[dict[str, Any]] = []
    for platform, platform_data in catalog["platforms"].items():
        reference = root / platform_data["reference"]
        if (root / "claude_ads_core/locales/manifest.json").is_file():
            reference = root / "claude_ads_core/locales/en/documents" / platform_data["reference"]
        categorized, rows = _reference_rows(reference)
        for control_id in platform_data["check_ids"]:
            if control_id not in rows:
                raise SystemExit(t('maintenance.build_control_registry.missing_reference_row', v0=platform, v1=control_id))
            second, third = rows[control_id]
            if categorized:
                category = second.lower().replace(" ", "-")
                intent = third
                disposition = "conditional_watchlist"
            else:
                category = "unclassified"
                intent = second
                disposition = (
                    "source_refresh_discovery"
                    if third.startswith("Unscored source-refresh discovery")
                    else "conditional_watchlist"
                )
            claim_ids, source_ids = CLAIM_SUPPORT.get((platform, control_id), ((), ()))
            for claim_id in claim_ids:
                unsupported = set(source_ids) - set(claims[claim_id]["source_ids"])
                if unsupported:
                    raise SystemExit(
                        t('maintenance.build_control_registry.maps_sources_outside', v0=platform, v1=control_id, v2=claim_id, v3=sorted(unsupported))
                    )
            approved = APPROVED_HEALTH.get(platform, {}).get("controls", {}).get(control_id)
            if approved:
                if not claim_ids:
                    raise SystemExit(t('maintenance.build_control_registry.missing_reference_row', v0=platform, v1=control_id))
                disposition, category = "health", approved[0]
            controls.append(
                {
                    "platform": platform,
                    "control_id": control_id,
                    "intent": intent,
                    "disposition": disposition,
                    "source_claim_ids": list(claim_ids),
                    "control_definition": {
                        "schema_version": "1.0.0",
                        "control_id": control_id,
                        "category": category,
                        "severity": approved[1] if approved else "informational",
                        "required_inputs": [
                            "applicability_context",
                            "current_account_evidence",
                            "current_source_support",
                        ],
                        "source_ids": list(source_ids),
                        "maturity": "source-grounded" if claim_ids else "inventory-baselined",
                        "geographies": ["account-configured"],
                        "scoring_behavior": "health" if approved else "watchlist",
                        "stability": "stable" if approved else "experimental",
                    },
                }
            )
    # This is canonical registry evidence, not CLI prose. Preserve it exactly
    # across locales so rebuilding does not rewrite the reviewed manifests.
    reason = (
        "No approved source-grounded control-severity decision set exists; "
        "enabling health would invent severity or category weights."
    )
    profiles = [
        (
            {
                "profile_id": f"{platform}-health-v1",
                "platform": platform,
                "status": "enabled",
                "category_weights": dict(APPROVED_HEALTH[platform]["category_weights"]),
                "health_control_ids": list(APPROVED_HEALTH[platform]["controls"]),
            }
            if platform in APPROVED_HEALTH
            else {
                "profile_id": f"{platform}-health-v1",
                "platform": platform,
                "status": "disabled",
                "category_weights": {},
                "health_control_ids": [],
                "disabled_reason": reason,
            }
        )
        for platform in sorted(catalog["platforms"])
    ]
    return (
        {
            "schema_version": "1.0.0",
            "registry_version": "1.0.0",
            "catalog_version": str(catalog["version"]),
            "controls": controls,
        },
        {
            "schema_version": "1.0.0",
            "profile_version": "1.0.0",
            "profiles": profiles,
        },
    )


def main(argv: list[str] | None = None) -> int:
    with locale_scope(cli_locale(argv)):
        return _main(argv)


def _main(argv: list[str] | None = None) -> int:
    parser = LocaleArgumentParser(description=t("maintenance.build_control_registry.description"))
    parser.parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    try:
        registry, profiles = build(root)
        manifest_root = root / "control-plane" / "manifests"
        (manifest_root / "control-registry.json").write_text(
            json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (manifest_root / "scoring-profiles.json").write_text(
            json.dumps(profiles, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError, KeyError) as exc:
        print(t("maintenance.build_control_registry.failed", error=exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
