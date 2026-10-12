# Claude Ads 提示词模式

这些原创示例规定路由、工作代理契约、不确定性和变更安全。在行为微妙时使用；对于简单计算或路由明确的平台问题，不必加载。

## 1. 按目标产物路由

用户：“使用这张产品照片制作四个 Meta 广告概念。”

- 当用户需要概念、信息、吸引点或简报时，路由至 `ads-create`。
- 只有在已存在验证过的简报且请求图像文件时，才路由至 `ads-generate`。
- 当主要请求是产品摄影转换，而非组合式广告概念时，路由至 `ads-photoshoot`。
- 若请求同时包含概念和渲染，先执行 create，获得批准，再执行 generate。不要跳过中间清单。

## 2. 有界平台工作代理

```json
{
  "objective": "Audit Google conversion measurement for the supplied window",
  "scope": ["conversion taxonomy", "tag and enhanced-conversion evidence", "deduplication"],
  "exclusions": ["creative", "budget", "account mutation"],
  "evidence_policy": ["account export", "official current sources"],
  "privacy_class": "confidential",
  "mutation_authority": "read-only",
  "inputs": ["run:20260711-demo/account-snapshot.json"],
  "output_contract": "Finding[] v1.0.0",
  "verification": ["schema validate", "cite every failed control"],
  "recovery": ["return needs_input for missing tag evidence"]
}
```

工作代理将发现和恢复提示返回给协调者。它不写入 `google-audit-results.md`，不计算平台分数，也不扩展至预算工作。

## 3. 缺失证据

用户：“我的 Meta CPA 翻倍了。暂停表现最差的广告。”

如果提供的数据缺少转化延迟、归因定义、支出、样本量、近期变更或当前远端状态：

1. 仅在窗口可比时记录观察到的 CPA 变化。
2. 对变更返回 `needs_input`。
3. 提供只读诊断和明确的数据请求。
4. 不要应用固定 CPA 倍数，也不要推断观察到的最差广告导致了账户层面的变化。

## 4. 已批准变更

批准仅对所呈现的精确变更计划有效：

```json
{
  "account_id": "redacted-demo",
  "object_id": "campaign-123",
  "operation": "pause",
  "before": {"status": "ACTIVE"},
  "after": {"status": "PAUSED"},
  "reason": "Operator-approved policy containment",
  "blast_radius": "one campaign",
  "idempotency_key": "sha256:...",
  "verification_window": "immediate plus 15 minutes",
  "rollback": {"operation": "restore_status", "value": "ACTIVE"}
}
```

如果远端状态不再匹配 `before`，停止并重新生成计划。针对某一广告系列、预算或日期的批准，绝不转移至其他对象。

## 5. 研究与独立验证

研究工作代理提出来源记录和受影响声明。独立的来源验证者检查权威性、日期、范围、地理区域、方法、许可证，以及声明与来源的适配性。只有之后，协调者才可更新规范参考文档和测试。社区帖子可以产生研究线索；不能确立官方 API 或政策声明。

## 6. 部分完成的全面审计

如果 Google、Meta 和跟踪成功，但所请求的 Amazon 工作代理认证失败：

- 保留成功的平台结果。
- 将结果包标记为 `partial`。
- 从数值组合健康状况中排除 Amazon，并展示其缺失权重。
- 返回认证恢复步骤。
- 绝不要将交付物标题写成“完整多平台审计”。
