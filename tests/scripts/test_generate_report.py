"""Security regressions for the legacy ReportLab renderer."""

from __future__ import annotations

import base64
import html
from pathlib import Path
import sys

import pytest


SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_report  # noqa: E402


# Distinct payloads per value so the assertions can tell which route leaked.
IMG_ATTACK = "<img src='file:///private/sentinel.png'>"
GRADE_ATTACK = "<font color='red'>INJECTED</font>"
SCORE_ATTACK = "<img src='file:///private/score.png'>"
ESCAPED_IMG = html.escape(IMG_ATTACK, quote=True)

# 1x1 white PNG so the chart routes can be exercised without matplotlib output.
_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def _malicious_text() -> str:
    return f"{IMG_ATTACK} **verified bold**"


def _report(**overrides) -> dict:
    attack = _malicious_text()
    data = {
        "title": attack,
        "health_score": None,
        "grade": "",
        "platform_scores": {},
        "critical_issues": [attack],
        "quick_wins": [attack],
        "sections": [
            {
                "title": attack,
                "items": [
                    {"type": "subtitle", "text": attack},
                    {"type": "bullet", "text": attack},
                    {"type": "text", "text": attack},
                    {"type": "table", "headers": [attack], "rows": [[attack]]},
                ],
            }
        ],
        "tables": [],
        "result_counts": {"Pass": 0, "Warning": 0, "Fail": 0},
    }
    data.update(overrides)
    return data


def _assert_no_raw_markup(paragraphs: list[str]) -> None:
    leaked = [text for text in paragraphs if "<img" in text or "<font color" in text]
    assert leaked == []


@pytest.fixture
def rendered(monkeypatch, tmp_path: Path):
    """Build a PDF while recording every Paragraph text and Table cell given to ReportLab."""
    pytest.importorskip("reportlab")
    paragraphs: list[str] = []
    cells: list[object] = []
    original_paragraph = generate_report.Paragraph
    original_table = generate_report.Table

    def inspect_paragraph(text, *args, **kwargs):
        paragraphs.append(str(text))
        return original_paragraph(text, *args, **kwargs)

    def inspect_table(rows, *args, **kwargs):
        cells.extend(cell for row in rows for cell in row)
        return original_table(rows, *args, **kwargs)

    monkeypatch.setattr(generate_report, "Paragraph", inspect_paragraph)
    monkeypatch.setattr(generate_report, "Table", inspect_table)
    monkeypatch.setattr(
        generate_report, "build_result_distribution_chart", lambda *_args: None
    )
    monkeypatch.setenv("CLAUDE_ADS_OUTPUT_ROOT", str(tmp_path))
    counter = {"png": 0}

    def png_factory(enabled: bool):
        def build_chart(*_args):
            if not enabled:
                return None
            counter["png"] += 1
            path = tmp_path / f"chart-{counter['png']}.png"
            path.write_bytes(_PNG)
            return str(path)

        return build_chart

    def build(data: dict, *, gauge: bool, platform: bool, brand: str = ""):
        monkeypatch.setattr(generate_report, "build_gauge_chart", png_factory(gauge))
        monkeypatch.setattr(generate_report, "build_platform_chart", png_factory(platform))
        output = tmp_path / "report.pdf"
        generate_report.build_pdf(data, str(output), brand, locale="en")
        assert output.is_file()
        return paragraphs, cells

    return build


def test_markdown_conversion_escapes_reportlab_markup_before_formatting() -> None:
    converted = generate_report._md_to_html(_malicious_text())

    assert "<img" not in converted
    assert ESCAPED_IMG in converted
    assert "<b>verified bold</b>" in converted


def test_pdf_builder_escapes_every_body_paragraph_route(rendered) -> None:
    paragraphs, _cells = rendered(
        _report(), gauge=False, platform=False, brand=_malicious_text()
    )

    _assert_no_raw_markup(paragraphs)
    # One escaped copy per route: brand title, critical issue, quick win,
    # section title, subtitle, bullet, text, table header, table cell.
    assert sum(ESCAPED_IMG in text for text in paragraphs) == 9


