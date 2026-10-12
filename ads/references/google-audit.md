# Google Ads 审计控制项目录

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

- `google-ads-api-official`：[Google Ads API 文档](https://developers.google.com/google-ads/api/docs/start)
- `google-ads-conversion-goals-official`：[Google Ads 转化目标](https://support.google.com/google-ads/answer/10995103)
- `google-ads-enhanced-conversions-official`：[Google Ads 增强型转化](https://support.google.com/google-ads/answer/9888656)
- `google-ads-dsa-ad-rank-official`：[关于动态搜索广告、广告评级和表现](https://support.google.com/google-ads/answer/7018712)
- `google-ads-keyword-prioritization-official`：[关于 Google Ads 账户内广告组和素材组的优先级](https://support.google.com/google-ads/answer/2756257)
- `google-ads-dsa-targets-official`：[关于动态搜索广告的定位目标](https://support.google.com/google-ads/answer/7334472)

## 控制项注册表

| ID | 审计意图 | 运行时处理 |
|---|---|---|
| G42 | 转化操作已定义 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G43 | 增强型转化适用性与状态 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G44 | 服务器端跟踪 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G45 | 同意信号和区域要求 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G46 | 转化窗口适当 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G47 | 微观与宏观转化分离 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G48 | 归因模型 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G49 | 转化价值分配 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-CT1 | 无重复计数 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-CT2 | GA4 已关联且数据流通 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-CT3 | Google Tag 正常触发 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G13 | 搜索词审计时效性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G14 | 否定关键词治理 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G15 | 已应用账户级否定关键词 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G16 | 重大不相关搜索词支出 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G17 | 广泛匹配控制 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G18 | 近似变体污染 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G19 | 搜索词可见性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-WS1 | 零转化关键词调查 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G01 | 广告系列命名规范 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G02 | 广告组命名规范 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G03 | 广告组主题一致性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G04 | 广告系列碎片化 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G05 | 品牌与非品牌分离 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G06 | Performance Max 适用性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G07 | Search + PMax 重叠 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G08 | 预算分配匹配优先级 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G09 | 预算投放节奏 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G10 | 广告投放时间已配置 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G11 | 地理定向准确性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G12 | 网络设置 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G20 | 平均质量得分 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G21 | 关键 QS 关键词 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G22 | 预期 CTR 组成项 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G23 | 广告相关性组成项 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G24 | 落地页体验 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G25 | 主要关键词 QS | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-KW1 | 零展示关键词 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-KW2 | 关键词与广告相关性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G26 | 每广告组 RSA | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G27 | RSA 标题数量 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G28 | RSA 描述数量 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G29 | RSA 广告效力 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G30 | RSA 固定策略 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G31 | PMax 素材覆盖 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G32 | PMax 视频素材存在 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G33 | PMax 素材组数量 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G34 | PMax 最终 URL 扩展 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G35 | 广告文案与关键词相关性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-AD1 | 广告新鲜度 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-AD2 | CTR 背景 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G50 | 附加链接 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G51 | 附加宣传信息 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G52 | 结构化摘要 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G53 | 附加图片 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G54 | 附加电话 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G55 | 附加潜在客户表单 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G56 | 已应用受众细分 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G57 | Customer Match 名单 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G58 | 版位排除 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G59 | 落地页移动速度 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G60 | 落地页相关性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G61 | 落地页 schema 标记 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-PM1 | 受众信号已配置 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-PM2 | PMax 广告效力 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-PM3 | 品牌增量效果审查 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-PM4 | 搜索主题 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-PM5 | 否定关键词 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-PM6 | PMax 否定关键词适用性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-AI1 | AI Max for Search 评估 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G-DG1 | Demand Gen 图像素材 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-DG2 | VAC 迁移状态 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-DG3 | Demand Gen 频次上限丢失 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G-CTV1 | CTV Floodlight 跟踪限制 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G36 | 智能出价策略处于活跃状态 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G37 | 目标 CPA/ROAS 合理性 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G38 | 学习阶段状态 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G39 | 预算受限广告系列 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G40 | 手动 CPC 理由 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G41 | 组合出价策略 | 条件性证据控制项：确定适用性，并依据当前账户证据评估；否则返回 `unknown` 或 `not_applicable`。 |
| G81 | Ask Advisor 治理 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G82 | Business Agent for Leads 资格 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G83 | Direct Offers 扩展 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G84 | AI Mode 广告格式准备情况 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G85 | 旅程感知出价 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G86 | PMax + Shopping 上的 Smart Bidding Exploration | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G87 | 广告系列总预算 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G88 | 需求驱动投放节奏 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G89 | Meridian 衡量适用性 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G90 | Qualified Future Conversions | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G91 | Attributed Branded Searches | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G92 | Asset Studio Gemini Omni 准备情况 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G93 | Demand Gen 功能组合 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G94 | Ads Advisor 安全功能 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G95 | DSA 迁移准备证据 | 不评分的来源刷新发现：核实当前官方可用性、账户资格和治理需求；未采用绝不算失败。 |
| G96 | 同一广告系列中 Search 与 DSA 重叠 | 条件性证据控制项：根据当前账户证据确定适用性（同一广告系列中已启用的动态搜索广告组和已启用的关键词定向广告组、动态广告定位范围，例如所有网页或提供的 URL，以及各广告组投放的搜索词），然后评估 DSA 广告组是否正在投放该广告系列关键词也覆盖的搜索词，以及负责人是否有意采用该路由；在运行时核实当前官方关键词与 DSA 选择规则（`google-ads-dsa-ad-rank-official`、`google-ads-keyword-prioritization-official`），除非有当前证据支持，否则不得将重叠描述为竞价中的自我竞争或广告评级稀释；否则返回 `unknown` 或 `not_applicable`。 |
| G97 | 跨广告系列关键词重复 | 条件性证据控制项：根据当前账户证据确定适用性（同一账户中多个广告系列启用了相同关键词文本和匹配类型，包括共享预算、近乎休眠和按地理拆分的广告系列），然后依据搜索词和展示证据评估实际触发哪个广告系列，以及重复是否为有意设置；在运行时核实当前官方账户内关键词优先级规则（`google-ads-keyword-prioritization-official`），除非有当前证据支持，否则不得将重复报告为自我竞价或成本膨胀；否则返回 `unknown` 或 `not_applicable`。 |

## 建议边界

建议必须指出观察到的证据、账户专属基线或负责人阈值、预期机制、置信度、可逆下一步、衡量窗口和回滚条件。不要仅从控制项名称推断建议。
