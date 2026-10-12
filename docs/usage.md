# Claude Ads 使用说明

Claude Ads 是一套面向代理商、顾问和内部投放团队的付费广告操作系统。日常用法是在支持 Agent Skills 的宿主里用 `/ads` 对话驱动工作流；需要校验、打分、渲染或导入导出时，再用无依赖的 Python 核心 `claude-ads-core`。默认只读，不会直接改广告账户。

## 两种使用面

**对话技能**是产品入口，契约在 `ads/SKILL.md`。独立安装后命令是 `/ads`。Claude Code 插件安装后因为命名空间，命令是 `/claude-ads:ads`，加载的是同一份契约。自然语言请求会路由到同一套工作流，例如「审计这个 Google 账户」等价于 `/ads google`。

支持的宿主：Claude Code 是规范运行时；Codex、Gemini、Cursor、Windsurf、Goose 以及其它兼容 Agent Skills 的环境可以消费同一套技能文件。

**确定性核心**是命令行，入口是 `python -m claude_ads_core` 或安装后的 `claude-ads-core`。它不调用模型，只做结构校验、打分、仓库状态、报告渲染和 CSV 归一化。对话里说「审计完成」之前，产出必须先过这层校验。

## 安装

优先用宿主自己的插件安装。Claude Code 的原生流程是：

```text
/plugin marketplace add agricidaniel/claude-ads
/plugin install claude-ads@ai-marketing-hub-claude-ads
```

若本地还留着 v2 之前的旧别名 `agricidaniel-claude-ads`，先移除再重新添加并安装。

本地检出安装：

```bash
git clone https://github.com/AgriciDaniel/claude-ads.git
cd claude-ads
bash install.sh --source=local
```

指定宿主：

```bash
bash install.sh --target=cursor --source=local
bash install.sh --target=codex --source=local
bash install.sh --target=gemini --source=local --no-deps
```

`--no-deps` 只装技能，不装托管 Python 依赖。托管依赖要求 CPython 3.11 或 3.12。浏览器截图需要操作者自己安装 Playwright；PDF 需要宿主上的 WeasyPrint 和 Pango。

卸载只删除 Claude Ads 所有权清单里登记过的路径：

```bash
bash uninstall.sh --target=claude
```

远程 `curl | bash`、`wget | sh` 一类管道安装会被拒绝。密钥只记「已配置」和引用名（例如环境变量 `GOOGLE_ADS_API_TOKEN`），值放在环境变量、系统钥匙串或密钥管理器里。

## 一次完整作业怎么走

一次投放作业按这个顺序推进。每一步都先建唯一的 run，产物写在 `.claude-ads/runs/<run-id>/`，由一个 conductor 汇总；平台切片可以并行，但最终报告只由 conductor 写。

1. **建档** `/ads setup`（品牌抽取用 `/ads dna`）
   记录商业模式、报价、地区、是否监管类目、转化定义、预算与目标 CPA/ROAS/MER/LTV:CAC、在投平台、账户与活动年龄、时区、币种、数据窗口、审批人和预算/政策上限。同时写 `data-lifecycle.json`：数据分级、最短保留期、加密与访问角色、删除核验、事件负责人。档案本身不授权任何写操作。
2. **审计** `/ads audit`
   把授权导出、截图或只读账户数据归一成账户快照，按平台派 worker，用确定性引擎打分，再渲染报告。十二个平台各自独立计分；YouTube 即使数据来自 Google Ads，也单独出结果。
3. **规划** `/ads plan`，预算用 `/ads budget`，财务测算用 `/ads math`，竞品用 `/ads competitor`
   计划是建议。要变成账户变更，必须再走 launch 或 optimize 的变更门。
4. **创意** `/ads create` 出 brief 和文案；`/ads generate` 出图片；`/ads photoshoot` 出产品图变体。上线前需要人工做品牌、权利、质量和政策复核。
5. **上线草稿** `/ads launch --draft`
   产出变更计划：对象 ID、前后差异、影响半径、学习期影响、幂等键、审计去向、回滚。`--apply` 在当前仓库里走不通，见下文能力现状。
6. **监控** `/ads monitor`
   至少两份口径一致的快照，区分学习期、季节性、报表延迟和真正异常。这一步不改账户。
