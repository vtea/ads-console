#!/usr/bin/env python3
"""
Generate professional PDF audit report from markdown audit results.

Produces a client-ready PDF with health score gauge, platform bar charts,
pass/fail distribution chart, formatted tables, and zero overlap.

Usage:
    python generate_report.py audit-results.md
    python generate_report.py audit-results.md --output report.pdf
    python generate_report.py audit-results.md --brand "Client Name"

Dependencies:
    pip install reportlab matplotlib
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import hashlib
import html
import io
import json
import logging
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from url_utils import resolve_output_path, sanitize_error

# Direct script execution also resolves the installed/source core package.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from claude_ads_core.cli_support import LocaleArgumentParser, cli_locale
from claude_ads_core.i18n import catalog, label, locale_scope, resolve_locale, t
from claude_ads_core.reporting import PDFDependencyError, _load_system_font, _redact_text

# Version stamp shown in PDF header/footer. Keep in sync with
# .claude-plugin/plugin.json `version`.
__version__ = "2.0.2"

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, Image, KeepTogether
    )
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    colors = None

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

logger = logging.getLogger("generate_report")

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

C_PRIMARY = colors.HexColor("#1a1a2e") if HAS_REPORTLAB else None
C_ACCENT = colors.HexColor("#0f3460") if HAS_REPORTLAB else None
C_PASS = colors.HexColor("#16a34a") if HAS_REPORTLAB else None
C_WARN = colors.HexColor("#f59e0b") if HAS_REPORTLAB else None
C_FAIL = colors.HexColor("#dc2626") if HAS_REPORTLAB else None
C_LIGHT = colors.HexColor("#f8fafc") if HAS_REPORTLAB else None
C_ROW_ALT = colors.HexColor("#f1f5f9") if HAS_REPORTLAB else None
C_HEADER = colors.HexColor("#1e293b") if HAS_REPORTLAB else None

GRADE_COLORS = {
    "A": "#16a34a", "B": "#22c55e", "C": "#f59e0b",
    "D": "#f97316", "F": "#dc2626",
}

# English-only reports retain their legacy serif fallback. CJK reports must
# pass coverage verification and use an explicit embedded font on every route.
_english_body = "Times-Roman"
if HAS_REPORTLAB:
    for path in (
        "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "C:/Windows/Fonts/times.ttf",
    ):
        if os.path.isfile(path):
            try:
                pdfmetrics.registerFont(TTFont("TimesNewRoman", path))
                _english_body = "TimesNewRoman"
                break
            except Exception:
                pass
_FONT_NAMES = ContextVar("legacy_report_fonts", default=(_english_body, "Times-Bold", "Helvetica-Bold"))
_CHART_FONT_PATH = ContextVar("legacy_chart_font", default=None)


def _font(index: int) -> str:
    return _FONT_NAMES.get()[index]


def _font_text(data, brand_name: str) -> str:
    texts = [brand_name, "•", _report_date(), __version__]
    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                texts.append(str(key))
                visit(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                visit(item)
        elif value is not None:
            texts.append(str(value))
    visit(data)
    texts.extend(value for key, value in catalog(resolve_locale()).items()
                 if key.startswith("legacy_report.") or key.startswith("label.result."))
    return _redact_text(" ".join(texts))


@contextmanager
def _font_scope(data, brand_name: str, font: str | Path | None):
    font_bytes = _load_system_font(_font_text(data, brand_name), font=font, true_type_only=True)
    if font_bytes is None:
        yield
        return
    name = "ReportCJK-" + hashlib.sha256(font_bytes).hexdigest()[:16]
    try:
        pdfmetrics.registerFont(TTFont(name, io.BytesIO(font_bytes)))
        pdfmetrics.registerFontFamily(name, normal=name, bold=name, italic=name, boldItalic=name)
    except Exception as exc:
        raise PDFDependencyError(t("report.font_dependency")) from exc
    token = _FONT_NAMES.set((name, name, name))
    try:
        # Matplotlib receives the same checked standalone font. Its temporary
        # path is created by us, never from report content, and is cleaned up.
        with tempfile.TemporaryDirectory(prefix="claude-ads-font-") as directory:
            path = Path(directory) / "report.ttf"
            path.write_bytes(font_bytes)
            chart_token = _CHART_FONT_PATH.set(str(path))
            try:
                yield
            finally:
                _CHART_FONT_PATH.reset(chart_token)
    finally:
        _FONT_NAMES.reset(token)


def _localized(function):
    @wraps(function)
    def localized(*args, locale=None, **kwargs):
        with locale_scope(locale):
            return function(*args, **kwargs)
    return localized


def _localized_chart(function):
    @wraps(function)
    def localized(*args, locale=None, **kwargs):
        with locale_scope(locale):
            if not HAS_MATPLOTLIB:
                return None
            if _CHART_FONT_PATH.get():
                return function(*args, **kwargs)
            font_bytes = _load_system_font(_font_text(args, ""), true_type_only=True)
            if font_bytes is None:
                return function(*args, **kwargs)
            with tempfile.TemporaryDirectory(prefix="claude-ads-chart-font-") as directory:
                path = Path(directory) / "report.ttf"
                path.write_bytes(font_bytes)
                token = _CHART_FONT_PATH.set(str(path))
                try:
                    return function(*args, **kwargs)
                finally:
                    _CHART_FONT_PATH.reset(token)
    return localized


def _apply_chart_font(figure):
    path = _CHART_FONT_PATH.get()
    if path:
        from matplotlib.font_manager import FontProperties
        from matplotlib.text import Text
        for text in figure.findobj(match=Text):
            properties = FontProperties(fname=path, size=text.get_fontsize(), weight=text.get_fontweight())
            text.set_fontproperties(properties)


# Page geometry is unchanged; the fallback permits --help/--json without PDF deps.
if not HAS_REPORTLAB:
    inch = 72
PAGE_WIDTH = 7.0 * inch  # letter minus margins
MAX_IMG_W = 6.5 * inch
MAX_IMG_H = 4.0 * inch

# Sections already rendered in the header area (skip as body sections)
SKIP_SECTIONS = {"executive summary", "critical issues", "quick wins", "执行摘要", "关键问题", "快速改进", "快速改进（本周执行）"}


# ---------------------------------------------------------------------------
# Markdown to HTML converter (for reportlab Paragraph)
# ---------------------------------------------------------------------------

def _md_to_html(text: str) -> str:
    """Escape untrusted text, then add a constrained set of ReportLab tags."""
    text = html.escape(_redact_text(str(text)), quote=True)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    code_font = _font(0) if _CHART_FONT_PATH.get() else "Courier"
    text = re.sub(r"`(.+?)`", lambda match: f"<font face='{code_font}' size='9'>{match.group(1)}</font>", text)
    return text


# ---------------------------------------------------------------------------
# Markdown Parser (state machine)
# ---------------------------------------------------------------------------

def parse_markdown(filepath: str) -> dict:
    """Parse audit results markdown into structured data."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    data = {
        "title": "",
        "health_score": None,
        "grade": "",
        "platform_scores": {},
        "critical_issues": [],
        "high_issues": [],
        "quick_wins": [],
        "sections": [],
        "tables": [],
        "result_counts": {"Pass": 0, "Warning": 0, "Fail": 0},
    }

    lines = content.split("\n")
    section_title = None
    section_items = []
    in_table = False
    table_rows = []
    table_headers = []

    for line in lines:
        stripped = line.strip()

        # Title
        if line.startswith("# ") and not data["title"]:
            data["title"] = line[2:].strip()
            continue

        # Presentation may be Chinese or English; canonical output keys stay English.
        score_line = re.sub(r"[*`\\]", "", line)
        m = re.search(r"(?:(?:Ads\s+)?Health\s+Score|(?:广告)?健康评[分估])[:：\s]*(\d+(?:\.\d+)?)\s*/\s*100", score_line, re.I)
        if m:
            value = float(m.group(1))
            data["health_score"] = int(value) if value.is_integer() else value

        # Grade letters are schema values, not translated labels.
        m = re.search(r"(?:Grade|等级|评级)[:：\s]*([A-F])\b", score_line)
        if m:
            data["grade"] = m.group(1)

        # Platform scores: handle both "Google Ads: 78/100" and table rows
        # Use a pattern that can cross table pipes
        m = re.search(
            r"(Google|Meta|LinkedIn|TikTok|Microsoft|Apple|YouTube)"
            r".*?(\d{1,3})\s*/\s*100",
            line, re.I
        )
        if m:
            data["platform_scores"][m.group(1)] = int(m.group(2))

        # Preserve legacy English matching and recognize localized status cells.
        if stripped.startswith("|"):
            lower = stripped.lower()
            cells = {re.sub(r"[*`\\]", "", cell).strip() for cell in stripped.split("|")[1:-1]}
            if "| pass" in lower or "通过" in cells:
                data["result_counts"]["Pass"] += 1
            if "| warning" in lower or "警告" in cells:
                data["result_counts"]["Warning"] += 1
            if "| fail" in lower or cells & {"未通过", "失败"}:
                data["result_counts"]["Fail"] += 1

        # Critical / High issues
        if stripped.startswith("- "):
            text = stripped.lstrip("- ").strip()
            if "Critical" in line or "关键" in line:
                data["critical_issues"].append(text)
            elif section_title and (("High" in line and "high" in section_title.lower()) or
                                    ("高" in line and "高" in section_title)):
                data["high_issues"].append(text)

        # Quick wins
        quick_section = section_title and ("quick win" in section_title.lower() or "快速改进" in section_title)
        if re.match(r"^[\d]+\.\s", stripped) and quick_section:
            data["quick_wins"].append(re.sub(r"^\d+\.\s*", "", stripped))
        elif stripped.startswith("- ") and quick_section:
            data["quick_wins"].append(stripped.lstrip("- ").strip())

        # Table detection
        if stripped.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", stripped):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if not in_table:
                in_table = True
                table_headers = cells
                table_rows = []
            else:
                table_rows.append(cells)
            continue
        elif stripped.startswith("|") and re.match(r"^\|[\s\-:|]+\|$", stripped):
            continue  # separator row
        else:
            if in_table and table_headers:
                section_items.append({
                    "type": "table",
                    "headers": table_headers,
                    "rows": table_rows,
                })
                data["tables"].append({"headers": table_headers, "rows": table_rows})
                in_table = False
                table_headers = []
                table_rows = []

        # Section tracking
        if line.startswith("## "):
            if section_title is not None:
                _flush_section(data, section_title, section_items)
            section_title = line[3:].strip()
            section_items = []
        elif line.startswith("### "):
            section_items.append({"type": "subtitle", "text": line[4:].strip()})
        elif stripped.startswith("- "):
            section_items.append({"type": "bullet", "text": stripped.lstrip("- ").strip()})
        elif stripped and not stripped.startswith("#"):
            section_items.append({"type": "text", "text": stripped})

    if section_title is not None:
        if in_table and table_headers:
            section_items.append({"type": "table", "headers": table_headers, "rows": table_rows})
        _flush_section(data, section_title, section_items)

    return data


