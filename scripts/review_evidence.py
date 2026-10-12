#!/usr/bin/env python3
"""Verify external, independently signed Claude Ads release-review evidence."""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from typing import Any

# Source checkouts and installed skills both keep core beside scripts/.
_CORE_PARENT = str(Path(__file__).resolve().parents[1])
if _CORE_PARENT not in sys.path:
    sys.path.insert(0, _CORE_PARENT)
from claude_ads_core.cli_support import LocaleArgumentParser, cli_locale
from claude_ads_core.i18n import locale_scope, t

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
except ImportError:  # pragma: no cover - verification fails closed below
    InvalidSignature = ValueError  # type: ignore[assignment,misc]
    Ed25519PublicKey = None  # type: ignore[assignment,misc]


REPOSITORY = "https://github.com/AI-Marketing-Hub/claude-ads"
REVIEW_TYPES = {"code", "evidence", "security", "privacy", "licensing"}
SEVERITIES = {"critical", "high", "medium", "low", "informational"}
EVIDENCE_KINDS = {
    "ci-run",
    "command-output",
    "diff",
    "document",
    "issue",
    "pull-request",
    "report",
    "source-ledger",
    "test-artifact",
}
REVIEW_MAX_BYTES = 1024 * 1024
REVIEW_MAX_FILES = 100
TRUST_BUNDLE_MAX_BYTES = 256 * 1024


class ReviewEvidenceError(RuntimeError):
    """Independent review evidence failed closed."""


