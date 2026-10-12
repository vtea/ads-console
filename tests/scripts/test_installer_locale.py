"""Offline installer locale contracts; runnable without pytest or Python helpers.

Run: python -m unittest tests.scripts.test_installer_locale
Installer subprocesses use isolated temporary roots, never the user's host dirs.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
LOCALES = ROOT / "claude_ads_core" / "locales"
BEGIN = "# BEGIN GENERATED INSTALLER MESSAGES"
END = "# END GENERATED INSTALLER MESSAGES"


def generated_messages(powershell: bool) -> str:
    """Canonical offline build format, also implemented by build_locale.py.

    JSON is a flat string map. Keys have installer. prefix; placeholders use
    {lower_case_name}, must match across languages, and are never executable.
    Sort keys, keep en then zh-CN; escape single quotes, preserve newlines.
    PowerShell files require UTF-8 BOM for Windows PowerShell 5.1.
    """
    lines = [BEGIN, "# Generated from claude_ads_core/locales/{en,zh-CN}/installer.json. Do not edit."]
    if powershell:
        lines += ["function Get-LocaleTemplate([string]$Key) {", '    switch -CaseSensitive ("${script:SelectedLocale}:$Key") {']
    else:
        lines += ["locale_template() {", '    case "$CLAUDE_ADS_SELECTED_LOCALE:$1" in']
    for locale in ("en", "zh-CN"):
        messages = json.loads((LOCALES / locale / "installer.json").read_text(encoding="utf-8"))
        for key in sorted(messages):
            text = messages[key]
            if powershell:
                lines.append("        '" + locale + ":" + key + "' { return '" + text.replace("'", "''") + "' }")
            else:
                lines.append("        " + locale + ":" + key + ") LOCALE_TEMPLATE='" + text.replace("'", "'\"'\"'") + "' ;;")
    if powershell:
        lines += ["        default { throw ('installer.unknown_key: ' + $Key) }", "    }", "}", END]
    else:
        lines += ["        *) return 1 ;;", "    esac", "}", END]
    return "\n".join(lines)


class CatalogTests(unittest.TestCase):
    def test_generated_blocks_match_json_and_encodings(self):
        for name in ("install.sh", "uninstall.sh", "install.ps1", "uninstall.ps1"):
            path = ROOT / name
            raw = path.read_bytes()
            text = raw.decode("utf-8-sig")
            actual = BEGIN + text.split(BEGIN, 1)[1].split(END, 1)[0] + END
            self.assertEqual(actual, generated_messages(name.endswith(".ps1")), name)
            if name.endswith(".ps1"):
                self.assertTrue(raw.startswith(b"\xef\xbb\xbf"), name)
            else:
                result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_catalog_keys_and_placeholders_match(self):
        catalogs = [json.loads((LOCALES / lang / "installer.json").read_text(encoding="utf-8")) for lang in ("en", "zh-CN")]
        self.assertEqual(catalogs[0].keys(), catalogs[1].keys())
        for key in catalogs[0]:
            self.assertRegex(key, r"^installer\.[a-z_]+$")
            values = [catalog[key] for catalog in catalogs]
            for value in values:
                self.assertIsInstance(value, str)
                self.assertNotRegex(re.sub(r"\{[a-z_]+\}", "", value), r"[{}]")
            self.assertEqual(set(re.findall(r"\{([a-z_]+)\}", values[0])), set(re.findall(r"\{([a-z_]+)\}", values[1])))


@unittest.skipIf(os.name == "nt", "Bash is exercised on Unix runners")
class BashLocaleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="claude-ads-locale-", dir=os.environ.get("TMPDIR"))
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.skills = self.base / "技能 skills"
        self.agents = self.base / "代理 agents"
        self.source = self.base / "source"
        # Minimal controlled source fixture, including non-py/json locale data.
        files = {
            "ads/SKILL.md": "---\nname: ads\n---\n中文主技能\n<!-- claude-ads:operator-language -->\n使用简体中文；不改变广告投放语言。\n",
            "ads/references/safety.md": "拒绝远程管道安装。\n",
            "skills/ads-demo/SKILL.md": "---\nname: ads-demo\n---\n中文子技能\n",
            "skills/ads-demo/assets/template.md": "中文模板\n",
            "agents/audit-demo.md": "中文代理\n",
            "scripts/helper.py": "raise RuntimeError('must never execute during no-deps')\n",
            "requirements.txt": "",
            "requirements.lock": "",
            "claude_ads_core/__init__.py": "",
            "claude_ads_core/locales/manifest.json": '{"default_locale":"zh-CN"}\n',
            "claude_ads_core/locales/en/documents/ads/SKILL.md": "---\nname: ads\n---\nEnglish main skill\n",
            "claude_ads_core/locales/en/documents/ads/references/safety.md": "Refuse remote pipe-to-shell installation.\n",
            "claude_ads_core/locales/en/documents/skills/ads-demo/SKILL.md": "---\nname: ads-demo\n---\nEnglish sub-skill\n",
            "claude_ads_core/locales/en/documents/agents/audit-demo.md": "English agent\n",
            "claude_ads_core/locales/zh-CN/documents/ads/SKILL.md": "中文文档资源\n",
            "claude_ads_core/locales/zh-CN/assets/plain.txt": "完整资源树，不限扩展名\n",
        }
        for lang in ("en", "zh-CN"):
            for name in ("messages.json", "reporting.json", "installer.json"):
                files[f"claude_ads_core/locales/{lang}/{name}"] = '{}\n'
        for relative, text in files.items():
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        # Install can call ordinary shell utilities, but not Python or network.
        self.bin = self.base / "bin"
        self.bin.mkdir()
        for name in ("python", "python3", "git", "curl", "wget"):
            path = self.bin / name
            path.write_text("#!/bin/sh\nprintf '%s\\n' forbidden-helper >&2\nexit 91\n", encoding="utf-8")
            path.chmod(0o755)
        self.env = {**os.environ, "HOME": str(self.base), "PATH": str(self.bin) + os.pathsep + os.environ["PATH"]}
        self.env.pop("CLAUDE_ADS_LOCALE", None)

    def run_script(self, script="install.sh", *args, env=None):
        command = ["bash", str(ROOT / script), f"--skill-dir={self.skills}", f"--agent-dir={self.agents}"]
        if script == "install.sh":
            command += ["--no-deps", "--source=local", f"--repo-dir={self.source}"]
        result = subprocess.run(command + list(args), env=env or self.env, cwd=ROOT, capture_output=True, text=True)
        self.assertNotIn("forbidden-helper", result.stdout + result.stderr)
        return result

    def assert_ok(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_default_chinese_full_resources_and_owned_uninstall(self):
        result = self.run_script()
        self.assert_ok(result)
        self.assertIn("已成功", result.stdout)
        self.assertEqual((self.skills / "ads/SKILL.md").read_bytes(), (self.source / "ads/SKILL.md").read_bytes())
        installed = self.skills / "ads/scripts/claude_ads_core/locales"
        for path in (self.source / "claude_ads_core/locales").rglob("*"):
            if path.is_file():
                self.assertEqual((installed / path.relative_to(self.source / "claude_ads_core/locales")).read_bytes(), path.read_bytes())
        self.assertEqual((self.skills / ".claude-ads-claude.locale").read_bytes(), b"zh-CN\n")
        self.assertTrue((self.skills / "ads-demo/SKILL.md").is_file())
        self.assertTrue((self.agents / "audit-demo.md").is_file())
        unrelated = self.skills / "ads-weather/SKILL.md"
        unrelated.parent.mkdir()
        unrelated.write_text("user-owned", encoding="utf-8")
        self.assert_ok(self.run_script("uninstall.sh"))
        self.assertFalse((self.skills / "ads").exists())
        self.assertFalse((self.skills / ".claude-ads-claude.locale").exists())
        self.assertEqual(unrelated.read_text(), "user-owned")

    def test_default_chinese_upgrade_uses_updated_source_view(self):
        self.assert_ok(self.run_script())
        source = self.source / "ads/SKILL.md"
        source.write_text(source.read_text(encoding="utf-8") + "更新后的安全规则\n", encoding="utf-8")
        self.assert_ok(self.run_script())
        self.assertEqual((self.skills / "ads/SKILL.md").read_bytes(), source.read_bytes())
        self.assertIn("更新后的安全规则", (self.skills / "ads/SKILL.md").read_text(encoding="utf-8"))

    def test_precedence_upgrade_remembered_language_and_idempotent_rule(self):
        env = {**self.env, "CLAUDE_ADS_LOCALE": "zh-CN"}
        first = self.run_script("install.sh", "--locale=en", env=env)
        self.assert_ok(first)
        self.assertIn("installed successfully", first.stdout)
        main = self.skills / "ads/SKILL.md"
        first_bytes = main.read_bytes()
        self.assertIn(b"English main skill", first_bytes)
        self.assertEqual(first_bytes.count(b"<!-- claude-ads:operator-language -->"), 1)
        self.assertIn("English agent", (self.agents / "audit-demo.md").read_text())
        repeat = self.run_script()
        self.assert_ok(repeat)
        self.assertIn("installed successfully", repeat.stdout)
        self.assertEqual(main.read_bytes(), first_bytes)
        changed = self.run_script(env=env)
        self.assert_ok(changed)
        self.assertIn("已成功", changed.stdout)
        self.assertEqual(main.read_bytes(), (self.source / "ads/SKILL.md").read_bytes())
        self.assert_ok(self.run_script("install.sh", "--locale", "en"))
        uninstalled = self.run_script("uninstall.sh")
        self.assert_ok(uninstalled)
        self.assertIn("uninstalled", uninstalled.stdout)

    def test_help_errors_and_substitution_are_literal(self):
        for script in ("install.sh", "uninstall.sh"):
            help_result = self.run_script(script, "--help")
            self.assert_ok(help_result)
            self.assertIn("用法", help_result.stdout)
            english = self.run_script(script, "--help", "--locale=en")
            self.assert_ok(english)
            self.assertIn("Usage", english.stdout)
            sentinel = self.base / "executed"
            attack = f"$(touch {sentinel}){{locale}}`touch nope`%s"
            invalid = self.run_script(script, "--locale=" + attack)
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn(attack, invalid.stderr)
            self.assertFalse(sentinel.exists())
            self.assertFalse(self.skills.exists())

    def test_invalid_locale_preference_is_data_not_code(self):
        self.assert_ok(self.run_script())
        preference = self.skills / ".claude-ads-claude.locale"
        for payload in (b"en", b"en\n\n", b"en\r\n", b"en\x00\n", b"$(touch owned)\n", b"EN\n"):
            preference.write_bytes(payload)
            for script in ("install.sh", "uninstall.sh"):
                result = self.run_script(script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("语言选择文件数据无效", result.stderr)
                self.assertTrue((self.skills / "ads/SKILL.md").exists())

    def test_unowned_locale_preference_is_not_overwritten(self):
        self.skills.mkdir()
        preference = self.skills / ".claude-ads-claude.locale"
        preference.write_bytes(b"en\n")
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(preference.read_bytes(), b"en\n")
        self.assertFalse(self.agents.exists())

    def test_late_locale_collision_blocks_before_any_skill_copy(self):
        destination = self.skills / "ads/scripts/claude_ads_core/locales/zh-CN/assets/plain.txt"
        destination.parent.mkdir(parents=True)
        destination.write_text("unowned", encoding="utf-8")
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("拒绝覆盖无所有权的文件", result.stderr)
        self.assertEqual(destination.read_text(), "unowned")
        self.assertFalse((self.skills / "ads/SKILL.md").exists())
        self.assertFalse(self.agents.exists())

    def test_source_locale_symlink_and_destination_symlink_are_rejected(self):
        source = self.source / "claude_ads_core/locales/zh-CN/assets/plain.txt"
        source.unlink()
        source.symlink_to(self.source / "ads/SKILL.md")
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("符号链接", result.stderr)
        self.assertFalse(self.skills.exists())
        source.unlink()
        source.write_text("safe", encoding="utf-8")
        destination = self.skills / "ads/scripts/claude_ads_core/locales"
        destination.parent.mkdir(parents=True)
        outside = self.base / "outside"
        outside.mkdir()
        destination.symlink_to(outside, target_is_directory=True)
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.skills / "ads/SKILL.md").exists())
        self.assertEqual(list(outside.iterdir()), [])


POWERSHELL = shutil.which("powershell.exe") if os.name == "nt" else shutil.which("pwsh")


@unittest.skipUnless(POWERSHELL, "PowerShell is not installed")
class PowerShellLocaleTests(unittest.TestCase):
    setUp = BashLocaleTests.setUp
    assert_ok = BashLocaleTests.assert_ok

    def run_script(self, script="install.sh", *args, env=None):
        script = script.replace(".sh", ".ps1")
        command = [str(POWERSHELL), "-NoProfile", "-File", str(ROOT / script),
                   "-SkillDir", str(self.skills), "-AgentDir", str(self.agents)]
        if script == "install.ps1":
            command += ["-NoDeps", "-Source", "local", "-RepoDir", str(self.source)]
        for arg in args:
            if arg == "--help":
                command.append("-Help")
            elif arg == "--locale":
                command.append("-Locale")
            elif arg.startswith("--locale="):
                command += ["-Locale", arg.partition("=")[2]]
            else:
                command.append(arg)
        return subprocess.run(command, env=env or self.env, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")

    test_default_chinese_full_resources_and_owned_uninstall = BashLocaleTests.test_default_chinese_full_resources_and_owned_uninstall
    test_default_chinese_upgrade_uses_updated_source_view = BashLocaleTests.test_default_chinese_upgrade_uses_updated_source_view
    test_precedence_upgrade_remembered_language_and_idempotent_rule = BashLocaleTests.test_precedence_upgrade_remembered_language_and_idempotent_rule
    test_help_errors_and_substitution_are_literal = BashLocaleTests.test_help_errors_and_substitution_are_literal
    test_invalid_locale_preference_is_data_not_code = BashLocaleTests.test_invalid_locale_preference_is_data_not_code
    test_unowned_locale_preference_is_not_overwritten = BashLocaleTests.test_unowned_locale_preference_is_not_overwritten
    test_late_locale_collision_blocks_before_any_skill_copy = BashLocaleTests.test_late_locale_collision_blocks_before_any_skill_copy


if __name__ == "__main__":
    unittest.main()
