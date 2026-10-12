# LinkedIn Ads 审计控制项目录

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

- `linkedin-marketing-api-official`：[LinkedIn 营销开发者平台](https://learn.microsoft.com/en-us/linkedin/marketing/overview)
- `linkedin-conversion-tracking-official`：[LinkedIn 转化跟踪](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/conversion-tracking)
- `linkedin-conversions-api-official`：[LinkedIn Conversions API 用例](https://learn.microsoft.com/en-us/linkedin/marketing/conversions/conversions-usecase)

## 控制项注册表

| ID | 审计意图 | 运行时处理 |
|---|---|---|
| L01 | Insight Tag 已安装 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L02 | Conversions API 适用性与状态 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L03 | 职位名称定向精度 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L04 | 公司规模筛选 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L05 | 职级定向 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L06 | Matched Audiences | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L07 | ABM 公司名单适用性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L08 | 受众扩展设置 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L09 | 预测受众 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L10 | Thought Leader Ads 适用性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L11 | 广告格式多样性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L12 | 视频广告存在 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L13 | 创意刷新频率 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L14 | Lead Gen Form 摩擦 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L15 | Lead Gen Form CRM 集成 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L16 | 出价策略适当 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L17 | 预算充足性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L18 | Ad Set 目标一致性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L19 | A/B 测试正在进行 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L20 | 频次监控 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L21 | CTR 基准 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L22 | CPC 基准 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L23 | 线索质量跟踪 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L24 | 转化跟踪归因 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L25 | 人口统计报告审查 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L-CRM1 | 用于收入归因的 CRM 集成 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L-EU1 | 欧盟 Sponsored Messaging 合规 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| L28 | Off-Platform Event Ads | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L29 | Campaign Manager 术语更名陷阱 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L30 | Accelerate 自动创建广告系列 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L31 | AI Ad Variants | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L32 | Career Journey 定向 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L33 | Reserved Ads | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L34 | First Impression Ads | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L35 | BrandLink 扩展 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L36 | Wire | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L37 | Thought Leader Event Ads | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L38 | CTV 扩展 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L39 | Revenue Attribution Report 中的 Company Attribution | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L40 | 视频指标的 MRC 认证 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L41 | Company Intelligence API | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L42 | Flexible Ad Creation 可用性 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L43 | SMB 自动定向 + Draft with AI | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L44 | Campaign Manager 中的实时 CRM 数据 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L45 | Ads Agency Certification | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| L46 | 自然信号相关性 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |

## 建议边界

建议必须指出观察到的证据、账户专属基线或负责人阈值、预期机制、置信度、可逆下一步、衡量窗口和回滚条件。不要仅从控制项名称推断建议。