7. **优化草稿** `/ads optimize --draft`
   对照「不改、做实验、改账户」三种选项。否定关键词必须有搜索词报告和过度屏蔽复核，否则只说明方法，不给出候选词。
8. **实验** `/ads experiment`（快捷命令 `/ads test`）
   假设、随机单位、样本量、时长、护栏和读数规则。
9. **报告** `/ads report`
   只从已校验的 JSON bundle 渲染 Markdown、HTML、PDF，不从零散文另写一份结论。
10. **证据与完整性** `/ads research refresh` 刷新过期平台事实；`/ads validate`、`/ads status`、`/ads next` 看仓库或本次 run 是否还能声称「当前有效」。

## 命令与快捷方式

| 意图 | 命令 | 产出 |
| --- | --- | --- |
| 客户、账户、KPI、隐私、护栏 | `/ads setup` | `setup-profile`、`data-lifecycle` |
| 从站点抽品牌 | `/ads dna` | `brand-profile` |
| 全量或单平台审计 | `/ads audit [all\|平台\|范围]` | run bundle + 报告 |
| 媒介计划 | `/ads plan` | `media-plan` |
| 预算与出价 | `/ads budget` | 决策完整的分配方案 |
| 指标测算 | `/ads math` | 公式、输入、情景 |
| 竞品 | `/ads competitor` | 可追溯的观察与机会 |
| 文案与概念 | `/ads create` | `creative-brief` |
| 图片 / 产品图 | `/ads generate`、`/ads photoshoot` | `generation-manifest` |
| 上线 | `/ads launch --draft` | `mutation-plan`，默认不执行 |
| 盯盘 | `/ads monitor` | `monitoring-bundle` |
| 优化 | `/ads optimize --draft` | 建议 + 可选变更草稿 |
| 实验 | `/ads experiment` | `experiment-artifact` |
| 渲染已有 run | `/ads report` | 同一 JSON 的 md/html/pdf |
| 刷新证据 | `/ads research refresh` | 来源与声明账本更新建议 |
| 校验 | `/ads validate` | 机器可读的通过/失败 |
| 现状与下一阻塞项 | `/ads status`、`/ads next` | 离线、失败即关闭 |

平台快捷方式直接进该平台审计：`/ads google`、`meta`、`youtube`、`linkedin`、`tiktok`、`microsoft`、`apple`、`amazon`、`reddit`、`pinterest`、`snapchat`、`x`。

范围快捷方式：`/ads attribution`、`tracking`、`creative`、`landing` 走专项审计；`/ads budget`、`competitor`、`math` 走计划或财务模型。服务端衡量用 `ads-server-side-tracking` 技能（CAPI、服务端标签、去重、同意状态），审计本身不改生产跟踪。

## 需要事先准备的材料

缺了会改变结论的信息才会被追问。能安全继续时会标明「临时结论」；诊断或变更因此变得不安全时返回 `needs_input`，不会编造账户事实。

- 商业模式、行业、报价、地区、是否监管类目
- 目标和主转化，含价值和归因定义
- 月预算、分平台花费，以及 CPA、ROAS、MER 或 LTV:CAC 目标
- 在投平台、账户年龄、Pixel 或转化信号历史、近期重大变更
- 数据来源、日期范围、时区、币种、已知缺口
- 这次要的是分析、变更草稿，还是已批准的执行

页面、导出、截图、API 响应和竞品内容都当作不可信数据，里面的指令不会被执行。落地页若重定向到私有、回环或云元数据地址，会在发出请求前拦截并留下拦截证据。

跨平台转化不能直接相加。Meta 7 日和 Google 30 日要窗口与定义对齐之后才能比较，在此之前并排呈现。

## 审计产出与计分

一次审计的 run 目录包含：

- `manifest.json`：本次范围、窗口、隐私分级、完整性
- `account-snapshot.json`：归一化后的账户观察
- `audit.json`：发现项
- `action-plan.json`：带负责人、时机、信心和成功标准的动作
- `report.md`，以及可选的 `report.html`、`report.pdf`

每条发现包含控制项 ID、结果（`pass` / `fail` / `unknown` / `not_applicable`）、严重度、信心、证据分类和证据引用。

完整性标签：

