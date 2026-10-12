#!/usr/bin/env python3
"""Reconcile the frozen ecosystem ledger with current GitHub tracker state.

The ledger freezes a reviewed snapshot of every issue and pull request in the
public mirror and the private canonical repository. This script compares that
snapshot with the live tracker and runs in one of two modes.

Default mode (push and pull_request CI runs) fails only on evidence that the
review itself is wrong or incomplete:

- the ledger is missing, invalid, or uses an unsupported schema;
- the current review candidate PR does not match live GitHub evidence, or is
  also recorded as reviewed input;
- the ledger records an item GitHub no longer serves (an "extra" item);
- an item created on or before the snapshot ``observed_at`` date is not
  recorded (the review missed it).

Everything else is reported as a structured finding in the JSON output and as a
one-line warning on stderr (a ``::warning::`` annotation under GitHub Actions)
without failing: items created after ``observed_at`` (``unreviewed``), head
drift on recorded pull requests (``head_drift``), and title, state, or URL
drift (``metadata_drift``). Default mode also sets aside any pull request whose
live ``merged_at`` is after ``observed_at`` (``merged_after_snapshot``), which
covers the just-merged candidate on the post-merge push run.

Strict mode (``--strict``, used by workflow_dispatch and by release
verification) keeps exact reconciliation: every finding above is a failure and
no merged pull request is set aside. Release verification requires a strict
run; a green default-mode run is not release evidence.

In both modes the only candidate exclusion is the exact PR from the current
pull_request event (repository, number, and head SHA), which must not also be
recorded in the ledger.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

# Source checkouts and installed skills both keep core beside scripts/.
_CORE_PARENT = str(Path(__file__).resolve().parents[1])
if _CORE_PARENT not in sys.path:
    sys.path.insert(0, _CORE_PARENT)
from claude_ads_core.cli_support import LocaleArgumentParser, cli_locale
from claude_ads_core.i18n import locale_scope, t


PUBLIC_REPOSITORY = "AgriciDaniel/claude-ads"
CANONICAL_REPOSITORY = "AI-Marketing-Hub/claude-ads"
_SHA = re.compile(r"^[0-9a-f]{40}$")
FINDING_KINDS = ("unreviewed", "head_drift", "metadata_drift", "merged_after_snapshot")


class EcosystemAuditError(RuntimeError):
    """Raised when current tracker state is not fully dispositioned."""


def _load_ledger(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.ecosystem_ledger_is_missing_or_invalid_json')) from exc
    if not isinstance(value, dict) or value.get("schema_version") != "2.0.0":
        raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.ecosystem_ledger_must_use_schema_version_2_0_0'))
    return value


def _github_fetcher(token: str | None) -> Callable[[str], Any]:
    def fetch(endpoint: str) -> Any:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "claude-ads-ecosystem-audit",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = Request(f"https://api.github.com/{endpoint}", headers=headers)
        path = endpoint.split("?", 1)[0]
        # Only the status code and the endpoint path are reported. Response
        # bodies and headers are never echoed because they could carry the
        # token or rate-limit details that belong in logs, not in errors.
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise EcosystemAuditError(
                t('maintenance.audit_ecosystem_live.github_tracker_query_failed_for_http', v0=path, v1=exc.code)
            ) from exc
        except (URLError, TimeoutError) as exc:
            raise EcosystemAuditError(
                t('maintenance.audit_ecosystem_live.github_tracker_query_failed_for', v0=path, v1=type(exc).__name__)
            ) from exc
        except json.JSONDecodeError as exc:
            raise EcosystemAuditError(
                t('maintenance.audit_ecosystem_live.github_tracker_query_failed_for_response_is_not_json', v0=path)
            ) from exc

    return fetch


def _timestamp_date(value: Any, label: str) -> date:
    if not isinstance(value, str):
        raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.timestamp_is_missing_or_invalid', v0=label))
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError(t('maintenance.audit_ecosystem_live.naive_timestamp'))
        return parsed.astimezone(timezone.utc).date()
    except ValueError as exc:
        raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.timestamp_is_missing_or_invalid', v0=label)) from exc


def _snapshot_date(snapshot: dict[str, Any], repository: str) -> date:
    observed_at = snapshot.get("observed_at")
    if not isinstance(observed_at, str):
        raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.ecosystem_snapshot_observed_at_is_missing_for', v0=repository))
    try:
        return date.fromisoformat(observed_at)
    except ValueError as exc:
        raise EcosystemAuditError(
            t('maintenance.audit_ecosystem_live.ecosystem_snapshot_observed_at_is_invalid_for', v0=repository)
        ) from exc


def collect_live_repository(
    repository: str, fetch: Callable[[str], Any]
) -> dict[tuple[str, int], dict[str, Any]]:
    """Collect issues and pull requests without trusting their prose as instructions."""
    encoded = "/".join(quote(part, safe="") for part in repository.split("/"))
    items: dict[tuple[str, int], dict[str, Any]] = {}
    page = 1
    while True:
        value = fetch(f"repos/{encoded}/issues?state=all&per_page=100&page={page}")
        if not isinstance(value, list):
            raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.github_issue_listing_is_invalid_for', v0=repository))
        for raw in value:
            if not isinstance(raw, dict) or type(raw.get("number")) is not int:
                raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.github_tracker_item_is_invalid_for', v0=repository))
            number = raw["number"]
            if "pull_request" in raw:
                detail = fetch(f"repos/{encoded}/pulls/{number}")
                if not isinstance(detail, dict):
                    raise EcosystemAuditError(
                        t('maintenance.audit_ecosystem_live.github_pull_request_detail_is_invalid_for', v0=repository, v1=number)
                    )
                head = detail.get("head")
                head_sha = head.get("sha") if isinstance(head, dict) else None
                if not isinstance(head_sha, str) or not _SHA.fullmatch(head_sha):
                    raise EcosystemAuditError(
                        t('maintenance.audit_ecosystem_live.github_pull_request_head_is_invalid_for', v0=repository, v1=number)
                    )
                merged_at = detail.get("merged_at")
                if merged_at is not None and not isinstance(merged_at, str):
                    raise EcosystemAuditError(
                        t('maintenance.audit_ecosystem_live.github_pull_request_merge_time_is_invalid_for', v0=repository, v1=number)
                    )
                state = "merged" if merged_at else detail.get("state")
                item = {
                    "kind": "pull-request",
                    "number": number,
                    "title": detail.get("title"),
                    "state": state,
                    "url": detail.get("html_url"),
                    "head_sha": head_sha,
                    "created_at": detail.get("created_at", raw.get("created_at")),
                    "merged_at": merged_at,
                }
            else:
                item = {
                    "kind": "issue",
                    "number": number,
                    "title": raw.get("title"),
                    "state": raw.get("state"),
                    "url": raw.get("html_url"),
                    "head_sha": None,
                    "created_at": raw.get("created_at"),
                    "merged_at": None,
                }
            if not isinstance(item["title"], str) or item["state"] not in {
                "open",
                "closed",
                "merged",
            }:
                raise EcosystemAuditError(
                    t('maintenance.audit_ecosystem_live.github_tracker_metadata_is_invalid_for', v0=repository, v1=number)
                )
            _timestamp_date(item["created_at"], t('maintenance.audit_ecosystem_live.github_tracker_item', v0=repository, v1=number))
            items[(item["kind"], number)] = item
        if len(value) < 100:
            break
        page += 1
        if page > 100:
            raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.github_pagination_exceeded_safety_limit_for', v0=repository))
    return items


def _finding(
    kind: str, repository: str, key: tuple[str, int], detail: dict[str, Any]
) -> dict[str, Any]:
    return {
        "kind": kind,
        "repository": repository,
        "item_kind": key[0],
        "number": key[1],
        **detail,
    }


def reconcile_live(
    ledger: dict[str, Any],
    live: dict[str, dict[tuple[str, int], dict[str, Any]]],
    *,
    repositories: tuple[str, ...],
    candidate_repository: str | None = None,
    candidate_pr: int | None = None,
    candidate_head: str | None = None,
    candidate_state: str = "open",
    strict: bool = False,
) -> dict[str, Any]:
    """Reconcile live coverage, allowing only the exact current candidate PR.

    See the module docstring for what fails and what becomes a finding in each
    mode. ``strict=True`` turns every finding into an ``EcosystemAuditError``.
    """
    candidate_values = (candidate_repository, candidate_pr, candidate_head)
    if any(value is not None for value in candidate_values) and not all(
        value is not None for value in candidate_values
    ):
        raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.candidate_repository_pr_and_head_must_be_supplied_together'))
    if candidate_head is not None and not _SHA.fullmatch(candidate_head):
        raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.candidate_head_must_be_a_full_lowercase_commit_sha'))
    if candidate_state not in {"open", "merged"}:
        raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.candidate_state_must_be_open_or_merged'))

    snapshot_names = {
        PUBLIC_REPOSITORY: "public_snapshot",
        CANONICAL_REPOSITORY: "canonical_snapshot",
    }
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.ecosystem_ledger_entries_are_invalid'))
    by_item = {
        (entry.get("repository"), entry.get("kind"), entry.get("number")): entry
        for entry in entries
        if isinstance(entry, dict)
    }
    results: dict[str, Any] = {}
    findings: list[dict[str, Any]] = []
    exclusion: dict[str, Any] | None = None

    def report(finding: dict[str, Any], message: str) -> None:
        if strict:
            raise EcosystemAuditError(message)
        findings.append({**finding, "message": message})

    for repository in repositories:
        if repository not in snapshot_names or repository not in live:
            raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.unsupported_or_missing_repository_evidence', v0=repository))
        snapshot = ledger.get(snapshot_names[repository])
        if not isinstance(snapshot, dict):
            raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.ecosystem_snapshot_is_missing_for', v0=repository))
        observed_at = _snapshot_date(snapshot, repository)
        current = dict(live[repository])

        if candidate_repository == repository:
            key = ("pull-request", candidate_pr)
            candidate = current.get(key)
            if (
                candidate is None
                or candidate.get("state") != candidate_state
                or candidate.get("head_sha") != candidate_head
            ):
                raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.candidate_pr_does_not_match_current_github_evidence'))
            if key[1] in snapshot.get("pull_request_numbers", []) or (
                repository,
                key[0],
                key[1],
            ) in by_item:
                raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.candidate_pr_must_not_also_be_recorded_as_reviewed_input'))
            current.pop(key)
            exclusion = {
                "repository": repository,
                "pull_request": candidate_pr,
                "head_sha": candidate_head,
                "state": candidate_state,
                "reason": t('maintenance.audit_ecosystem_live.exact_current_review_candidate'),
            }

        stored_issues = snapshot.get("issue_numbers")
        stored_pulls = snapshot.get("pull_request_numbers")
        if not isinstance(stored_issues, list) or not isinstance(stored_pulls, list):
            raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.ecosystem_snapshot_numbers_are_invalid_for', v0=repository))
        stored = {
            *(("issue", number) for number in stored_issues),
            *(("pull-request", number) for number in stored_pulls),
        }
        heads = snapshot.get("pull_request_heads")
        if not isinstance(heads, dict):
            raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.pull_request_heads_are_missing_for', v0=repository))
        for key in sorted(stored):
            if (repository, key[0], key[1]) not in by_item:
                raise EcosystemAuditError(
                    t('maintenance.audit_ecosystem_live.ecosystem_snapshot_item_has_no_ledger_entry', v0=repository, v1=key[0], v2=key[1])
                )

        # Default mode sets aside pull requests merged after the snapshot; the
        # post-merge push run for a review candidate is the canonical case.
        merged_after: list[int] = []
        if not strict:
            for key in sorted(current):
                item = current[key]
                if key[0] != "pull-request" or not item.get("merged_at"):
                    continue
                merged_on = _timestamp_date(
                    item["merged_at"], t('maintenance.audit_ecosystem_live.github_pull_request_merged_at', v0=repository, v1=key[1])
                )
                created_on = _timestamp_date(
                    item["created_at"], t('maintenance.audit_ecosystem_live.github_pull_request_created_at', v0=repository, v1=key[1])
                )
                if merged_on > observed_at and (key in stored or created_on > observed_at):
                    current.pop(key)
                    merged_after.append(key[1])
                    findings.append(
                        {
                            **_finding(
                                "merged_after_snapshot",
                                repository,
                                key,
                                {"merged_at": item["merged_at"], "recorded": key in stored},
                            ),
                            "message": (
                                t('maintenance.audit_ecosystem_live.pull_request_merged_after_the_snapshot_is_set_aside', v0=repository, v1=key[1])
                            ),
                        }
                    )

        extra = sorted(stored - set(current) - {("pull-request", n) for n in merged_after})
        if extra:
            raise EcosystemAuditError(
                t('maintenance.audit_ecosystem_live.ledger_records_items_github_does_not_serve_for_extra', v0=repository, v1=extra)
            )

        unreviewed: list[tuple[str, int]] = []
        for key in sorted(set(current) - stored):
            item = current[key]
            created_on = _timestamp_date(
                item.get("created_at"), t('maintenance.audit_ecosystem_live.github_tracker_item_created_at', v0=repository, v1=key[1])
            )
            if created_on <= observed_at:
                raise EcosystemAuditError(
                    t('maintenance.audit_ecosystem_live.live_tracker_item_predates_the_snapshot_and_is_not_recorded_created', v0=repository, v1=key[0], v2=key[1], v3=item['created_at'])
                )
            unreviewed.append(key)
            report(
                _finding("unreviewed", repository, key, {"created_at": item["created_at"]}),
                t('maintenance.audit_ecosystem_live.live_ecosystem_coverage_mismatch_for_unreviewed_created', v0=repository, v1=key[0], v2=key[1], v3=item['created_at']),
            )

        reviewed_keys = sorted(set(current) & stored)
        for key in reviewed_keys:
            item = current[key]
            if key[0] == "pull-request" and heads.get(str(key[1])) != item["head_sha"]:
                report(
                    _finding(
                        "head_drift",
                        repository,
                        key,
                        {"recorded_head": heads.get(str(key[1])), "live_head": item["head_sha"]},
                    ),
                    t('maintenance.audit_ecosystem_live.live_pull_request_head_drift_for', v0=repository, v1=key[1]),
                )
            entry = by_item[(repository, key[0], key[1])]
            for field in ("title", "state", "url"):
                if entry.get(field) != item.get(field):
                    report(
                        _finding(
                            "metadata_drift",
                            repository,
                            key,
                            {"field": field, "recorded": entry.get(field), "live": item.get(field)},
                        ),
                        t('maintenance.audit_ecosystem_live.live_tracker_metadata_drift_for', v0=repository, v1=key[0], v2=key[1], v3=field),
                    )

        repository_findings = [f for f in findings if f["repository"] == repository]
        results[repository] = {
            "issue_count": sum(1 for kind, _ in current if kind == "issue"),
            "pull_request_count": sum(1 for kind, _ in current if kind == "pull-request"),
            "unreviewed": [f"{kind}/{number}" for kind, number in unreviewed],
            "merged_after_snapshot": merged_after,
            "status": "reconciled-with-findings" if repository_findings else "reconciled",
        }

    if candidate_repository is not None and exclusion is None:
        raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.candidate_repository_was_outside_the_audited_scope'))
    return {
        "status": "pass",
        "mode": "strict" if strict else "default",
        "ledger_reviewed_at": ledger.get("reviewed_at"),
        "repositories": results,
        "findings": findings,
        "candidate_exclusion": exclusion,
    }


def _candidate_from_event(path: str | None) -> tuple[str | None, int | None, str | None]:
    if not path:
        return None, None, None
    try:
        event = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.github_event_payload_is_missing_or_invalid')) from exc
    pull = event.get("pull_request") if isinstance(event, dict) else None
    repository = event.get("repository") if isinstance(event, dict) else None
    if not isinstance(pull, dict):
        return None, None, None
    full_name = repository.get("full_name") if isinstance(repository, dict) else None
    head = pull.get("head")
    return full_name, pull.get("number"), head.get("sha") if isinstance(head, dict) else None


def _candidate_from_commit(
    fetch: Callable[[str], Any], repository: str, sha: str | None
) -> tuple[str | None, int | None, str | None, str]:
    """Identify the pull request that produced ``sha`` on a non-PR run.

    A branch head matches the open pull request whose head is ``sha``; a merge
    commit matches the merged pull request whose ``merge_commit_sha`` is
    ``sha``. Anything else has no candidate, so every live item must be
    recorded.
    """

    if not sha or not _SHA.fullmatch(sha):
        return None, None, None, "open"
    encoded = quote(repository, safe="/")
    value = fetch(f"repos/{encoded}/commits/{sha}/pulls?per_page=100")
    if not isinstance(value, list):
        raise EcosystemAuditError(t('maintenance.audit_ecosystem_live.github_commit_pull_listing_is_invalid_for', v0=repository))
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("number"), int):
            continue
        head = item.get("head") if isinstance(item.get("head"), dict) else {}
        head_sha = head.get("sha")
        if head_sha == sha and item.get("state") == "open":
            return repository, item["number"], sha, "open"
        if item.get("merge_commit_sha") == sha and item.get("merged_at") and _SHA.fullmatch(
            str(head_sha)
        ):
            return repository, item["number"], head_sha, "merged"
    return None, None, None, "open"


def _emit_warnings(findings: list[dict[str, Any]]) -> None:
    prefix = "::warning::" if os.environ.get("GITHUB_ACTIONS") else t("maintenance.audit_ecosystem_live.warning_prefix")
    for finding in findings:
        print(t('maintenance.audit_ecosystem_live.ecosystem_live_audit', v0=prefix, v1=finding['message']), file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    with locale_scope(cli_locale(argv)):
        return _main(argv)


def _main(argv: list[str] | None = None) -> int:
    parser = LocaleArgumentParser(description=t('maintenance.audit_ecosystem_live.reconcile_the_frozen_ecosystem_ledger_with_current_github_tracker_state_the'))
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path("control-plane/manifests/ecosystem-dispositions.json"),
        help=t("maintenance.audit_ecosystem_live.ledger_help"),
    )
    parser.add_argument("--public-only", action="store_true", help=t("maintenance.audit_ecosystem_live.public_only_help"))
    parser.add_argument(
        "--strict",
        action="store_true",
        help=t('maintenance.audit_ecosystem_live.fail_on_every_drift_or_unreviewed_item_instead_of_reporting_findings'),
    )
    parser.add_argument("--event-path", default=os.environ.get("GITHUB_EVENT_PATH"), help=t("maintenance.audit_ecosystem_live.event_help"))
    parser.add_argument("--candidate-repository", help=t("maintenance.audit_ecosystem_live.candidate_repository_help"))
    parser.add_argument("--candidate-pr", type=int, help=t("maintenance.audit_ecosystem_live.candidate_pr_help"))
    parser.add_argument("--candidate-head", help=t("maintenance.audit_ecosystem_live.candidate_head_help"))
    parser.add_argument("--json", action="store_true", help=t("maintenance.audit_ecosystem_live.json_help"))
    args = parser.parse_args(argv)

    try:
        ledger = _load_ledger(args.ledger)
        repositories = (PUBLIC_REPOSITORY,) if args.public_only else (
            PUBLIC_REPOSITORY,
            CANONICAL_REPOSITORY,
        )
        fetch = _github_fetcher(os.environ.get("GITHUB_TOKEN"))
        live = {repository: collect_live_repository(repository, fetch) for repository in repositories}
        candidate_repository, candidate_pr, candidate_head = _candidate_from_event(args.event_path)
        candidate_state = "open"
        explicit_candidate = (
            args.candidate_repository,
            args.candidate_pr,
            args.candidate_head,
        )
        if any(value is not None for value in explicit_candidate):
            candidate_repository, candidate_pr, candidate_head = explicit_candidate
        elif candidate_pr is None:
            run_repository = os.environ.get("GITHUB_REPOSITORY")
            if run_repository in repositories:
                candidate_repository, candidate_pr, candidate_head, candidate_state = (
                    _candidate_from_commit(fetch, run_repository, os.environ.get("GITHUB_SHA"))
                )
        if candidate_repository not in repositories:
            candidate_repository = candidate_pr = candidate_head = None
        result = reconcile_live(
            ledger,
            live,
            repositories=repositories,
            candidate_repository=candidate_repository,
            candidate_pr=candidate_pr,
            candidate_head=candidate_head,
            candidate_state=candidate_state,
            strict=args.strict,
        )
    except EcosystemAuditError as exc:
        print(t('maintenance.audit_ecosystem_live.ecosystem_live_audit_failed', v0=exc), file=sys.stderr)
        return 1

    _emit_warnings(result["findings"])
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        counts = ", ".join(
            t("maintenance.audit_ecosystem_live.repository_counts", repository=repo, issues=value['issue_count'], pulls=value['pull_request_count'])
            for repo, value in result["repositories"].items()
        )
        print(
            t('maintenance.audit_ecosystem_live.ecosystem_live_audit_passed_in_mode_findings', v0=result['mode'], v1=counts, v2=len(result['findings']))
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
