"""Deterministic, privacy-aware renderers for validated report bundles.

JSON remains the canonical artifact.  This module produces human-readable
views without recalculating scores, loading remote assets, or embedding the
source bundle in the output.
"""

from __future__ import annotations

import base64
import html
import importlib
import io
import json
import os
import re
import stat
import tempfile
from pathlib import Path
from typing import Any, Mapping

from .contracts import ContractError, validate_contract
from .i18n import catalog, label, locale_scope, resolve_locale, t


class ReportRenderError(ValueError):
    """Raised when a report cannot be rendered or written safely."""


class PDFDependencyError(ReportRenderError):
    """Raised when the optional PDF renderer is unavailable."""


_EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])")
_BEARER_RE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+")
_SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(access[_-]?token|refresh[_-]?token|api[_-]?key|client[_-]?secret|"
    r"password|passwd|authorization|cookie)\s*([:=])\s*([^\s&;,]+)"
)
_SENSITIVE_KEY_RE = re.compile(
    r"(?i)(^|[_-])(access[_-]?token|refresh[_-]?token|api[_-]?key|client[_-]?secret|"
    r"password|passwd|authorization|cookie|set[_-]?cookie|email|phone)([_-]|$)"
)
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

def _display_label(group: str, value: Any, *, locale: str | None = None) -> str:
    """Translate known labels only; preserve unknown/custom values as data."""

    selected = resolve_locale(locale)
    key = f"label.{group}.{value}"
    if key in catalog(selected):
        return label(group, value, locale=selected)
    # Preserve the legacy English renderer's casing without translating prose.
    if selected == "en":
        return str(value).replace("_", " ").title() if group == "extension_field" else str(value).title()
    return str(value)


def _extension_value(key: str, value: Any, *, locale: str) -> str:
    if locale != "en" and key in {"confidence", "severity", "status"}:
        return label("extension_status" if key == "status" else key, value, locale=locale)
    return _text(value)


def _redact_text(value: str) -> str:
    value = _CONTROL_CHARS_RE.sub("", value).replace("\r\n", "\n").replace("\r", "\n")
    value = _BEARER_RE.sub("Bearer [REDACTED]", value)
    value = _SECRET_ASSIGNMENT_RE.sub(lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]", value)
    return _EMAIL_RE.sub("[REDACTED EMAIL]", value)


def _redact_value(value: Any, *, key: str | None = None) -> Any:
    if key is not None and _SENSITIVE_KEY_RE.search(key):
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return {str(item_key): _redact_value(item, key=str(item_key)) for item_key, item in value.items()}
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, tuple):
        return [_redact_value(item) for item in value]
    if isinstance(value, str):
        return _redact_text(value)
    return value


def _text(value: Any) -> str:
    if value is None:
        return ""
    return _redact_text(str(value)).replace("\n", " ").strip()


def _md(value: Any) -> str:
    """Make untrusted text inert in a single Markdown paragraph."""

    text = _text(value)
    return re.sub(r"([\\`*_{}\[\]()<>#+.!|>-])", r"\\\1", text)


def _html(value: Any) -> str:
    return html.escape(_text(value), quote=True)