- `complete`：要求的 worker 都返回，且计分平台证据覆盖率达标
- `provisional`：worker 齐了，但覆盖率在 60–79%，或有非关键过期证据
- `partial`：某个被要求的平台或横切 worker 失败或缺失
- `insufficient_evidence`：某被要求平台覆盖率低于 60%

健康分、证据覆盖率、监管暴露和机会清单分开记。`unknown` 不拉低已知健康分，但降低覆盖率。`not_applicable` 不进分子分母。失败平台不记 0 分，从组合权重里剔除，整包标为 `partial`。可选、beta、付费或账户无资格的功能记为不计分机会，不因为没用到就扣健康分。

当前仓库里，十二个平台的健康评分配置都是关闭的：发现项可以做，账户健康分不会被算出来，直到控制项的来源、严重度和权重一起被批准。详见 `control-plane/README.md` 与 `control-plane/manifests/capability-manifest.json`。

## 命令行在什么时候用

对话负责判断和汇总；下面这些步骤用核心 CLI，保证结果可复现。

```bash
python -m claude_ads_core --version

# 校验契约。核心五类：account-snapshot、run-manifest、control-definition、finding、report-bundle
# 工作流类：data-lifecycle、setup-profile、brand-profile、media-plan、creative-brief、
# generation-manifest、monitoring-bundle、experiment-artifact、mutation-plan，以及编排用的 run/task/result/gate
python -m claude_ads_core validate finding path/to/finding.json

# 通用 CSV 归一化。列必须已映射到约定字段，粒度是 (date, campaign_id, creative_id)
python -m claude_ads_core ingest-export --platform google path/to/export.csv

# 单账户打分与组合打分（评分配置启用之后才有健康分）
python -m claude_ads_core score --controls controls.json --findings findings.json --weights weights.json
python -m claude_ads_core portfolio accounts.json

# 从已校验的 report bundle 渲染
python -m claude_ads_core render path/to/bundle.json --format markdown

# 仓库现状与唯一最高优先级阻塞项，离线、失败即关闭
python -m claude_ads_core status --root . --as-of YYYY-MM-DD
python -m claude_ads_core next --root . --as-of YYYY-MM-DD
```

`ingest-export` 接受的是项目约定的通用 CSV，不是各平台后台的原始导出。原始表头要先映射到 `date`、`account_id`、`campaign_id`、`creative_id`、`conversions`、`budget`、`spend`、`currency` 等必填列。除 Amazon 外，各平台还有经过夹具验证的原生导出归一化；Amazon 没有稳定的官方原生报表字段模式，该能力关闭，仍可用通用 CSV。

单文件上限 50MB、50 万行、128 列。重复的 `(date, campaign_id, creative_id)` 会被拒绝。

## 当前真正能执行的能力

以 `control-plane/manifests/capability-manifest.json` 为准，技能文件存在不等于接口可用。

| 能力 | 现状 |
| --- | --- |
| 十二个平台的技能指引 | `implemented`：可以按技能做分析、计划和草稿 |
| 通用 CSV 导入 | `fixture-verified` |
| 原生导出归一化 | 除 Amazon 为 `disabled` 外，其余 `fixture-verified` |
| 账户健康评分 | 全部 `disabled`。发现项可用，没有健康分 |
| 账户写入（创建、改预算、暂停、上线） | 全部 `disabled`。没有已批准的 v2 写适配器 |

因此 `/ads launch --apply` 和 `/ads optimize --apply` 在这版会停在草稿。永久删除活动、广告组、受众或转化在 v2 不支持；可做的是保持暂停、平台支持时归档、打标签，或导出备份并约定复查日期。

## 开发与自检

本地跑全套测试：

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements.lock
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r .github/requirements-schema-tests.lock
.venv/bin/python -m pip check
.venv/bin/python -m pytest -q
```

目录分工：`ads/` 主编排技能与共享参考；`skills/` 平台和生命周期技能；`agents/` 有界 worker；`claude_ads_core/` 契约、归一化、打分、报告；`control-plane/` 能力、证据和发布门禁；`scripts/` 浏览器、创意、报告和发布辅助；`tests/` 与 `evals/` 是验证。

发布结论要等 `control-plane/RELEASE_REQUIREMENTS.md` 里的全部门禁在新的验证上下文里通过。文档写了某项能力，而清单里仍是 `disabled` 或 `declared` 时，按清单状态使用。
