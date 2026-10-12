# 仓库状态契约

对 `/ads status` 和 `/ads next` 使用确定性核心；不要根据文字说明推断就绪状态，也不要发起网络调用。

```bash
python -m claude_ads_core status --root . --as-of YYYY-MM-DD
python -m claude_ads_core next --root . --as-of YYYY-MM-DD
```

可选地传入 `--release-gate PATH`，使用精确的发布关卡报告。`artifact-order-v1` 政策按以下顺序恰好选择一个结果：未经验证的关键声明、过时的关键声明、第一个已声明的成熟度阻碍项、第一个规范失败的发布检查、第一个禁用评分配置、第一个禁用能力，然后是最低的未满足成熟度等级。仓库清单和可选报告是唯一证据。必需输入缺失或格式错误时，按失败关闭原则处理。
