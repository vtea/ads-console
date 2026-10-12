"""Metadata-level collision tests for platform and lifecycle routing.

These are deterministic guards around skill descriptions. Model-level forward
evaluations remain a separate release gate.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


STOP = {
    "a", "an", "and", "or", "the", "to", "for", "from", "with", "our",
    "my", "of", "in", "on", "paid", "ads", "ad", "campaign", "campaigns",
    "audit", "review", "use", "when",
}


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9+]+", text.lower())
        if len(token) > 1 and token not in STOP
    }


def _score(prompt: str, description: str) -> int:
    return len(_tokens(prompt) & _tokens(description))


def test_platform_and_workflow_descriptions_win_declared_collisions(english_skill_descriptions, repo_root: Path):
    fixture = json.loads(
        (repo_root / "evals" / "platform-workflow-routing.json").read_text(encoding="utf-8")
    )
    failures: list[str] = []
    for case in fixture:
        expected = case["expected_skill"]
        expected_desc = english_skill_descriptions.get(expected)
        if expected_desc is None:
            failures.append(f"{case['id']}: missing expected skill {expected}")
            continue
        expected_score = _score(case["prompt"], expected_desc)
        if expected_score < 2:
            failures.append(f"{case['id']}: expected description has weak score {expected_score}")
        for forbidden in case["forbidden_skills"]:
            forbidden_desc = english_skill_descriptions.get(forbidden)
            if forbidden_desc is None:
                failures.append(f"{case['id']}: missing forbidden skill {forbidden}")
                continue
            forbidden_score = _score(case["prompt"], forbidden_desc)
            if expected_score <= forbidden_score:
                failures.append(
                    f"{case['id']}: {expected} score {expected_score} does not beat "
                    f"{forbidden} score {forbidden_score}"
                )
    assert not failures, "Routing description collisions:\n  " + "\n  ".join(failures)


def test_near_miss_language_does_not_appear_as_paid_platform_intent(english_skill_descriptions):
    near_misses = {
        "ads-reddit": "Write moderation rules for an organic subreddit community",
        "ads-pinterest": "Pin this note to the project dashboard",
        "ads-snapchat": "Take a quick snapshot of the local test results",
        "ads-x": "Label the x axis on this performance chart",
    }
    for skill, prompt in near_misses.items():
        description = english_skill_descriptions[skill]
        assert _score(prompt, description) < 2, f"near miss overlaps too broadly with {skill}"


# Short operator requests, not copies of complete description sentences. These
# guard lexical routing in the generated Chinese surface; they are not a model
# dispatch simulation and do not modify the retained English evaluation pack.
CHINESE_ROUTING_CASES = (
    ("检查 Reddit 社区定向", "ads-reddit", ("ads-pinterest", "ads-x")),
    ("检查 Pinterest 目录销售", "ads-pinterest", ("ads-reddit", "ads-snapchat")),
    ("检查 Snapchat AR Lens 广告", "ads-snapchat", ("ads-pinterest", "ads-x")),
    ("检查 X 对话定向", "ads-x", ("ads-reddit", "ads-apple")),
    ("规划媒体预算分配", "ads-budget", ("ads-math", "ads-plan")),
    ("生成广告图片", "ads-generate", ("ads-creative", "ads-create", "ads-photoshoot")),
    ("制作产品摄影变体", "ads-photoshoot", ("ads-create", "ads-generate")),
    ("创建广告系列概念", "ads-create", ("ads-dna", "ads-creative", "ads-generate")),
    ("分析品牌语气和视觉识别", "ads-dna", ("ads-create", "ads-creative")),
    ("配置 API 令牌和钥匙串", "ads-setup", ("ads-launch", "ads-research")),
    ("卸载并保留无关技能", "ads-validate", ("ads-setup", "ads-optimize")),
    ("审查搜索词报告与否定关键词", "ads-google", ("ads-meta", "ads-microsoft")),
    ("设计 A/B 测试的样本量", "ads-test", ("ads-monitor", "ads-plan")),
    ("渲染客户报告 PDF", "ads-report", ("ads-plan", "ads-monitor")),
    ("检查服务器端跟踪去重", "ads-server-side-tracking", ("ads-attribution", "ads-meta")),
    ("汇总 Meta 与 Google 转化", "ads-attribution", ("ads-google", "ads-meta")),
    ("检查预算节奏和投放异常", "ads-monitor", ("ads-report", "ads-create")),
)


def _chinese_tokens(text: str) -> set[str]:
    """CJK bigrams plus platform names, without a segmentation dependency."""
    tokens = set(re.findall(r"[a-z][a-z0-9+]*", text.lower()))
    for segment in re.findall(r"[一-鿿]+", text):
        tokens.update(segment[index:index + 2] for index in range(len(segment) - 1))
    return tokens - {"ads", "ad", "api", "广告", "平台", "付费", "进行", "检查"}


def _chinese_score(prompt: str, description: str) -> int:
    return len(_chinese_tokens(prompt) & _chinese_tokens(description))


def test_chinese_short_intents_win_declared_collisions(skill_descriptions):
    failures = []
    for prompt, expected, forbidden_skills in CHINESE_ROUTING_CASES:
        expected_score = _chinese_score(prompt, skill_descriptions[expected])
        if expected_score < 2:
            failures.append(f"{prompt!r}: {expected} has weak score {expected_score}")
        for forbidden in forbidden_skills:
            forbidden_score = _chinese_score(prompt, skill_descriptions[forbidden])
            if expected_score <= forbidden_score:
                failures.append(
                    f"{prompt!r}: {expected} ({expected_score}) does not beat "
                    f"{forbidden} ({forbidden_score})"
                )
    assert not failures, "Chinese routing collisions:\n  " + "\n  ".join(failures)


def test_chinese_near_misses_do_not_imply_paid_platform_intent(skill_descriptions):
    near_misses = {
        "ads-reddit": "写社区版规",
        "ads-pinterest": "把便签固定到项目看板",
        "ads-snapchat": "截取本地测试快照",
        "ads-x": "给图表的 x 轴加标签",
    }
    for skill, prompt in near_misses.items():
        assert _chinese_score(prompt, skill_descriptions[skill]) < 2, (
            f"{prompt!r} overlaps too broadly with {skill}"
        )
