"""Pytest configuration for the claude-ads eval harness.

Shared fixtures:
- ``repo_root``        — path to the repo root
- ``check_catalog``    — parsed dict from fixtures/check-catalog.yaml
- ``creative_evals``   — parsed list from evals/creative-evals.json
- ``skill_descriptions`` — installed/generated-view skill descriptions
- ``english_documents_root`` — preserved English Markdown baseline (not repo_root)
- ``english_skill_descriptions`` — English baseline for retained English lexical evals

These are session-scoped to keep test runs fast even as the harness grows.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def check_catalog() -> dict:
    try:
        import yaml
    except ImportError:
        pytest.skip("pyyaml not installed; run `pip install -r requirements-dev.txt`")
    catalog_path = REPO_ROOT / "tests" / "fixtures" / "check-catalog.yaml"
    return yaml.safe_load(catalog_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def creative_evals() -> list[dict]:
    evals_path = REPO_ROOT / "evals" / "creative-evals.json"
    return json.loads(evals_path.read_text(encoding="utf-8"))


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
_DESC_RE = re.compile(r'^description:\s*"(.+?)"\s*$', re.MULTILINE | re.DOTALL)


def _parse_frontmatter(text: str) -> dict:
    """Minimal frontmatter parser — pulls name + description out of a SKILL.md.

    Intentionally tolerant of multi-line descriptions and missing fields so a
    malformed file fails loudly elsewhere (in coverage tests) rather than here.
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = m.group(1)
    out = {}
    name_match = _NAME_RE.search(fm)
    if name_match:
        out["name"] = name_match.group(1).strip()
    desc_match = _DESC_RE.search(fm)
    if desc_match:
        out["description"] = desc_match.group(1).strip()
    return out


def _skill_descriptions(documents_root: Path) -> dict[str, str]:
    """Parse descriptions from one explicit document surface; never fall back."""
    skill_files = [documents_root / "ads" / "SKILL.md"] + sorted(
        (documents_root / "skills").glob("*/SKILL.md")
    )
    result: dict[str, str] = {}
    for path in skill_files:
        fm = _parse_frontmatter(path.read_text(encoding="utf-8"))
        if "name" in fm and "description" in fm:
            result[fm["name"]] = fm["description"]
    return result


@pytest.fixture(scope="session")
def skill_descriptions(repo_root: Path) -> dict[str, str]:
    """Descriptions from actual installed/generated views, not locale resources."""
    return _skill_descriptions(repo_root)


@pytest.fixture(scope="session")
def english_documents_root(repo_root: Path) -> Path:
    """Explicit English baseline for language-dependent regression assertions.

    Manifests, schemas, implementations, and generated Chinese surfaces must still
    use repo_root. A missing baseline is an error, not a reason to skip coverage.
    """
    root = repo_root / "claude_ads_core" / "locales" / "en" / "documents"
    assert (root / "ads" / "SKILL.md").is_file(), "English document baseline is missing"
    return root


@pytest.fixture(scope="session")
def english_skill_descriptions(english_documents_root: Path) -> dict[str, str]:
    """Retain English lexical evaluation independently of Chinese frontmatter."""
    return _skill_descriptions(english_documents_root)