@pytest.mark.parametrize(
    ("gauge", "platform", "suffix"),
    [
        (True, True, "  |  Fig 2: Platform Score Comparison"),
        (True, False, ""),
    ],
)
def test_health_caption_routes_escape_score_and_grade(
    rendered, gauge: bool, platform: bool, suffix: str
) -> None:
    paragraphs, _cells = rendered(
        _report(
            health_score=SCORE_ATTACK,
            grade=GRADE_ATTACK,
            platform_scores={"Google": 70},
        ),
        gauge=gauge,
        platform=platform,
    )

    captions = [text for text in paragraphs if text.startswith("Fig 1:")]
    expected = (
        f"Fig 1: Health Score {html.escape(SCORE_ATTACK, quote=True)}/100 "
        f"(Grade {html.escape(GRADE_ATTACK, quote=True)}){suffix}"
    )
    assert captions == [expected]
    _assert_no_raw_markup(paragraphs)


def test_health_score_fallback_table_uses_literal_cells(rendered) -> None:
    paragraphs, cells = rendered(
        _report(health_score=SCORE_ATTACK, grade=GRADE_ATTACK),
        gauge=False,
        platform=False,
    )

    # ReportLab draws plain string cells literally, so the fallback score table
    # must keep raw strings rather than Paragraphs with unescaped markup.
    literal_cells = [cell for cell in cells if isinstance(cell, str)]
    assert f"{SCORE_ATTACK}/100" in literal_cells
    assert f"Grade: {GRADE_ATTACK}" in literal_cells
    assert not [text for text in paragraphs if text.startswith("Fig 1:")]
    _assert_no_raw_markup(paragraphs)


@pytest.mark.parametrize(
    ("heading", "score", "grade", "statuses"),
    [
        ("报告", "**健康评分：37.50 / 100**", "等级：C", ["通过", "警告", "未通过"]),
        ("Report", "Ads Health Score: 78/100", "Grade: B", ["Pass", "Warning", "Fail"]),
    ],
)
def test_parser_accepts_both_languages_without_translating_machine_keys(tmp_path, heading, score, grade, statuses):
    source = tmp_path / "report.md"
    source.write_text(
        f"# {heading}\n{score}\n{grade}\n## Checks\n| ID | Result |\n| --- | --- |\n"
        + "\n".join(f"| {index} | {status} |" for index, status in enumerate(statuses)),
        encoding="utf-8",
    )
    data = generate_report.parse_markdown(str(source))
    assert data["health_score"] == (37.5 if heading == "报告" else 78)
    assert data["grade"] == ("C" if heading == "报告" else "B")
    assert data["result_counts"] == {"Pass": 1, "Warning": 1, "Fail": 1}
    assert data["sections"][0]["items"][0]["rows"][0][1] == statuses[0]


def test_chinese_critical_and_quick_win_sections(tmp_path):
    source = tmp_path / "report.md"
    source.write_text("# 报告\n## 关键问题\n- 关键：修复转化\n## 快速改进\n1. 补充证据\n", encoding="utf-8")
    data = generate_report.parse_markdown(str(source))
    assert data["critical_issues"] == ["关键：修复转化"]
    assert data["quick_wins"] == ["补充证据"]
    assert data["sections"] == []


def test_report_messages_and_help_default_to_chinese(capsys, monkeypatch):
    monkeypatch.delenv("CLAUDE_ADS_LOCALE", raising=False)
    with pytest.raises(SystemExit) as exc:
        generate_report.main(["--help"])
    assert exc.value.code == 0
    help_text = capsys.readouterr().out
    assert "生成专业 PDF 报告" in help_text
    assert "--locale" in help_text and "--font" in help_text
    with pytest.raises(SystemExit):
        generate_report.main(["--locale", "en", "--help"])
    assert "Generate professional PDF" in capsys.readouterr().out
    warnings = generate_report.check_content(_report(), locale="zh-CN")
    assert any("未找到健康评分" in warning for warning in warnings)
    assert all(not warning.startswith("LAYOUT:") for warning in warnings)


