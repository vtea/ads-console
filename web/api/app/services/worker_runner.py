"""Claude-backed audit worker. The Anthropic SDK reads its key from the environment itself.

Only the conductor (RunService) writes artifacts; this module returns validated
orchestration-result payloads and finding lists.
"""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from claude_ads_core.contracts import ContractError, validate_contract

from ..prompts.render import render_system_prompt, render_user_message
from ..security.redact import redact_mapping, sanitize_error
from .lifecycle import now_iso

FINDING_KEYS = ("control_id", "status", "evidence", "confidence", "observation", "diagnosis", "recommendation")


class WorkerClient(Protocol):
    def complete(self, *, model: str, system: str, user: str, max_tokens: int) -> tuple[str, int, int]:
        """Return (text, input_tokens, output_tokens)."""


class AnthropicWorkerClient:
    def __init__(self) -> None:
        import anthropic

        self._client = anthropic.Anthropic()

    def complete(self, *, model: str, system: str, user: str, max_tokens: int) -> tuple[str, int, int]:
        response = self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
        usage = getattr(response, "usage", None)
        return text, int(getattr(usage, "input_tokens", 0) or 0), int(getattr(usage, "output_tokens", 0) or 0)


@dataclass
class WorkerOutcome:
    status: str
    findings: list[dict[str, Any]] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)
    recovery_hints: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    attempts: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    raw_summary: str = ""


def _extract_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    fence = re.match(r"^```(?:json)?\s*([\s\S]*?)\s*```$", stripped)
    if fence:
        stripped = fence.group(1)
    start, end = stripped.find("{"), stripped.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in worker output")
    payload = json.loads(stripped[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("worker output is not a JSON object")
    return payload


def _normalize_findings(items: Any, known_controls: set[str]) -> tuple[list[dict[str, Any]], list[str]]:
    findings: list[dict[str, Any]] = []
    problems: list[str] = []
    if not isinstance(items, list):
        raise ValueError("findings must be a list")
    for index, raw in enumerate(items):
        if not isinstance(raw, dict):
            problems.append(f"findings[{index}] is not an object")
            continue
        finding = {key: raw.get(key) for key in FINDING_KEYS}
        finding["schema_version"] = "1.0.0"
        finding["evidence"] = [item for item in (finding.get("evidence") or []) if isinstance(item, dict)]
        for key in ("observation", "diagnosis", "recommendation"):
            finding[key] = str(finding.get(key) or "")
        if raw.get("source_classification") in {"evidence_based", "practitioner", "contested", "folklore"}:
            finding["source_classification"] = raw["source_classification"]
        if finding.get("status") in {"pass", "fail"} and not finding["evidence"]:
            finding["status"] = "unknown"
            finding["diagnosis"] = (finding["diagnosis"] + " [降级为 unknown：缺少证据]").strip()
        if finding.get("control_id") not in known_controls:
            problems.append(f"findings[{index}] unknown control {finding.get('control_id')!r} dropped")
            continue
        try:
            validate_contract("finding", finding)
        except ContractError as exc:
            problems.append(f"findings[{index}] invalid: {sanitize_error(exc)}")
            continue
        findings.append(redact_mapping(finding))
    return findings, problems


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(str(item) for item in value if str(item).strip()))


class WorkerRunner:
    def __init__(self, client: WorkerClient, *, model: str, max_tokens: int, token_budget: int, concurrency: int = 3) -> None:
        self._client = client
        self._model = model
        self._max_tokens = max_tokens
        self._budget = token_budget
        self._semaphore = asyncio.Semaphore(max(1, min(concurrency, 3)))

    def run_sync(self, *, repo_root: Path, platform: str, snapshot: dict[str, Any], context: dict[str, Any], known_controls: set[str], locale: str) -> WorkerOutcome:
        system = render_system_prompt(repo_root, platform, locale=locale)
        user = render_user_message(json.dumps(snapshot, ensure_ascii=False, sort_keys=True), context)
        outcome = WorkerOutcome(status="failed")
        last_error = ""
        for attempt in (1, 2):
            outcome.attempts = attempt
            try:
                text, tin, tout = self._client.complete(model=self._model, system=system, user=user, max_tokens=self._max_tokens)
            except Exception as exc:  # noqa: BLE001 - provider errors are redacted and surfaced
                last_error = sanitize_error(exc)
                continue
            outcome.tokens_in += tin
            outcome.tokens_out += tout
            if outcome.tokens_in + outcome.tokens_out > self._budget:
                outcome.blockers = ["token budget exceeded"]
                outcome.recovery_hints = ["提高 CLAUDE_ADS_RUN_TOKEN_BUDGET 或缩小审计窗口后重试"]
                return outcome
            try:
                payload = _extract_json(text)
                findings, problems = _normalize_findings(payload.get("findings"), known_controls)
            except (ValueError, json.JSONDecodeError) as exc:
                last_error = sanitize_error(exc)
                continue
            status = payload.get("status") if payload.get("status") in {"ok", "needs_input", "blocked", "failed"} else "ok"
            outcome.status = status
            outcome.findings = findings
            outcome.contradictions = _strings(payload.get("contradictions"))
            outcome.missing_inputs = _strings(payload.get("missing_inputs"))
            outcome.recovery_hints = _strings(payload.get("recovery_hints"))
            if problems:
                outcome.contradictions.extend(f"worker-output: {item}" for item in problems)
            if status != "ok":
                outcome.blockers = outcome.missing_inputs or ["worker returned non-ok status"]
                if not outcome.recovery_hints:
                    outcome.recovery_hints = ["补充缺失输入后重新运行"]
            outcome.raw_summary = f"{len(findings)} findings, {len(problems)} dropped"
            return outcome
        outcome.status = "failed"
        outcome.blockers = [f"worker failed after {outcome.attempts} attempts: {last_error}"]
        outcome.recovery_hints = ["检查 Anthropic 配置与模型名称，然后重试"]
        return outcome

    async def run(self, **kwargs: Any) -> WorkerOutcome:
        async with self._semaphore:
            return await asyncio.to_thread(self.run_sync, **kwargs)


def result_packet(run_id: str, task_id: str, role: str, outcome: WorkerOutcome, output_artifacts: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "artifact_type": "orchestration-result",
        "result_id": f"{task_id}-r{outcome.attempts}",
        "task_id": task_id,
        "run_id": run_id,
        "role": role,
        "created_at": now_iso(),
        "status": outcome.status,
        "output_artifacts": output_artifacts,
        "evidence_refs": [f"finding:{f['control_id']}" for f in outcome.findings],
        "summary": outcome.raw_summary or outcome.status,
        "blockers": outcome.blockers,
        "recovery_hints": outcome.recovery_hints,
        "supersedes": None,
    }
