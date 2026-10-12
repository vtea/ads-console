from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence

from claude_ads_core import load_control_registry
from claude_ads_core.control_registry import ControlRegistry


@lru_cache(maxsize=4)
def registry(repo_root: str) -> ControlRegistry:
    return load_control_registry(Path(repo_root))


def control_definitions(repo_root: Path, platform: str) -> list[dict[str, Any]]:
    return [dict(item) for item in registry(str(repo_root)).controls_for(platform)]


def known_control_ids(repo_root: Path, platform: str) -> set[str]:
    return {item["control_id"] for item in control_definitions(repo_root, platform)}


def score(repo_root: Path, platform: str, findings: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    result = registry(str(repo_root)).score_platform(platform, findings)
    return {
        "health_score": result.health_score,
        "evidence_coverage": result.evidence_coverage,
        "status": result.status,
        "categories": [c.to_dict() for c in result.categories],
    }
