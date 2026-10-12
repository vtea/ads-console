# Claude Ads 评分契约

生产评分引擎是健康分数的唯一权威。提示词、代理、报告和测试必须调用该引擎，而不是重新实现本文档。

## 输出

将四种输出分开：

1. `health_score`：观察到的表现和实施健康状况，0-100。
2. `evidence_coverage`：适用控制项权重中结果已知的比例。
3. `regulatory_exposure`：独立的 P0/P1 风险摘要，而非分数填充。
4. `opportunities`：不评分的可选、测试版、高级或不符合资格的能力。

不要发布字母评级。每个分数都要搭配覆盖状态和数据窗口。

## 控制项状态

- `pass`：证据满足控制项。
- `fail`：证据不满足控制项。
- `unknown`：适用，但证据缺失或不确定。
- `not_applicable`：控制项不适用于此账户或广告系列。

`not_applicable` 从健康和覆盖率分母中移除。`unknown` 从健康计算中移除，但仍保留在覆盖率分母中。

## 严重程度权重

| 严重程度 | 权重 | 含义 |
| --- | ---: | --- |
| critical | 5 | 即时且重大的收入、数据、账户、隐私或政策风险 |
| high | 3 | 重大的表现或运营风险 |
| medium | 1 | 有意义但紧迫性较低的改进 |
| informational | 0 | 背景或不评分的机会 |

严重程度表示控制项失败时的影响。不得因功能新颖或具有战略吸引力就抬高。

## 类别计算

对每个类别，仅使用结果已知且适用的控制项：

```text
category_health = 100 * sum(pass_weight) / sum(known_control_weight)
```

其中 `control_weight` 是严重程度权重。失败控制项得零分。类别不得将其声明的类别权重乘入每个控制项。

类别覆盖率为：

```text
category_coverage = 100 * sum(known_control_weight) / sum(applicable_control_weight)
```

平台健康状况在类别计算后应用标准化类别权重：

```text
platform_health = sum(category_health * category_weight)
```

调用方必须提供带版本的评分配置，其类别权重总计精确为 100；生产引擎验证此不变量。能力清单描述可执行平台范围，其本身不是评分配置。没有适用控制项的类别被移除，该次运行中其余类别权重重新归一化。

## 覆盖状态

| 覆盖率 | 状态 | 报告规则 |
| ---: | --- | --- |
| 80-100% | graded | 发布健康分数并附覆盖率 |
| 60-79.99% | provisional | 发布健康分数并标记为暂定 |
| 低于 60% | insufficient_evidence | 不得将健康分数呈现为账户评级 |

即使总覆盖率仍高于 80%，未知的关键控制项也必须出现在优先事项输出中。

## 平台类别

以下是初始产品参考配置。它们不是从平台行为推断而来，也不会仅因出现在此文件中就变为可执行：

- Google：measurement 25、waste 20、structure 15、keywords 15、creative 15、settings 10。
- Meta：measurement 25、creative 25、structure 20、audiences 15、delivery 10、policy 5。
- YouTube：measurement 25、creative 25、structure 20、audiences 15、delivery 10、policy 5。
- LinkedIn：measurement 25、audiences 20、creative 20、structure 15、delivery 15、policy 5。
- TikTok：measurement 25、creative 25、delivery 15、structure 15、audiences 15、policy 5。
- Microsoft：measurement 25、structure 20、delivery 15、creative 15、audiences 15、policy 10。
- Apple：measurement 25、structure 20、keywords 20、creative 15、delivery 15、policy 5。
- Amazon：measurement 20、retail 20、targeting 20、structure 15、creative 10、delivery 10、policy 5。
- Reddit：measurement 25、structure 20、creative 20、audiences 15、delivery 10、policy 10。
- Pinterest：measurement 25、retail 20、creative 20、structure 15、audiences 10、policy 10。
- Snapchat：measurement 25、creative 20、structure 20、audiences 15、delivery 10、policy 10。
- X：measurement 25、structure 20、creative 20、audiences 15、delivery 10、policy 10。

实际使用前，将所选配置绑定到运行清单，并验证其类别名称与适用控制项匹配。仅通过带版本的产品决定和回归分析更改配置。

可执行状态位于 `control-plane/manifests/control-registry.json` 和 `control-plane/manifests/scoring-profiles.json`。当前 v1 配置中仅 Meta 已启用（M01–M03，severity high，measurement=100）；其余十一个平台明确禁用：目录行仍是带类型的信息性观察列表或来源刷新发现项。禁用配置不会产生账户健康分数，且已批准证据覆盖率为零。不要将上述参考权重复制到运行中，也不要在提示词中指定严重程度。

## 组合健康状况

使用相同时间窗口的平台支出：

```text
portfolio_health = sum(platform_health * platform_spend_share)
```

支出不可用时，对平台使用等权重，并将结果标记为暂定。不得将证据不足的平台纳入数值汇总；明确展示其缺失权重及由此产生的组合覆盖率。

## 去重与适用性

- 将一个规范风险建模为一个评分控制项，可包含多个观察。
- 不要将根本跟踪故障及其每个症状都分别作为处罚评分。
- 在宣布控制项适用前，记录功能可用性、账户资格、地理区域、广告系列类型和成熟度。
- 观察列表和即将变化的事项在影响账户前保持不评分。
- 不要将采用新宣布功能作为健康状况评分。

## 建议

分数用于确定调查优先级；不会授权变更。每项建议必须引用相关发现、声明置信度、考虑样本量和转化延迟，并在任何账户写入前通过变更关卡。
