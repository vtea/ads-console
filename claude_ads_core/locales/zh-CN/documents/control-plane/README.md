# Claude Ads 控制面

本目录是 Claude Ads v2 可安全公开的契约层。它记录产品可以作出哪些声明、实际能做什么、由哪些证据支持、如何协调工作，以及发布之前必须通过哪些检查。

该设计以洁净室方式综合了来源优先的研究纪律、能力如实披露、渐进式披露、可逆操作以及全新上下文验证。目录不包含复制的私有提示词、捕获的系统文本、账户导出文件、凭据或原始私有语料。

## 契约

- `PRODUCT_BOUNDARIES.md`：目标客户、承诺、支持的工作流及明确不作出的承诺。
- `PUBLISHING_POLICY.md`：私有/公开分类及公开发布门禁。
- `RELEASE_REQUIREMENTS.md`：成熟度、测试、安全、打包和远程 CI 要求。
- `schemas/`：JSON Schema Draft 2020-12 契约。
- `schemas/independent-review-evidence.schema.json` 和 `schemas/review-trust-bundle.schema.json`：由外部签名的发布审查契约；仓库模板不能满足此门禁。
- `manifests/`：当前产品、证据、能力、安全、编排、成熟度及生态审查状态。
- `manifests/data-lifecycle-policy.json`：版本化的分类、最短保留期、加密、访问、删除验证和事件规则。对应 schema 为 `schemas/data-lifecycle-policy.schema.json`；每次运行的值使用 `claude_ads_core/schemas/v1/data-lifecycle.schema.json`。
- `manifests/control-registry.json` 和 `manifests/scoring-profiles.json`：完整的类型化审计目录，以及失败即关闭的平台健康度状态。除非对应版本化配置已启用，否则具名检查不可评分。

schema 的 `$id` 值采用稳定的 `urn:ai-marketing-hub:claude-ads:schema:*` 标识符。它们是标识符，不是网络地址。`claude_ads_core/schemas/v1/`、`control-plane/schemas/` 和 `evals/schemas/` 中已跟踪的文件是规范验证资源。

## 原则

1. 没有来源，就没有当前声明。
2. 没有实现、固定测试数据和测试，就没有能力声明。
3. 没有批准和回滚，就没有账户变更。
4. 没有独立验证路径，就不能发布。
5. 来源过期、安全失败或评估失效都会降低成熟度。

清单是发布输入，不是营销文案。规划中的能力必须标记为 `declared` 或 `disabled`；只有经过验证的行为才能标记为 `fixture-verified` 或 `live-verified`。

无依赖核心也会验证严格的 v1 工作流产物，包括设置、品牌、规划、创意/文案、生成、监控、实验和变更计划。这些契约仅确立结构；并不证明来源真实性、平台资格、供应商可用性、账户权限或批准。基于文件的编排使用不可变的运行、任务、结果以及仅含产物的门禁包。重新运行需要明确的 `supersedes` 链。

当前目录可用于发现类结果，但不能用于账户健康度评级。全部十二个平台评分配置均保持禁用，直到逐项控制的来源支持、严重程度决策、类型化输入、权重和回归证据一并获得批准。

运行 `python scripts/release.py gate` 时，应提供精确的规范模型报告、外部签名审查目录、审查者公钥信任包、实现主体列表及 GitHub Actions 运行 ID。生成的评估符合 `schemas/release-gate-report.schema.json`，在任一输入缺失、过期、未签名、不匹配、不完整或未成功时失败即关闭。

规范模型证据使用分别受外部信任的运行执行者和评估者密钥。通过 `RELEASE_REQUIREMENTS.md` 中记录的 `CLAUDE_ADS_MODEL_EVAL_*_JSON` 环境变量提供模型信任包和实现主体排除项；任何仓库文件都不是信任根。

运行 `python -m claude_ads_core status --root . --as-of YYYY-MM-DD` 可查看基于仓库产物的状态，或将 `status` 替换为 `next`，获取确定性选择的恰好一个阻碍项。两个命令均离线运行，且失败即关闭。
