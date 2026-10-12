"""Offline operator-language regressions; runnable with unittest or pytest.

No browser, provider SDK, HTTP library, network, or additional test dependency is
needed. Provider/browser calls are replaced only at their existing boundaries.
"""

from __future__ import annotations

import argparse
import base64
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import socket
from string import Formatter
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import analyze_landing
import capture_screenshot
import fetch_page
import generate_image
import url_utils
from claude_ads_core.i18n import locale_scope, resolve_locale, t


PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)
MODULES = (fetch_page, capture_screenshot, analyze_landing, generate_image)


def landing_result():
    return {
        "url": "https://example.com/landing",
        "performance": {"lcp_ms": 1800, "cls": 0.02, "ttfb_ms": 120},
        "content": {"title": "Original English 标题", "h1": "Buy Now", "word_count": 12},
        "conversion": {
            "cta_above_fold": True, "form_present": True, "form_fields": 3,
            "phone_number": False, "chat_widget": False,
        },
        "schema": {"types_found": ["Service"], "product_schema": False, "faq_schema": False, "service_schema": True},
        "mobile": {"viewport_meta": True, "horizontal_scroll": False},
        "error": None,
    }


class ToolLocaleTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict(os.environ, {"CLAUDE_ADS_LOCALE": "zh-CN"}))
        self.stack.enter_context(patch.object(socket, "getaddrinfo", side_effect=AssertionError("unexpected DNS")))

    def call_main(self, module, argv):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                status = module.main(argv)
            except SystemExit as exc:
                status = exc.code
        return status, stdout.getvalue(), stderr.getvalue()

    def test_catalog_keys_and_placeholders_match_without_duplicates(self):
        catalogs = {}
        for locale in ("en", "zh-CN"):
            def unique_pairs(pairs):
                result = {}
                for key, value in pairs:
                    self.assertNotIn(key, result)
                    self.assertTrue(key.startswith("tools."))
                    self.assertIsInstance(value, str)
                    result[key] = value
                return result

            catalogs[locale] = json.loads(
                (ROOT / "claude_ads_core" / "locales" / locale / "tools.json").read_text(encoding="utf-8"),
                object_pairs_hook=unique_pairs,
            )
        self.assertEqual(catalogs["en"].keys(), catalogs["zh-CN"].keys())
        for key in catalogs["en"]:
            with self.subTest(key=key):
                placeholders = lambda text: {field for _, field, _, _ in Formatter().parse(text) if field is not None}
                self.assertEqual(placeholders(catalogs["en"][key]), placeholders(catalogs["zh-CN"][key]))

    def test_all_cli_help_defaults_to_chinese_and_switches_without_global_argparse_mutation(self):
        original_translation = argparse._
        descriptions = {
            fetch_page: ("抓取落地页", "Fetch a landing page"),
            capture_screenshot: ("落地页截图", "Capture ad landing page"),
            analyze_landing: ("落地页质量", "Analyze landing page"),
            generate_image: ("广告创意图像", "Generate ad creative images"),
        }
        os.environ.pop("CLAUDE_ADS_LOCALE", None)
        for module, texts in descriptions.items():
            for locale, expected in zip(("zh-CN", "en"), texts):
                with self.subTest(module=module.__name__, locale=locale):
                    arguments = ["--help"] if locale == "zh-CN" else ["--locale=en", "--help"]
                    status, out, err = self.call_main(module, arguments)
                    self.assertEqual(status, 0)
                    self.assertEqual(err, "")
                    self.assertIn(expected, out)
                    self.assertIn("--locale {zh-CN,en}", out)
                    self.assertTrue(out.startswith("用法：" if locale == "zh-CN" else "usage:"))
        self.assertIs(argparse._, original_translation)
        self.assertEqual(resolve_locale(), "zh-CN")

    def test_environment_language_and_explicit_flag_precedence(self):
        for module in MODULES:
            with self.subTest(module=module.__name__):
                with patch.dict(os.environ, {"CLAUDE_ADS_LOCALE": "en"}):
                    self.assertTrue(self.call_main(module, ["--help"])[1].startswith("usage:"))
                    self.assertTrue(self.call_main(module, ["--locale", "zh-CN", "--help"])[1].startswith("用法："))
                with patch.dict(os.environ, {"CLAUDE_ADS_LOCALE": "invalid"}):
                    self.assertEqual(self.call_main(module, ["--locale", "en", "--help"])[0], 0)

    def test_parser_errors_are_localized_and_redacted(self):
        for module in MODULES:
            with self.subTest(module=module.__name__):
                status, out, err = self.call_main(module, [])
                self.assertEqual(status, 2)
                self.assertEqual(out, "")
                self.assertIn("错误", err)
                self.assertNotIn("the following arguments are required", err)
                status, _, err = self.call_main(module, ["--locale", "token=private-locale-value"])
                self.assertEqual(status, 2)
                self.assertNotIn("private-locale-value", err)
        status, _, err = self.call_main(fetch_page, ["https://example.com", "--timeout", "token=private-timeout"])
        self.assertEqual(status, 2)
        self.assertIn("错误", err)
        self.assertNotIn("private-timeout", err)

    def test_direct_scripts_work_outside_repository_without_site_packages(self):
        # -S makes this smoke test independent of optional third-party packages.
        with tempfile.TemporaryDirectory() as workdir:
            for module in MODULES:
                with self.subTest(module=module.__name__):
                    completed = subprocess.run(
                        [sys.executable, "-S", str(SCRIPTS / (module.__name__ + ".py")), "--help"],
                        cwd=workdir, env={**os.environ, "PYTHONPATH": ""},
                        capture_output=True, text=True, check=False,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    self.assertIn("用法：", completed.stdout)
                    self.assertEqual(completed.stderr, "")

    def test_installed_scripts_layout_loads_adjacent_core(self):
        with tempfile.TemporaryDirectory() as workdir:
            scripts = Path(workdir) / "scripts"
            scripts.mkdir()
            for name in ("fetch_page.py", "url_utils.py"):
                shutil.copyfile(SCRIPTS / name, scripts / name)
            shutil.copytree(ROOT / "claude_ads_core", scripts / "claude_ads_core", ignore=shutil.ignore_patterns("__pycache__"))
            completed = subprocess.run(
                [sys.executable, "-S", str(scripts / "fetch_page.py"), "--locale", "en", "--help"],
                cwd=workdir, env={**os.environ, "PYTHONPATH": ""},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("Fetch a landing page", completed.stdout)

    def test_missing_optional_dependencies_report_selected_language(self):
        with patch.object(fetch_page, "requests", None):
            for locale, expected in (("zh-CN", "需要 requests"), ("en", "requests library required")):
                status, _, err = self.call_main(fetch_page, ["https://example.com", "--locale", locale])
                self.assertEqual(status, 1)
                self.assertIn(expected, err)
        with patch.object(analyze_landing, "sync_playwright", None):
            status, _, err = self.call_main(analyze_landing, ["https://example.com"])
            self.assertEqual(status, 1)
            self.assertIn("需要 playwright", err)
        with patch.object(capture_screenshot, "sync_playwright", None):
            status, _, err = self.call_main(capture_screenshot, [
                "https://example.com", "--egress-attestation", "unused.json", "--data-lifecycle", "unused.json",
            ])
            self.assertEqual(status, 1)
            self.assertIn("需要 playwright", err)

    def test_fetch_preserves_raw_html_headers_and_redirect_policy(self):
        html = '<html lang="en"><h1>Buy Now 原始页面</h1></html>'
        session = SimpleNamespace(trust_env=True)
        response = SimpleNamespace(status_code=200, headers={"Content-Type": "text/html"}, text=html)
        with patch.object(fetch_page, "requests", SimpleNamespace(Session=lambda: session)), patch.object(fetch_page, "validate_url", side_effect=lambda value: value), patch.object(fetch_page, "guarded_request", return_value=response) as dispatch:
            for locale in ("zh-CN", "en"):
                with locale_scope(locale):
                    result = fetch_page.fetch_page("https://example.com")
                self.assertEqual(result["content"], html)
                self.assertEqual(result["status_code"], 200)
                self.assertFalse(session.trust_env)
                self.assertEqual(dispatch.call_args.kwargs["headers"]["Accept-Language"], "en-US,en;q=0.5")
                self.assertEqual(dispatch.call_args.kwargs["timeout"], 30)
        with patch.object(fetch_page, "fetch_page", return_value=result):
            status, out, err = self.call_main(fetch_page, ["https://example.com"])
        self.assertIsNone(status)
        self.assertEqual(out, html + "\n")
        self.assertIn("状态码：200", err)

    def test_fetch_redirect_failure_is_localized_without_dispatching_target(self):
        response = SimpleNamespace(status_code=302, headers={"Location": "http://localhost/private"})
        def validate(value):
            if "localhost" in value:
                raise ValueError(t("tools.url.local_hostname"))
            return value
        with patch.object(fetch_page, "requests", SimpleNamespace(Session=lambda: SimpleNamespace())), patch.object(fetch_page, "validate_url", side_effect=validate), patch.object(fetch_page, "guarded_request", return_value=response) as dispatch:
            result = fetch_page.fetch_page("https://example.com")
        self.assertIn("已阻止重定向", result["error"])
        self.assertIsNone(result["content"])
        self.assertEqual(dispatch.call_count, 1)

    def test_fetch_external_error_stays_original_and_redacted(self):
        class RequestError(Exception):
            pass
        dependencies = SimpleNamespace(
            Session=lambda: SimpleNamespace(),
            exceptions=SimpleNamespace(Timeout=TimeoutError, SSLError=LookupError, ConnectionError=ConnectionError, RequestException=RequestError),
        )
        with patch.object(fetch_page, "requests", dependencies), patch.object(fetch_page, "validate_url", side_effect=lambda url: url), patch.object(fetch_page, "guarded_request", side_effect=RequestError("upstream unavailable token=private-token")):
            result = fetch_page.fetch_page("https://example.com")
        self.assertEqual(result["error"], "请求失败：upstream unavailable token=***")

    def test_landing_json_keys_grades_and_page_text_are_not_translated(self):
        result = landing_result()
        with patch.object(analyze_landing, "analyze_landing", return_value=result):
            status, out, err = self.call_main(analyze_landing, ["https://example.com", "--json"])
            english = self.call_main(analyze_landing, ["https://example.com", "--json", "--locale", "en"])[1]
            human = self.call_main(analyze_landing, ["https://example.com"])[1]
        self.assertEqual(status, 0)
        self.assertEqual(err, "")
        self.assertIn("标题", out)
        self.assertNotIn("\\u", out)
        payload = json.loads(out)
        self.assertEqual(payload, json.loads(english))
        self.assertEqual(payload["content"]["h1"], "Buy Now")
        self.assertEqual(payload["grades"]["G59_mobile_speed"], "PASS")
        self.assertIn("落地页质量分析", human)
        self.assertIn("[通过] G59_mobile_speed", human)
        self.assertIn("Original English 标题", human)

    def test_landing_failure_never_emits_grades(self):
        result = {**landing_result(), "error": "页面加载失败 token=private-token"}
        with patch.object(analyze_landing, "analyze_landing", return_value=result), patch.object(analyze_landing, "grade_landing", side_effect=AssertionError("must not grade")):
            status, out, err = self.call_main(analyze_landing, ["https://example.com", "--json"])
        self.assertEqual(status, 1)
        self.assertEqual(json.loads(out)["error"], "页面加载失败 token=***")
        self.assertNotIn("grades", json.loads(out))
        self.assertIn("错误", err)
        self.assertNotIn("private-token", out + err)

    def test_capture_preflight_failure_is_private_and_localized(self):
        with patch.object(capture_screenshot, "sync_playwright", Mock()) as browser, redirect_stderr(io.StringIO()):
            result = capture_screenshot.capture_screenshot("https://example.com/private?token=private-token", "capture.png")
        self.assertIn("截图预检失败", result["error"])
        self.assertFalse(result["success"])
        self.assertIsNone(result["output_locator"])
        self.assertNotIn("private-token", json.dumps(result))
        browser.assert_not_called()

    def test_capture_progress_and_receipt_preserve_machine_identity(self):
        attestation = SimpleNamespace(audit_reference=lambda: {"attestation_id": "test-attestation"})
        lifecycle = {"classification": "confidential", "purpose": "截图验证"}
        with tempfile.TemporaryDirectory() as workdir, patch.dict(os.environ, {"CLAUDE_ADS_OUTPUT_ROOT": workdir}), patch.object(capture_screenshot, "validate_contract"):
            screenshot = Path(workdir) / "页面.png"
            screenshot.write_bytes(PNG)
            receipt = capture_screenshot._write_capture_receipt(
                screenshot, "https://example.com/private?token=private-token", attestation, lifecycle,
            )
            encoded = receipt.read_text(encoding="utf-8")
            payload = json.loads(encoded)
            self.assertIn("截图验证", encoded)
            self.assertIn("页面.png", encoded)
            self.assertNotIn("\\\\u", encoded)
            self.assertNotIn("private-token", encoded)
            self.assertEqual(payload["operation"], "browser-screenshot-capture")
            self.assertEqual(payload["privacy_class"], "confidential")
            self.assertEqual(payload["artifact"]["sha256"], hashlib.sha256(PNG).hexdigest())
            self.assertEqual(payload["target"]["origin"], "https://example.com")
            result = {"success": True, "output_locator": "页面.png", "receipt_locator": "页面.png.receipt.json"}
            with patch.object(capture_screenshot, "sync_playwright", Mock()), patch.object(capture_screenshot, "load_egress_sandbox_attestation", return_value=attestation), patch.object(capture_screenshot, "load_contract", return_value=lifecycle), patch.object(capture_screenshot, "capture_screenshot", return_value=result) as capture:
                status, out, err = self.call_main(capture_screenshot, ["https://example.com", "--egress-attestation", "unused.json", "--data-lifecycle", "unused.json", "--viewport", "mobile"])
            self.assertIsNone(status)
            self.assertEqual(err, "")
            self.assertIn("正在截取 mobile 视口截图", out)
            self.assertIn("已保存产物：页面.png", out)
            self.assertIn("回执：页面.png.receipt.json", out)
            self.assertEqual(capture.call_args.kwargs["viewport"], "mobile")
            self.assertIs(capture.call_args.kwargs["egress_attestation"], attestation)

    def test_url_guards_remain_fail_closed_and_switch_language(self):
        for locale, expected in (("zh-CN", "非公网 IP"), ("en", "non-public IP")):
            with self.subTest(locale=locale), locale_scope(locale), patch.object(socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("127.0.0.1", 0))]):
                with self.assertRaisesRegex(ValueError, expected):
                    url_utils.validate_url("https://example.com")
        with self.assertRaisesRegex(ValueError, "出站网络沙箱证明"):
            url_utils.validate_browser_url("https://example.com")
        with self.assertRaisesRegex(ValueError, "URL 中不允许包含凭据"):
            url_utils.validate_url("https://name:private-password@example.com")
        with tempfile.TemporaryDirectory() as workdir:
            with self.assertRaisesRegex(ValueError, "超出配置的根目录"):
                url_utils.resolve_output_path("../outside", root=workdir)

    def test_generation_selection_errors_do_not_read_keys_or_dispatch(self):
        with patch.dict(os.environ, {"ADS_IMAGE_PROVIDER": "", "ADS_IMAGE_MODEL": ""}), patch.object(generate_image, "_get_api_key", side_effect=AssertionError("must not read credentials")):
            status, _, err = self.call_main(generate_image, ["Original prompt", "--model", "unchanged-model", "--data-lifecycle", "unused.json"])
        self.assertEqual(status, 2)
        self.assertIn("必须指定图像供应商", err)

    def test_image_generation_json_localizes_only_human_summary(self):
        prompt = "Do not translate this original creative prompt"
        with tempfile.TemporaryDirectory() as workdir, patch.dict(os.environ, {"CLAUDE_ADS_OUTPUT_ROOT": workdir}), patch.object(generate_image, "_get_api_key", return_value="private-key"), patch.object(generate_image, "load_contract", return_value={"classification": "internal"}), patch.object(generate_image, "generate_image", return_value=(PNG, 1, 1)) as provider:
            status, out, err = self.call_main(generate_image, [prompt, "--provider", "gemini", "--model", "operator-model", "--data-lifecycle", "unused.json", "--output", "广告.png", "--json"])
            self.assertIsNone(status)
            self.assertEqual(err, "")
            payload = json.loads(out)
            self.assertEqual(payload["provider"], "gemini")
            self.assertEqual(payload["model"], "operator-model")
            self.assertEqual(payload["ratio"], "1:1")
            self.assertEqual(payload["data_lifecycle"]["classification"], "internal")
            self.assertEqual(payload["prompt_sha256"], hashlib.sha256(prompt.encode()).hexdigest())
            self.assertEqual(payload["prompt_summary"], "[已脱敏：原始提示词仅临时使用，不会持久保存]")
            self.assertIn("广告.png", out)
            self.assertNotIn(prompt, out)
            self.assertNotIn("private-key", out)
            self.assertEqual(provider.call_args.args[:5], (prompt, "1:1", "gemini", "operator-model", "private-key"))
            self.assertEqual((Path(workdir) / "广告.png").read_bytes(), PNG)

    def test_gemini_prompt_language_and_retry_policy_do_not_follow_operator_locale(self):
        google = ModuleType("google")
        genai = ModuleType("google.genai")
        types = ModuleType("google.genai.types")
        google.genai = genai
        genai.types = types
        types.Part = SimpleNamespace(from_bytes=lambda **kwargs: kwargs)
        types.ImageConfig = lambda **kwargs: kwargs
        types.GenerateContentConfig = lambda **kwargs: kwargs
        response = SimpleNamespace(candidates=[SimpleNamespace(content=SimpleNamespace(parts=[SimpleNamespace(inline_data=SimpleNamespace(mime_type="image/png", data=PNG))]))])
        generate = Mock(side_effect=[RuntimeError("429 token=private-token")] * 3 + [response])
        genai.Client = lambda **kwargs: SimpleNamespace(models=SimpleNamespace(generate_content=generate))
        with tempfile.TemporaryDirectory() as workdir:
            reference = Path(workdir) / "reference.png"
            reference.write_bytes(PNG)
            with patch.dict(sys.modules, {"google": google, "google.genai": genai, "google.genai.types": types}), patch.object(generate_image.time, "sleep") as sleep, redirect_stderr(io.StringIO()) as stderr:
                data = generate_image.generate_gemini("Original English prompt", 1080, 1080, "private-key", "operator-model", str(reference))
            self.assertEqual(data, PNG)
            self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2, 4])
            self.assertEqual(generate.call_count, 4)
            contents = generate.call_args.kwargs["contents"]
            self.assertEqual(contents[1], "Generate an ad creative that matches the visual style, color palette, and aesthetic of the brand shown in the reference image. Original English prompt")
            self.assertEqual(generate.call_args.kwargs["model"], "operator-model")
            self.assertIn("速率限制", stderr.getvalue())
            self.assertNotIn("private-token", stderr.getvalue())

    def test_batch_failure_json_is_chinese_and_does_not_persist_external_error(self):
        with tempfile.TemporaryDirectory() as workdir:
            batch = Path(workdir) / "batch.json"
            batch.write_text(json.dumps([{"prompt": "private prompt", "output": "ad.png"}]), encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with patch.dict(os.environ, {"CLAUDE_ADS_OUTPUT_ROOT": workdir}), patch.object(generate_image, "validate_contract"), patch.object(generate_image, "generate_image", side_effect=RuntimeError("upstream rejected token=private-token")), redirect_stdout(out), redirect_stderr(err):
                generate_image.run_batch(str(batch), "assets", "gemini", "unchanged-model", "private-key", True, {})
            payload = json.loads(out.getvalue())[0]
            self.assertFalse(payload["generation_success"])
            self.assertEqual(payload["error"], "生成失败；请检查私有临时运行日志")
            self.assertIn("正在生成", err.getvalue())
            self.assertIn("upstream rejected token=***", err.getvalue())
            self.assertNotIn("private-token", out.getvalue() + err.getvalue())
            self.assertNotIn("private prompt", out.getvalue() + err.getvalue())

    def test_error_redaction_removes_url_userinfo_in_both_locales(self):
        for locale in ("zh-CN", "en"):
            with self.subTest(locale=locale), locale_scope(locale):
                raw = "upstream https://operator:private-pass@example.com/api?token=private-token failed"
                cleaned = url_utils.sanitize_error(RuntimeError(raw))
                self.assertEqual(cleaned, "upstream https://example.com/api?token=*** failed")
                self.assertNotIn("operator", cleaned)
                self.assertNotIn("private-pass", cleaned)
                self.assertNotIn("private-token", cleaned)

    def test_uncaught_filesystem_error_uses_sanitized_cli_diagnostic(self):
        for module in MODULES:
            with self.subTest(module=module.__name__), patch.object(module, "_main", side_effect=OSError("disk unavailable password=private-password")):
                status, out, err = self.call_main(module, [])
                self.assertEqual(status, 1)
                self.assertEqual(out, "")
                self.assertEqual(err, "错误：disk unavailable password=***\n")


if __name__ == "__main__":
    unittest.main()
