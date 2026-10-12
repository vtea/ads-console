"""Deterministic repository status and next-blocker selection.

This module has no network or account access. It reports only what versioned
repository artifacts establish and uses an explicit, stable blocker order.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping

from .contracts import PLATFORMS
from .errors import LocalizedError
from .i18n import guidance_text, t
from .control_registry import RegistryError, load_control_registry

STATUS_SCHEMA_VERSION = "1.0.0"
MATURITY_IDS = (
    "inventory-baselined",
    "source-grounded",
    "domain-integrated",
    "eval-verified",
    "release-ready",
)
CAPABILITY_STATUSES = {"declared", "implemented", "fixture-verified", "live-verified", "disabled"}
RELEASE_CHECK_IDS = (
    "repository-audit",
    "clean-subject",
    "source-capability-integrity",
    "ecosystem-dispositions",
    "canonical-model-evaluation",
    "independent-reviews",
    "remote-ci",
)
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class ProductStatusError(LocalizedError, ValueError):
    """Raised when required repository status evidence is missing or malformed."""


def _read_json(path: Path, label: str) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductStatusError('core.status.read', label=label, exc=exc) from exc
    if not isinstance(value, Mapping):
        raise ProductStatusError('core.status.json_object', label=label)
    return value


def _date(value: Any, path: str) -> date:
    if not isinstance(value, str):
        raise ProductStatusError('core.validation.date', path=path)
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ProductStatusError('core.validation.date', path=path) from exc


def _nonempty(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProductStatusError('core.validation.nonempty_string', path=path)
    return value


def _strings(value: Any, path: str, *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise ProductStatusError('core.validation.array', path=path)
    result = [_nonempty(item, f"{path}[{index}]") for index, item in enumerate(value)]
    if len(result) != len(set(result)):
        raise ProductStatusError('core.validation.unique', path=path)
    return result


def _validate_maturity(document: Mapping[str, Any]) -> tuple[str, list[dict[str, Any]], list[str]]:
    required = {"schema_version", "evaluated_at", "current", "levels", "automatic_demotion", "blockers"}
    allowed = required
    if set(document) != allowed or document.get("schema_version") != "1.0.0":
        raise ProductStatusError('core.status.maturity_fields')
    _date(document.get("evaluated_at"), "maturity.evaluated_at")
    current = _nonempty(document.get("current"), "maturity.current")
    if current not in MATURITY_IDS:
        raise ProductStatusError('core.status.maturity_current')
    raw_levels = document.get("levels")
    if not isinstance(raw_levels, list) or len(raw_levels) != len(MATURITY_IDS):
        raise ProductStatusError('core.status.maturity_levels')
    levels: list[dict[str, Any]] = []
    seen_unsatisfied = False
    for index, raw in enumerate(raw_levels):
        if not isinstance(raw, Mapping):
            raise ProductStatusError('core.status.maturity_level_object', index=index)
        if set(raw) - {"id", "ordinal", "requirements", "satisfied", "evidence"}:
            raise ProductStatusError('core.status.maturity_level_fields', index=index)
        level_id = raw.get("id")
        if level_id != MATURITY_IDS[index] or raw.get("ordinal") != index + 1:
            raise ProductStatusError('core.status.maturity_order')
        requirements = _strings(raw.get("requirements"), f"maturity.levels[{index}].requirements", allow_empty=False)
        evidence = _strings(raw.get("evidence", []), f"maturity.levels[{index}].evidence")
        satisfied = raw.get("satisfied")
        if not isinstance(satisfied, bool):
            raise ProductStatusError('core.status.maturity_satisfied', index=index)
        if seen_unsatisfied and satisfied:
            raise ProductStatusError('core.status.maturity_prefix')
        seen_unsatisfied = seen_unsatisfied or not satisfied
        levels.append(
            {
                "id": level_id,
                "ordinal": index + 1,
                "satisfied": satisfied,
                "requirements": requirements,
                "evidence": evidence,
            }
        )
    satisfied_ids = [level["id"] for level in levels if level["satisfied"]]
    if not satisfied_ids or satisfied_ids[-1] != current:
        raise ProductStatusError('core.status.maturity_highest')
    _strings(document.get("automatic_demotion"), "maturity.automatic_demotion", allow_empty=False)
    blockers = _strings(document.get("blockers"), "maturity.blockers")
    return current, levels, blockers


def _validate_evidence_ledgers(
    claim_document: Mapping[str, Any],
    source_document: Mapping[str, Any],
    as_of: date,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    for label, document, collection in (
        ("claim ledger", claim_document, "claims"),
        ("source ledger", source_document, "sources"),
    ):
        if document.get("schema_version") != "1.0.0":
            raise ProductStatusError('core.status.ledger_version', label=label)
        _date(document.get("generated_at"), f"{label}.generated_at")
        if not isinstance(document.get(collection), list):
            raise ProductStatusError('core.status.ledger_array', label=label, collection=collection)
    raw_sources = source_document["sources"]
    sources: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(raw_sources):
        if not isinstance(raw, Mapping):
            raise ProductStatusError('core.status.source_object', index=index)
        source_id = _nonempty(raw.get("id"), f"source ledger.sources[{index}].id")
        if source_id in sources:
            raise ProductStatusError('core.status.source_duplicate', source_id=source_id)
        _date(raw.get("refresh_due"), f"source {source_id}.refresh_due")
        _strings(raw.get("claim_ids"), f"source {source_id}.claim_ids")
        sources[source_id] = raw
    stale: list[dict[str, Any]] = []
    unverified: list[dict[str, Any]] = []
    claims: dict[str, set[str]] = {}
    for index, raw in enumerate(claim_document["claims"]):
        if not isinstance(raw, Mapping):
            raise ProductStatusError('core.status.claim_object', index=index)
        claim_id = _nonempty(raw.get("id"), f"claim ledger.claims[{index}].id")
        if claim_id in claims:
            raise ProductStatusError('core.status.claim_duplicate', claim_id=claim_id)
        source_ids = _strings(raw.get("source_ids"), f"claim {claim_id}.source_ids", allow_empty=False)
        claims[claim_id] = set(source_ids)
        refresh_due = _date(raw.get("refresh_due"), f"claim {claim_id}.refresh_due")
        _date(raw.get("last_verified"), f"claim {claim_id}.last_verified")
        for source_id in source_ids:
            source = sources.get(source_id)
            if source is None or claim_id not in source.get("claim_ids", []):
                raise ProductStatusError('core.status.claim_source_link', claim_id=claim_id, source_id=source_id)
        load_bearing = raw.get("load_bearing")
        if not isinstance(load_bearing, bool):
            raise ProductStatusError('core.status.claim_load_bearing', claim_id=claim_id)
        if load_bearing and raw.get("verdict") != "verified":
            unverified.append(
                {
                    "claim_id": claim_id,
                    "verdict": _nonempty(raw.get("verdict"), f"claim {claim_id}.verdict"),
                    "source_ids": sorted(source_ids),
                }
            )
        if load_bearing and refresh_due < as_of:
            stale.append(
                {
                    "claim_id": claim_id,
                    "refresh_due": refresh_due.isoformat(),
                    "source_ids": sorted(source_ids),
                }
            )
    for source_id, source in sources.items():
        for claim_id in source.get("claim_ids", []):
            if claim_id not in claims or source_id not in claims[claim_id]:
                raise ProductStatusError('core.status.source_claim_link', source_id=source_id, claim_id=claim_id)
    return sorted(stale, key=lambda item: (item["refresh_due"], item["claim_id"])), sorted(
        unverified, key=lambda item: item["claim_id"]
    )


def _disabled_capabilities(document: Mapping[str, Any]) -> list[dict[str, str]]:
    if set(document) != {"schema_version", "snapshot_at", "default_mutation_mode", "platforms"}:
        raise ProductStatusError('core.status.capability_fields')
    if document.get("schema_version") != "1.0.0" or document.get("default_mutation_mode") != "read-only":
        raise ProductStatusError('core.status.capability_header')
    raw_platforms = document.get("platforms")
    if not isinstance(raw_platforms, list):
        raise ProductStatusError('core.status.capability_platforms')
    platform_ids: set[str] = set()
    disabled: list[dict[str, str]] = []
    for index, raw_platform in enumerate(raw_platforms):
        if not isinstance(raw_platform, Mapping):
            raise ProductStatusError('core.status.platform_object', index=index)
        if set(raw_platform) != {"id", "display_name", "target_tier", "skill_path", "capabilities"}:
            raise ProductStatusError('core.status.platform_fields', index=index)
        platform = _nonempty(raw_platform.get("id"), f"capability platforms[{index}].id")
        if platform not in PLATFORMS or platform in platform_ids:
            raise ProductStatusError('core.status.platform_duplicate', platform=platform)
        platform_ids.add(platform)
        capabilities = raw_platform.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities:
            raise ProductStatusError('core.status.platform_empty', platform=platform)
        capability_ids: set[str] = set()
        for cap_index, raw_capability in enumerate(capabilities):
            if not isinstance(raw_capability, Mapping):
                raise ProductStatusError('core.status.capability_object', platform=platform, cap_index=cap_index)
            required = {"id", "mode", "status", "implementation_paths", "fixture_paths", "test_paths", "source_ids"}
            allowed = required | {"disabled_reason"}
            if not required <= set(raw_capability) or set(raw_capability) - allowed:
                raise ProductStatusError('core.status.capability_item_fields', platform=platform, cap_index=cap_index)
            capability_id = _nonempty(raw_capability.get("id"), f"{platform}.capabilities[{cap_index}].id")
            status = _nonempty(raw_capability.get("status"), f"{platform}.{capability_id}.status")
            if capability_id in capability_ids or status not in CAPABILITY_STATUSES:
                raise ProductStatusError('core.status.capability_duplicate', platform=platform, capability_id=capability_id)
            capability_ids.add(capability_id)
            if status == "disabled":
                disabled.append(
                    {
                        "platform": platform,
                        "capability_id": capability_id,
                        "reason": _nonempty(
                            raw_capability.get("disabled_reason"),
                            f"{platform}.{capability_id}.disabled_reason",
                        ),
                    }
                )
    if platform_ids != PLATFORMS:
        raise ProductStatusError('core.status.capability_coverage')
    return sorted(disabled, key=lambda item: (item["platform"], item["capability_id"]))


def _release_gate(path: Path | None, root: Path) -> dict[str, Any] | None:
    if path is None:
        return None
    document = _read_json(path, "release gate report")
    expected_fields = {
        "schema_version",
        "evidence_class",
        "evaluated_at",
        "subject",
        "checks",
        "release_gate_satisfied",
    }
    if set(document) != expected_fields or document.get("schema_version") != "1.0.0":
        raise ProductStatusError('core.status.release_fields')
    if document.get("evidence_class") != "release-gate-assessment":
        raise ProductStatusError('core.status.release_evidence_class')
    try:
        evaluated = datetime.fromisoformat(str(document.get("evaluated_at")).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProductStatusError('core.status.release_evaluated_at') from exc
    if evaluated.tzinfo is None:
        raise ProductStatusError('core.status.release_offset')
    subject = document.get("subject")
    if not isinstance(subject, Mapping) or set(subject) != {"commit_sha", "tree_sha"}:
        raise ProductStatusError('core.status.release_subject')
    if not all(SHA_PATTERN.fullmatch(str(subject.get(key, ""))) for key in ("commit_sha", "tree_sha")):
        raise ProductStatusError('core.status.release_hashes')
    raw_checks = document.get("checks")
    if not isinstance(raw_checks, list) or len(raw_checks) != len(RELEASE_CHECK_IDS):
        raise ProductStatusError('core.status.release_check_count')
    checks: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(raw_checks):
        if not isinstance(raw, Mapping):
            raise ProductStatusError('core.status.release_check_object', index=index)
        check_id = _nonempty(raw.get("id"), f"release gate checks[{index}].id")
        status = raw.get("status")
        if check_id not in RELEASE_CHECK_IDS or check_id in checks or status not in {"pass", "fail"}:
            raise ProductStatusError('core.status.release_check_duplicate', check_id=check_id)
        expected_check_fields = {"id", "status", "evidence"} if status == "pass" else {"id", "status", "error"}
        if set(raw) != expected_check_fields:
            raise ProductStatusError('core.status.release_check_fields', check_id=check_id)
        if status == "pass":
            if not isinstance(raw.get("evidence"), Mapping) or "error" in raw:
                raise ProductStatusError('core.status.release_missing_evidence', check_id=check_id)
        elif not isinstance(raw.get("error"), str) or not raw["error"].strip() or "evidence" in raw:
            raise ProductStatusError('core.status.release_missing_error', check_id=check_id)
        checks[check_id] = raw
    if set(checks) != set(RELEASE_CHECK_IDS):
        raise ProductStatusError('core.status.release_coverage')
    satisfied = document.get("release_gate_satisfied")
    if not isinstance(satisfied, bool) or satisfied != all(checks[item]["status"] == "pass" for item in RELEASE_CHECK_IDS):
        raise ProductStatusError('core.status.release_satisfied')
    failed = [
        {"id": check_id, "error": str(checks[check_id]["error"])}
        for check_id in RELEASE_CHECK_IDS
        if checks[check_id]["status"] == "fail"
    ]
    try:
        evidence_path = str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        evidence_path = "external-release-gate-report"
    return {
        "evaluated_at": evaluated.isoformat(),
        "subject": dict(subject),
        "release_gate_satisfied": satisfied,
        "failed_checks": failed,
        "evidence_path": evidence_path,
    }


def _next_blocker(
    *,
    stale: list[dict[str, Any]],
    unverified: list[dict[str, Any]],
    blockers: list[str],
    release_gate: dict[str, Any] | None,
    disabled_profiles: list[dict[str, str]],
    disabled_capabilities: list[dict[str, str]],
    levels: list[dict[str, Any]],
) -> dict[str, Any]:
    """Apply artifact-order-v1 and return exactly one decision object."""

    if unverified:
        selected = unverified[0]
        return {
            "kind": "unverified-load-bearing-claim",
            "id": selected["claim_id"],
            "summary": t("core.status.unverified_summary", claim_id=selected["claim_id"]),
            "rationale": t("core.status.unverified_rationale"),
            "evidence_paths": [
                "control-plane/manifests/claim-ledger.json",
                "control-plane/manifests/source-ledger.json",
            ],
        }
    if stale:
        selected = stale[0]
        return {
            "kind": "stale-load-bearing-claim",
            "id": selected["claim_id"],
            "summary": t("core.status.stale_summary", claim_id=selected["claim_id"], refresh_due=selected["refresh_due"]),
            "rationale": t("core.status.stale_rationale"),
            "evidence_paths": [
                "control-plane/manifests/maturity-status.json",
                "control-plane/manifests/claim-ledger.json",
                "control-plane/manifests/source-ledger.json",
            ],
        }
    if blockers:
        return {
            "kind": "maturity-blocker",
            "id": "maturity-blocker-001",
            "summary": t("core.status.external_reason", reason=blockers[0]),
            "rationale": t("core.status.maturity_rationale"),
            "evidence_paths": ["control-plane/manifests/maturity-status.json"],
        }
    if release_gate and release_gate["failed_checks"]:
        selected = release_gate["failed_checks"][0]
        return {
            "kind": "release-gate-check",
            "id": selected["id"],
            "summary": t("core.status.external_reason", reason=selected["error"]),
            "rationale": t("core.status.release_rationale"),
            "evidence_paths": [release_gate["evidence_path"]],
        }
    if disabled_profiles:
        selected = disabled_profiles[0]
        return {
            "kind": "disabled-scoring-profile",
            "id": selected["profile_id"],
            "summary": t("core.status.external_reason", reason=selected["reason"]),
            "rationale": t("core.status.profile_rationale"),
            "evidence_paths": [
                "control-plane/manifests/scoring-profiles.json",
                "control-plane/manifests/control-registry.json",
            ],
        }
    if disabled_capabilities:
        selected = disabled_capabilities[0]
        return {
            "kind": "disabled-capability",
            "id": f"{selected['platform']}/{selected['capability_id']}",
            "summary": t("core.status.external_reason", reason=selected["reason"]),
            "rationale": t("core.status.capability_rationale"),
            "evidence_paths": ["control-plane/manifests/capability-manifest.json"],
        }
    unsatisfied = [level for level in levels if not level["satisfied"]]
    if unsatisfied:
        selected = unsatisfied[0]
        return {
            "kind": "unsatisfied-maturity-level",
            "id": selected["id"],
            "summary": t("core.status.external_reason", reason=selected["requirements"][0]),
            "rationale": t("core.status.unsatisfied_rationale"),
            "evidence_paths": ["control-plane/manifests/maturity-status.json", *selected["evidence"]],
        }
    return {
        "kind": "none",
        "id": "release-ready",
        "summary": t("core.status.none_summary"),
        "rationale": t("core.status.none_rationale"),
        "evidence_paths": ["control-plane/manifests/maturity-status.json"],
    }


def evaluate_product_status(
    root: str | Path,
    *,
    as_of: date,
    release_gate_path: str | Path | None = None,
) -> dict[str, Any]:
    """Return repository-only product status and one deterministic next blocker."""

    repo_root = Path(root).resolve()
    manifests = repo_root / "control-plane" / "manifests"
    maturity_document = _read_json(manifests / "maturity-status.json", "maturity status")
    claim_document = _read_json(manifests / "claim-ledger.json", "claim ledger")
    source_document = _read_json(manifests / "source-ledger.json", "source ledger")
    capability_document = _read_json(manifests / "capability-manifest.json", "capability manifest")
    current, levels, blockers = _validate_maturity(maturity_document)
    stale, unverified = _validate_evidence_ledgers(claim_document, source_document, as_of)
    disabled_capabilities = _disabled_capabilities(capability_document)
    try:
        registry = load_control_registry(repo_root)
    except RegistryError as exc:
        raise ProductStatusError('core.status.registry', exc=exc) from exc
    disabled_profiles = sorted(
        (
            {
                "platform": profile.platform,
                "profile_id": profile.profile_id,
                "reason": profile.disabled_reason or t("core.status.disabled_without_reason"),
            }
            for profile in registry.profiles
            if profile.status == "disabled"
        ),
        key=lambda item: (item["platform"], item["profile_id"]),
    )
    gate_path = None if release_gate_path is None else Path(release_gate_path)
    release_gate = _release_gate(gate_path, repo_root)
    next_level = next((level["id"] for level in levels if not level["satisfied"]), None)
    maturity_path = "control-plane/manifests/maturity-status.json"
    shown_blockers = [guidance_text(value, maturity_path) for value in blockers]
    shown_levels = [
        {**level, "requirements": [guidance_text(value, maturity_path) for value in level["requirements"]]}
        for level in levels
    ]
    for profile in disabled_profiles:
        profile["reason"] = guidance_text(profile["reason"], "control-plane/manifests/scoring-profiles.json")
    for capability in disabled_capabilities:
        capability["reason"] = guidance_text(capability["reason"], "control-plane/manifests/capability-manifest.json")
    next_blocker = _next_blocker(
        stale=stale,
        unverified=unverified,
        blockers=shown_blockers,
        release_gate=release_gate,
        disabled_profiles=disabled_profiles,
        disabled_capabilities=disabled_capabilities,
        levels=shown_levels,
    )
    return {
        "schema_version": STATUS_SCHEMA_VERSION,
        "evidence_class": "repository-artifact-status",
        "as_of": as_of.isoformat(),
        "selection_policy": "artifact-order-v1",
        "maturity": {
            "current": current,
            "next_level": next_level,
            "evaluated_at": maturity_document["evaluated_at"],
            "levels": [
                {"id": level["id"], "ordinal": level["ordinal"], "satisfied": level["satisfied"]}
                for level in levels
            ],
            "declared_blockers": shown_blockers,
        },
        "evidence": {
            "stale_load_bearing_claims": stale,
            "unverified_load_bearing_claims": unverified,
        },
        "capabilities": {"disabled": disabled_capabilities},
        "scoring_profiles": {"disabled": disabled_profiles},
        "release_gate": release_gate,
        "next_blocker": next_blocker,
    }
