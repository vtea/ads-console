"""Regression checks for v2 reference-layer evidence and safety boundaries."""

from __future__ import annotations

import json


AUDIT_SOURCES = {
    "amazon": "amazon-ads-api-official",
    "apple": "apple-ads-api-official",
    "youtube": "youtube-google-ads-video-official",
    "reddit": "reddit-business-help",
    "pinterest": "pinterest-conversions-api",
    "snapchat": "snap-marketing-api",
    "x": "x-conversion-tracking",
}


def test_additional_audits_name_registered_sources_and_runtime_boundary(repo_root, english_documents_root):
    ledger = json.loads(
        (repo_root / "control-plane/manifests/source-ledger.json").read_text(
            encoding="utf-8"
        )
    )
    registered = {source["id"] for source in ledger["sources"]}

    for platform, source_id in AUDIT_SOURCES.items():
        text = (english_documents_root / f"ads/references/{platform}-audit.md").read_text(
            encoding="utf-8"
        )
        assert source_id in registered
        assert f"`{source_id}`" in text
        assert "## Runtime evaluation contract" in text
        assert "`unknown`" in text
        assert "`not_applicable`" in text
        assert "does not provide a live" in text


def test_reference_layer_rejects_legacy_automatic_actions(english_documents_root):
    references = english_documents_root / "ads/references"
    text = "\n".join(
        (references / name).read_text(encoding="utf-8")
        for name in (
            "gaql-notes.md",
            "thinking-framework.md",
            "tiktok-creative-specs.md",
            "image-providers.md",
        )
    )
    forbidden = (
        "True intentional broad match is ALWAYS",
        "The 3× Kill Rule",
        "There is no alternative",
        "default image generation provider",
        "auto-uses `gemini",
    )
    for phrase in forbidden:
        assert phrase not in text


def test_creative_guides_require_current_specification_evidence(english_documents_root):
    for platform in ("google", "meta", "linkedin", "tiktok", "microsoft", "youtube"):
        text = (
            english_documents_root / f"ads/references/{platform}-creative-specs.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        assert "## Specification gate" in text
        assert "official source ID" in normalized
        assert "does not imply" in normalized or "no live" in normalized


def test_chinese_additional_audits_require_evidence_and_disclaim_live_adapters(repo_root):
    ledger = json.loads(
        (repo_root / "control-plane/manifests/source-ledger.json").read_text(encoding="utf-8")
    )
    registered = {source["id"] for source in ledger["sources"]}
    for platform, source_id in AUDIT_SOURCES.items():
        text = (repo_root / f"ads/references/{platform}-audit.md").read_text(encoding="utf-8")
        assert source_id in registered
        assert f"`{source_id}`" in text
        for phrase in (
            "## 运行时评估契约", "`unknown`", "`not_applicable`",
            "本参考文档仅用于咨询和读取导出数据", "不提供实时", "读取器或变更适配器",
            "注明日期的官方来源 ID 或账户证据",
        ):
            assert phrase in text, f"{platform} omits {phrase!r}"


def test_chinese_reference_layer_rejects_automatic_actions_and_assumed_providers(repo_root):
    requirements = {
        "gaql-notes.md": (
            "将历史分类报告为 `unknown`；不得将其转化为失败或自动否定关键词操作",
            "检查注明日期的变更历史、搜索词、当前匹配行为、广告系列控制和负责人意图",
        ),
        "thinking-framework.md": (
            "在形成任何假设之前，导出实际账户数据",
            "不要急着解决它们",
            "没有具体建议、也没有逐项负责人分配",
        ),
        "image-providers.md": (
            "不承诺默认图像提供商、模型、MCP 服务器、价格、速率限制或宽高比集合",
            "若未安装合适能力，返回生成简报和 `needs_input`；不得声称已产出图像文件",
            "不得在随包 JSON、仓库或客户报告中存储凭据、原始私密提示词",
            "生成创建的是草稿，而不是获授权的广告上传或账户变更",
        ),
    }
    for name, phrases in requirements.items():
        text = (repo_root / "ads/references" / name).read_text(encoding="utf-8")
        for phrase in phrases:
            assert phrase in text, f"{name} omits {phrase!r}"


def test_chinese_creative_guides_require_live_specs_and_draft_only_output(repo_root):
    for platform in ("google", "meta", "linkedin", "tiktok", "microsoft", "youtube"):
        text = (repo_root / f"ads/references/{platform}-creative-specs.md").read_text(encoding="utf-8")
        for phrase in ("## 规格关卡", "官方来源 ID", "草稿", "不意味着", "实时"):
            assert phrase in text, f"{platform} omits {phrase!r}"
        assert "`needs_input`" in text, platform
