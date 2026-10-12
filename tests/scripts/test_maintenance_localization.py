"""Offline maintenance localization regressions (also runnable with unittest)."""
from __future__ import annotations

import ast
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
from string import Formatter
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from claude_ads_core.i18n import catalog, locale_scope, resolve_locale, t


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_NAMES = (
    "release", "review_evidence", "audit_dependencies", "audit_ecosystem_live",
    "build_control_registry", "verify_managed_install", "verify_target_lock",
    "write_install_receipt",
)


def load_script(name):
    spec = importlib.util.spec_from_file_location(f"maintenance_test_{name}", ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def invoke(module, argv):
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            code = module.main(argv)
        except SystemExit as exc:
            code = exc.code
    return code, stdout.getvalue(), stderr.getvalue()


class MaintenanceLocaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Preload catalogs before any tests replace a script's json.loads.
        catalog("en")
        catalog("zh-CN")
        cls.modules = {name: load_script(name) for name in SCRIPT_NAMES}

    def setUp(self):
        environment = patch.dict(os.environ)
        environment.start()
        self.addCleanup(environment.stop)
        for name in (
            "CLAUDE_ADS_LOCALE", "CLAUDE_ADS_REVIEW_EVIDENCE_DIR", "GITHUB_RUN_ID",
            "GITHUB_REPOSITORY", "GITHUB_EVENT_PATH", "GITHUB_SHA", "GITHUB_ACTIONS",
        ):
            os.environ.pop(name, None)
        scope = locale_scope("zh-CN")
        scope.__enter__()
        self.addCleanup(scope.__exit__, None, None, None)

    def test_catalog_keys_placeholders_and_english_chinese_coverage(self):
        en = {key: value for key, value in catalog("en").items() if key.startswith("maintenance.")}
        zh = {key: value for key, value in catalog("zh-CN").items() if key.startswith("maintenance.")}
        self.assertEqual(en.keys(), zh.keys())
        self.assertGreater(len(en), 500)
        def fields(value):
            return {(field, spec, conversion) for _, field, spec, conversion in Formatter().parse(value) if field is not None}
        for key in en:
            with self.subTest(key=key):
                self.assertEqual(fields(en[key]), fields(zh[key]))
                if key != "maintenance.release.secret.jwt":
                    self.assertNotEqual(en[key], zh[key])
                # Render every catalog entry to catch broken interpolation, including repr conversions.
                parameters = {field: "fixture/测试:ID-123" for field, _, _ in fields(en[key])}
                self.assertIsInstance(t(key, locale="en", **parameters), str)
                self.assertIsInstance(t(key, locale="zh-CN", **parameters), str)

    def test_all_help_defaults_chinese_and_explicit_english(self):
        for name, module in self.modules.items():
            for locale in (None, "en", "zh-CN"):
                argv = ["--help"] if locale is None else ["--locale", locale, "--help"]
                with self.subTest(script=name, locale=locale):
                    code, out, err = invoke(module, argv)
                    self.assertEqual(code, 0)
                    self.assertFalse(err)
                    self.assertIn("--locale", out)
                    self.assertIn("usage:" if locale == "en" else "用法", out)

    def test_locale_environment_override_and_scope_does_not_leak(self):
        # An explicit locale scope outranks the environment by core contract;
        # test environment selection in a fresh standalone process instead.
        module = self.modules["release"]
        before = resolve_locale()
        code, out, err = invoke(module, ["--locale", "en", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("usage:", out)
        self.assertEqual(resolve_locale(), before)
        code, out, err = invoke(module, ["package", "--locale", "en", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("usage:", out)

    def test_standalone_source_and_installed_layout_help(self):
        with tempfile.TemporaryDirectory(prefix="maintenance-layout-") as temporary:
            base = Path(temporary)
            scripts = base / "scripts"
            scripts.mkdir()
            # An installed skill also has scripts/ and claude_ads_core/ as siblings.
            import shutil
            shutil.copytree(ROOT / "claude_ads_core", base / "claude_ads_core", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            for name in SCRIPT_NAMES:
                shutil.copy2(ROOT / "scripts" / f"{name}.py", scripts / f"{name}.py")
            for name in SCRIPT_NAMES:
                for root in (ROOT, base):
                    environment = {**os.environ, "CLAUDE_ADS_LOCALE": "en", "PYTHONDONTWRITEBYTECODE": "1"}
                    result = subprocess.run(
                        [sys.executable, str(root / "scripts" / f"{name}.py"), "--help"],
                        cwd=base, env=environment, check=False, capture_output=True, text=True,
                    )
                    with self.subTest(script=name, root="installed" if root == base else "source"):
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertIn("usage:", result.stdout)
                        self.assertFalse(result.stderr)
            result = subprocess.run(
                [sys.executable, str(scripts / "release.py"), "--locale", "zh-CN", "--help"],
                cwd=base, env=environment, check=False, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("用法", result.stdout)

    def test_argument_failures_are_localized_and_stdout_is_empty(self):
        cases = {
            "release": [],
            "review_evidence": ["--unknown"],
            "audit_dependencies": ["--as-of", "not-a-date"],
            "audit_ecosystem_live": ["--candidate-pr", "not-a-number"],
            "build_control_registry": ["--unknown"],
            "verify_managed_install": [],
            "verify_target_lock": ["--profile", "unknown"],
            "write_install_receipt": [],
        }
        for name, argv in cases.items():
            for locale in ("zh-CN", "en"):
                with self.subTest(script=name, locale=locale):
                    code, out, err = invoke(self.modules[name], ["--locale", locale, *argv])
                    self.assertEqual(code, 2)
                    self.assertFalse(out)
                    self.assertIn("错误" if locale == "zh-CN" else "error", err)
        for name, module in self.modules.items():
            code, out, err = invoke(module, ["--locale", "unsupported"])
            self.assertEqual(code, 2)
            self.assertFalse(out)
            self.assertIn("错误", err)

    def test_clean_head_guard_remains_fail_closed_in_both_languages(self):
        release = self.modules["release"]
        for locale in ("en", "zh-CN"):
            with locale_scope(locale), patch.object(release, "_git", return_value=b" M README.md\n"):
                with self.assertRaises(release.ReleaseError) as caught:
                    release._assert_clean_head_release_subject(ROOT)
                self.assertEqual(str(caught.exception), t("maintenance.release.release_packaging_requires_a_clean_index_and_worktree"))

    def test_release_trust_anchors_and_canonical_hash_are_unchanged(self):
        release = self.modules["release"]
        self.assertEqual(release.EXPECTED_DEPENDENCY_INVENTORY_SHA256, "48ed1cdd3023bdb9781e7ffe9d987fb9425cc23e2dea053e2da5e8d461e588de")
        self.assertEqual(release.EXPECTED_THIRD_PARTY_NOTICES_SHA256, "b90c38b4cce60c06c0090be31ee721d3482640923d9ff6f3c711c047317746d0")
        self.assertEqual(release.EXPECTED_EXTERNAL_RUNTIME_DEPENDENCIES_SHA256, "c5962746f3a49570c810525c5a8557a3884e64e3b764476ff18cb65741853bc2")
        payload = {"title": "原始证据", "count": 3, "status": "pass", "id": "CLM-0001"}
        expected = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        for locale in ("en", "zh-CN"):
            with locale_scope(locale):
                self.assertEqual(release._canonical_json_sha256(payload), expected)
                rendered = release._json_bytes(payload)
                self.assertIn("原始证据", rendered.decode("utf-8"))
                self.assertEqual(json.loads(rendered), payload)

    def test_review_signature_payload_retains_raw_evidence_and_exact_utf8(self):
        review = self.modules["review_evidence"]
        document = {"title": "签名证据", "id": "REV-001", "authentication": {"algorithm": "ed25519", "key_id": "key-1", "signature_b64url": "raw-signature"}}
        before = json.loads(json.dumps(document))
        unsigned = json.loads(json.dumps(document))
        unsigned["authentication"].pop("signature_b64url")
        expected = json.dumps(unsigned, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        for locale in ("en", "zh-CN"):
            with locale_scope(locale):
                self.assertEqual(review._canonical_review_payload(document), expected)
                self.assertEqual(document, before)
        self.assertIn("签名证据".encode("utf-8"), expected)

    def test_review_failures_keep_guard_and_localize_first_party_message(self):
        review = self.modules["review_evidence"]
        for locale in ("en", "zh-CN"):
            code, out, err = invoke(review, ["--locale", locale])
            self.assertEqual(code, 1)
            self.assertFalse(out)
            self.assertIn("external evidence directory is required" if locale == "en" else "需要外部证据目录", err)
            with locale_scope(locale):
                with self.assertRaises(review.ReviewEvidenceError):
                    review.verify_independent_reviews(ROOT, ROOT / "control-plane/manifests/reviews")
                with self.assertRaises(review.ReviewEvidenceError):
                    review._load_trust_bundle(None)

    def test_review_machine_json_remains_clean_unicode_and_identical(self):
        review = self.modules["review_evidence"]
        fixture = {"schema_version": "1.0.0", "satisfied": True, "reviews": [{"review_id": "REV-001", "review_type": "code", "reviewer_id": "审查者甲", "key_id": "key-1"}]}
        outputs = []
        with patch.object(review, "verify_independent_reviews", return_value=fixture):
            for locale in ("en", "zh-CN"):
                code, out, err = invoke(review, ["--locale", locale, "--evidence-dir", "fixture"])
                self.assertEqual(code, 0)
                self.assertFalse(err)
                self.assertIn("审查者甲", out)
                outputs.append(json.loads(out))
        self.assertEqual(outputs, [fixture, fixture])

    def test_ecosystem_raw_metadata_and_enum_values_survive_translation(self):
        ecosystem = self.modules["audit_ecosystem_live"]
        repository = ecosystem.PUBLIC_REPOSITORY
        ledger = {
            "reviewed_at": "2026-09-10",
            "public_snapshot": {"observed_at": "2026-09-10", "issue_numbers": [1], "pull_request_numbers": [], "pull_request_heads": {}},
            "entries": [{"repository": repository, "kind": "issue", "number": 1, "title": "Original title", "state": "open", "url": "https://example.invalid/1"}],
        }
        live = {repository: {("issue", 1): {"kind": "issue", "number": 1, "title": "原始外部标题", "state": "open", "url": "https://example.invalid/1", "head_sha": None, "created_at": "2026-09-01T00:00:00Z", "merged_at": None}}}
        results = []
        for locale in ("en", "zh-CN"):
            with locale_scope(locale):
                result = ecosystem.reconcile_live(ledger, live, repositories=(repository,))
                finding = result["findings"][0]
                self.assertEqual(result["status"], "pass")
                self.assertEqual(result["mode"], "default")
                self.assertEqual(finding["kind"], "metadata_drift")
                self.assertEqual(finding["live"], "原始外部标题")
                self.assertEqual(finding["recorded"], "Original title")
                with self.assertRaises(ecosystem.EcosystemAuditError):
                    ecosystem.reconcile_live(ledger, live, repositories=(repository,), strict=True)
                results.append(result)
        self.assertNotEqual(results[0]["findings"][0]["message"], results[1]["findings"][0]["message"])
        for result in results:
            result["findings"][0].pop("message")
        self.assertEqual(results[0], results[1])

    def test_ecosystem_annotations_stay_stderr_and_do_not_leak_http_details(self):
        ecosystem = self.modules["audit_ecosystem_live"]
        from urllib.error import HTTPError
        fake_token = "fixture-token-not-a-credential"
        with patch.object(ecosystem, "urlopen", side_effect=HTTPError("https://example.invalid", 403, fake_token, {}, None)):
            with self.assertRaises(ecosystem.EcosystemAuditError) as caught:
                ecosystem._github_fetcher(fake_token)("repos/fixture/issues?secret=hidden")
            self.assertIn("HTTP 403", str(caught.exception))
            self.assertNotIn(fake_token, str(caught.exception))
            self.assertNotIn("secret=", str(caught.exception))
        os.environ["GITHUB_ACTIONS"] = "true"
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            ecosystem._emit_warnings([{"message": "中文问题"}])
        self.assertFalse(out.getvalue())
        self.assertTrue(err.getvalue().startswith("::warning::"))
        self.assertIn("中文问题", err.getvalue())

    def test_dependency_summary_and_syntactic_guards_are_locale_independent(self):
        audit = self.modules["audit_dependencies"]
        record = audit.ExceptionRecord("PYSEC-2026-1", "fixture", "1.0", ("forbidden",))
        reports = {"runtime": {"dependencies": [{"name": "fixture", "version": "1.0", "vulns": [{"id": "PYSEC-2026-1"}]}]}}
        summaries = []
        for locale in ("en", "zh-CN"):
            with locale_scope(locale):
                summaries.append(audit.evaluate_reports(reports, {record.advisory_id: record}))
                self.assertTrue(audit._matches_prefix("forbidden.module", "forbidden"))
                self.assertTrue(audit._matches_call_keyword("write_pdf:**", "write_pdf:stylesheets"))
                self.assertFalse(audit._matches_call_keyword("safe:base_url", "write_pdf:stylesheets"))
                tree = ast.parse('import importlib\nname = "forbidden"\nimportlib.import_module(name)\n')
                with self.assertRaises(audit.DependencyAuditError):
                    audit._ImportGuard(Path("fixture.py"), tree).dynamic_imports()
        self.assertEqual(summaries[0], summaries[1])
        self.assertEqual(summaries[0]["status"], "pass")
        self.assertEqual(summaries[0]["not_affected_advisory_count"], 1)

    def test_external_error_text_is_preserved_inside_localized_context(self):
        managed = self.modules["verify_managed_install"]
        message = "upstream opaque diagnostic [fixture:42]"
        with patch.object(managed, "verify", side_effect=OSError(message)):
            code, out, err = invoke(managed, ["--skill-dir", "fixture"])
        self.assertEqual(code, 1)
        self.assertFalse(out)
        self.assertIn("受管安装验证失败", err)
        self.assertIn(message, err)

    def test_gate_report_keeps_structured_failures_and_external_diagnostics(self):
        release = self.modules["release"]
        opaque = "external adapter diagnostic [fixture:42]"
        def git(_root, *args):
            if args == ("rev-parse", "HEAD"):
                return ("a" * 40).encode()
            if args == ("rev-parse", "HEAD^{tree}"):
                return ("b" * 40).encode()
            return b""
        with (
            patch.object(release, "_git", side_effect=git),
            patch.object(release, "tracked_files", return_value=[]),
            patch.object(release, "audit_repository", return_value=[]),
            patch.object(release, "_check_grounding_and_capabilities", side_effect=ValueError(opaque)),
            patch.object(release, "_check_vulnerability_exceptions", return_value={}),
            patch.object(release, "_check_ecosystem", return_value={}),
        ):
            code, out, err = invoke(release, ["gate", "--model-report", ""])
        self.assertEqual(code, 1)
        self.assertFalse(err)
        result = json.loads(out)
        self.assertEqual(result["schema_version"], "2.0.0")
        self.assertFalse(result["release_gate_satisfied"])
        self.assertEqual(len(result["checks"]), 8)
        checks = {item["id"]: item for item in result["checks"]}
        self.assertEqual(checks["source-capability-integrity"]["status"], "fail")
        self.assertIn("原始诊断", checks["source-capability-integrity"]["error"])
        self.assertIn(opaque, checks["source-capability-integrity"]["error"])
        self.assertEqual(checks["canonical-model-evaluation"]["status"], "fail")
        self.assertEqual(checks["independent-reviews"]["status"], "fail")
        self.assertEqual(checks["remote-ci"]["status"], "fail")

    def test_ecosystem_cli_json_keeps_warnings_off_stdout(self):
        ecosystem = self.modules["audit_ecosystem_live"]
        fixture = {"status": "pass", "mode": "default", "repositories": {}, "findings": [{"kind": "metadata_drift", "number": 7, "message": "中文问题", "live": "Raw title"}], "candidate_exclusion": None}
        with (
            patch.object(ecosystem, "_load_ledger", return_value={}),
            patch.object(ecosystem, "collect_live_repository", return_value={}),
            patch.object(ecosystem, "reconcile_live", return_value=fixture),
        ):
            code, out, err = invoke(ecosystem, ["--json", "--public-only"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), fixture)
        self.assertIn("中文问题", out)
        self.assertIn("警告", err)
        self.assertNotIn("警告", out)

    def test_packaging_scope_is_explicit_not_all_tests_or_docs(self):
        release = self.modules["release"]
        allowed = ["AGENTS.md", "CLAUDE.md", "CODEX.md", "GEMINI.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "claude_ads_core/locales/en/maintenance.json", "claude_ads_core/locales/zh-CN/maintenance.json"]
        self.assertEqual(release.package_files(allowed), allowed)
        self.assertFalse(release.package_files(["docs/private.md", "tests/not-packaged.py", "ads/research-sources/raw.md"]))


if __name__ == "__main__":
    unittest.main()