def _parse_utc(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        raise ReviewEvidenceError(t('maintenance.review_evidence.must_be_an_rfc_3339_timestamp', v0=label))
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReviewEvidenceError(t('maintenance.review_evidence.must_be_an_rfc_3339_timestamp', v0=label)) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ReviewEvidenceError(t('maintenance.review_evidence.must_include_a_timezone', v0=label))
    return parsed.astimezone(timezone.utc)


def _format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _decode_b64url(value: Any, label: str, expected_length: int) -> bytes:
    if not isinstance(value, str) or not value:
        raise ReviewEvidenceError(t('maintenance.review_evidence.must_be_base64url_text', v0=label))
    try:
        decoded = base64.b64decode(
            value + "=" * (-len(value) % 4),
            altchars=b"-_",
            validate=True,
        )
    except (TypeError, ValueError) as exc:
        raise ReviewEvidenceError(t('maintenance.review_evidence.is_not_valid_base64url', v0=label)) from exc
    canonical = base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii")
    if canonical != value.rstrip("=") or len(decoded) != expected_length:
        raise ReviewEvidenceError(t('maintenance.review_evidence.is_not_canonical_or_has_the_wrong_length', v0=label))
    return decoded


def _canonical_review_payload(document: dict[str, Any]) -> bytes:
    authenticated = json.loads(json.dumps(document))
    authentication = authenticated.get("authentication")
    if not isinstance(authentication, dict):
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_authentication_must_be_an_object'))
    authentication.pop("signature_b64url", None)
    return json.dumps(
        authenticated,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _read_regular_file(path: Path, maximum_bytes: int, label: str) -> bytes:
    if path.is_symlink():
        raise ReviewEvidenceError(t('maintenance.review_evidence.must_not_be_a_symlink', v0=label, v1=path.name))
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ReviewEvidenceError(t('maintenance.review_evidence.cannot_open', v0=label, v1=path.name)) from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ReviewEvidenceError(t('maintenance.review_evidence.must_be_a_regular_file', v0=label, v1=path.name))
        if metadata.st_size > maximum_bytes:
            raise ReviewEvidenceError(t('maintenance.review_evidence.is_too_large', v0=label, v1=path.name))
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            data = stream.read(maximum_bytes + 1)
        if len(data) > maximum_bytes:
            raise ReviewEvidenceError(t('maintenance.review_evidence.is_too_large', v0=label, v1=path.name))
        return data
    finally:
        os.close(descriptor)


def _load_json_bytes(raw: bytes, label: str) -> Any:
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReviewEvidenceError(t('maintenance.review_evidence.must_be_valid_utf_8_json', v0=label)) from exc


def _git(root: Path, expression: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", expression],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode:
        raise ReviewEvidenceError(t('maintenance.review_evidence.cannot_resolve_release_subject', v0=expression))
    value = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ReviewEvidenceError(t('maintenance.review_evidence.release_subject_is_not_a_full_git_object_id', v0=expression))
    return value


def _load_policy(root: Path) -> dict[str, Any]:
    path = root / "control-plane" / "manifests" / "review-policy.json"
    document = _load_json_bytes(_read_regular_file(path, REVIEW_MAX_BYTES, t('maintenance.review_evidence.review_policy')), t('maintenance.review_evidence.review_policy'))
    if not isinstance(document, dict):
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_policy_must_be_an_object'))
    expected = {
        "schema_version",
        "subject_repository",
        "required_review_types",
        "required_decision",
        "subject_binding",
        "authentication",
        "independence",
        "freshness",
        "findings",
        "templates_are_evidence",
    }
    if set(document) != expected:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_policy_fields_do_not_match_the_v1_contract'))
    if (
        document["schema_version"] != "1.0.0"
        or document["subject_repository"] != REPOSITORY
        or set(document["required_review_types"]) != REVIEW_TYPES
        or document["required_decision"] != "approved"
        or document["templates_are_evidence"] is not False
    ):
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_policy_weakens_the_required_release_contract'))
    if document["subject_binding"] != {
        "require_exact_commit_sha": True,
        "require_exact_tree_sha": True,
    }:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_policy_must_bind_the_exact_commit_and_tree'))
    authentication = document["authentication"]
    if authentication != {
        "algorithm": "ed25519",
        "trust_keys_environment": "CLAUDE_ADS_REVIEW_TRUST_KEYS_JSON",
        "allow_repository_local_trust_keys": False,
        "bind_key_to_reviewer_id_and_review_types": True,
    }:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_policy_must_use_external_reviewer_bound_ed25519_keys'))
    independence = document["independence"]
    if (
        not isinstance(independence, dict)
        or independence.get("minimum_distinct_reviewer_ids", 0) < 2
        or independence.get("implementation_principal_environment")
        != "CLAUDE_ADS_IMPLEMENTATION_PRINCIPALS_JSON"
        or independence.get("implementation_principals_may_not_review") is not True
    ):
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_policy_independence_requirements_are_too_weak'))
    freshness = document["freshness"]
    maximum_age_days = freshness.get("maximum_age_days") if isinstance(freshness, dict) else None
    if not isinstance(maximum_age_days, int) or not 1 <= maximum_age_days <= 30:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_policy_freshness_is_invalid'))
    findings = document["findings"]
    if (
        not isinstance(findings, dict)
        or set(findings.get("forbid_open_severities", [])) != {"critical", "high"}
        or findings.get("accepted_risk_requires_owner_gate") is not True
    ):
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_policy_finding_requirements_are_too_weak'))
    return document


def _load_trust_bundle(raw_json: str | None) -> dict[str, dict[str, Any]]:
    if not raw_json:
        raise ReviewEvidenceError(t('maintenance.review_evidence.external_review_trust_bundle_is_required'))
    if len(raw_json.encode("utf-8")) > TRUST_BUNDLE_MAX_BYTES:
        raise ReviewEvidenceError(t('maintenance.review_evidence.external_review_trust_bundle_is_too_large'))
    document = _load_json_bytes(raw_json.encode("utf-8"), t('maintenance.review_evidence.review_trust_bundle'))
    if not isinstance(document, dict) or set(document) != {"schema_version", "keys"}:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_trust_bundle_fields_are_invalid'))
    if (
        document["schema_version"] != "1.0.0"
        or not isinstance(document["keys"], list)
        or not 1 <= len(document["keys"]) <= 100
    ):
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_trust_bundle_version_or_keys_are_invalid'))
    keys: dict[str, dict[str, Any]] = {}
    for entry in document["keys"]:
        expected = {
            "key_id",
            "public_key_b64url",
            "reviewer_id",
            "allowed_review_types",
            "valid_from",
            "valid_until",
            "revoked",
        }
        if not isinstance(entry, dict) or set(entry) != expected:
            raise ReviewEvidenceError(t('maintenance.review_evidence.review_trust_key_fields_are_invalid'))
        key_id = entry["key_id"]
        reviewer_id = entry["reviewer_id"]
        allowed = entry["allowed_review_types"]
        if (
            not isinstance(key_id, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}", key_id)
            or not isinstance(reviewer_id, str)
            or len(reviewer_id) < 3
            or not isinstance(allowed, list)
            or not allowed
            or not set(allowed) <= REVIEW_TYPES
            or len(set(allowed)) != len(allowed)
            or not isinstance(entry["revoked"], bool)
        ):
            raise ReviewEvidenceError(t('maintenance.review_evidence.review_trust_key_identity_or_scope_is_invalid'))
        if key_id in keys:
            raise ReviewEvidenceError(t('maintenance.review_evidence.duplicate_review_trust_key', v0=key_id))
        entry = dict(entry)
        entry["public_key"] = _decode_b64url(
            entry["public_key_b64url"],
            t('maintenance.review_evidence.review_public_key', v0=key_id),
            32,
        )
        entry["valid_from_parsed"] = _parse_utc(entry["valid_from"], f"{key_id}.valid_from")
        entry["valid_until_parsed"] = _parse_utc(entry["valid_until"], f"{key_id}.valid_until")
        if entry["valid_from_parsed"] >= entry["valid_until_parsed"]:
            raise ReviewEvidenceError(t('maintenance.review_evidence.review_trust_key_validity_is_inconsistent', v0=key_id))
        keys[key_id] = entry
    if not keys:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_trust_bundle_has_no_keys'))
    return keys


def _load_implementation_principals(raw_json: str | None) -> set[str]:
    if not raw_json:
        raise ReviewEvidenceError(t('maintenance.review_evidence.external_implementation_principal_list_is_required'))
    document = _load_json_bytes(raw_json.encode("utf-8"), t('maintenance.review_evidence.implementation_principal_list'))
    if (
        not isinstance(document, list)
        or not document
        or len(document) > 1000
        or any(not isinstance(value, str) or len(value) < 3 for value in document)
        or len(set(document)) != len(document)
    ):
        raise ReviewEvidenceError(t('maintenance.review_evidence.implementation_principal_list_must_be_a_unique_non_empty_array'))
    return set(document)


def _validate_review_document(
    document: Any,
    *,
    filename: str,
    commit_sha: str,
    tree_sha: str,
    trust_keys: dict[str, dict[str, Any]],
    implementation_principals: set[str],
    policy: dict[str, Any],
    now: datetime,
) -> dict[str, str]:
    expected = {
        "schema_version",
        "review_id",
        "review_type",
        "subject",
        "reviewer",
        "reviewed_at",
        "decision",
        "evidence_refs",
        "findings",
        "authentication",
    }
    if not isinstance(document, dict) or set(document) != expected:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_fields_are_invalid', v0=filename))
    review_id = document["review_id"]
    review_type = document["review_type"]
    if (
        document["schema_version"] != "1.0.0"
        or not isinstance(review_id, str)
        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}", review_id)
        or review_id.startswith("TEMPLATE-")
        or review_type not in REVIEW_TYPES
        or document["decision"] != "approved"
    ):
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_is_not_an_approvable_v1_document', v0=filename))
    if document["subject"] != {
        "repository": REPOSITORY,
        "commit_sha": commit_sha,
        "tree_sha": tree_sha,
    }:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_does_not_bind_the_exact_release_subject', v0=filename))

    reviewer = document["reviewer"]
    if not isinstance(reviewer, dict) or set(reviewer) != {
        "id",
        "independence_basis",
        "conflict_disclosure",
    }:
        raise ReviewEvidenceError(t('maintenance.review_evidence.reviewer_fields_are_invalid', v0=filename))
    reviewer_id = reviewer["id"]
    if (
        not isinstance(reviewer_id, str)
        or len(reviewer_id) < 3
        or not isinstance(reviewer["independence_basis"], str)
        or len(reviewer["independence_basis"]) < 20
        or not isinstance(reviewer["conflict_disclosure"], str)
        or len(reviewer["conflict_disclosure"]) < 4
    ):
        raise ReviewEvidenceError(t('maintenance.review_evidence.reviewer_identity_or_independence_is_incomplete', v0=filename))
    if reviewer_id in implementation_principals:
        raise ReviewEvidenceError(t('maintenance.review_evidence.implementation_principal_cannot_approve_review', v0=reviewer_id))

    reviewed_at = _parse_utc(document["reviewed_at"], f"{filename}.reviewed_at")
    maximum_age = timedelta(days=policy["freshness"]["maximum_age_days"])
    if reviewed_at > now + timedelta(minutes=5):
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_timestamp_is_in_the_future', v0=filename))
    if now - reviewed_at > maximum_age:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_evidence_is_stale', v0=filename))

    evidence_refs = document["evidence_refs"]
    if (
        not isinstance(evidence_refs, list)
        or not evidence_refs
        or len(evidence_refs) > 100
    ):
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_evidence_references_are_incomplete', v0=filename))
    for reference in evidence_refs:
        if not isinstance(reference, dict) or set(reference) != {"kind", "locator", "sha256"}:
            raise ReviewEvidenceError(t('maintenance.review_evidence.review_evidence_reference_fields_are_invalid', v0=filename))
        if (
            reference["kind"] not in EVIDENCE_KINDS
            or not isinstance(reference["locator"], str)
            or not reference["locator"].strip()
            or (
                reference["sha256"] is not None
                and not (
                    isinstance(reference["sha256"], str)
                    and re.fullmatch(r"[0-9a-f]{64}", reference["sha256"])
                )
            )
        ):
            raise ReviewEvidenceError(t('maintenance.review_evidence.review_evidence_reference_is_invalid', v0=filename))

    findings = document["findings"]
    if not isinstance(findings, list) or len(findings) > 500:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_findings_are_invalid', v0=filename))
    finding_ids: set[str] = set()
    for finding in findings:
        required = {"id", "severity", "status", "title", "evidence_refs", "resolution"}
        if not isinstance(finding, dict) or set(finding) != required:
            raise ReviewEvidenceError(t('maintenance.review_evidence.review_finding_fields_are_invalid', v0=filename))
        finding_id = finding["id"]
        if (
            not isinstance(finding_id, str)
            or not re.fullmatch(r"[A-Z][A-Z0-9-]{2,63}", finding_id)
            or finding_id in finding_ids
            or finding["severity"] not in SEVERITIES
            or finding["status"] not in {"open", "resolved", "accepted-risk"}
            or not isinstance(finding["title"], str)
            or not 3 <= len(finding["title"]) <= 500
            or not isinstance(finding["evidence_refs"], list)
            or not finding["evidence_refs"]
            or any(
                not isinstance(index, int) or not 0 <= index < len(evidence_refs)
                for index in finding["evidence_refs"]
            )
        ):
            raise ReviewEvidenceError(t('maintenance.review_evidence.review_finding_is_invalid', v0=filename))
        finding_ids.add(finding_id)
        if finding["status"] == "accepted-risk":
            raise ReviewEvidenceError(
                t('maintenance.review_evidence.accepted_risk_finding_requires_a_separate_owner_gate', v0=finding_id)
            )
        if finding["status"] == "open" and finding["severity"] in {"critical", "high"}:
            raise ReviewEvidenceError(t('maintenance.review_evidence.open_release_blocking_finding', v0=finding_id))
        if finding["status"] == "resolved" and (
            not isinstance(finding["resolution"], str) or not finding["resolution"].strip()
        ):
            raise ReviewEvidenceError(t('maintenance.review_evidence.resolved_finding_lacks_resolution', v0=finding_id))
        if finding["resolution"] is not None and (
            not isinstance(finding["resolution"], str) or len(finding["resolution"]) > 2000
        ):
            raise ReviewEvidenceError(t('maintenance.review_evidence.review_finding_resolution_is_invalid', v0=finding_id))

    authentication = document["authentication"]
    if not isinstance(authentication, dict) or set(authentication) != {
        "algorithm",
        "key_id",
        "signature_b64url",
    }:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_authentication_fields_are_invalid', v0=filename))
    if authentication["algorithm"] != "ed25519":
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_authentication_algorithm_is_unsupported', v0=filename))
    key_id = authentication["key_id"]
    key = trust_keys.get(key_id)
    if not key or key["revoked"]:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_key_is_absent_or_revoked', v0=key_id))
    if key["reviewer_id"] != reviewer_id or review_type not in key["allowed_review_types"]:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_key_is_not_authorized_for_reviewer_and_type', v0=key_id))
    if not key["valid_from_parsed"] <= reviewed_at < key["valid_until_parsed"]:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_key_was_not_valid_at_review_time', v0=key_id))
    if Ed25519PublicKey is None:
        raise ReviewEvidenceError(t('maintenance.review_evidence.cryptography_is_required_for_ed25519_review_verification'))
    signature = _decode_b64url(
        authentication["signature_b64url"],
        t('maintenance.review_evidence.review_signature', v0=review_id),
        64,
    )
    try:
        Ed25519PublicKey.from_public_bytes(key["public_key"]).verify(
            signature,
            _canonical_review_payload(document),
        )
    except (InvalidSignature, ValueError) as exc:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_signature_verification_failed', v0=review_id)) from exc
    return {
        "review_id": review_id,
        "review_type": review_type,
        "reviewer_id": reviewer_id,
        "key_id": key_id,
        "reviewed_at": _format_utc(reviewed_at),
    }


def verify_independent_reviews(
    root: str | os.PathLike[str],
    evidence_dir: str | os.PathLike[str],
    *,
    trust_bundle_json: str | None = None,
    implementation_principals_json: str | None = None,
    commit_sha: str | None = None,
    tree_sha: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Verify the complete external independent-review set for one Git tree."""
    repository_root = Path(root).resolve()
    raw_evidence_dir = Path(evidence_dir).expanduser()
    if raw_evidence_dir.is_symlink():
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_evidence_directory_must_not_be_a_symlink'))
    directory = raw_evidence_dir.resolve()
    try:
        directory.relative_to(repository_root)
    except ValueError:
        pass
    else:
        raise ReviewEvidenceError(t('maintenance.review_evidence.review_evidence_must_be_outside_the_repository_checkout'))
    if not directory.is_dir():
        raise ReviewEvidenceError(t('maintenance.review_evidence.external_review_evidence_directory_does_not_exist'))

    policy = _load_policy(repository_root)
    trust_keys = _load_trust_bundle(
        trust_bundle_json or os.environ.get(policy["authentication"]["trust_keys_environment"])
    )
    implementation_principals = _load_implementation_principals(
        implementation_principals_json
        or os.environ.get(policy["independence"]["implementation_principal_environment"])
    )
    subject_commit = commit_sha or _git(repository_root, "HEAD")
    subject_tree = tree_sha or _git(repository_root, "HEAD^{tree}")
    if not re.fullmatch(r"[0-9a-f]{40}", subject_commit) or not re.fullmatch(
        r"[0-9a-f]{40}", subject_tree
    ):
        raise ReviewEvidenceError(t('maintenance.review_evidence.release_subject_requires_full_lowercase_git_object_ids'))
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)

    entries = sorted(directory.iterdir())
    if any(path.suffix != ".json" or not path.is_file() for path in entries):
        raise ReviewEvidenceError(t('maintenance.review_evidence.external_review_evidence_directory_contains_unexpected_entries'))
    files = entries
    if not files or len(files) > REVIEW_MAX_FILES:
        raise ReviewEvidenceError(t('maintenance.review_evidence.external_review_evidence_must_contain_1_100_json_files'))
    verified: list[dict[str, str]] = []
    document_digests: list[dict[str, str]] = []
    seen_types: set[str] = set()
    seen_ids: set[str] = set()
    for path in files:
        raw = _read_regular_file(path, REVIEW_MAX_BYTES, t('maintenance.review_evidence.review_evidence'))
        document = _load_json_bytes(raw, t('maintenance.review_evidence.review_evidence_2', v0=path.name))
        item = _validate_review_document(
            document,
            filename=path.name,
            commit_sha=subject_commit,
            tree_sha=subject_tree,
            trust_keys=trust_keys,
            implementation_principals=implementation_principals,
            policy=policy,
            now=current,
        )
        if item["review_type"] in seen_types:
            raise ReviewEvidenceError(t('maintenance.review_evidence.duplicate_review_type', v0=item['review_type']))
        if item["review_id"] in seen_ids:
            raise ReviewEvidenceError(t('maintenance.review_evidence.duplicate_review_id', v0=item['review_id']))
        seen_types.add(item["review_type"])
        seen_ids.add(item["review_id"])
        verified.append(item)
        document_digests.append(
            {"review_id": item["review_id"], "sha256": hashlib.sha256(raw).hexdigest()}
        )

    if seen_types != REVIEW_TYPES:
        missing = ", ".join(sorted(REVIEW_TYPES - seen_types))
        raise ReviewEvidenceError(t('maintenance.review_evidence.required_review_types_are_missing', v0=missing))
    reviewers = {item["reviewer_id"] for item in verified}
    if len(reviewers) < policy["independence"]["minimum_distinct_reviewer_ids"]:
        raise ReviewEvidenceError(t('maintenance.review_evidence.independent_review_requires_at_least_two_distinct_reviewers'))

    return {
        "schema_version": "1.0.0",
        "satisfied": True,
        "evaluated_at": _format_utc(current),
        "subject": {
            "repository": REPOSITORY,
            "commit_sha": subject_commit,
            "tree_sha": subject_tree,
        },
        "reviewers": sorted(reviewers),
        "reviews": sorted(verified, key=lambda item: item["review_type"]),
        "evidence_documents": sorted(document_digests, key=lambda item: item["review_id"]),
    }


def main(argv: list[str] | None = None) -> int:
    with locale_scope(cli_locale(argv)):
        return _main(argv)


def _main(argv: list[str] | None = None) -> int:
    parser = LocaleArgumentParser(description=t('maintenance.review_evidence.verify_external_independently_signed_claude_ads_release_review_evidence'))
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1], help=t("maintenance.common.root_help"))
    parser.add_argument(
        "--evidence-dir",
        default=os.environ.get("CLAUDE_ADS_REVIEW_EVIDENCE_DIR"),
        help=t('maintenance.review_evidence.external_directory_containing_signed_review_json_documents'),
    )
    parser.add_argument("--commit-sha", help=t("maintenance.review_evidence.commit_help"))
    parser.add_argument("--tree-sha", help=t("maintenance.review_evidence.tree_help"))
    args = parser.parse_args(argv)
    if not args.evidence_dir:
        print(t('maintenance.review_evidence.review_evidence_error_external_evidence_directory_is_required'), file=sys.stderr)
        return 1
    try:
        report = verify_independent_reviews(
            args.root,
            args.evidence_dir,
            commit_sha=args.commit_sha,
            tree_sha=args.tree_sha,
        )
    except (OSError, TypeError, ValueError, ReviewEvidenceError) as exc:
        print(t('maintenance.review_evidence.review_evidence_error', v0=exc), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
