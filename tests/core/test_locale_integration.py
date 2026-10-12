from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import copy
from datetime import date
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

from claude_ads_core.adapters import GenericCSVExportAdapter
from claude_ads_core.cli import main
from claude_ads_core.contracts import PLATFORMS, ContractError, validate_contract
from claude_ads_core.i18n import guidance_text, locale_scope
from claude_ads_core.product_status import evaluate_product_status
from claude_ads_core.reporting import PDFDependencyError, render_html, render_markdown, render_pdf, write_report_bundle
from scripts.build_locale import inspect_guidance


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures"


class LocaleIntegrationTests(unittest.TestCase):
    def bundle(self):
        return json.loads((FIXTURES / "reports/sanitized-report-bundle.json").read_text(encoding="utf-8"))

    def test_english_goldens_are_unchanged(self):
        data = self.bundle()
        self.assertEqual(render_html(data, locale="en"), (FIXTURES / "reports/sanitized-report.html").read_text(encoding="utf-8"))
        self.assertEqual(render_markdown(data, locale="en"), (FIXTURES / "reports/sanitized-report.md").read_text(encoding="utf-8"))

    def test_chinese_report_preserves_scores_and_input(self):
        data = self.bundle()
        data["findings"][0]["observation"] = "中文观察 <script>bad()</script> access_token=secret-value"
        original = copy.deepcopy(data)
        document = render_html(data, locale="zh-CN")
        self.assertIn('lang="zh-CN"', document)
        self.assertIn("不得将本报告表述为完整审计", document)
        self.assertIn("37.50 / 100", document)
        self.assertIn("61.54%", document)
        self.assertNotIn("<script>", document)
        self.assertNotIn("secret-value", document)
        self.assertIn("&lt;script&gt;", document)
        self.assertEqual(data, original)

    def test_all_empty_statuses_are_chinese(self):
        for completeness in ("complete", "partial", "failed"):
            for status in ("normal", "provisional", "insufficient_evidence"):
                with self.subTest(completeness=completeness, status=status):
                    data = self.bundle()
                    data["run_manifest"]["completeness"] = completeness
                    data["scoring"].update(health_score=None, evidence_coverage=0, status=status, categories=[])
                    data.update(findings=[], contradictions=[], actions=[])
                    for renderer in (render_html, render_markdown):
                        text = renderer(data, locale="zh-CN")
                        self.assertIn("未评分", text)
                        self.assertIn("未提供审计发现", text)
                        self.assertEqual("不得将本报告表述为完整审计" in text, completeness != "complete")

    def test_export_machine_data_is_locale_independent(self):
        for platform in sorted(PLATFORMS):
            with self.subTest(platform=platform):
                path = FIXTURES / "exports" / f"{platform}.csv"
                with locale_scope("en"):
                    english = GenericCSVExportAdapter(platform).read_snapshot(path)
                with locale_scope("zh-CN"):
                    chinese = GenericCSVExportAdapter(platform).read_snapshot(path)
                self.assertEqual(chinese, english)
                validate_contract("account-snapshot", chinese)

    def test_status_identity_and_source_binding(self):
        self.assertEqual(inspect_guidance(ROOT), [])
        with locale_scope("en"):
            english = evaluate_product_status(ROOT, as_of=date(2026, 9, 29))
        with locale_scope("zh-CN"):
            chinese = evaluate_product_status(ROOT, as_of=date(2026, 9, 29))
        self.assertEqual(chinese["next_blocker"]["id"], english["next_blocker"]["id"])
        self.assertEqual(chinese["next_blocker"]["evidence_paths"], english["next_blocker"]["evidence_paths"])
        self.assertIn("尚未获批", chinese["next_blocker"]["summary"])
        self.assertEqual(guidance_text("new unknown external reason", "control-plane/manifests/maturity-status.json"), "new unknown external reason")

    def test_cli_errors_remain_json_and_do_not_leak_secrets(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.json"
            path.write_text('{}', encoding="utf-8")
            for locale in ("en", "zh-CN"):
                output, error = io.StringIO(), io.StringIO()
                with redirect_stdout(output), redirect_stderr(error):
                    status = main(["validate", "finding", str(path), "--locale", locale])
                self.assertEqual(status, 2)
                self.assertEqual(output.getvalue(), "")
                self.assertEqual(json.loads(error.getvalue())["status"], "invalid")
        with locale_scope("zh-CN"):
            with self.assertRaises(ContractError) as caught:
                validate_contract("finding", {})
            self.assertIn("缺少", str(caught.exception))

    def test_registry_rebuild_reads_machine_stable_english_source(self):
        from unittest.mock import patch
        from scripts import build_control_registry
        source = ROOT / "claude_ads_core/locales/en/documents/ads/references/google-audit.md"
        categorized, rows = build_control_registry._reference_rows(source)
        self.assertFalse(categorized)
        self.assertTrue(rows["G-AI1"][1].startswith("Unscored source-refresh discovery"))
        catalog = {"version": "1.0", "platforms": {"google": {"reference": "ads/references/google-audit.md", "check_ids": ["G-AI1"]}}}
        with patch.object(build_control_registry, "_load_yaml", return_value=catalog):
            with locale_scope("zh-CN"):
                chinese = build_control_registry.build(ROOT)
            with locale_scope("en"):
                english = build_control_registry.build(ROOT)
        self.assertEqual(chinese, english)
        self.assertEqual(chinese[0]["controls"][0]["disposition"], "source_refresh_discovery")
        self.assertEqual(chinese[0]["controls"][0]["intent"], rows["G-AI1"][0])

    def test_write_and_missing_pdf_dependency(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write_report_bundle(self.bundle(), "html", folder, "report.html", locale="zh-CN")
            self.assertIn("审计报告", path.read_text(encoding="utf-8"))
        from unittest.mock import patch
        with patch.dict(sys.modules, {"weasyprint": None}):
            with self.assertRaises(PDFDependencyError):
                render_pdf(self.bundle(), locale="zh-CN")

    def test_legacy_parser_handles_translated_fixture(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            from scripts.generate_report import parse_markdown
            chinese = ROOT / "claude_ads_core/locales/zh-CN/documents/tests/fixtures/reports/sanitized-report.md"
            with locale_scope("zh-CN"):
                data = parse_markdown(str(chinese))
            self.assertIn("title", data)
            self.assertTrue(data["sections"])
        finally:
            sys.path.remove(str(ROOT / "scripts"))


if __name__ == "__main__":
    unittest.main()
