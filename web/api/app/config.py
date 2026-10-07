"""Environment-driven settings. Secret values are read from the environment and never persisted."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    data_dir: Path
    database_url: str
    session_secret: str
    locale: str
    cors_origins: tuple[str, ...]
    worker_model: str
    worker_max_tokens: int
    run_token_budget: int
    meta_graph_api_version: str
    anthropic_api_key_ref: str = "ANTHROPIC_API_KEY"
    max_upload_bytes: int = 25 * 1024 * 1024
    worker_concurrency: int = 3
    extra: dict[str, str] = field(default_factory=dict)

    @property
    def runs_root(self) -> Path:
        return self.data_dir / ".claude-ads" / "runs"

    @property
    def uploads_root(self) -> Path:
        return self.data_dir / "uploads"

    def anthropic_api_key(self) -> str | None:
        return _env(self.anthropic_api_key_ref)


def load_settings() -> Settings:
    here = Path(__file__).resolve().parents[1]
    repo_root = Path(_env("CLAUDE_ADS_REPO_ROOT", str(here.parents[1]))).resolve()
    data_dir = Path(_env("CLAUDE_ADS_DATA_DIR", str(here / "data"))).resolve()
    database_url = _env("CLAUDE_ADS_DATABASE_URL", f"sqlite:///{(data_dir / 'claude-ads-web.db').as_posix()}")
    session_secret = _env("CLAUDE_ADS_SESSION_SECRET")
    if not session_secret:
        raise RuntimeError("CLAUDE_ADS_SESSION_SECRET must be set")
    origins = tuple(item.strip() for item in (_env("CLAUDE_ADS_CORS_ORIGINS", "http://localhost:3000") or "").split(",") if item.strip())
    version = _env("META_GRAPH_API_VERSION", "v23.0") or "v23.0"
    return Settings(
        repo_root=repo_root,
        data_dir=data_dir,
        database_url=database_url,
        session_secret=session_secret,
        locale=_env("CLAUDE_ADS_LOCALE", "zh-CN") or "zh-CN",
        cors_origins=origins,
        worker_model=_env("CLAUDE_ADS_WORKER_MODEL", "claude-sonnet-5-5") or "claude-sonnet-5-5",
        worker_max_tokens=int(_env("CLAUDE_ADS_WORKER_MAX_TOKENS", "8000") or 8000),
        run_token_budget=int(_env("CLAUDE_ADS_RUN_TOKEN_BUDGET", "200000") or 200000),
        meta_graph_api_version=version,
    )
