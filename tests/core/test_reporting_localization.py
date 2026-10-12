from __future__ import annotations

import copy
import html
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from claude_ads_core import reporting
from claude_ads_core.i18n import catalog, locale_scope


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "reports"


def bundle():
    return json.loads((FIXTURES / "sanitized-report-bundle.json").read_text(encoding="utf-8"))


def test_default_chinese_does_not_translate_free_text_or_mutate_bundle(monkeypatch):
    monkeypatch.delenv("CLAUDE_ADS_LOCALE", raising=False)
    data = bundle()
    data["findings"][0]["observation"] = "中文观察：主要转化未启用。"
    original = copy.deepcopy(data)
    markdown = reporting.render_markdown(data)
    document = reporting.render_html(data)
    assert markdown.startswith("# Claude Ads 审计报告")
    assert 'lang="zh-CN"' in document
    for text in (markdown, document):
        assert "部分完成" in text and "暂定" in text
        assert "关键" in text and "置信度" in text
        assert "中文观察：主要转化未启用。" in text
        assert "Creative rows were not included in the export" in text
        assert "不得将本报告表述为完整审计" in text
        assert "37.50 / 100" in text and "61.54%" in text
    assert data == original
    assert '{"field":"primary_conversion_status","value":"inactive"}' in markdown
    assert html.escape('{"field":"primary_conversion_status","value":"inactive"}') in document


@pytest.mark.parametrize("completeness", ["complete", "partial", "failed"])
@pytest.mark.parametrize("status", ["normal", "provisional", "insufficient_evidence"])
def test_empty_and_partial_states_are_localized_without_inventing_scores(completeness, status):
    data = bundle()
    data["run_manifest"]["completeness"] = completeness
    data["scoring"].update(health_score=None, evidence_coverage=0, status=status, categories=[])
    data["findings"] = []
    data["contradictions"] = []
    data["actions"] = []
    for render in (reporting.render_markdown, reporting.render_html):
        text = render(data, locale="zh-CN")
        for expected in ("未评分", "未提供类别评分", "未提供审计发现", "未报告矛盾信息", "未报告后续操作"):
            assert expected in text
        assert ("不得将本报告表述为完整审计" in text) == (completeness != "complete")
        assert ("证据不足，无法提供" in text) == (status == "insufficient_evidence")


def test_chinese_rendering_keeps_injection_inert_and_redacts_secrets():
    data = bundle()
    data["findings"][0]["observation"] = "中文 <img src='file:///private/secret'> analyst@example.test access_token=secret-value"
    data["findings"][0]["evidence"].append({"email": "person@example.test", "api_key": "sensitive", "备注": "原始证据"})
    data["actions"] = [{"action": "<script>alert(1)</script>", "owner": "person@example.test", "confidence": "high"}]
    markdown = reporting.render_markdown(data, locale="zh-CN")
    document = reporting.render_html(data, locale="zh-CN")
    assert "<script>" not in document and "<img" not in document
    assert "&lt;img" in document and "\\<img" in markdown
    for secret in ("analyst@example.test", "person@example.test", "secret-value", "sensitive"):
        assert secret not in markdown + document
    assert "[REDACTED]" in document and "原始证据" in document
    assert "负责人" in document and "置信度: 高" in document


