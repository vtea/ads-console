# Microsoft Advertising 审计控制项目录

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

- `microsoft-advertising-api-official`：[Microsoft Advertising API 概览](https://learn.microsoft.com/en-us/advertising/guides/?view=bingads-13)
- `microsoft-uet-official`：[Microsoft UET 设置](https://learn.microsoft.com/en-us/advertising/msa-help/hlp_ba_conc_uet_setup_master)
- `microsoft-conversions-api-official`：[Microsoft Conversions API 指南](https://learn.microsoft.com/en-us/advertising/guides/uet-conversion-api-integration?view=bingads-13)
- `microsoft-google-import-official`：[Microsoft Google Ads 导入映射](https://learn.microsoft.com/en-us/advertising/msa-help/hlp_ba_conc_importwhatinfo)

## 控制项注册表

| ID | 审计意图 | 运行时处理 |
|---|---|---|
| MS01 | UET 标签已安装 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS02 | 增强型转化 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS03 | Google Ads 导入验证 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS04 | 品牌联合分发控制 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS05 | Audience Network 设置 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS06 | 出价策略一致性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS07 | 新客优化适用性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS08 | 广告系列结构 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS09 | 预算分配 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS10 | LinkedIn 档案定向适用性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS11 | RSA 素材数量 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS12 | Multimedia Ads | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS13 | 广告文案独特性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS19 | Action Extension | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS20 | Filter Link Extension | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS14 | Copilot 和新版位适用性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS15 | 转化目标 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS16 | 跨平台 CPC 背景 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS17 | 转化率比较 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS18 | 展示份额 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS-SI1 | 定时导入状态 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS-CM1 | Consent Mode 合规 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS-CT1 | CTV 广告资源覆盖 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS-VD1 | 视频广告资源利用 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| MS25 | AI Max for Search 适用性 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS26 | Copilot 中的 Offer Highlights | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS27 | Audience Generation | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS28 | PMax 最终 URL 报告 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS29 | Clarity AI Visibility | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS30 | 电商平台上的 Brand Agents | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS31 | Merchant Center 中的 UCP | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS32 | Copilot Checkout | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS33 | Rewarded Portals | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS34 | Import Center | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS35 | 自动出价 + 自定义列 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS36 | 表现变化根因分析 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS37 | 转化跟踪诊断 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS38 | 数据驱动归因采用 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS39 | Conversion API | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS40 | Ad Studio Brand Kit | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| MS41 | API 传输迁移证据 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |

## 建议边界

建议必须指出观察到的证据、账户专属基线或负责人阈值、预期机制、置信度、可逆下一步、衡量窗口和回滚条件。不要仅从控制项名称推断建议。