def _flush_section(data, title, items):
    """Add section only if it has meaningful content and is not a duplicate."""
    if title.lower().strip() in SKIP_SECTIONS:
        logger.info(t("legacy_report.skipped_duplicate", title=_redact_text(title)))
        return
    meaningful = [i for i in items if i.get("text") or i.get("type") == "table"]
    if meaningful:
        data["sections"].append({"title": title, "items": items})
    else:
        logger.warning(t("legacy_report.skipped_empty", title=_redact_text(title)))


# ---------------------------------------------------------------------------
# Chart Generators (matplotlib)
# ---------------------------------------------------------------------------

@_localized_chart
def build_gauge_chart(score: int, grade: str) -> str | None:
    """Build health score donut gauge chart, return temp PNG path."""
    if not HAS_MATPLOTLIB:
        return None

    color = GRADE_COLORS.get(grade, "#64748b")
    bg = "#e2e8f0"

    fig, ax = plt.subplots(figsize=(3, 3), subplot_kw={"projection": "polar"})
    fig.patch.set_facecolor("white")

    theta = 2 * math.pi * (score / 100)
    ax.barh(1, theta, height=0.6, color=color, alpha=0.9)
    ax.barh(1, 2 * math.pi - theta, left=theta, height=0.6, color=bg, alpha=0.4)
    ax.set_ylim(0, 2)
    ax.set_axis_off()
    ax.text(0, 0, f"{score}", ha="center", va="center", fontsize=28,
            fontweight="bold", color=color, transform=ax.transAxes)
    ax.text(0, -0.15, t("legacy_report.grade", grade=_redact_text(str(grade))), ha="center", va="center",
            fontsize=12, color="#475569", transform=ax.transAxes)

    _apply_chart_font(fig)
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    fig.savefig(path, dpi=150, bbox_inches="tight", transparent=False)
    plt.close(fig)
    return path