def test_locale_precedence_and_atomic_bundle_write(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_ADS_LOCALE", "en")
    assert reporting.render_html(bundle()).startswith('<!doctype html>\n<html lang="en"')
    with locale_scope("zh-CN"):
        assert "审计报告" in reporting.render_markdown(bundle())
        assert "Audit Report" in reporting.render_markdown(bundle(), locale="en")
        path = reporting.write_report_bundle(bundle(), "html", tmp_path, "report.html", locale="en")
    assert 'lang="en"' in path.read_text(encoding="utf-8")
    with pytest.raises(reporting.ReportRenderError, match="相对路径"):
        reporting.write_report_bundle(bundle(), "html", tmp_path, "../escape.html", locale="zh-CN")
    assert not (tmp_path.parent / "escape.html").exists()


def test_reporting_catalog_key_and_placeholder_parity():
    from string import Formatter
    english = {key: value for key, value in catalog("en").items() if key.startswith(("report.", "legacy_report.", "label."))}
    chinese = {key: value for key, value in catalog("zh-CN").items() if key.startswith(("report.", "legacy_report.", "label."))}
    assert english.keys() == chinese.keys()
    for key in english:
        fields = lambda text: {field for _, field, _, _ in Formatter().parse(text) if field is not None}
        assert fields(english[key]) == fields(chinese[key]), key


def test_missing_cjk_font_fails_before_weasyprint_output(monkeypatch):
    monkeypatch.setattr(reporting, "_system_font_candidates", lambda: [])
    monkeypatch.setattr(reporting.importlib, "import_module", lambda name: SimpleNamespace())
    with pytest.raises(reporting.PDFDependencyError, match="中文 PDF"):
        reporting.render_pdf(bundle(), locale="zh-CN")


@pytest.mark.parametrize("font", ["https://example.test/font.ttf", "font.ttf", "../font.ttf"])
def test_font_parameter_does_not_accept_urls_or_relative_paths(font):
    with pytest.raises(reporting.PDFDependencyError, match="系统字体目录"):
        reporting._validated_font_path(font, locale="zh-CN")


def test_font_path_rejects_symlink_escape_and_nonfont_files(tmp_path, monkeypatch):
    system = tmp_path / "fonts"
    system.mkdir()
    outside = tmp_path / "outside.ttf"
    outside.write_bytes(b"not a font")
    monkeypatch.setattr(reporting, "_system_font_roots", lambda: (system,))
    with pytest.raises(reporting.PDFDependencyError):
        reporting._validated_font_path(outside)
    link = system / "escape.ttf"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlinks unavailable")
    with pytest.raises(reporting.PDFDependencyError):
        reporting._validated_font_path(link)
    invalid = system / "font.txt"
    invalid.write_text("not a font", encoding="utf-8")
    with pytest.raises(reporting.PDFDependencyError):
        reporting._validated_font_path(invalid)


def test_checked_font_is_embedded_and_only_that_asset_can_be_fetched(monkeypatch):
    captured = {}
    def fake_html(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(write_pdf=lambda: b"%PDF-test")
    monkeypatch.setattr(reporting.importlib, "import_module", lambda name: SimpleNamespace(HTML=fake_html))
    monkeypatch.setattr(reporting, "_load_system_font", lambda *args, **kwargs: b"checked-font")
    assert reporting.render_pdf(bundle(), locale="zh-CN") == b"%PDF-test"
    assert 'lang="zh-CN"' in captured["string"]
    assert '@font-face{font-family:"ReportCJK"' in captured["string"]
    assert "data:font/ttf;base64," in captured["string"]
    assert captured["base_url"] is None
    for url in ("file:///private/secret", "https://example.test/font.ttf", "data:text/plain,other"):
        with pytest.raises(reporting.ReportRenderError):
            captured["url_fetcher"](url)


def test_font_coverage_checks_every_glyph_and_extracts_font_bytes(tmp_path, monkeypatch):
    font = tmp_path / "installed.ttf"
    font.write_bytes(b"fixture-font")
    monkeypatch.setattr(reporting, "_system_font_roots", lambda: (tmp_path,))
    required = "中文观察ABC"
    class Face:
        def getBestCmap(self):
            return {ord(char): "glyph" for char in required}
        def save(self, output):
            output.write(b"verified-font")
        def close(self):
            pass
        def __contains__(self, key):
            return key == "glyf"
    ttlib = SimpleNamespace(TTFont=lambda *args, **kwargs: Face(), TTLibError=RuntimeError)
    monkeypatch.setattr(reporting.importlib, "import_module", lambda name: ttlib)
    assert reporting._load_system_font(required, font=font, locale="zh-CN", true_type_only=True) == b"verified-font"
    with pytest.raises(reporting.PDFDependencyError):
        reporting._load_system_font(required + "缺", font=font, locale="zh-CN")


def test_real_chinese_pdf_when_optional_dependencies_and_system_font_exist():
    pytest.importorskip("weasyprint")
    pytest.importorskip("fontTools")
    try:
        result = reporting.render_pdf(bundle(), locale="zh-CN")
    except reporting.PDFDependencyError as exc:
        pytest.skip(str(exc))
    assert result.startswith(b"%PDF-")
    assert len(result) > 1000
