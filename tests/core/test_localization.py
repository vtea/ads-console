"""Chinese-default core regressions; no blanket English locale fixture."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pytest

from claude_ads_core.adapters import GenericCSVExportAdapter, MutationDisabledError, NativeCSVExportAdapter
from claude_ads_core.cli import main
from claude_ads_core.cli_support import LocaleArgumentParser, LocaleRawDescriptionHelpFormatter, cli_locale
from claude_ads_core.contracts import ContractError, validate_contract
from claude_ads_core.i18n import locale_scope, resolve_locale, validate_catalogs
from claude_ads_core.product_status import _next_blocker, evaluate_product_status
from claude_ads_core.scoring import ScoringError, score_account
from tests.core.test_contracts import report_bundle


@pytest.fixture(autouse=True)
def _no_locale_environment(monkeypatch):
    monkeypatch.delenv("CLAUDE_ADS_LOCALE", raising=False)


def test_core_catalogs_have_identical_keys_and_placeholders():
    assert validate_catalogs() == []


@pytest.mark.parametrize("command", [None, "validate", "score", "portfolio", "status", "next", "render", "report", "ingest-export"])
def test_each_core_help_is_chinese_by_default(command, capsys):
    argv = [command] if command else []
    with pytest.raises(SystemExit) as caught:
        main([*argv, "--help"])
    assert caught.value.code == 0
    output = capsys.readouterr().out
    assert output.startswith("用法：")
    assert "显示此帮助信息并退出" in output
    assert "show this help" not in output
    assert "--locale" in output


@pytest.mark.parametrize("argv", [["--locale", "en", "score", "--help"], ["score", "--help", "--locale=en"]])
def test_explicit_english_before_or_after_command_controls_help(argv, capsys):
    with pytest.raises(SystemExit) as caught:
        main(argv)
    assert caught.value.code == 0
    output = capsys.readouterr().out
    assert output.startswith("usage: ")
    assert "show this help message and exit" in output
    assert resolve_locale() == "zh-CN"


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        ([], "缺少必需参数"),
        (["score"], "缺少必需参数"),
        (["score", "--controls"], "需要一个参数值"),
        (["validate", "wrong", "input.json"], "无效选项值"),
        (["render", "input.json", "--format", "wrong"], "无效选项值"),
        (["status", "--unexpected"], "无法识别的参数"),
        (["--locale", "wrong"], "不支持的语言"),
        (["--locale"], "需要一个参数值"),
    ],
)
def test_argparse_diagnostics_keep_standard_exit_two(argv, message, capsys):
    with pytest.raises(SystemExit) as caught:
        main(argv)
    assert caught.value.code == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err.startswith("用法：")
    assert "错误：" in output.err
    assert message in output.err


def test_environment_and_explicit_locale_precedence(monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_ADS_LOCALE", "en")
    assert cli_locale([]) == "en"
    assert cli_locale(["status", "--locale", "zh-CN"]) == "zh-CN"
    with locale_scope("zh-CN"):
        assert cli_locale([]) == "zh-CN"
        assert cli_locale(["--locale=en", "status"]) == "en"
    monkeypatch.setenv("CLAUDE_ADS_LOCALE", "invalid")
    assert cli_locale(["--locale=en"]) == "en"
    with pytest.raises(SystemExit) as caught:
        cli_locale([])
    assert caught.value.code == 2
    assert "不支持的语言" in capsys.readouterr().err


def test_locale_preflight_does_not_parse_unrelated_arguments():
    assert cli_locale(["--locale", "en", "--local-file", "x", "--other=raw"]) == "en"
    assert cli_locale(["--", "--locale", "en"]) == "zh-CN"


def test_locale_namespace_is_not_overwritten_by_subparser():
    with locale_scope("en"):
        parser = LocaleArgumentParser(prog="test")
        parser.add_subparsers(dest="command", required=True).add_parser("check")
        assert parser.parse_args(["--locale", "en", "check"]).locale == "en"
        assert parser.parse_args(["check", "--locale", "zh-CN"]).locale == "zh-CN"


def test_argument_types_counts_and_mutex_diagnostics(capsys):
    parser = LocaleArgumentParser(prog="test")
    parser.add_argument("--count", type=int)
    parser.add_argument("--pair", nargs=2)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--one", action="store_true")
    group.add_argument("--two", action="store_true")
    for argv, message in [(["--count", "bad"], "无效的 int 值"), (["--pair", "one"], "需要 2 个参数值"), (["--one", "--two"], "不能与参数 --one 同时使用")]:
        with pytest.raises(SystemExit) as caught:
            parser.parse_args(argv)
        assert caught.value.code == 2
        assert message in capsys.readouterr().err


def test_raw_description_formatter_preserves_layout_and_localized_usage():
    parser = LocaleArgumentParser(prog="test", description="line one\n  line two", formatter_class=LocaleRawDescriptionHelpFormatter)
    output = parser.format_help()
    assert output.startswith("用法：")
    assert "line one\n  line two" in output


def test_argparse_global_translation_and_concurrent_contexts_are_unchanged():
    original_gettext = argparse._
    def help_for(locale):
        with locale_scope(locale):
            return LocaleArgumentParser(prog="test").format_help()
    with ThreadPoolExecutor(max_workers=2) as executor:
        chinese, english = list(executor.map(help_for, ["zh-CN", "en"]))
    assert chinese.startswith("用法：")
    assert english.startswith("usage: ")
    assert argparse._ is original_gettext
    assert argparse.ArgumentParser(prog="plain").format_help().startswith("usage: ")
    assert resolve_locale() == "zh-CN"


@pytest.mark.parametrize("locale", ["zh-CN", "en"])
def test_parser_and_json_error_redact_credentials(locale, capsys):
    secret_url = "https://demo-user:demo-password@example.invalid/?token=private-value&code=private-code"
    with locale_scope(locale):
        parser = LocaleArgumentParser(prog="test")
        with pytest.raises(SystemExit):
            parser.parse_args(["--unknown", secret_url, "--token", "secret-option-value", "sk-live-fixturetoken123"])
        output = capsys.readouterr().err
        for forbidden in ["demo-user", "demo-password", "private-value", "private-code", "secret-option-value", "sk-live-fixturetoken123"]:
            assert forbidden not in output
        assert "[REDACTED]" in output
    assert main(["ingest-export", "--locale", locale, "--platform", secret_url, "unused.csv"]) == 2
    error = json.loads(capsys.readouterr().err)
    assert "private-value" not in error["error"]
    assert "demo-password" not in error["error"]


def test_invalid_locale_never_echoes_opaque_value(capsys):
    with pytest.raises(SystemExit):
        cli_locale(["--locale", "private-arbitrary-value"])
    assert "private-arbitrary-value" not in capsys.readouterr().err


def test_business_errors_keep_ids_params_and_exception_hierarchy():
    with pytest.raises(ContractError) as caught:
        validate_contract("account-snapshot", [])
    error = caught.value
    assert isinstance(error, ValueError)
    assert error.message_id == "core.validation.object"
    assert error.params == {"path": "$"}
    assert str(error) == "$ 必须为对象"
    with locale_scope("en"):
        assert str(error) == "$ must be an object"
    wrapped = ScoringError(error)
    assert wrapped.message_id == error.message_id
    assert wrapped.params == error.params
    assert str(wrapped) == "$ 必须为对象"


@pytest.mark.parametrize("locale", ["zh-CN", "en"])
def test_scoring_and_snapshot_machine_values_are_locale_independent(locale, repo_root):
    bundle = report_bundle()
    with locale_scope(locale):
        result = score_account(bundle["control_definitions"], bundle["findings"], {"tracking": 100}).to_dict()
        snapshot = GenericCSVExportAdapter("google").read_snapshot(repo_root / "tests/fixtures/exports/google.csv")
    assert result["health_score"] == 100.0
    assert result["status"] == "normal"
    assert snapshot["spend"] == 42.5
    assert snapshot["account"]["platform"] == "google"


@pytest.mark.parametrize("operation", ["draft_changes", "apply_changes", "verify_changes", "rollback"])
def test_default_chinese_mutation_guard_still_denies_every_operation(operation):
    adapter = GenericCSVExportAdapter("google")
    with pytest.raises(MutationDisabledError, match="为只读") as caught:
        getattr(adapter, operation)({})
    assert isinstance(caught.value, RuntimeError)
    assert caught.value.message_id == "core.adapter.mutation_disabled"
    assert adapter.discover_capabilities().writes_enabled is False


def test_disabled_native_profiles_fail_closed_in_chinese():
    adapter = NativeCSVExportAdapter("amazon")
    with pytest.raises(RuntimeError, match="已禁用"):
        adapter.read_snapshot("does-not-exist.csv")
    assert "官方来源" in adapter.discover_capabilities().capabilities[0].disabled_reason
    assert "The curated" in adapter.profile.disabled_reason


def test_nested_workflow_error_remains_localizable_and_strict(repo_root):
    path = repo_root / "tests/fixtures/workflows/valid-artifacts.json"
    payload = json.loads(path.read_text(encoding="utf-8"))["mutation-plan"]
    payload["operation"] = "permanent-delete"
    for locale, expected in [("zh-CN", "永久删除"), ("en", "deletion is outside")]:
        with locale_scope(locale), pytest.raises(ContractError, match=expected) as caught:
            validate_contract("mutation-plan", payload)
        assert caught.value.message_id == "core.workflow.permanent_deletion"
    payload["operation"] = "pause"
    payload["data_lifecycle"]["retention"]["minimum_seconds"] = True
    with pytest.raises(ContractError, match="必须为整数"):
        validate_contract("mutation-plan", payload)


def test_status_localizes_presentation_without_modifying_evidence(repo_root):
    manifests = repo_root / "control-plane/manifests"
    before = {path: path.read_bytes() for path in manifests.glob("*.json")}
    chinese = evaluate_product_status(repo_root, as_of=date(2026, 7, 11))
    with locale_scope("en"):
        english = evaluate_product_status(repo_root, as_of=date(2026, 7, 11))
    assert chinese["next_blocker"]["kind"] == english["next_blocker"]["kind"]
    assert chinese["next_blocker"]["summary"].startswith("原始证据说明：")
    assert english["next_blocker"]["summary"] in chinese["next_blocker"]["summary"]
    for key in chinese.keys() - {"next_blocker"}:
        assert chinese[key] == english[key]
    assert before == {path: path.read_bytes() for path in before}


def test_next_blocker_keeps_opaque_external_reason_and_priority():
    arguments = dict(stale=[], unverified=[], blockers=["Original operator rationale {untouched}"], release_gate=None, disabled_profiles=[], disabled_capabilities=[], levels=[])
    result = _next_blocker(**arguments)
    assert result["id"] == "maturity-blocker-001"
    assert result["summary"].endswith(arguments["blockers"][0])
    arguments["stale"] = [{"claim_id": "test-claim", "refresh_due": "2026-01-01"}]
    result = _next_blocker(**arguments)
    assert result["id"] == "test-claim"
    assert "过期" in result["summary"]
    assert "自动降低" in result["rationale"]