@_localized_chart
def build_platform_chart(platform_scores: dict) -> str | None:
    """Build horizontal bar chart of platform scores, return temp PNG path."""
    if not HAS_MATPLOTLIB or not platform_scores:
        return None

    platforms = [_redact_text(str(platform)) for platform in platform_scores]
    scores = list(platform_scores.values())
    bar_colors = []
    for s in scores:
        if s >= 90:
            bar_colors.append("#16a34a")
        elif s >= 75:
            bar_colors.append("#22c55e")
        elif s >= 60:
            bar_colors.append("#f59e0b")
        else:
            bar_colors.append("#dc2626")

    fig, ax = plt.subplots(figsize=(5, max(2, len(platforms) * 0.7)))
    fig.patch.set_facecolor("white")
    bars = ax.barh(platforms, scores, color=bar_colors, height=0.5, edgecolor="white")
    ax.set_xlim(0, 100)
    ax.set_xlabel(t("legacy_report.health_score"), fontsize=9, color="#475569")
    ax.tick_params(axis="y", labelsize=9)
    ax.tick_params(axis="x", labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for bar, s in zip(bars, scores):
        ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2,
                f"{s}", va="center", fontsize=9, fontweight="bold", color="#334155")

    _apply_chart_font(fig)
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


@_localized_chart
def build_result_distribution_chart(result_counts: dict) -> str | None:
    """Build pass/warning/fail donut chart from audit results."""
    if not HAS_MATPLOTLIB:
        return None
    total = sum(result_counts.values())
    if total == 0:
        return None

    labels = []
    sizes = []
    chart_colors = []
    color_map = {"Pass": "#16a34a", "Warning": "#f59e0b", "Fail": "#dc2626"}

    for result in ["Pass", "Warning", "Fail"]:
        count = result_counts.get(result, 0)
        if count > 0:
            labels.append(f"{label('result', result)} ({count})")
            sizes.append(count)
            chart_colors.append(color_map[result])

    fig, ax = plt.subplots(figsize=(3.5, 3))
    fig.patch.set_facecolor("white")
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=chart_colors, autopct="%1.0f%%",
        startangle=90, pctdistance=0.75, wedgeprops={"width": 0.4, "edgecolor": "white"},
        textprops={"fontsize": 8}
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_fontweight("bold")
        at.set_color("white")
    ax.set_title(t("legacy_report.distribution_title"), fontsize=10, fontweight="bold",
                 color="#1e293b", pad=10)

    _apply_chart_font(fig)
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def render_mermaid(mermaid_code: str) -> str | None:
    """Render mermaid diagram to PNG if mmdc is available."""
    mmdc = shutil.which("mmdc")
    if not mmdc:
        return None
    try:
        fd_src, src = tempfile.mkstemp(suffix=".mmd")
        os.close(fd_src)
        fd_out, out = tempfile.mkstemp(suffix=".png")
        os.close(fd_out)
        with open(src, "w") as f:
            f.write(mermaid_code)
        subprocess.run([mmdc, "-i", src, "-o", out, "-b", "white", "-w", "600"],
                       capture_output=True, timeout=15)
        if os.path.exists(out) and os.path.getsize(out) > 0:
            return out
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# PDF Builder
# ---------------------------------------------------------------------------

