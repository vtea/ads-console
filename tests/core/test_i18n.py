from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from claude_ads_core.i18n import LocaleError, locale_scope, resolve_locale, t, validate_catalogs
from scripts.build_locale import _document_path, _safe_path, inspect_documents, inspect_guidance, inspect_installer_messages, inspect_metadata


ROOT = Path(__file__).resolve().parents[2]


class LocaleTests(unittest.TestCase):
    def test_default_and_explicit_language(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(resolve_locale(), "zh-CN")
            self.assertIn("中文", t("metadata.short_description"))
            self.assertEqual(t("metadata.short_description", locale="en"), "Source-grounded paid media operations")

    def test_environment_and_scope_are_isolated(self):
        with patch.dict(os.environ, {"CLAUDE_ADS_LOCALE": "en"}):
            self.assertEqual(resolve_locale(), "en")
            with locale_scope("zh-CN"):
                self.assertEqual(resolve_locale(), "zh-CN")
                self.assertEqual(resolve_locale("en"), "en")
            self.assertEqual(resolve_locale(), "en")

    def test_bad_locale_and_missing_key_fail_closed(self):
        for invalid in ("../en", "zh", "fr"):
            with self.assertRaises(LocaleError):
                resolve_locale(invalid)
        with self.assertRaises(LocaleError):
            t("missing.message")

    def test_catalog_keys_and_parameters_match(self):
        self.assertEqual(validate_catalogs(), [])

    def test_generated_documents_are_current(self):
        errors, _ = inspect_documents(ROOT)
        self.assertEqual(errors, [])

    def test_discovery_metadata_is_chinese(self):
        errors, _ = inspect_metadata(ROOT)
        self.assertEqual(errors, [])

    def test_installer_messages_and_guidance_are_current(self):
        errors, _ = inspect_installer_messages(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(inspect_guidance(ROOT), [])

    def test_unmanaged_documents_are_not_generation_targets(self):
        for path in ("docs/user-notes.md", ".claude/settings.json", "scripts/run.py"):
            with self.assertRaises(ValueError):
                _document_path(ROOT, path)

    def test_package_data_covers_locale_files(self):
        import tomllib
        from scripts.release import package_files
        core = ROOT / "claude_ads_core"
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        patterns = project["tool"]["setuptools"]["package-data"]["claude_ads_core"]
        selected = {path.relative_to(core).as_posix() for pattern in patterns for path in core.glob(pattern) if path.is_file()}
        expected = {path.relative_to(core).as_posix() for path in (core / "locales").rglob("*") if path.is_file()}
        self.assertTrue(expected <= selected, expected - selected)
        paths = ["claude_ads_core/" + path for path in expected]
        self.assertEqual(set(package_files(paths)), set(paths))

    def test_paths_cannot_escape_or_follow_links(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for invalid in ("../escape", "/absolute", "nested/../../escape", "back\\slash"):
                with self.assertRaises(ValueError):
                    _safe_path(root, invalid)
            (root / "link").symlink_to(root / "target")
            with self.assertRaises(ValueError):
                _safe_path(root, "link/file.md")


if __name__ == "__main__":
    unittest.main()
