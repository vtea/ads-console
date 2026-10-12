from __future__ import annotations

import re
from pathlib import Path


REFERENCE_NAMES = (
    "benchmarks.md",
    "platform-specs.md",
    "compliance.md",
    "compliance-requirements.md",
    "conversion-tracking.md",
    "bidding-strategies.md",
    "budget-allocation.md",
    "mcp-integration.md",
    "automation-tier-classifier.md",
    "meta-ai-stack.md",
)

LEGACY_BRITTLE_FRAGMENTS = (
    "all cited figures verified current",
    "70/20/10",
    "3× kill rule",
    "20% rule (scale up)",
    "50 conversions per week per ad set",
    "200 calls/hour",
    "22-state map",
    "server-side conversion apis are now mandatory",
    "dda (data-driven attribution) is now mandatory",
    "creative similarity score >60%",
    "always overclaims 20-40%",
)

REQUIRED_SOURCE_IDS = {
    "google-smart-bidding-official",
    "google-rsa-official",
    "google-consent-modeling-official",
    "google-consent-modeling-improvement-official",
    "tiktok-events-api-official",
    "eu-ai-act-article-50-official",
    "eu-dsa-official",
    "hhs-tracking-guidance-official",
    "ftc-endorsement-guides-official",
    "google-ads-mcp-official",
    "amazon-ads-mcp-official",
    "tiktok-ads-mcp-official",
    "microsoft-ads-mcp-official",
    "meta-andromeda-engineering-official",
    "meta-ai-ads-ranking-official",
    "meta-gem-training-official",
    "meta-sequence-ranking-official",
}


def _reference_texts(documents_root: Path) -> dict[str, str]:
    root = documents_root / "ads" / "references"
    return {
        name: (root / name).read_text(encoding="utf-8") for name in REFERENCE_NAMES
    }


def test_cross_platform_references_have_verification_and_refresh_metadata(english_documents_root):
    for name, text in _reference_texts(english_documents_root).items():
        assert re.search(r"\*\*Verified:\*\* 20\d{2}-\d{2}-\d{2}", text), name
        assert "**Refresh" in text, name


def test_cross_platform_references_do_not_restore_legacy_universal_claims(english_documents_root):
    corpus = "\n".join(_reference_texts(english_documents_root).values()).lower()
    for fragment in LEGACY_BRITTLE_FRAGMENTS:
        assert fragment not in corpus


def test_precise_current_claims_use_named_first_party_or_regulator_sources(english_documents_root):
    corpus = "\n".join(_reference_texts(english_documents_root).values())
    cited_ids = set(re.findall(r"`([a-z0-9][a-z0-9-]+)`", corpus))
    assert REQUIRED_SOURCE_IDS <= cited_ids

    markdown_links = re.findall(r"\[[^]]+\]\((https://[^)]+)\)", corpus)
    assert len(markdown_links) >= len(REQUIRED_SOURCE_IDS)
    assert all(" " not in link for link in markdown_links)


def test_benchmarks_are_contextual_and_vendor_evidence_is_labeled(english_documents_root):
    texts = _reference_texts(english_documents_root)
    assert "Benchmarks are comparison evidence, not pass/fail controls" in texts[
        "benchmarks.md"
    ]
    assert "vendor-supplied" in texts["benchmarks.md"]
    assert "vendor-supplied" in texts["meta-ai-stack.md"]


def test_meta_architecture_does_not_adopt_unverified_issue_prescriptions(english_documents_root):
    meta = " ".join(_reference_texts(english_documents_root)["meta-ai-stack.md"].lower().split())
    for unsupported in (
        "1-2 campaigns max",
        "campaign consolidation | 1-2 campaigns",
        "4×4 creative framework",
        "cpmr (cost per 1,000 reached)",
    ):
        assert unsupported not in meta
    assert "cited practitioner articles, not a current meta source" in meta


def test_consent_reference_does_not_invent_an_unpublished_threshold(english_documents_root):
    conversion = " ".join(
        _reference_texts(english_documents_root)["conversion-tracking.md"].lower().split()
    )
    assert "100 ad clicks" not in conversion
    assert "does not publish another numeric click threshold" in conversion