def _make_styles():
    """Create professional styles with proper spacing to prevent overlap."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle("RTitle", fontName=_font(2), fontSize=22,
                              textColor=C_PRIMARY, spaceAfter=2, alignment=TA_LEFT))
    styles.add(ParagraphStyle("RSubtitle", fontName=_font(0), fontSize=10,
                              textColor=colors.HexColor("#64748b"),
                              spaceBefore=2, spaceAfter=10))
    styles.add(ParagraphStyle("RSectionHead", fontName=_font(2), fontSize=14,
                              textColor=C_ACCENT, spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle("RSubHead", fontName=_font(2), fontSize=11,
                              textColor=C_PRIMARY, spaceBefore=8, spaceAfter=3))
    styles.add(ParagraphStyle("RBody", fontName=_font(0), fontSize=10,
                              leading=14, spaceAfter=4))
    styles.add(ParagraphStyle("RBullet", fontName=_font(0), fontSize=10,
                              leading=14, leftIndent=18, bulletIndent=8,
                              spaceAfter=3))
    styles.add(ParagraphStyle("RCaption", fontName=_font(0), fontSize=8,
                              textColor=colors.HexColor("#64748b"),
                              alignment=TA_CENTER, spaceBefore=2, spaceAfter=10))
    styles.add(ParagraphStyle("RFooter", fontName=_font(0), fontSize=7,
                              textColor=colors.HexColor("#94a3b8"),
                              alignment=TA_CENTER))
    if _CHART_FONT_PATH.get():
        for name in ("RTitle", "RSubtitle", "RSectionHead", "RSubHead", "RBody", "RBullet", "RCaption", "RFooter"):
            styles[name].wordWrap = "CJK"
    return styles


def _health_caption(score, grade) -> str:
    """Build the Fig 1 caption with every report-supplied value escaped.

    ``score`` and ``grade`` come from the parsed report dictionary, which any
    caller of ``build_pdf`` controls, so both go through ``_md_to_html`` before
    they reach a ReportLab Paragraph.
    """
    return t("legacy_report.health_caption", score=_md_to_html(score), grade=_md_to_html(grade))


def _wrap_cell(text, style):
    """Wrap cell text in a Paragraph to prevent overflow and render markdown."""
    if not isinstance(text, str):
        text = str(text)
    text = _md_to_html(text)
    if len(text) > 50:
        return Paragraph(text, style)
    return Paragraph(text, style)


def _build_table(headers: list, rows: list, col_widths=None) -> Table:
    """Build a formatted Table with word-wrapped cells and alternating rows."""
    wrap_style = ParagraphStyle("CellWrap", fontName=_font(0), fontSize=8,
                                leading=10, wordWrap="CJK")
    header_wrap = ParagraphStyle("HeaderWrap", fontName=_font(2), fontSize=8,
                                 leading=10, textColor=colors.white, wordWrap="CJK")

    wrapped_headers = [_wrap_cell(h, header_wrap) for h in headers]
    wrapped_rows = [[_wrap_cell(c, wrap_style) for c in row] for row in rows]

    all_rows = [wrapped_headers] + wrapped_rows
    if col_widths is None:
        n = len(headers)
        if n <= 3:
            col_widths = [PAGE_WIDTH / n] * n
        elif n == 4:
            col_widths = [PAGE_WIDTH * 0.10, PAGE_WIDTH * 0.30,
                          PAGE_WIDTH * 0.12, PAGE_WIDTH * 0.48]
        elif n == 5:
            col_widths = [PAGE_WIDTH * 0.08, PAGE_WIDTH * 0.25,
                          PAGE_WIDTH * 0.12, PAGE_WIDTH * 0.12, PAGE_WIDTH * 0.43]
        else:
            first_col = PAGE_WIDTH * 0.08
            remaining = (PAGE_WIDTH - first_col) / (n - 1)
            col_widths = [first_col] + [remaining] * (n - 1)

    tbl = Table(all_rows, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), C_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), _font(2)),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTNAME", (0, 1), (-1, -1), _font(0)),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(all_rows)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), C_ROW_ALT))

    tbl.setStyle(TableStyle(style_cmds))
    return tbl


def _report_date() -> str:
    return datetime.now().strftime("%Y年%m月%d日" if resolve_locale() == "zh-CN" else "%B %d, %Y")


def _add_page_footer(canvas, doc):
    """Add footer with page number and branding on every page."""
    canvas.saveState()
    canvas.setFont(_font(0), 7)
    canvas.setFillColor(colors.HexColor("#94a3b8"))
    canvas.drawCentredString(
        letter[0] / 2, 0.4 * inch,
        t("legacy_report.page_footer", version=__version__, page=doc.page, date=_report_date())
    )
    canvas.restoreState()


def build_pdf(data: dict, output_path: str, brand_name: str = "", *, locale=None, font=None):
    """Build the complete PDF with an explicit locale and checked local font."""
    with locale_scope(locale):
        if not HAS_REPORTLAB:
            raise PDFDependencyError(t("legacy_report.dependency"))
        with _font_scope(data, brand_name, font):
            return _build_pdf(data, output_path, brand_name)


def _build_pdf(data: dict, output_path: str, brand_name: str = ""):
    output_path = str(resolve_output_path(output_path, create_parent=True))
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
    )
    styles = _make_styles()
    elements = []
    temp_files = []

    # --- Title Page Header ---
    title = brand_name or data.get("title") or t("legacy_report.title")
    elements.append(Paragraph(_md_to_html(title), styles["RTitle"]))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        t("legacy_report.generated", date=_report_date(), version=__version__),
        styles["RSubtitle"],
    ))
    elements.append(HRFlowable(width="100%", thickness=2, color=C_ACCENT))
    elements.append(Spacer(1, 12))

    # --- Charts Row: Gauge + Platform Bar (side by side) ---
    score = data.get("health_score")
    grade = data.get("grade", "")

    gauge_path = build_gauge_chart(score, grade) if score is not None else None
    platform_path = build_platform_chart(data.get("platform_scores", {}))

    if gauge_path and platform_path:
        temp_files.extend([gauge_path, platform_path])
        ph = min(max(1.8, len(data["platform_scores"]) * 0.55) * inch, MAX_IMG_H)
        chart_row = [
            Image(gauge_path, width=2.2 * inch, height=2.2 * inch),
            Image(platform_path, width=4.3 * inch, height=ph),
        ]
        chart_table = Table([chart_row], colWidths=[2.7 * inch, 4.3 * inch])
        chart_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ]))
        elements.append(chart_table)
        elements.append(Paragraph(
            f"{_health_caption(score, grade)}  |  {t('legacy_report.platform_caption')}",
            styles["RCaption"],
        ))
    elif gauge_path:
        temp_files.append(gauge_path)
        elements.append(Image(gauge_path, width=2.5 * inch, height=2.5 * inch))
        elements.append(Paragraph(_health_caption(score, grade), styles["RCaption"]))
    elif score is not None:
        grade_color = colors.HexColor(GRADE_COLORS.get(grade, "#64748b"))
        # Plain string cells are drawn literally by ReportLab (no markup
        # parsing). Escape via _md_to_html before converting any of these
        # cells to a Paragraph.
        score_tbl = Table(
            [[t("legacy_report.ads_health_score"), f"{_redact_text(str(score))}/100", t("legacy_report.grade_cell", grade=_redact_text(str(grade)))]],
            colWidths=[3 * inch, 2 * inch, 2 * inch],
        )
        score_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_LIGHT),
            ("TEXTCOLOR", (1, 0), (2, 0), grade_color),
            ("FONTNAME", (0, 0), (-1, -1), _font(2)),
            ("FONTSIZE", (0, 0), (-1, -1), 14),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 1, C_ACCENT),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(score_tbl)
        elements.append(Spacer(1, 8))

    # --- Result Distribution Chart (pass/warning/fail donut) ---
    dist_path = build_result_distribution_chart(data.get("result_counts", {}))
    if dist_path:
        temp_files.append(dist_path)
        elements.append(Spacer(1, 4))
        elements.append(Image(dist_path, width=3.0 * inch, height=2.5 * inch))
        elements.append(Paragraph(t("legacy_report.distribution_caption"), styles["RCaption"]))

    # --- Critical Issues ---
    if data.get("critical_issues"):
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(t("legacy_report.critical_issues"), styles["RSectionHead"]))
        for issue in data["critical_issues"][:10]:
            elements.append(Paragraph(
                f"\u2022 {_md_to_html(issue)}", styles["RBullet"]))

    # --- Quick Wins ---
    if data.get("quick_wins"):
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(t("legacy_report.quick_wins"), styles["RSectionHead"]))
        for i, win in enumerate(data["quick_wins"][:7], 1):
            elements.append(Paragraph(
                f"{i}. {_md_to_html(win)}", styles["RBullet"]))

    # --- Body Sections ---
    for idx, section in enumerate(data.get("sections", [])):
        items = section.get("items", [])
        meaningful = [i for i in items if i.get("text") or i.get("type") == "table"]
        if not meaningful:
            continue

        # Section divider
        elements.append(Spacer(1, 6))
        elements.append(HRFlowable(width="100%", thickness=0.5,
                                   color=colors.HexColor("#e2e8f0")))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(_md_to_html(section["title"]), styles["RSectionHead"]))

        for item in items:
            itype = item.get("type", "")
            if itype == "subtitle":
                elements.append(Paragraph(
                    _md_to_html(item["text"]), styles["RSubHead"]))
            elif itype == "bullet":
                elements.append(Paragraph(
                    f"\u2022 {_md_to_html(item['text'])}", styles["RBullet"]))
            elif itype == "text":
                elements.append(Paragraph(
                    _md_to_html(item["text"]), styles["RBody"]))
            elif itype == "table":
                headers = item.get("headers", [])
                rows = item.get("rows", [])
                if headers and rows:
                    tbl = _build_table(headers, rows)
                    elements.append(KeepTogether([
                        Spacer(1, 4), tbl, Spacer(1, 6)
                    ]))

    # --- End Footer ---
    elements.append(Spacer(1, 16))
    elements.append(HRFlowable(width="100%", thickness=1, color=C_ACCENT))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        t("legacy_report.footer", version=__version__),
        styles["RFooter"],
    ))

    doc.build(elements, onFirstPage=_add_page_footer, onLaterPages=_add_page_footer)

    for f in temp_files:
        try:
            os.unlink(f)
        except OSError:
            pass

    return output_path


# ---------------------------------------------------------------------------
# Content Quality Checker (guardrail)
# ---------------------------------------------------------------------------

@_localized
def check_content(data: dict) -> list:
    """Validate report content quality, layout safety, and formatting."""
    warnings = []

    # Content completeness
    if data["health_score"] is None:
        warnings.append(t("legacy_report.missing_score"))
    if not data["grade"]:
        warnings.append(t("legacy_report.missing_grade"))
    if not data.get("platform_scores"):
        warnings.append(t("legacy_report.missing_platforms"))
    if not data["critical_issues"] and not data["sections"]:
        warnings.append(t("legacy_report.empty_content"))

    # Section quality
    for section in data["sections"]:
        items = section.get("items", [])
        meaningful = [it for it in items if it.get("text") or it.get("type") == "table"]
        if len(meaningful) < 2:
            warnings.append(
                t("legacy_report.sparse_section", title=_redact_text(section["title"])))

    # Empty tables
    empty_tables = sum(1 for table in data["tables"] if not table["rows"])
    if empty_tables:
        warnings.append(t("legacy_report.empty_tables", count=empty_tables))

    # Overflow risk: tables with too many columns
    for table in data["tables"]:
        ncols = len(table.get("headers", []))
        if ncols > 6:
            warnings.append(t("legacy_report.wide_table", count=ncols))

    # Raw markdown syntax check (would render as literal ** in PDF)
    for section in data["sections"]:
        for item in section.get("items", []):
            text = item.get("text", "")
            if "**" in text and item.get("type") != "table":
                # This is expected and will be converted by _md_to_html
                pass

    # Result distribution check
    total = sum(data.get("result_counts", {}).values())
    if total == 0:
        warnings.append(t("legacy_report.missing_results"))

    return warnings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    with locale_scope(cli_locale(argv)):
        return _main(argv)


def _main(argv):
    parser = LocaleArgumentParser(description=t("legacy_report.cli_description"))
    parser.add_argument("input", help=t("legacy_report.cli_input"))
    parser.add_argument("--output", "-o", default=None, help=t("legacy_report.cli_output"))
    parser.add_argument("--brand", "-b", default="", help=t("legacy_report.cli_brand"))
    parser.add_argument("--json", action="store_true", help=t("legacy_report.cli_json"))
    parser.add_argument("--check", action="store_true", help=t("legacy_report.cli_check"))
    parser.add_argument("--verbose", "-v", action="store_true", help=t("legacy_report.cli_verbose"))
    parser.add_argument("--font", default=None, help=t("legacy_report.cli_font"))
    args = parser.parse_args(argv)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if not os.path.exists(args.input):
        print(t("legacy_report.file_missing", path=sanitize_error(args.input)), file=sys.stderr)
        sys.exit(1)

    data = parse_markdown(args.input)

    if args.check:
        warnings = check_content(data)
        if warnings:
            for warning in warnings:
                print(t("legacy_report.warning", warning=warning))
            print("\n" + t("legacy_report.warning_count", count=len(warnings)))
        else:
            print(t("legacy_report.check_passed"))
        return

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        return

    output_path = args.output or f"{Path(args.input).stem}-report.pdf"
    try:
        output_path = build_pdf(data, output_path, args.brand, font=args.font)
    except ValueError as exc:
        print(t("legacy_report.error", error=sanitize_error(exc)), file=sys.stderr)
        sys.exit(1)
    print(t("legacy_report.generated_path", path=output_path))

    # Auto-run content check post-build
    warnings = check_content(data)
    if warnings:
        print("\n" + t("legacy_report.content_warnings", count=len(warnings)))
        for warning in warnings:
            print(f"  - {warning}")


if __name__ == "__main__":
    main()