def test_json_cli_preserves_cjk_and_machine_keys(tmp_path, capsys):
    import json
    source = tmp_path / "report.md"
    source.write_text("# 中文报告\n健康评分：78/100\n等级：B\n## 观察\n原始中文证据\n", encoding="utf-8")
    generate_report.main([str(source), "--json", "--locale", "zh-CN"])
    output = capsys.readouterr().out
    assert "中文报告" in output
    data = json.loads(output)
    assert data["health_score"] == 78 and data["grade"] == "B"
    assert "result_counts" in data and "健康评分" not in data


def test_no_reportlab_dependency_is_a_localized_error_before_output(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_report, "HAS_REPORTLAB", False)
    with pytest.raises(generate_report.PDFDependencyError, match="需要 reportlab"):
        generate_report.build_pdf(_report(), str(tmp_path / "never.pdf"), locale="zh-CN")
    assert not (tmp_path / "never.pdf").exists()


def test_cjk_font_failure_precedes_report_output(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_report, "HAS_REPORTLAB", True)
    def unavailable(*args, **kwargs):
        raise generate_report.PDFDependencyError("中文 PDF 缺少本地字体")
    monkeypatch.setattr(generate_report, "_load_system_font", unavailable)
    with pytest.raises(generate_report.PDFDependencyError, match="中文 PDF"):
        generate_report.build_pdf(_report(title="中文报告"), str(tmp_path / "never.pdf"), locale="zh-CN")
    assert not (tmp_path / "never.pdf").exists()


def test_legacy_markdown_redacts_chinese_mixed_injection():
    text = generate_report._md_to_html("中文 **重点** <img src='file:///private/secret'> user@example.test api_key=secret-value")
    assert "中文 <b>重点</b>" in text
    assert "&lt;img" in text and "<img" not in text
    assert "user@example.test" not in text and "secret-value" not in text


def test_chinese_caption_escapes_untrusted_values():
    with generate_report.locale_scope("zh-CN"):
        caption = generate_report._health_caption(SCORE_ATTACK, GRADE_ATTACK)
    assert caption.startswith("图 1：健康评分")
    assert "<img" not in caption and "<font color" not in caption
    assert html.escape(SCORE_ATTACK, quote=True) in caption


def test_localized_chart_labels_preserve_result_keys(monkeypatch):
    pytest.importorskip("matplotlib")
    from matplotlib.figure import Figure
    from matplotlib.text import Text
    captured = []
    monkeypatch.setattr(generate_report, "_load_system_font", lambda *args, **kwargs: None)
    monkeypatch.setattr(Figure, "savefig", lambda figure, *args, **kwargs: captured.extend(text.get_text() for text in figure.findobj(match=Text)))
    counts = {"Pass": 2, "Warning": 1, "Fail": 1}
    path = generate_report.build_result_distribution_chart(counts, locale="zh-CN")
    try:
        assert "检查结果分布" in captured
        assert "通过 (2)" in captured and "警告 (1)" in captured and "未通过 (1)" in captured
        assert counts == {"Pass": 2, "Warning": 1, "Fail": 1}
    finally:
        if path:
            Path(path).unlink(missing_ok=True)


def test_real_legacy_chinese_pdf_when_local_font_is_available(tmp_path, monkeypatch):
    pytest.importorskip("reportlab")
    pytest.importorskip("fontTools")
    monkeypatch.setenv("CLAUDE_ADS_OUTPUT_ROOT", str(tmp_path))
    data = _report(title="中文审计报告", critical_issues=["关键：验证主要转化"], quick_wins=["补充证据"], sections=[])
    try:
        output = generate_report.build_pdf(data, str(tmp_path / "report.pdf"), locale="zh-CN")
    except generate_report.PDFDependencyError as exc:
        pytest.skip(str(exc))
    assert Path(output).read_bytes().startswith(b"%PDF-")