def _canonical_json(value: Any) -> str:
    return json.dumps(_redact_value(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _validated_bundle(bundle: Mapping[str, Any], *, locale: str | None = None) -> Mapping[str, Any]:
    with locale_scope(locale):
        try:
            validate_contract("report-bundle", bundle)
        except ContractError as exc:
            raise ReportRenderError(t("report.invalid_bundle", error=exc)) from exc
    for field in ("contradictions", "actions"):
        if field in bundle and not isinstance(bundle[field], list):
            raise ReportRenderError(t("report.invalid_array", locale=locale, field=field))
    return bundle


def _score_text(score: Any, *, locale: str | None = None) -> str:
    if score is None:
        return t("report.not_scored", locale=locale)
    return f"{float(score):.2f} / 100"


def _coverage_text(coverage: Any) -> str:
    return f"{float(coverage):.2f}%"


def _controls(bundle: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(control["control_id"]): control for control in bundle["control_definitions"]}


def _findings(bundle: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return sorted(bundle["findings"], key=lambda finding: str(finding["control_id"]))


def _categories(bundle: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return sorted(bundle["scoring"]["categories"], key=lambda category: str(category.get("category", "")))


def _extension_item_text(item: Any, *, locale: str | None = None) -> str:
    locale = resolve_locale(locale)
    if isinstance(item, str):
        return _text(item)
    if isinstance(item, Mapping):
        preferred = ("summary", "title", "action", "claim", "description", "recommendation")
        headline = next((_text(item[key]) for key in preferred if item.get(key)), "")
        details = [
            f"{_display_label('extension_field', key, locale=locale)}: {_extension_value(str(key), value, locale=locale)}"
            for key, value in sorted(item.items(), key=lambda pair: str(pair[0]))
            if key not in preferred and value not in (None, "", [], {})
        ]
        if headline and details:
            return f"{headline} ({'; '.join(details)})"
        return headline or "; ".join(details) or _canonical_json(item)
    return _text(item)


def _actions(bundle: Mapping[str, Any]) -> list[Any]:
    explicit = list(bundle.get("actions", []))
    if explicit:
        return explicit
    return [
        {
            "action": finding["recommendation"],
            "confidence": finding["confidence"],
            "control_id": finding["control_id"],
        }
        for finding in _findings(bundle)
        if finding["status"] in {"fail", "unknown"} and _text(finding.get("recommendation"))
    ]


def render_markdown(bundle: Mapping[str, Any], *, locale: str | None = None) -> str:
    """Render a validated ReportBundle without translating supplied free text."""

    locale = resolve_locale(locale)
    bundle = _validated_bundle(bundle, locale=locale)
    manifest = bundle["run_manifest"]
    snapshot = bundle["account_snapshot"]
    scoring = bundle["scoring"]
    controls = _controls(bundle)
    completeness = str(manifest["completeness"])
    score_status = str(scoring["status"])
    account = snapshot["account"]

    def message(key: str, **values: Any) -> str:
        return t(f"report.{key}", locale=locale, **values)

    def display(group: str, value: Any) -> str:
        return _md(_display_label(group, value, locale=locale))

    completeness_text = label("completeness", completeness, locale=locale)
    score_status_text = label("score_status", score_status, locale=locale)
    lines = [
        f"# {message('title')}",
        "",
        f"> {message('completeness')}: **{completeness_text}** · {message('evidence_status')}: **{score_status_text}**",
        "",
        f"## {message('run_summary')}",
        "",
        f"- {message('run_id')}: {_md(manifest['run_id'])}",
        f"- {message('started')}: {_md(manifest['started_at'])}",
        f"- {message('platform')}: {_md(str(account['platform']).title())}",
        f"- {message('account')}: {_md(account.get('name') or account['account_id'])}",
        f"- {message('window')}: {message('window_range', start=_md(snapshot['window']['start']), end=_md(snapshot['window']['end']))}",
        f"- {message('privacy_class')}: {display('privacy_class', manifest['privacy_class'])}",
        "",
        f"## {message('decision_status')}",
        "",
        f"- {message('completeness')}: **{completeness_text}**",
        f"- {message('evidence_status')}: **{score_status_text}**",
        f"- {message('health_score')}: **{_score_text(scoring['health_score'], locale=locale)}**",
        f"- {message('evidence_coverage')}: **{_coverage_text(scoring['evidence_coverage'])}**",
    ]
    warning_keys = []
    if completeness != "complete":
        warning_keys.append("warning_incomplete")
    if score_status == "provisional":
        warning_keys.append("warning_provisional")
    elif score_status == "insufficient_evidence":
        warning_keys.append("warning_insufficient")
    for key in warning_keys:
        lines.extend(("", f"> {message('warning').upper()}: {message(key)}"))

    lines.extend(("", f"## {message('category_health')}", ""))
    categories = _categories(bundle)
    if categories:
        for category in categories:
            lines.append(
                f"- **{display('category', category.get('category', 'uncategorized'))}:** "
                + message("category_score", score=_score_text(category.get("health_score"), locale=locale),
                          coverage=_coverage_text(category.get("evidence_coverage", 0)))
            )
    else:
        lines.append(message("no_categories"))

    lines.extend(("", f"## {message('findings')}", ""))
    findings = _findings(bundle)
    if not findings:
        lines.append(message("no_findings"))
    for finding in findings:
        control = controls.get(str(finding["control_id"]), {})
        heading = (
            f"### [{display('finding_status', finding['status'])}] "
            f"{_md(finding['control_id'])} — {display('category', control.get('category', 'uncategorized'))}"
        )
        lines.extend(
            (
                heading,
                "",
                f"- {message('severity')}: {display('severity', control.get('severity', 'not specified'))}",
                f"- {message('confidence')}: {display('confidence', finding['confidence'])}",
                f"- {message('source_classification')}: {display('source_classification', finding.get('source_classification', 'not specified'))}",
                "",
                f"**{message('observation')}:** {_md(finding['observation']) or message('not_supplied')}",
                "",
                f"**{message('diagnosis')}:** {_md(finding['diagnosis']) or message('not_supplied')}",
                "",
                f"**{message('recommendation')}:** {_md(finding['recommendation']) or message('no_action')}",
                "",
                f"**{message('evidence')}:**",
                "",
            )
        )
        if finding["evidence"]:
            for index, evidence in enumerate(finding["evidence"], start=1):
                lines.extend((f"{index}.", "", f"        {_canonical_json(evidence)}", ""))
        else:
            lines.extend((message("no_evidence"), ""))

    lines.extend((f"## {message('contradictions')}", ""))
    contradictions = list(bundle.get("contradictions", []))
    if contradictions:
        lines.extend(f"- {_md(_extension_item_text(item, locale=locale))}" for item in contradictions)
    else:
        lines.append(message("no_contradictions"))

    lines.extend(("", f"## {message('actions')}", ""))
    actions = _actions(bundle)
    if actions:
        lines.extend(f"{index}. {_md(_extension_item_text(item, locale=locale))}" for index, item in enumerate(actions, start=1))
    else:
        lines.append(message("no_actions"))

    lines.extend(("", "---", "", message("footer"), ""))
    return "\n".join(lines)


_HTML_STYLE = """
:root{color-scheme:light;--ink:#172033;--muted:#596579;--line:#d8dee9;--paper:#fff;--soft:#f5f7fa;--ok:#18794e;--warn:#9a6700;--bad:#c62828}
*{box-sizing:border-box}body{margin:0;background:#eef1f5;color:var(--ink);font:15px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
main{max-width:960px;margin:32px auto;padding:40px;background:var(--paper);box-shadow:0 8px 30px #17203318}h1,h2,h3{line-height:1.2}h1{margin-top:0}h2{margin-top:2rem;border-bottom:1px solid var(--line);padding-bottom:.4rem}h3{margin-top:1.5rem}.banner{padding:12px 16px;border-left:5px solid var(--ok);background:var(--soft);font-weight:700}.banner.partial,.banner.failed,.banner.provisional{border-color:var(--warn)}.banner.insufficient_evidence{border-color:var(--bad)}.warning{padding:10px 14px;background:#fff6d6;border:1px solid #e9c46a}.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}.metric{padding:14px;background:var(--soft);border:1px solid var(--line)}.metric strong{display:block;font-size:1.25rem}.meta{display:grid;grid-template-columns:max-content 1fr;gap:4px 16px}.finding{padding:18px;margin:14px 0;border:1px solid var(--line);border-radius:6px}.status-pass{border-left:5px solid var(--ok)}.status-fail{border-left:5px solid var(--bad)}.status-unknown{border-left:5px solid var(--warn)}pre{overflow-wrap:anywhere;white-space:pre-wrap;background:var(--soft);padding:10px;border:1px solid var(--line)}dt{font-weight:700}dd{margin:0 0 10px}footer{margin-top:2rem;padding-top:1rem;border-top:1px solid var(--line);color:var(--muted)}@media print{body{background:#fff}main{box-shadow:none;margin:0;max-width:none}}
""".strip()


def render_html(bundle: Mapping[str, Any], *, locale: str | None = None) -> str:
    """Render a validated ReportBundle as self-contained deterministic HTML."""

    locale = resolve_locale(locale)
    bundle = _validated_bundle(bundle, locale=locale)
    manifest = bundle["run_manifest"]
    snapshot = bundle["account_snapshot"]
    scoring = bundle["scoring"]
    controls = _controls(bundle)
    completeness = str(manifest["completeness"])
    score_status = str(scoring["status"])
    account = snapshot["account"]

    def message(key: str, **values: Any) -> str:
        return _html(t(f"report.{key}", locale=locale, **values))

    def display(group: str, value: Any) -> str:
        return _html(_display_label(group, value, locale=locale))

    warnings: list[str] = []
    if completeness != "complete":
        warnings.append(message("warning_incomplete"))
    if score_status == "provisional":
        warnings.append(message("warning_provisional"))
    elif score_status == "insufficient_evidence":
        warnings.append(message("warning_insufficient"))

    category_html = "".join(
        "<li><strong>{}</strong>: {}</li>".format(
            display("category", category.get("category", "uncategorized")),
            message("category_score", score=_score_text(category.get("health_score"), locale=locale),
                    coverage=_coverage_text(category.get("evidence_coverage", 0))),
        )
        for category in _categories(bundle)
    ) or f"<li>{message('no_categories')}</li>"

    finding_parts: list[str] = []
    for finding in _findings(bundle):
        control = controls.get(str(finding["control_id"]), {})
        evidence = "".join(f"<pre>{html.escape(_canonical_json(item))}</pre>" for item in finding["evidence"])
        if not evidence:
            evidence = f"<p>{message('no_evidence')}</p>"
        status = str(finding["status"])
        finding_parts.append(
            f'<article class="finding status-{html.escape(status)}">'
            f"<h3>[{display('finding_status', status)}] {_html(finding['control_id'])} — "
            f"{display('category', control.get('category', 'uncategorized'))}</h3>"
            "<dl>"
            f"<dt>{message('severity')}</dt><dd>{display('severity', control.get('severity', 'not specified'))}</dd>"
            f"<dt>{message('confidence')}</dt><dd>{display('confidence', finding['confidence'])}</dd>"
            f"<dt>{message('source_classification')}</dt><dd>{display('source_classification', finding.get('source_classification', 'not specified'))}</dd>"
            f"<dt>{message('observation')}</dt><dd>{_html(finding['observation']) or message('not_supplied')}</dd>"
            f"<dt>{message('diagnosis')}</dt><dd>{_html(finding['diagnosis']) or message('not_supplied')}</dd>"
            f"<dt>{message('recommendation')}</dt><dd>{_html(finding['recommendation']) or message('no_action')}</dd>"
            f"</dl><h4>{message('evidence')}</h4>{evidence}</article>"
        )
    findings_html = "".join(finding_parts) or f"<p>{message('no_findings')}</p>"

    contradictions = list(bundle.get("contradictions", []))
    contradictions_html = (
        "<ul>" + "".join(f"<li>{_html(_extension_item_text(item, locale=locale))}</li>" for item in contradictions) + "</ul>"
        if contradictions
        else f"<p>{message('no_contradictions')}</p>"
    )
    actions = _actions(bundle)
    actions_html = (
        "<ol>" + "".join(f"<li>{_html(_extension_item_text(item, locale=locale))}</li>" for item in actions) + "</ol>"
        if actions
        else f"<p>{message('no_actions')}</p>"
    )
    warnings_html = "".join(f'<p class="warning"><strong>{message("warning")}:</strong> {item}</p>' for item in warnings)

    return (
        f'<!doctype html>\n<html lang="{locale}"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{message('title')}</title><style>" + _HTML_STYLE + "</style></head><body><main>"
        f"<h1>{message('title')}</h1>"
        f'<p class="banner {html.escape(completeness)} {html.escape(score_status)}">{message("completeness")}: '
        f"{display('completeness', completeness)} · {message('evidence_status')}: {display('score_status', score_status)}</p>"
        f'<h2>{message("run_summary")}</h2><dl class="meta">'
        f"<dt>{message('run_id')}</dt><dd>{_html(manifest['run_id'])}</dd><dt>{message('started')}</dt><dd>{_html(manifest['started_at'])}</dd>"
        f"<dt>{message('platform')}</dt><dd>{_html(str(account['platform']).title())}</dd>"
        f"<dt>{message('account')}</dt><dd>{_html(account.get('name') or account['account_id'])}</dd>"
        f"<dt>{message('window')}</dt><dd>{message('window_range', start=snapshot['window']['start'], end=snapshot['window']['end'])}</dd>"
        f"<dt>{message('privacy_class')}</dt><dd>{display('privacy_class', manifest['privacy_class'])}</dd></dl>"
        f'<h2>{message("decision_status")}</h2><div class="metrics">'
        f'<div class="metric">{message("completeness")}<strong>{display("completeness", completeness)}</strong></div>'
        f'<div class="metric">{message("evidence_status")}<strong>{display("score_status", score_status)}</strong></div>'
        f'<div class="metric">{message("health_score")}<strong>{_html(_score_text(scoring["health_score"], locale=locale))}</strong></div>'
        f'<div class="metric">{message("evidence_coverage")}<strong>{_html(_coverage_text(scoring["evidence_coverage"]))}</strong></div></div>'
        + warnings_html
        + f"<h2>{message('category_health')}</h2><ul>{category_html}</ul><h2>{message('findings')}</h2>{findings_html}"
        + f"<h2>{message('contradictions')}</h2>{contradictions_html}<h2>{message('actions')}</h2>{actions_html}"
        + f"<footer>{message('footer')}</footer>"
        + "</main></body></html>\n"
    )


_CJK_RE = re.compile(r"[\u2e80-\u9fff\uac00-\ud7af\uf900-\ufaff\uff00-\uffef\U00020000-\U000323af]")
_FONT_SUFFIXES = {".ttf", ".otf", ".ttc", ".otc"}
_MAX_FONT_BYTES = 64 * 1024 * 1024


def _system_font_roots() -> tuple[Path, ...]:
    """Only OS font locations, never a directory supplied in report data."""

    roots = (
        Path("/System/Library/Fonts"), Path("/Library/Fonts"), Path.home() / "Library/Fonts",
        Path("/usr/share/fonts"), Path("/usr/local/share/fonts"),
        Path.home() / ".fonts", Path.home() / ".local/share/fonts",
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts",
    )
    return tuple(root.resolve() for root in roots if root.is_dir())


def _validated_font_path(font: str | Path, *, locale: str | None = None) -> Path:
    path = Path(font)
    try:
        if not path.is_absolute() or path.suffix.lower() not in _FONT_SUFFIXES:
            raise ValueError
        resolved = path.resolve(strict=True)
        if not any(resolved.is_relative_to(root) for root in _system_font_roots()):
            raise ValueError
        if not resolved.is_file() or not 0 < resolved.stat().st_size <= _MAX_FONT_BYTES:
            raise ValueError
        return resolved
    except (OSError, ValueError, RuntimeError) as exc:
        raise PDFDependencyError(t("report.font_invalid", locale=locale)) from exc


def _system_font_candidates() -> list[Path]:
    candidates: set[Path] = set()
    for root in _system_font_roots():
        for directory, _subdirs, files in os.walk(root, followlinks=False):
            for name in files:
                if Path(name).suffix.lower() in _FONT_SUFFIXES:
                    candidates.add(Path(directory) / name)
    # Prefer common CJK families but verify actual coverage, not the filename.
    names = ("notosanscjk", "notoserifcjk", "sourcehan", "pingfang", "songti", "heiti", "msyh", "simsun", "arial unicode")
    return sorted(candidates, key=lambda path: (not any(name in path.name.lower() for name in names), str(path)))


def _load_system_font(
    text: str, *, font: str | Path | None = None, locale: str | None = None,
    true_type_only: bool = False,
) -> bytes | None:
    """Return a verified standalone font, or fail before rendering CJK boxes.

    The caller may explicitly name an installed system font. Report content
    cannot choose any file. Font data is loaded once and passed as bytes so the
    PDF renderer never receives filesystem URLs or arbitrary fetch authority.
    """

    locale = resolve_locale(locale)
    explicit = _validated_font_path(font, locale=locale) if font is not None else None
    if explicit is None and not _CJK_RE.search(text):
        return None
    try:
        ttlib = importlib.import_module("fontTools.ttLib")
    except (ImportError, OSError) as exc:
        raise PDFDependencyError(t("report.font_dependency", locale=locale)) from exc
    required = {ord(character) for character in text if not character.isspace() and ord(character) >= 32}
    for candidate in [explicit] if explicit is not None else _system_font_candidates():
        collection = None
        faces = []
        try:
            path = _validated_font_path(candidate, locale=locale)
            content = path.read_bytes()
            if len(content) > _MAX_FONT_BYTES:
                continue
            if content.startswith(b"ttcf"):
                collection = ttlib.TTCollection(io.BytesIO(content), lazy=False)
                faces = collection.fonts
            else:
                faces = [ttlib.TTFont(io.BytesIO(content), lazy=False)]
            for face in faces:
                if true_type_only and "glyf" not in face:
                    continue
                cmap = face.getBestCmap() or {}
                if not required.issubset(cmap) or any(cmap[codepoint] == ".notdef" for codepoint in required):
                    continue
                output = io.BytesIO()
                face.save(output)
                return output.getvalue()
        except (OSError, ValueError, KeyError, ttlib.TTLibError):
            continue
        finally:
            if collection is not None:
                collection.close()
            else:
                for face in faces:
                    face.close()
    raise PDFDependencyError(t("report.font_dependency", locale=locale))


def render_pdf(
    bundle: Mapping[str, Any], *, locale: str | None = None, font: str | Path | None = None,
) -> bytes:
    """Render PDF bytes through the optional, offline WeasyPrint bridge."""

    locale = resolve_locale(locale)
    source = render_html(bundle, locale=locale)
    explicit_font = _validated_font_path(font, locale=locale) if font is not None else None
    try:
        weasyprint = importlib.import_module("weasyprint")
    except (ImportError, OSError) as exc:
        raise PDFDependencyError(t("report.pdf_dependency", locale=locale)) from exc
    font_bytes = _load_system_font(render_markdown(bundle, locale=locale), font=explicit_font, locale=locale)
    font_url = "data:font/ttf;base64," + base64.b64encode(font_bytes).decode("ascii") if font_bytes else None
    if font_url:
        font_style = (
            f'@font-face{{font-family:"ReportCJK";src:url("{font_url}")}}'
            'body,pre,code{font-family:"ReportCJK",sans-serif}'
        )
        source = source.replace("</style>", font_style + "</style>", 1)

    def fetch_asset(url: str, *args: Any, **kwargs: Any) -> Mapping[str, Any]:
        if font_url is not None and url == font_url:
            return {"string": font_bytes, "mime_type": "font/ttf"}
        raise ReportRenderError(t("report.asset_blocked", locale=locale))

    try:
        result = weasyprint.HTML(string=source, base_url=None, url_fetcher=fetch_asset).write_pdf()
    except Exception as exc:
        raise ReportRenderError(t("report.pdf_failed", locale=locale, error=_text(exc))) from exc
    if not isinstance(result, bytes):
        raise ReportRenderError(t("report.pdf_invalid_result", locale=locale))
    return result


def render_report(
    bundle: Mapping[str, Any], output_format: str, *, locale: str | None = None,
    font: str | Path | None = None,
) -> str | bytes:
    """Render *bundle* to ``markdown``, ``html``, or ``pdf``."""

    normalized = output_format.lower()
    if normalized in {"md", "markdown"}:
        return render_markdown(bundle, locale=locale)
    if normalized == "html":
        return render_html(bundle, locale=locale)
    if normalized == "pdf":
        return render_pdf(bundle, locale=locale, font=font)
    raise ReportRenderError(t("report.invalid_format", locale=locale))


def resolve_report_path(root: str | Path, destination: str | Path) -> Path:
    """Resolve a relative output path beneath *root*, rejecting symlinks."""

    relative = Path(destination)
    if relative.is_absolute() or not relative.name or any(part in {"", ".", ".."} for part in relative.parts):
        raise ReportRenderError(t("report.path_relative"))
    root_path = Path(root)
    root_path.mkdir(parents=True, exist_ok=True)
    root_resolved = root_path.resolve(strict=True)
    if not root_resolved.is_dir():
        raise ReportRenderError(t("report.root_directory"))

    parent = root_resolved
    for part in relative.parts[:-1]:
        candidate = parent / part
        if os.path.lexists(candidate):
            mode = candidate.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise ReportRenderError(t("report.parent_symlink"))
            if not stat.S_ISDIR(mode):
                raise ReportRenderError(t("report.parent_directory"))
        else:
            candidate.mkdir(mode=0o700)
        parent = candidate

    destination_path = parent / relative.name
    if os.path.lexists(destination_path) and stat.S_ISLNK(destination_path.lstat().st_mode):
        raise ReportRenderError(t("report.output_symlink"))
    try:
        parent.resolve(strict=True).relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise ReportRenderError(t("report.path_escape")) from exc
    return destination_path


def atomic_write_report(root: str | Path, destination: str | Path, content: str | bytes) -> Path:
    """Atomically write report content beneath a safe root."""

    output_path = resolve_report_path(root, destination)
    file_descriptor, temporary_name = tempfile.mkstemp(prefix=f".{output_path.name}.", dir=output_path.parent)
    temporary_path = Path(temporary_name)
    try:
        mode = "wb" if isinstance(content, bytes) else "w"
        kwargs = {} if isinstance(content, bytes) else {"encoding": "utf-8", "newline": "\n"}
        with os.fdopen(file_descriptor, mode, **kwargs) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_path, 0o600)
        # Recheck after writing so a swapped parent or destination cannot be
        # silently followed at commit time.
        checked_path = resolve_report_path(root, destination)
        if checked_path.parent.resolve(strict=True) != output_path.parent.resolve(strict=True):
            raise ReportRenderError(t("report.parent_changed"))
        os.replace(temporary_path, checked_path)
        return checked_path
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def write_report_bundle(
    bundle: Mapping[str, Any],
    output_format: str,
    root: str | Path,
    destination: str | Path,
    *,
    locale: str | None = None,
    font: str | Path | None = None,
) -> Path:
    """Validate, render, and atomically write a report bundle."""

    with locale_scope(locale):
        return atomic_write_report(root, destination, render_report(bundle, output_format, font=font))
