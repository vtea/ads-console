# TikTok Ads 审计控制项目录

<!-- 目录 ID 沿用旧版运行时；当前平台事实需要注明日期的来源或账户证据。 -->

## 运行时评估契约

- 从目标、地理区域、账户类型、广告系列类型、数据窗口、转化延迟、样本量和功能访问权限开始。
- 当广告载体或要求不适用时，返回 `not_applicable`；当所需证据缺失时，返回 `unknown`。
- 只有当前账户证据、负责人定义的经济数据和适用官方来源共同确立预期时，条件性控制项才可影响健康状况。
- 产品采用、可用性、测试版访问、公告知晓程度和供应商报告的表现不是健康控制项。仅将其记录为不评分的发现。
- 不要从本目录采用固定的平台级阈值、广泛基准、上线日期、停用日期，或通用网络、出价、预算、受众、创意或归因规则。
- 在运行时验证可变事实。已确认的政策、支持状态或迁移要求，在产生发现之前，需有自身的当前声明覆盖。

## 来源覆盖边界

下列已登记来源仅涵盖声明台账中所述的衡量、API 和导入基础。它们并不支持本目录中每个具名产品或控制项。在存在更具体的当前声明之前，将这些名称视为路由标签，并收集最新官方或账户内证据。

## 官方证据

- `tiktok-business-api-official`：[TikTok API for Business](https://business-api.tiktok.com/portal)
- `tiktok-events-api-official`：[TikTok Events API](https://ads.tiktok.com/help/article/events-api)
- `tiktok-pixel-official`：[TikTok Pixel](https://ads.tiktok.com/help/article/tiktok-pixel)

## 控制项注册表

| ID | 审计意图 | 运行时处理 |
|---|---|---|
| T05 | 创意测试能力 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T06 | 竖屏视频格式 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T07 | 具有原生观感的内容 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T08 | 吸引点策略 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T09 | 创意疲劳 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T10 | Spark Ads 适用性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T20 | TikTok Shop 集成 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T21 | Video Shopping Ads | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T22 | 说明文字 SEO | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T23 | 声音/音乐使用 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T24 | CTA 按钮 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T25 | 安全区域合规 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T01 | TikTok Pixel 已安装 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T02 | Events API + ttclid | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T11 | 出价策略 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T12 | 预算充足性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T13 | 学习证据 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T03 | 广告系列结构 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T04 | Smart+ 适用性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T14 | Search Ads 适用性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T15 | 版位选择 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T16 | 分时投放 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T17 | CTR 基准 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T18 | CPA 目标 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T19 | 视频完播率 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T-SR1 | 与 In-Feed 并行的 Search Ads | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T-GM1 | Shop 广告系列的 GMV Max | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T-EA1 | Events API Gateway 设置 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| T29 | TikTok Ads MCP Server | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T30 | TikTok Ads Skills | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T31 | Smart+ One Buying Experience 模块控制 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T32 | Smart+ Music Autofix | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T33 | Smart+ 创意报告 + 多 URL | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T34 | 用于应用目标的 Smart+ | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T35 | TopReach + Creative Sequencing | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T36 | Branded Buzz | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T37 | Search Hubs | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T38 | Symphony AI 创意功能组合 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T39 | TikTok GO 预订集成 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T40 | Mini Series & Mini Games | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T41 | Collage Carousel 可用性 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T42 | One Asset Manager | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T43 | 用于 Pulse Core Max 的 View+ | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T44 | TikTok Market Scope | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T45 | TikTok Real + 英国无广告订阅 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| T46 | GMV Max 市场扩展 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |

## 建议边界

建议必须指出观察到的证据、账户专属基线或负责人阈值、预期机制、置信度、可逆下一步、衡量窗口和回滚条件。不要仅从控制项名称推断建议。