def test_automation_and_mcp_do_not_imply_write_authority(english_documents_root):
    texts = _reference_texts(english_documents_root)
    assert "disabled by default" in texts["mcp-integration.md"]
    assert "A server's write capability does not upgrade" in texts[
        "mcp-integration.md"
    ]
    assert "not an account-health score" in texts["automation-tier-classifier.md"]


def test_chinese_cross_platform_references_have_dates_and_registered_source_links(repo_root):
    texts = _reference_texts(repo_root)
    for name, text in texts.items():
        assert re.search(r"\*\*已核验：\*\* 20\d{2}-\d{2}-\d{2}", text), name
        assert "**刷新" in text, name
    corpus = "\n".join(texts.values())
    cited_ids = set(re.findall(r"`([a-z0-9][a-z0-9-]+)`", corpus))
    assert REQUIRED_SOURCE_IDS <= cited_ids
    links = re.findall(r"\[[^]]+\]\((https://[^)]+)\)", corpus)
    assert len(links) >= len(REQUIRED_SOURCE_IDS)
    assert all(" " not in link for link in links)
    for fragment in LEGACY_BRITTLE_FRAGMENTS:
        assert fragment not in corpus.lower()


def test_chinese_benchmarks_require_comparability_and_label_vendor_evidence(repo_root):
    texts = _reference_texts(repo_root)
    benchmarks = texts["benchmarks.md"]
    for phrase in (
        "基准是比较证据，不是通过/失败控制项",
        "不得仅因账户偏离跨行业中位数就降低其分数",
        "任何可能改变结论的字段未知时，将基准标记为 `provisional`",
        "平台发布的提升数字为 `vendor-supplied`；案例研究不是通用基线",
        "归因窗口、货币、转化定义或漏斗阶段不同的来源，未经标准化并披露换算，不得混合",
        "若没有适合账户的当前来源包，省略数字，将其转为衡量问题",
    ):
        assert phrase in benchmarks
    meta = texts["meta-ai-stack.md"]
    assert "表现提升由供应商提供，未经 Claude Ads 独立验证" in meta
    assert "引用的是从业者文章，而非当前 Meta 来源" in meta
    assert "都不是 Claude Ads 的产品规则" in meta
    assert "Meta 的系统架构不能证明通用账户配置" in meta
    assert "只有观察到的账户问题才成为健康发现" in meta


def test_chinese_consent_and_capi_require_evidence_not_universal_mandates(repo_root):
    conversion = _reference_texts(repo_root)["conversion-tracking.md"]
    for phrase in (
        "哈希处理不是同意，也不会使原本被禁止的收集行为合法化",
        "未公布另一个数值点击阈值。不得推断",
        "这些是资格事实，而非通用最低账户预算，也不是建模转化保证",
        "同一业务操作的浏览器和服务器副本必须共享平台文档规定的去重字段",
        "不要编造通用字段映射",
        "重试具有幂等性",
        "绝不要将跨平台的平台归因转化相加",
        "单纯缺少服务器端集成属于机会或覆盖缺口",
        "除非当前平台要求或观察到的衡量损失使其更严重",
        "绝不要仅凭配置截图推断健康状况",
    ):
        assert phrase in conversion
    assert "100 次广告点击" not in conversion
    assert "100 ad clicks" not in conversion


def test_chinese_automation_and_mcp_cannot_grant_write_authority(repo_root):
    texts = _reference_texts(repo_root)
    mcp = texts["mcp-integration.md"]
    for phrase in (
        "MCP 服务器是传输机制和工具接口，不是更改广告账户的授权",
        "服务器的写入能力不会提升 Claude Ads 能力清单的状态",
        "只有经过测试的精确操作可以启用",
        "每个具备写入能力的工具默认禁用",
        "负责人批准该精确变更和账户定义的上限",
        "幂等键、审计目标位置、验证窗口和回滚操作",
        "永久删除仍在 v2 范围之外",
        "任何第二次应用之前，都须使用幂等键读取远端状态",
    ):
        assert phrase in mcp
    automation = texts["automation-tier-classifier.md"]
    assert "而非账户健康分数" in automation
    assert "没有对精确能力的验证、批准、审计、远端验证和回滚，就不得写入" in automation
    assert "自动化采用程度和新颖性属于不评分的背景信息" in automation
