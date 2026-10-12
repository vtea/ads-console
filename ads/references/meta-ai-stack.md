# Meta Ads 排序架构

**已核验：** 2026-08-26
**刷新到期：** 2026-09-25
**证据状态：** 第一方架构认知；不是优化阈值

本参考文档仅保留 Meta 在当前第一方材料中描述的架构。它不推断隐藏的竞价行为，也不将供应商报告的提升转化为预期账户结果。

## 当前来源

- `meta-andromeda-engineering-official` — [Meta Andromeda 工程文章](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/)，发布于 2024-12-02。
- `meta-ai-ads-ranking-official` — [Meta：2026 AI 推动表现](https://about.fb.com/news/2026/01/2026-ai-drives-performance/)，发布于 2026-01-28。
- `meta-gem-training-official`：[Meta GEM 训练与架构](https://engineering.fb.com/2026/08/03/ml-applications/training-gem-at-llm-scale-meta-ads-recommendation-foundation-model/)，发布于 2026-08-03。
- `meta-sequence-ranking-official`：[Meta 多阶段序列架构](https://engineering.fb.com/2026/08/05/ml-applications/from-user-sequences-to-scaling-laws-a-multi-stage-architecture-for-metas-ads-ranking/)，发布于 2026-08-05。

全部来源均由 Meta 编写。架构描述是 Meta 公开陈述内容的高置信度证据。表现提升由供应商提供，未经 Claude Ads 独立验证。

## 有支持的内容

Meta 将广告选择描述为多阶段推荐系统。其工程文章将 Andromeda 定义为检索阶段：在后续排序前，从大得多的符合资格池中选出较小候选集。文章讨论了模型、系统和硬件之间的协同设计。

Meta 在 2026 年 1 月的公司文章中，将 GEM 描述为广告排序模型；还描述了使用更长行为序列及更多自然互动数据的序列学习架构，以及在更多 Facebook 广告载体之间整合排序的 Meta Lattice 模型。这些与创意生成功能不同。

Meta 在 2026 年 8 月的工程文章中进一步将 GEM 描述为核心广告推荐基础模型，并记录了将离线用户建模与在线排序分离的两阶段序列架构。它们并不确立面向广告主的广告系列结构、创意配额或优化规则。

Meta 还报告了部署带来的表现变化。只有当用户明确需要产品研究时，才将这些数字作为已标注的供应商证据保留；不得将其用于预测、通过标准，或作为重构账户的理由。

## 审计含义

架构认知支持提问，而非自动产生发现：

- 优化事件是否有效、及时、已去重，并与被接受的业务价值一致？
- 根据观察到的素材层面结果，账户是否提供了对其策略和版位而言具有实质差异的创意变体？
- 版位、受众和目标页面控制是否出于明确意图且符合政策安全要求？
- 广告系列结构是在解决真实约束，还是仅遵循架构叙事？
- 在可比且延迟已成熟的窗口中，自动化或创意变更是否改善了边际被接受成果？

不要根据这些来源规定固定创意角度数量、广告系列数量、广告系列年龄、受众宽度或转化阈值。Meta 的系统架构不能证明通用账户配置。

## 缺乏支持或已降级的概念

此前参考文档通过从业者综述描述了“ARM”层、精确的四层线性流水线、固定候选数量，以及大量 2026 年表现阈值。由于本来源包未为这些声明建立当前第一方支持，现已省略。只有具备直接、注明日期的第一方来源、明确范围和非规定性的审计用途时，才可重新引入其中某项。

同样，“创意相似性抑制”、广泛定向的保证性奖励，或最低创意数量等概念，在由账户证据或当前官方文档证明之前，都是假设。

2026 年 4 月的问题提案引用的是从业者文章，而非当前 Meta 来源。因此，其中固定一到两个广告系列的上限、固定广告组数量、强制采用 Advantage+、四乘四创意框架和 CPMr 规定，都不是 Claude Ads 的产品规则。只有当前第一方证据和账户自身结果支持具体决策时，才重新考虑其中任何一项。

## 发现契约

架构相关时，引用来源 ID 并区分：

- `observed`：账户配置或表现证据。
- `platform-stated`：Meta 文档中的架构或报告的结果。
- `inference`：可测试的账户专属假设。
- `unknown`：隐藏系统行为或缺失证据。

只有观察到的账户问题才成为健康发现。产品认知和供应商报告的提升仍然是不评分的背景信息。
