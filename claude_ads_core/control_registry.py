"""Versioned, fail-closed control registry and platform scoring profiles.

The audit catalog is useful for discovery, but a named check is not automatically
a scoreable control.  This loader enforces that distinction at runtime.  Only an
enabled profile whose health controls resolve to verified, load-bearing claims
may enter the deterministic scoring engine.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import PLATFORMS, ContractError, validate_contract
from .errors import LocalizedError
from .scoring import ScoreResult, score_account

REGISTRY_SCHEMA_VERSION = "1.0.0"
REGISTRY_VERSION = "1.0.0"
PROFILE_VERSION = "1.0.0"
DISPOSITIONS = {"conditional_watchlist", "source_refresh_discovery", "opportunity", "health"}
PROFILE_STATUSES = {"disabled", "enabled"}


class RegistryError(LocalizedError, ValueError):
    """Raised when registry or scoring-profile state is unsafe or inconsistent."""


@dataclass(frozen=True)
class RegistryEntry:
    platform: str
    control_id: str
    intent: str
    disposition: str
    source_claim_ids: tuple[str, ...]
    control_definition: Mapping[str, Any]


@dataclass(frozen=True)
class ScoringProfile:
    profile_id: str
    platform: str
    status: str
    category_weights: Mapping[str, float]
    health_control_ids: tuple[str, ...]
    disabled_reason: str | None


@dataclass(frozen=True)
class ControlRegistry:
    entries: tuple[RegistryEntry, ...]
    profiles: tuple[ScoringProfile, ...]

    def entries_for(self, platform: str) -> tuple[RegistryEntry, ...]:
        normalized = platform.lower()
        if normalized not in PLATFORMS:
            raise RegistryError('core.registry.unsupported_platform', platform=platform)
        return tuple(entry for entry in self.entries if entry.platform == normalized)

    def controls_for(self, platform: str) -> tuple[Mapping[str, Any], ...]:
        return tuple(entry.control_definition for entry in self.entries_for(platform))

    def profile_for(self, platform: str) -> ScoringProfile:
        normalized = platform.lower()
        for profile in self.profiles:
            if profile.platform == normalized:
                return profile
        raise RegistryError('core.registry.missing_profile', platform=platform)

    def scoring_inputs(self, platform: str) -> tuple[tuple[Mapping[str, Any], ...], Mapping[str, float]]:
        """Return approved health controls and weights, or fail closed."""

        profile = self.profile_for(platform)
        if profile.status != "enabled":
            raise RegistryError('core.registry.profile_disabled', value1=profile.profile_id, value2=profile.disabled_reason)
        entries = {entry.control_id: entry for entry in self.entries_for(platform)}
        return (
            tuple(entries[control_id].control_definition for control_id in profile.health_control_ids),
            profile.category_weights,
        )

    def score_platform(
        self,
        platform: str,
        findings: Sequence[Mapping[str, Any]],
    ) -> ScoreResult:
        """Score through the approved profile; disabled profiles yield no health.

        A disabled profile means no evidence obligation has been approved, so its
        evidence coverage is zero rather than the scoring engine's normal 100%
        result for an empty set of applicable controls.
        """

        profile = self.profile_for(platform)
        if profile.status != "enabled":
            return ScoreResult(
                health_score=None,
                evidence_coverage=0.0,
                status="insufficient_evidence",
                categories=(),
            )
        controls, weights = self.scoring_inputs(platform)
        return score_account(controls, findings, weights)


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError('core.io.load', path=path, exc=exc) from exc
    if not isinstance(payload, Mapping):
        raise RegistryError('core.registry.json_object', path=path)
    return payload


def _nonempty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RegistryError('core.validation.nonempty_string', path=path)
    return value


def _string_tuple(value: Any, path: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise RegistryError('core.validation.array', path=path)
    result = tuple(_nonempty_string(item, f"{path}[{index}]") for index, item in enumerate(value))
    if len(result) != len(set(result)):
        raise RegistryError('core.validation.unique', path=path)
    return result


def _verified_claims(claim_ledger: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    claims = claim_ledger.get("claims")
    if not isinstance(claims, list):
        raise RegistryError('core.registry.claim_array')
    result: dict[str, Mapping[str, Any]] = {}
    for index, raw_claim in enumerate(claims):
        if not isinstance(raw_claim, Mapping):
            raise RegistryError('core.registry.claim_object', index=index)
        claim_id = _nonempty_string(raw_claim.get("id"), f"claim ledger claims[{index}].id")
        if claim_id in result:
            raise RegistryError('core.registry.claim_duplicate', claim_id=claim_id)
        result[claim_id] = raw_claim
    return result


def _known_sources(source_ledger: Mapping[str, Any]) -> set[str]:
    sources = source_ledger.get("sources")
    if not isinstance(sources, list):
        raise RegistryError('core.registry.source_array')
    result: set[str] = set()
    for index, raw_source in enumerate(sources):
        if not isinstance(raw_source, Mapping):
            raise RegistryError('core.registry.source_object', index=index)
        source_id = _nonempty_string(raw_source.get("id"), f"source ledger sources[{index}].id")
        if source_id in result:
            raise RegistryError('core.registry.source_duplicate', source_id=source_id)
        result.add(source_id)
    return result


def _validate_entry(
    raw_entry: Any,
    index: int,
    claims: Mapping[str, Mapping[str, Any]],
    sources: set[str],
) -> RegistryEntry:
    if not isinstance(raw_entry, Mapping):
        raise RegistryError('core.registry.control_object', index=index)
    platform = _nonempty_string(raw_entry.get("platform"), f"controls[{index}].platform").lower()
    if platform not in PLATFORMS:
        raise RegistryError('core.registry.control_platform', index=index)
    control_id = _nonempty_string(raw_entry.get("control_id"), f"controls[{index}].control_id")
    intent = _nonempty_string(raw_entry.get("intent"), f"controls[{index}].intent")
    disposition = _nonempty_string(raw_entry.get("disposition"), f"controls[{index}].disposition")
    if disposition not in DISPOSITIONS:
        raise RegistryError('core.registry.control_disposition', index=index)
    claim_ids = _string_tuple(raw_entry.get("source_claim_ids"), f"controls[{index}].source_claim_ids")
    definition = raw_entry.get("control_definition")
    if not isinstance(definition, Mapping):
        raise RegistryError('core.registry.definition_object', index=index)
    try:
        validate_contract("control-definition", definition)
    except ContractError as exc:
        raise RegistryError('core.registry.control_definition', index=index, exc=exc) from exc
    if definition["control_id"] != control_id:
        raise RegistryError('core.registry.definition_id', index=index)
    expected_behavior = "health" if disposition == "health" else (
        "opportunity" if disposition == "opportunity" else "watchlist"
    )
    if definition["scoring_behavior"] != expected_behavior:
        raise RegistryError('core.registry.behavior', control_id=control_id)
    definition_sources = set(_string_tuple(definition["source_ids"], f"{control_id}.source_ids"))
    unknown_sources = definition_sources - sources
    if unknown_sources:
        raise RegistryError('core.registry.unknown_sources', control_id=control_id, value2=sorted(unknown_sources))
    for claim_id in claim_ids:
        if claim_id not in claims:
            raise RegistryError('core.registry.unknown_claim', control_id=control_id, claim_id=claim_id)
        claim_sources = set(claims[claim_id].get("source_ids", []))
        if not definition_sources <= claim_sources:
            raise RegistryError('core.registry.claim_support', control_id=control_id, claim_id=claim_id)
    if disposition == "health":
        if not claim_ids or not definition_sources or not definition["required_inputs"]:
            raise RegistryError('core.registry.health_evidence', control_id=control_id)
        if definition["severity"] == "informational":
            raise RegistryError('core.registry.health_severity', control_id=control_id)
        if definition["maturity"] not in {"source-grounded", "domain-integrated", "eval-verified", "release-ready"}:
            raise RegistryError('core.registry.health_maturity', control_id=control_id)
        if definition["stability"] != "stable":
            raise RegistryError('core.registry.health_stability', control_id=control_id)
        for claim_id in claim_ids:
            claim = claims[claim_id]
            if claim.get("verdict") != "verified" or claim.get("load_bearing") is not True:
                raise RegistryError('core.registry.unverified_claim', control_id=control_id, claim_id=claim_id)
    elif definition["severity"] != "informational":
        raise RegistryError('core.registry.unscored_severity', control_id=control_id)
    return RegistryEntry(platform, control_id, intent, disposition, claim_ids, definition)


def _validate_profile(raw_profile: Any, index: int, entries: Mapping[tuple[str, str], RegistryEntry]) -> ScoringProfile:
    if not isinstance(raw_profile, Mapping):
        raise RegistryError('core.registry.profile_object', index=index)
    profile_id = _nonempty_string(raw_profile.get("profile_id"), f"profiles[{index}].profile_id")
    platform = _nonempty_string(raw_profile.get("platform"), f"profiles[{index}].platform").lower()
    if platform not in PLATFORMS:
        raise RegistryError('core.registry.profile_platform', index=index)
    status = _nonempty_string(raw_profile.get("status"), f"profiles[{index}].status")
    if status not in PROFILE_STATUSES:
        raise RegistryError('core.registry.profile_status', index=index)
    raw_weights = raw_profile.get("category_weights")
    if not isinstance(raw_weights, Mapping):
        raise RegistryError('core.registry.profile_weights', index=index)
    weights: dict[str, float] = {}
    for category, raw_weight in raw_weights.items():
        if not isinstance(category, str) or not category:
            raise RegistryError('core.registry.category_names', index=index)
        if isinstance(raw_weight, bool) or not isinstance(raw_weight, (int, float)):
            raise RegistryError('core.registry.weight_numeric', index=index, category=category)
        weights[category] = float(raw_weight)
    health_ids = _string_tuple(raw_profile.get("health_control_ids"), f"profiles[{index}].health_control_ids")
    disabled_reason = raw_profile.get("disabled_reason")
    if disabled_reason is not None:
        disabled_reason = _nonempty_string(disabled_reason, f"profiles[{index}].disabled_reason")
    if status == "disabled":
        if weights or health_ids or disabled_reason is None:
            raise RegistryError('core.registry.disabled_reason', profile_id=profile_id)
    else:
        if disabled_reason is not None or not health_ids or sum(weights.values()) != 100.0:
            raise RegistryError('core.registry.enabled_weights', profile_id=profile_id)
        selected: list[RegistryEntry] = []
        for control_id in health_ids:
            entry = entries.get((platform, control_id))
            if entry is None:
                raise RegistryError('core.registry.unknown_control', profile_id=profile_id, control_id=control_id)
            if entry.disposition != "health":
                raise RegistryError('core.registry.unscored_control', profile_id=profile_id, control_id=control_id)
            selected.append(entry)
        categories = {str(entry.control_definition["category"]) for entry in selected}
        if set(weights) != categories:
            raise RegistryError('core.registry.category_match', profile_id=profile_id)
    return ScoringProfile(profile_id, platform, status, weights, health_ids, disabled_reason)


def load_control_registry(root: str | Path) -> ControlRegistry:
    """Load and semantically validate the repository control-plane registry."""

    repo_root = Path(root).resolve()
    manifest_root = repo_root / "control-plane" / "manifests"
    registry_payload = _read_json(manifest_root / "control-registry.json")
    profile_payload = _read_json(manifest_root / "scoring-profiles.json")
    claims = _verified_claims(_read_json(manifest_root / "claim-ledger.json"))
    sources = _known_sources(_read_json(manifest_root / "source-ledger.json"))
    if registry_payload.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        raise RegistryError('core.registry.schema_version')
    if registry_payload.get("registry_version") != REGISTRY_VERSION:
        raise RegistryError('core.registry.registry_version')
    if profile_payload.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        raise RegistryError('core.registry.profiles_schema_version')
    if profile_payload.get("profile_version") != PROFILE_VERSION:
        raise RegistryError('core.registry.profile_version')
    raw_entries = registry_payload.get("controls")
    if not isinstance(raw_entries, list):
        raise RegistryError('core.registry.controls_array')
    entries = tuple(_validate_entry(raw, index, claims, sources) for index, raw in enumerate(raw_entries))
    by_key: dict[tuple[str, str], RegistryEntry] = {}
    for entry in entries:
        key = (entry.platform, entry.control_id)
        if key in by_key:
            raise RegistryError('core.registry.duplicate_control', value1=entry.platform, value2=entry.control_id)
        by_key[key] = entry
    if {entry.platform for entry in entries} != PLATFORMS:
        raise RegistryError('core.registry.platform_coverage')
    raw_profiles = profile_payload.get("profiles")
    if not isinstance(raw_profiles, list):
        raise RegistryError('core.registry.profiles_array')
    profiles = tuple(_validate_profile(raw, index, by_key) for index, raw in enumerate(raw_profiles))
    profile_platforms = [profile.platform for profile in profiles]
    if set(profile_platforms) != PLATFORMS or len(profile_platforms) != len(PLATFORMS):
        raise RegistryError('core.registry.profile_coverage')
    return ControlRegistry(entries, profiles)
