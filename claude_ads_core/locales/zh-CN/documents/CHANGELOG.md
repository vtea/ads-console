# 更新日志

本文件记录 claude-ads 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)，本项目遵循[语义化版本](https://semver.org/spec/v2.0.0.html)。

> 本文完整保留各版本的历史记录。历史条目中的平台事实、阈值、能力和安全做法描述的是当时版本，不替代当前产品契约及证据台账。

## [2.0.2] - 2026-09-10

### 新增

* **Google Search 重叠控制项**（公开 issue 65）：`G96`（同一广告系列内 Search 与 Dynamic Search Ads 重叠）和 `G97`（跨广告系列关键词重复）作为条件性证据控制项加入 Google 目录。两者均依据当前官方账户内优先级和 DSA Ad Rank 页面；这些页面说明，定向同一域名且符合资格的关键词不会在竞价中相互竞争，因此控制项描述的是流量路由和预算限制，而不是自我竞价或 Ad Rank 稀释。
* **规划和创作中的 Meta 冷启动契约**（公开 issue 53）：`/ads plan` 和 `/ads create` 现在会在提出 Meta 预算、学习期预期、预测或创意基准之前，采集 `ads-meta` 定义的账户、Pixel 和转化冷启动维度；根级信息采集也询问 Pixel 和转化信号历史。

### 变更

* **生态台账刷新**：审查截至 2026-09-10 的公开跟踪器，新增公开 issue 63 和 65 以及拉取请求 66 的处置，移除 GitHub 已不再提供的公开拉取请求 45。
* **Microsoft Conversions API 声明**：对照当前 Microsoft Learn 页面重新验证，将 "in pilot" 改写为具有公开端点、载荷 schema、合作伙伴集成和 UET 去重的已文档化产品。
* **来源刷新 2026-09-10**：对照当前页面重新验证 61 个平台、API、政策和监管机构来源，以及 40 项依赖声明，未发现矛盾；Microsoft API 声明现在记录 2026-10-01 的 REST-only 切换，以及计划于 2027-01-31 的 SOAP 弃用；TikTok 报告来源指向 v1.3 basic-reports 参考资料。
* **旧安装预检**（公开 issue 57）：`install.sh` 和 `install.ps1` 现在检测没有所有权清单的现有 Claude Ads 安装（任何早于 v2.0.0 的安装），打印一条消息，列出检测到的文件及安装程序将拥有的每个路径，并在任何目标写入前退出，而不是每个文件分别失败。`uninstall.sh` 在清单缺失时也说明同样的 v2.0.0 边界。受管 v2 安装仍然原地升级。
* **市场别名说明**（公开 issue 56）：README 解释在 v2.0.0 之前添加的市场会保留过期的 `agricidaniel-claude-ads` 别名，并展示移除、添加及安装命令。
* **在线生态门禁模式**：`audit_ecosystem_live.py` 现在在 push 和 pull_request 上以默认模式运行，仅因无效台账、不匹配的审查候选、GitHub 已不再提供的台账项目，以及在快照日期当日或之前创建但未记录的项目而失败。快照后的项目、头提交漂移、元数据漂移，以及快照后合并的拉取请求，报告为结构化发现和 GitHub 警告注释。`--strict`（workflow_dispatch）保留精确对账，发布验证仅接受严格的 workflow_dispatch 运行。没有拉取请求事件时，候选从受测提交推导：其作为头提交的开放拉取请求，或其作为合并提交的已合并拉取请求。
* **依赖审计导入防护**：现在可识别采用 from-import、别名、`builtins`、`getattr` 和下标写法的 `importlib.import_module` 及 `__import__`；任何模块名不是字符串字面量的调用，或任何在直接调用之外引用的导入器，都会作为无法解析的动态导入导致审计失败。此防护是受保护范围内第一方源码的语法检查；它看不到第三方包内部的传递导入，也看不到 importlib 之外的加载器。
* **漏洞例外重新验证**：2026-09-10 对照当前导入图和 OSV 记录重新验证，新增 WeasyPrint PYSEC-2026-3940 的 `not_affected` 记录（产品从不向 `write_pdf` 或 `render` 传递 `stylesheets` 或 `xmp_metadata`）。对于漏洞通道为调用参数的安全公告，例外记录现在可携带经机器检查的 `forbidden_call_keywords` 防护；向任意可调用对象传递受保护关键词，或向受保护函数或无法解析的被调用方转发关键词映射，都会使审计失败。CI pip-audit 锁定现在包含 CPython 3.12 上 `cyclonedx-python-lib` 所需的 `typing_extensions`。

* **证据和生态审查**：对照当前一手来源核对承重声明集合，纠正无法访问的仓库证据 SHA，限定 Google 转化目标出价例外，并将受支持的 Meta 架构声明刷新至 2026 年 8 月。Google consent-mode 建模阈值对照当前官方页面重新验证，并新增第二个来源说明没有公布更多数值。冻结的审查台账现在具有远程门禁，用于核对当前跟踪器状态，且仅排除精确审查候选。
* **控制契约迁移**：将生态处置和发布门禁报告契约版本化为 2.0.0，保留 1.0.0 schema 以兼容已存储证据，并记录迁移边界。
* **CI 供应链**：使用已验证提交 SHA 固定 checkout、Python setup 和 Dependabot metadata actions 的当前主版本，并新增分支保护要求的汇总 `validate` 任务。Dependabot 工作流现在只读，批准和合并交由人工。
* **测试工具链隔离**：JSON Schema 测试工具从专用的六包哈希锁定（`.github/requirements-schema-tests.lock`）安装到核心和完整 CI 任务，以及文档中的本地环境，使全新环境不再在测试收集阶段失败。
* **模型评估对象绑定**：外部模型执行包现在将每个任务绑定到计划生成时解析的精确候选提交和树，以及固定的保留 v1 对象。

### 修复

* **依赖防护别名**：跟踪导入器模块的字面量导入，并检查通过简单可调用别名转发的关键词映射。简单别名循环失败即关闭；计算得出的别名值和过程间数据流仍不在此第一方语法防护范围内。

* **Microsoft 原生导出转化**：AdPerformanceReport 配置现在映射 `ConversionsQualified`；Microsoft 文档说明旧 `Conversions` 列自 2022 年起弃用且始终为零，因此基于该列构建的导出会将转化少报为零。
* **PDF 报告标记边界**：健康度分数说明现在使用与所有其他报告文本相同的辅助函数转义分数和评级值，关闭可经 `build_pdf` 调用方到达的 ReportLab 标记注入路径；回归测试现在使用标记载荷覆盖每条说明路径。
* **发布审计编码覆盖**：秘密和私有路径扫描现在还以 UTF-16 LE 和 BE 解码已跟踪文件，使 UTF-16 文件中的令牌无法再通过检查。在线跟踪器查询失败会报告 HTTP 状态和端点路径。
* **落地页审计完整性**：`analyze_landing.py` 在浏览器验证、导航或页面分析失败时，现在以非零状态退出并不提供审计评级。JSON 失败仍然机器可读，但不会将缺失观察呈现为失败的落地页控制项。
* **跨安装程序安全**：Bash 和 PowerShell 安装程序现在在任何变更前拒绝彼此的所有权清单。Bash 还将 Windows 依赖安装引导到 PowerShell，并提供聚焦的恢复指引和回归覆盖。
* **发布验证**：承重来源日期现在与声明日期一起失败即关闭；公开跟踪器覆盖必须精确匹配已审查快照；远程 CI 门禁核对当前 issue 和拉取请求元数据及精确头提交；目标锁定测试不再替换无关子进程调用。
* **图像供应商验证**：任何供应商结果在写入或报告成功前，生成图像都必须是完整、大小受限且输出扩展名匹配的 PNG 响应。
* **平台边界情况**：Meta 规划现在独立分类账户、Pixel 和转化冷启动。Google 和 Microsoft 建议现在要求先验证操作能力，再建议设置变更；公开市场命令使用规范化的小写仓库标识符。
* **产品元数据**：生成的 PDF 报告使用 2.0.2 产品版本，而 Python 核心正确保留独立的 2.0.0 版本。
* **旧报告标记边界**：用户控制的 Markdown、章节标题和品牌名称在引入受约束的 ReportLab 格式标签之前转义，防止原始 ReportLab 标记到达渲染器。

### 安全

* **依赖 VEX 门禁**：为当前 cryptography 和 Pillow 安全公告新增 16 项带到期时间的 `not_affected` 处置。每项绑定精确锁定版本、上游公告 ID、证据路径和禁止导入；任何新公告、执行路径漂移、接受风险或到期都会使 CI 失败。发行保留每个引用的证据路径。CI 从 CPython 3.12 Linux 哈希锁定，在隔离环境中安装当前固定的 `pip-audit` 2.10.1 补丁版及其完整依赖闭包。
* **代码扫描**：新增最小权限 Python CodeQL 工作流，使用 `security-extended` 查询套件和精确 action 提交固定。
* **敏感产物防御**：扩大忽略和发布审计覆盖范围，包括日志、本地数据库、凭据通配模式、本地配置，以及嵌入二进制文件的令牌模式。

## [2.0.1] - 2026-07-13

基于 v2.0.0、面向公开镜像发布的文档和元数据补丁。不涉及代码契约、评分、目录或行为变更。

### 变更

* **公开发布界面**：README 安装路径、`SUPPORT.md`、`SECURITY.md`、`CODE_OF_CONDUCT.md`、`CONTRIBUTING.md`、issue 模板、`CITATION.cff`，以及插件和市场清单中面向用户的仓库链接，现在指向公开的 `AgriciDaniel/claude-ads` 仓库，使安装、issue、讨论和私密漏洞报告无需 AI-Marketing-Hub 组织访问权限即可工作。社区镜像继续为 AI Marketing Hub Pro 会员保留文档说明。
* **安装程序默认克隆来源**（`install.sh`、`install.ps1`）从私有组织仓库改为公开仓库，使远程来源安装无需组织凭据即可克隆。
* **运行时署名 URL**：PDF 报告页脚（`generate_report.py`）和页面抓取 User-Agent 联系 URL（`fetch_page.py`）现在引用公开仓库。签名审查证据出处（`review_evidence.py`、审查模板）有意保留规范组织对象。
* **README**：新增双渠道发行说明和原生 Claude Code 插件安装命令。

## [2.0.0] - 2026-07-12

面向专业付费媒体运营的重大架构发布。

### 新增

* 为 Reddit、Pinterest、Snapchat 和 X 提供一等平台契约，使平台范围达到十二套专用技能、参考资料、审计工作代理和目录条目。
* 新增设置、上线、监控、优化、研究刷新、验证/状态，以及 JSON 优先报告渲染的生命周期技能。
* 版本化账户快照、运行清单、控制项、发现和报告契约，以及轻依赖 CLI。
* 类别优先的确定性评分，包含按严重程度加权的证据覆盖率、暂定及证据不足状态，以及考虑花费的组合评分。
* 混合式来源、声明、能力、安全、成熟度、编排、公开发布、issue 和拉取请求控制面。
* 能力驱动的适配器框架、脱敏导出固定测试数据、可移植接口元数据、研究/来源/技能/发布验证代理，以及扩展的路由评估。

### 变更

* 围绕渐进式披露、明确优先级、不可信输入边界、符合 schema 的工作代理结果、部分失败语义和产物支持的完成声明，重建主入口及平台提示词。
* 用唯一运行清单和版本化 JSON 作为记录系统，替代固定报告文件名和纯文字汇总。
* 将可选、测试版、付费高级、不可用和不符合资格的功能重新分类为不计分机会，而非账户健康度扣分项。
* 从运行时提示词中移除通用 CPA、预算、学习期、归因和功能采用规则。
* 安装现在使用经过身份验证/本地来源、受管环境、生成的数量和精确所有权清单。
* 从规范设计源安装预定的动画封面横幅，以及 architecture、how-it-works、platform-coverage 和 health-score 四张动画图。每个 SVG 均自包含，不含脚本、事件处理器、外部请求或远程资产。
* 围绕简洁快速入门、十二平台覆盖、规范命令、安全默认值和证据驱动评分重写 README，提供无空单元格的平台表以及面向用户的隐私章节。
* 保留 `assets/demo.gif`，并将其原始命令发现界面标为历史内容。
* 将可安全公开的研究支持整合到注明日期的来源及声明台账。原始研究会话记录和私有工作笔记现在保留在产品仓库之外。
* 将失效的 HTTP JSON Schema 标识符替换为稳定 URN，并记录已跟踪的规范 schema 位置。
* 扩展仓库审计，拒绝用于文档和下载的个人波浪号主目录路径，同时保留可移植安装示例。
* 为相邻平台参考资料、有界研究和全新上下文审查工作代理新增明确的渐进式披露路由。

### 移除

* 移除孤立的旧横幅、静态占位图，以及过时的可复用品牌提示词。若干旧图含有过期数量或与 v2 安装、评分、隐私和能力策略冲突的指令。
* 移除已跟踪的原始研究语料，其中包含本地机器路径或重复了已由可安全公开控制面表示的材料。
* 移除孤立的品牌 DNA 文字模板，该模板与严格 v1 brand-profile schema 冲突，且没有运行时路由。

### 安全

* 对 HTTP 和 Playwright 导航、重定向、框架及子资源新增执行前 SSRF 控制；禁用 service worker 和下载。
* 新增安全输出根目录及符号链接约束、凭据脱敏、私有语料边界、提示词注入规则和失败即关闭的变更门禁。
* 卸载拒绝命名空间通配模式、被篡改清单、非本项目所有的文件及规范路径逃逸。

### 破坏性变更

* v2 JSON 契约和运行目录输出替代 v1 固定报告文件。
* 不支持永久删除账户对象；线上写入保持禁用，直到每个精确平台操作通过能力专属发布门禁。

## [1.8.1] - 2026-05-27

基于 v1.8.0 的文档和元数据补丁。不涉及代码、检查目录或行为变更；59/59 pytest 仍通过。（由发布后审查发现。）

### 修复

* **README "What's new" 章节**从 v1.7.0（Wave 2）更新为 v1.8.0（Wave 3）：新增 91 项检查（目录共 300 项）、新的 `audit-regulatory-compliance` 代理及代理时代参考文档。此前仍以旧版本为主标题。
* **过期测试数量从 41 纠正为 59**（pytest 实际收集且通过的数量），涉及 README、`CITATION.cff`、`plugin.json` 和 `marketplace.json`。v1.7.0 CHANGELOG 条目保留 41（对该版本准确）。
* **路线图表述**刷新：v1.8.0 已发布/当前可用，不再是 "in active development"；移除不准确的 "v1.8.0 visual system" 图替代文本。

### 新增

* README 新增**限制章节**（手动数据输入、目录范围、时间点为 2026 的基准、实验性非 Claude 宿主），并添加目录条目。

## [1.8.0] - 2026-05-26

实质性的 Wave 3 发布。在五个目录平台（Google、Meta、TikTok、LinkedIn、Microsoft）中新增 91 项由目录跟踪的平台检查，新增监管合规审计代理（C01-C29 + C-MCP-1..6 + C-iOS-1），为代理/MCP/监管时代重写三份参考文档，新增七份逐平台研究笔记及监管风险敞口评分区间。来源为 `research/RESEARCH-NOTES-MAY-2026.md`（引用一手来源）。

### 新增

#### `/ads google` — Google Marketing Live 2026（May 20, 2026）补充（G81-G95，+15 项检查）

* Ask Advisor 治理、Business Agent for Leads、Direct Offers、AI Mode 广告格式（G81-G84）
* Journey-aware bidding、PMax + Shopping 上的 Smart Bidding Exploration、总预算、需求驱动的预算节奏（G85-G88）
* GA360 中的 Meridian、Qualified Future Conversions、Attributed Branded Searches、Asset Studio Gemini Omni、Demand Gen 技术栈、Ads Advisor 3（G89-G94）
* **G95：DSA → AI Max 强制迁移 P0 门禁（September 2026）**——无退出选项；迁移前 AI Brief / FUE / 品牌排除准备度检查

#### `/ads meta` — MCP + March 3 归因重建 + Q1 2026 AI 技术栈刷新（M51-M72，+22 项检查）

* Meta Ads MCP（`mcp.facebook.com/ads`，29 个工具）、默认暂停，结合 SurfaceLabs 警示案例的 **MCP 写操作治理**（M51-M53）
* March 3, 2026 归因重建：点击归因仅计链接点击、engage-through 列、10s→5s engaged-view、新默认窗口、同比不可比警告（M54-M59）
* Q1 2026 AI 技术栈指标 + **ARM（Adaptive Ranking Model）** + Incremental Attribution Q4 2025 模型（M60-M64）
* 广告级版位控制、AI Instant Forms、**730-day 受众 + Pixel 自动包含治理标记**、Advantage+ Creative Categories（M65-M69）
* **M70：Comscore Markets P0 门禁——June 22, 2026 汽车行业截止日期**（`dma_code` → `comscore_market_codes`）；DST 费用；CAPI 一键操作 + EMQ ≥ 7（M70-M72）

#### `/ads tiktok` — TikTok World 2026（May 13-15, 2026）（T29-T46，+18 项检查）

* TikTok Ads MCP + Ads Skills；**Smart+ One Buying Experience 模块级自动化分类器**（T29-T31）
* Music Autofix、创意报告、TopReach + Creative Sequencing、Branded Buzz、Search Hubs、Symphony / Dreamina、TikTok GO、Mini Series、Collage Carousel、One Asset Manager、View+、Market Scope、TikTok Real、GMV Max（T32-T46）

#### `/ads linkedin` — Off-Platform Event Ads + Campaign Manager 重命名（L28-L46，+19 项检查）

* **L28：Off-Platform Event Ads**（无需 LinkedIn Event Page；Cvent / ON24 / Integrate）
* **L29：Campaign Manager 术语重命名陷阱**（UI "Campaign Group"→"Campaign"，API 不变；UTM 不匹配警告）
* Career Journey、Reserved / First Impression Ads、BrandLink、Wire、Thought Leader、CTV、Company Attribution、Company Intelligence API、Agency Certification、Depth Score 自然内容算法（L30-L46）

#### `/ads microsoft` — AI Max for Search + Activate 2026（MS25-MS41，+17 项检查）

* **MS25：Microsoft AI Max for Search**（Copilot Search / Answers / Bing；区别于 Google）
* Offer Highlights、Audience Generation、PMax 透明度、Clarity AI Visibility、Brand Agents、Merchant Center 中的 UCP、Copilot Checkout、Rewarded Portals、Import Center、诊断、DDA、CAPI、Brand Kit、**SOAP API 弃用**（MS26-MS41）

#### `/ads compliance` — 新增 `audit-regulatory-compliance` 代理（C01-C29 + C-MCP-1..6 + C-iOS-1，+36 项检查）

新增专门负责监管范围的并行审计代理，由 `/ads audit` 与现有代理一起分派。

* **C01-C05**：EU AI Act Article 50——Aug 2, 2026 基线；Dec 2, 2026 水印存量豁免；€15M / 3% 处罚；多层水印；供应商与部署者义务
* **C06-C17**：美国州隐私——22 个州；12 州 GPC 列表；CCPA §7025(c)(6) 可见确认；Connecticut 神经数据（July 1, 2026）；Maryland MODPA；CA Delete Act DROP
* **C18-C21**：Privacy Sandbox 于 October 17, 2025 退役；保留 CHIPS / FedCM / Private State Tokens；UK CMA 85% 不准确 / 30% 收入下降引文
* **C-iOS-1**：iOS 26 ATFP / Link Tracking Protection——iOS Safari 流量 >5% 时强制服务端追踪
* **C22-C29**：DSA 执法 / HIPAA / LegitScript / Special Ad Categories / PIPL / LGPD / DPDPA / TCF v2.3 + GPP
* **C-MCP-1..6**：MCP 写操作治理——只读优先、人工批准门禁、默认暂停、速率限制、禁止自主预算循环、≥90-day 审计日志保留

#### 跨平台 2026 格局（X01-X25，研究笔记）

* Reddit Max / Dual Attribution / App Event Optimization；Pinterest tvScientific + CTV Audiences；Snap Smart Solutions / AI Sponsored Snaps；CTV/OTT 变化；Universal Commerce Protocol（NRF + AP2 → FIDO）；IAB Tech Lab AAMP + Agent Registry。记录于 `research/RESEARCH-NOTES-MAY-2026.md`；通过 `/ads attribution`、`/ads server-side-tracking` 和主协调器呈现（叙述/认知，尚未由目录跟踪）。

#### `/ads amazon` + `/ads apple` 差异（内联）

* Amazon：Unified Campaign Manager、Ads/Creative Agents、Full-Funnel Campaigns、MTA、Sponsored Brands Collections（Jan 28, 2026）、SP/SB Prompts GA（March 25, 2026）、Brand+ / Performance+、Prime Video 扩展、Complete TV（AMZ-new-1..17，内联于 `skills/ads-amazon/SKILL.md`）
* Apple：Multiple Search Ad Placements（无位置级报告）、AdAttributionKit 刷新、Custom Product Pages、iOS 26 ATFP/LTP、WWDC 2026 观察清单（A36-A42，内联于 `skills/ads-apple/SKILL.md`）

#### 新参考资料与研究文档

* `references/mcp-integration.md`——面向代理时代完整重写（Google / Amazon / Meta / Microsoft / TikTok MCP、IAB AAMP + Agent Registry、写操作治理策略 + SurfaceLabs 先例）
* `references/compliance-requirements.md`——EU AI Act + 美国 22 州隐私 + Privacy Sandbox + iOS 26 + DSA + HIPAA / LegitScript + 全球框架
* `references/meta-ai-stack.md`——整合 Andromeda + GEM + Lattice + ARM，包含 Q1 2026 指标及四项操作原则
* `research/RESEARCH-NOTES-MAY-2026.md` + `research/notes-{google,meta,tiktok,linkedin,microsoft,apple,amazon}.md`——引用一手来源的逐平台研究笔记
* `references/automation-tier-classifier.md`——模块级自动化分类（Smart+ One Buying Experience、Advantage+、AI Max、Accelerate、Microsoft AI Max）

### 变更

* **合规代理拆分**——`audit-compliance` 重命名为 `audit-policy-compliance`（平台广告政策、Special Ad Categories、弃用功能、表现基准）；新增 `audit-regulatory-compliance` 处理监管范围。代理数量 10 → **11**（7 个审计 + 4 个创意）。子技能数量**仍为 22**（新合规单元是审计代理，不是子技能）。
* **`tests/fixtures/check-catalog.yaml`**——五平台目录从 209 扩展到 **300** 项已验证检查（Google 95、Meta 72、LinkedIn 46、TikTok 46、Microsoft 41），由评估框架双向强制执行。Apple、Amazon、X01-X25 格局，以及归因 + 服务端内容仍内联，等待 Wave 3.x 目录提取。
* **`scoring-system.md`**——新增**监管风险敞口区间**（P0/P1/P2 → 严重程度乘数，按 100% 汇总权重评分）和五个严格监管时钟；将总检查数量表刷新为 v1.8.0。
* **README.md**——"250+ checks" → "300+ checks"；"10 agents" → "11 agents (7 audit + 4 creative)"；`/ads audit` 现在启动 7 个并行子代理，包括 `audit-regulatory-compliance`。
* **版本元数据**——`plugin.json`、`marketplace.json`、`CITATION.cff` 和 `scripts/generate_report.py` 升级为 1.8.0。

### 弃用

* 将 Privacy Sandbox API 作为未来追踪方向的引用（October 17, 2025 退役）
* `audit-meta` 报告中 March-3-2026 之前的 Meta 同比比较表述

### 修复

* 在 `research/notes-amazon.md` 中记录引文准确性："+143% click-attributed sales" 数值从 Sponsored Brands Collections 重新归属于 Sponsored Brands Reserve Share of Voice（依据 Amazon 官方 Reserve Share of Voice 页面）；Google AI Max 案例标记为供应商提供（JumpFly April 2026 独立分析显示中性至负面效果）。

### 安全

* MCP 写操作治理默认值记录于 `references/mcp-integration.md`，并由 `audit-regulatory-compliance` 强制执行（C-MCP-1..6）：默认暂停、≤200 calls/hour、≥90-day 审计日志保留，以及超过可配置阈值的预算变更需人工批准门禁。纳入 SurfaceLabs April 2026 永久账户封禁先例。

---

## [1.7.1] - 2026-05-18

涵盖 v1.7.0 之后完善阶段的补丁发布：将 README 全面重写至 SSS+ 级（在三轮独立审查中评分 64 → 81 → 94 → 96+），全新动画 SVG 横幅（比此前 PNG 小约 25×，包含 22 个实时 SMIL 动画），将规范仓库迁移至 AI-Marketing-Hub 私有组织（此前的 `AgriciDaniel/claude-ads` 位置保留为公开镜像），并深入验证各平台子技能中的每项量化事实声明。

没有新子技能、新代理或脚本行为变更；本次仅涉及文档、资产、品牌和整理工作。

### 新增

- **动画 SVG 横幅**（`assets/banner.svg`）替代静态 PNG。优化后 13.9 KB，22 个 SMIL 动画（徽标渐变呼吸、漂移扫描线、分隔线脉冲、带光标闪烁的 7 命令扫描高亮、状态栏脉冲点）。任意缩放下保持矢量清晰；借助 `role="img"`、描述性 aria-label 和 `<title>`/`<desc>`，支持文本搜索和屏幕阅读器。此前静态 PNG 保留于 `assets/banner.png`，供剥离 SVG 的查看器回退使用。
- **品牌套件**（`branding/banner-template.html`、`branding/AGENT-PROMPT.md`）：参数化 HTML 模板，用于在同一品牌系列的其他仓库（claude-seo、claude-blog 等）中克隆终端风格横幅。AGENT-PROMPT 提供五个预置调色板（暖橙/青绿/紫/钴蓝/绯红）、figlet ANSI-Shadow 生成步骤，以及可重复的 Playwright 渲染片段。
- **`assets/banner-pre-v1.7.0.png`**：保留旧平面横幅备份，方便引用旧设计。
- SSS+ 重写新增的 **README 章节**：
  - **痛点主视觉**（"manual audit takes 4-6 hours of senior PPC time; Claude Ads runs it in 10-15 minutes"），替代此前 80 词开场段落。
  - **"Who this is for"** 区块，包含三类具体用户（PPC 代理商负责人、企业内部营销人员、自由职业顾问）。
  - 首屏上方的 **"What's new in v1.7.0"** 亮点框。
  - **示例输出**预览：真实感的 `/ads audit` JSON 摘录，展示健康度分数、逐平台细分、带严重程度/影响/行动/ETA 的主要发现，以及快速收益。
  - **比较表**（Claude Ads vs 手工审计 vs 代理商服务 vs 商业 PPC 审计工具），覆盖时间、费用、可重复性、输出格式、数据驻留、锁定及平台功能认知。
  - **用例**：三种具体工作流模式。
  - **财务 KPI 常见问题条目**：将 ROAS / CPA / ACOS / TACOS / LTV:CAC / MER 映射到处理它们的命令。
  - **维护与支持常见问题条目**：披露单维护者模式及 48-hour 缺陷响应承诺。
  - **"Two versions of this skill"** 提示，解释公开与社区私有的双仓库结构。
  - **项目信息**章节，在 README 中内联链接 CHANGELOG、CONTRIBUTING、CODE OF CONDUCT、SECURITY、SUPPORT。

### 变更

- **规范仓库位置**迁至 `AI-Marketing-Hub/claude-ads`（私有组织仓库）。此前的 `AgriciDaniel/claude-ads` 位置保留为公开镜像，并在新 README 中称为 "stable open-source" 通道。统一修改 15 个文件中的所有安装命令、徽章、引用字段和文档路径。
- **README 重写**：从合格文档变为转化级产物，独立审查者在三轮中给出 64 → 81 → 94 → 96+。大幅重写主视觉、功能章节、FAQ 结构（现为 8 个问题的 `<details>` 区块），以及所有 H2 标题，以兼顾关键词和清晰度。
- 按内部文风**移除 README 中所有长破折号**（54 处）。根据上下文替换为冒号（定义/标签）、分号（独立分句）、逗号（句中衔接）、括号（插入分句）或中点（表格脚注）。
- **比较表平台功能单元格**从 "2026-current" 细化为具体功能名称和日期（"Andromeda (Oct 2025), AI Max (May 2025), AdAttributionKit + WWDC25 configurable windows, Consent Mode V2"）。
- 新增**公开仓库交叉引用**；README 现在以 Pro 社区徽章和双版本提示开场，将非会员引导到公开开源仓库。
- **徽章改指向**公开仓库（`AgriciDaniel/claude-ads`）的 Version + CI，因为 shields.io 无法读取私有仓库。新增 "AI Marketing Hub Pro community" 徽章。
- **仓库引用**在 `.github/ISSUE_TEMPLATE/`、`CITATION.cff`、`SECURITY.md`、`SUPPORT.md`、`CODE_OF_CONDUCT.md`、`CONTRIBUTING.md`、`install.sh`、`install.ps1`、插件/市场清单，以及包含 UA 字符串或版本引用的两个脚本中更新。
- **脚本文件模式**规范化：5 个 CLI 脚本设为 755（此前受作者 umask 影响为组可写 775）；作为库的 `url_utils.py` 正确保留为 644。

### 修复

- **事实声明对照一手来源引用。** `ads-meta`、`ads-apple`、`ads-budget`、`ads-google`、`ads-microsoft` 和 `ads-creative` 中十项量化声明，对照供应商/第一方文档验证或纠正：
  - Andromeda 10,000× 容量（Meta Engineering，Dec 2024）
  - Confect 60% 相似度阈值（confect.io）
  - WWDC25 AAK 可配置窗口（Apple Developer session 221）
  - AppTweak CPP +8% / +6.6% 转化提升（AppTweak 基准）
  - SoundCloud 58% CR / 39% CPI 案例（AppTweak 案例）
  - 78% Personalized-Ads-off App Store 搜索（Apple Q1 2022 数据，经 9to5Mac）
  - Google AI Max 14% 转化提升（Google Ads blog，May 2025）
  - Microsoft Copilot 73% CTR 提升（Microsoft Advertising blog，Aug 2025）
  - TikTok 平台中位 ROAS 1.41–1.67（从原文错误暗示的 Smart+ 专属表述改写）
  - Demand Gen "20% more conversions" 澄清为同 CPA 下视频+图像相较仅视频
- **过期的 `(latest: v1.5.1)` 引用**在公开推送使公开仓库达到 v1.7.0 内容后纠正。
- **README 徽章**此前指向私有组织仓库，显示 "no releases or repo not found"；改指向公开镜像。
- **过期 URL 引用**在 15 个文件中从 `AgriciDaniel/claude-ads` 统一改为 `AI-Marketing-Hub/claude-ads`，并更新对应插件 slug（`agricidaniel-claude-ads` → `ai-marketing-hub-claude-ads`）。

### 说明

- **`presentations/v1.7.0-release/`** 有意不跟踪（发行营销进行中工作，不随技能本身发布）。
- **进行中的视觉呈现**（5 张架构图 × A/B/C 变体 = 15 个新 SVG，加上 `branding/diagrams-preview.html` 比较工具和 `branding/scripts/` 渲染自动化）当前存在于工作树，但不属于此次发行。变体选择确定后，将在未来视觉系统版本中交付。
- **仓库位置**：规范开发位置现在是私有 `AI-Marketing-Hub/claude-ads` 仓库；`AgriciDaniel/claude-ads` 保留为公开镜像。后续开发先在私有仓库进行。

## [1.7.0] - 2026-05-17

90 天 "category leader" 计划的 Wave 2。交付跨运行时安装矩阵、信任护城河评估框架、面向 AI Max 和 Andromeda 时代的平台深度重写，以及涵盖归因、服务端追踪和 Amazon 零售媒体的三个新子技能。

### 新增

- **跨运行时安装矩阵**——`install.sh` / `install.ps1` 现在接受 `--target={claude,codex,cursor,windsurf,gemini,goose}`，并进行严格白名单验证。逐宿主路径表采用单一事实来源；pip 安装门禁仅允许 Claude Code + Codex CLI。可选 `--skill-dir` / `--agent-dir` 覆盖值会检查 `; & | $ ( ) < >`、反引号、前导连字符、`..` 穿越和 UNC 风格路径。`uninstall.sh` / `uninstall.ps1` 同步匹配。
- **`tests/` 中的 Pytest 评估框架**——41 项测试覆盖：
  - **路由快照**（3 项测试）：每个文档化触发短语通过 `evals/creative-evals.json` 路由到预期子技能。
  - **检查目录覆盖**（4 项测试）：`tests/fixtures/check-catalog.yaml`（G/M/L/T/MS 共 209 个 ID）与 `ads/references/` 下每个审计参考文件之间双向验证。无孤立 ID、无未跟踪行，总数 ≥ 209 基线。
  - **评分计算**（6 项测试）：重新实现 `scoring-system.md` 的加权评分算法，断言 10 次运行的确定性、正确严重程度加权和 NA 排除。
  - **SSRF 回归**（28 项测试）：14 个 IPv4/IPv6 私有/内部阻止列表案例（含 v1.6.0 的 `::/128`）、5 个非 HTTP 协议阻止、DNS 失败即关闭、有效公开 URL 放行，以及 6 个凭据脱敏 sanitize_error 案例和无害消息放行。
- **`tests/fixtures/check-catalog.yaml`**——规范 209 检查目录，带严重程度乘数和结果分值表，直接通过 grep 从参考文件推导。
- **`requirements-dev.txt`**——pytest ^8 + pyyaml ^6（仅测试使用，生产用户永远不需要）。
- **CI 集成**（`.github/workflows/ci.yml`）——在安装和 pip-audit 之间新增 "Run eval harness (pytest)" 步骤。任何回归都会使构建失败。
- **`SECURITY.md` 中的出站网络目标表**——每个脚本可到达的每个端点现均记录其门禁机制。
- **3 个新子技能**：
  - `ads-attribution`：跨平台归因审计，涵盖 iOS AdAttributionKit（展示后 24h 浏览归因、WWDC 2025 可配置窗口、ATT 选择加入监控）、Web（GA4 归因模型、Google Ads 归因、跨渠道自动标记）、Consent Mode V2 Advanced 强制要求、服务端拼接、MMP 健康度和跨设备匹配。
  - `ads-server-side-tracking`：服务端管道审计，涵盖 sGTM（自定义域名、Conversion Linker）、Meta CAPI / CAPI Gateway、event_id 去重、≥80% 服务端/客户端命中比、6 事件像素调试流程，以及小写化并去除首尾空白的 SHA-256 PII 哈希纪律。
  - `ads-amazon`：Amazon Ads 审计，涵盖 Sponsored Products（自动与手动 + 搜索词挖掘）、Sponsored Brands（HSA + SB Video）、Sponsored Display（受众与上下文）、按边际贡献确定的 ACOS / TACOS 目标、出价和预算管理，以及 Brand Analytics 集成。
- **多宿主 README**——主视觉围绕 Agent Skills 兼容性重新定位，新增带逐宿主路径映射的跨宿主安装矩阵表、实验性目标警告、宿主支持徽章行（Claude 已验证，其他为实验性），以及新的 "Eval Harness" 功能章节。
- `research/distribution-prep-v1.7.0.md` 中更新**仓库 About 字段文本**和 **Topics 列表**，反映 Wave 2 变更。
- **十大原则思考框架**（`ads/references/thinking-framework.md`）——按需加载的思考纪律（OBSERVE × 2 / LISTEN / THINK / CONNECT × 2 / FEEL / ACCEPT / CREATE / GROW），由主协调器和四个重思考子技能（`ads-audit`、`ads-plan`、`ads-create`、`ads-dna`）引用。每项原则映射到具体广告工作行为、反模式及工作流触发示例。交叉链接现有产物（3× Kill Rule、Context Intake gate、MER/LTV 计算、文案框架、语气到风格映射），使纪律成为原生组成部分，而不是额外附加层。

### 变更

- **`ads-google` SKILL.md**——AI Max for Search 章节扩展，加入 `ai_max_setting.enable_ai_max` 字段（Google Ads API v21+）、AI Brief 审计（企业名称、价值主张、受众、禁止话题、免责声明）、文本定制规则、Final URL Expansion（FUE）控制、品牌排除和文本免责声明（May 2026+ 逐步推出）。新增 **DSA 迁移预检清单**章节（11 项），用于 September 2026 将 DSA / ACA / 广告系列级广泛匹配自动迁移至 AI Max。
- **`ads-meta` SKILL.md**——Andromeda 章节扩展为 **Andromeda + GEM + Lattice（2026）**，涵盖三个技术栈组件，以及为什么创意如今成为机械式定向。新增**创意即定向评分标准**（5 个轴，总分 0-10）。新增 **Entity-ID Clustering Predictor** 章节（从 Wave 3 提前），包含 5 项预测启发式方法及上线前 `creative-cluster-risk.md` 交付物。新增 **MAPI v25 ASC/AAC Deprecation Detector** 章节。新增 **Sales/Leads/App 的 ASC 默认值**章节。
- **`ads/SKILL.md` 中的主协调器路由表**——新增 3 个命令（`/ads amazon`、`/ads attribution`、`/ads tracking`），子技能数量 19 → 22，Community Footer "When to show" 扩展到新命令，修复过期参考文件注释（google 74→80、meta 46→50、linkedin 25→27、tiktok 25→28、microsoft 20→24——现在与目录一致）。
- **`scripts/url_utils.py`**——将 `sanitize_error()` 规范化为异常消息脱敏的单一事实来源。`analyze_landing.py`、`capture_screenshot.py` 和 `fetch_page.py` 全部在每个宽泛异常捕获位置导入并应用它。
- **`scripts/generate_image.py`**——Replicate 结果 URL 在获取前重新对照 SSRF 阻止列表验证，并以 `allow_redirects=False` 运行 `requests.get`，使重定向到私有 IP 无法绕过门禁。
- **`scripts/fetch_page.py`**——所有 `RequestException` / `SSLError` / `ConnectionError` 插值现在经过 `sanitize_error`。
- **`uninstall.sh` / `uninstall.ps1`**——以基于通配模式的发现（`${SKILL_BASE}/ads-*/`）替代硬编码子技能列表。新增子技能不再需要更新卸载程序。

### 安全

- Wave 2 网络安全复审中，**v1.6.0 基线（92/100）提升至 94/100**。没有新增 HIGH/CRITICAL 发现。
- 全部 6 类安装矩阵注入攻击输入已验证被 `validate_install_path()` / case 语句白名单阻止（分号命令注入、shell 元字符、父目录穿越 `..`、前导连字符、UNC 路径、未知目标键）。
- 卸载程序的通配发现无法逃逸 `${SKILL_BASE}`，因为 `SKILL_BASE` 仅来自白名单目标映射；卸载侧没有 `--skill-dir` 覆盖。
- Replicate URL 再验证形成纵深防御，即使 Replicate 是可信供应商，也关闭假设的上游被攻陷攻击向量。

### 说明

- **Wave 3 待办**：`ads-walmart`、`ads-ctv` + `audit-ctv`、`ads-retail-media` 主协调器、`ads-pmax-feed`、`ads-mmm`、`ads-incrementality`、创意管道 v2（Veo 3.1、Runway Gen-4.5、Kling 3.0 Omni、Seedance 2.0）、4 个优先行业模板（DTC 订阅、市场卖家、汽车经销商、EdTech）、合规证明包、路由表两级重构（子技能数量超过约 25 时触发；当前 22），以及配套 `audit-amazon` / `audit-attribution` / `audit-server-side` 代理，使 `/ads audit` 可并行分派 Wave 2 子技能。
- **延续安全待办**：Wave 2 审计中的 2-MED 列表和 4-LOW 列表记录于计划文件。两者将与 Wave 3 子技能代理和 CTV 创意管道一同处理。

## [1.6.0] - 2026-05-17

### 新增

- 全部 20 个 SKILL.md 文件（主协调器 + 19 个子技能）新增 `tested_date: 2026-05-17` 和 `tested_with: claude-code v2.x` frontmatter，以符合正在形成的 Agent Skills 版本约定。
- `.github/CODEOWNERS`：将 PR 审查自动路由到维护者。
- `research/distribution-prep-v1.6.0.md`——面向 claudemarketplaces.com、awesome-claude-code 和 anthropics/skills 的提交包（本阶段仅跟踪，尚未提交）。
- 在 `scripts/url_utils.py` 的 SSRF 阻止列表中新增 IPv6 `::/128`（未指定地址）——关闭某些 Linux 内核将 `::` 别名化为 localhost 的内核强制转换边界情况。
- `CONTRIBUTING.md` 从 41 行扩展到约 120 行，新增三个章节：*添加新子技能*（镜像模式 + frontmatter 规格 + 路由表集成）、*添加参考文件*（渐进式披露约定）和*测试审计检查*（评估框架之前的手工工作流）。

### 变更

- 扩展 11 个子技能 `description:` 字段的触发范围——仅新增，不移除现有触发项：
  - `ads-google`：AI Max、AI Brief、广泛匹配审计、Quality Score 检查、搜索词审计、Smart Bidding、FUE、文本定制、品牌排除
  - `ads-meta`：Andromeda、GEM、Lattice、Entity-ID 聚类、ASC、AAC、创意多样性、Sales / Leads / App 优化、Threads ads
  - `ads-tiktok`：USDS（Jan-2026 分拆后）、用于检索的创意多样性
  - `ads-apple`：AdAttributionKit、浏览归因
  - `ads-audit`：付费媒体审计、付费广告审计、广告花费审计、广告审计
  - `ads-competitor`：Meta Ad Library、Facebook Ad Library、Google Ads Transparency、竞争对手创意、竞争对手研究
  - `ads-creative`：创意多样性分数、广告变体审计（Andromeda Entity-ID 检索评分）
  - `ads-landing`：LP 审计、落地页 CRO、点击后 CRO
  - `ads-linkedin`：ABM ads、Thought Leader Ads、预测受众、B2B paid（附 Oct 2025 术语变更说明）
  - `ads-microsoft`：Bing 搜索广告、Microsoft 搜索广告、Google 导入审计
  - `ads-youtube`：可跳过插播广告、YouTube Shorts ads、Demand Gen、VAC、CTV YouTube ads
- `ads/references/benchmarks.md`——澄清引用日期；WordStream / Triple Whale / SplitMetrics 2025 来源标注明确的 "verified current as of 2026-05-17" 标头。
- `skills/ads-plan/assets/mobile-app.md`——移除过期 Privacy Sandbox（Android）引用（Android Privacy Sandbox 于 Oct 17, 2025 退役）。替换为 Google Play Install Referrer + GA4 + MMP 指引。iOS 归因说明中，在 SKAdNetwork 旁新增 AdAttributionKit。
- `SECURITY.md`——明确私密披露渠道：GitHub Security Advisory 现在是唯一支持的渠道；移除模糊的 "or contact the maintainer directly" 回退说法。新增复现步骤要求。
- `.gitignore`——新增 `research-prompt*.md` 和 `.research-*.md` 模式，防止未来研究提示词草稿被意外提交。

### 安全

- 全新网络安全审计确认 v1.5.1 基线为 **91/100**（May 2026 基线检查）。新 IPv6 `::/128` 条目将分数提升到 **92/100**（+1）。
- Wave 1 引入**零新增攻击面**：没有新代码路径、新网络出口或新子进程调用。唯一脚本变更是在 `_BLOCKED_NETS` 中增加一行 `::/128`。
- 为跨运行时 `--target=<host>` 安装矩阵记录 Wave 2 前加固清单：Playwright 错误脱敏、Replicate 结果 URL 再验证、SECURITY.md 出口文档，以及严格拒绝模式（`;&|$()<>`、前导 `-`、`..` 段、UNC 路径）的 `validate_install_target()` shell 函数。

### 说明

- v1.7.0 将交付跨运行时安装矩阵（Codex CLI / Cursor / Windsurf / Gemini CLI / Goose 的 `--target=`）、含黄金固定数据的 `tests/` 目录、`ads-google` AI Max 重写、`ads-meta` Andromeda + Entity-ID 预测器，以及 `ads-attribution`、`ads-server-side-tracking` 和 `ads-amazon` 子技能。
- GitHub 仓库 About 字段文本（347 字符，已优化）及 15 个建议仓库主题记录于 `research/distribution-prep-v1.6.0.md`——当用户准备公开时，在 GitHub 侧应用。

## [1.5.1] - 2026-04-14

### 安全

- 新增共享 SSRF 验证模块（`scripts/url_utils.py`），供所有处理 URL 的脚本使用。
- 阻止 IPv4 私有范围（127/8、10/8、172.16/12、192.168/16、169.254/16、0/8、100.64/10）和 IPv6（::1、fc00::/7、fe80::/10、::ffff:0:0/96）。
- DNS 解析失败现在拒绝 URL，而不是静默放行。
- 新增 `_sanitize_error()`，从错误消息中移除 API 密钥、令牌和密码。
- 新增参考图像扩展名允许列表，防止任意文件读取。
- 新增批量大小限制（最多 50 个任务）和尺寸边界（最大 8192px）。
- 获取前验证 Replicate API 响应 URL 为 HTTPS。
- 截断 Stability API 错误响应，防止信息泄露。

### 变更

- GitHub Actions 固定到完整 SHA 哈希，而不是可变版本标签。
- Dependabot 自动合并仅限补丁更新（此前为所有版本）。
- CI 工作流范围限定为 `permissions: contents: read`（最小权限）。
- CI 新增 `pip-audit`，用于依赖漏洞扫描。
- `install.sh` 先尝试标准 pip，再带警告回退到 `--break-system-packages`。
- 修复 `install.sh` trap 变量引用，使清理更安全。
- `.gitignore` 现在排除 `*.pem`、`*.key`、`*.p12`、`*.pfx`、`credentials.json`、`service-account.json`。

## [1.4.0] - 2026-04-01

### 新增
- **banana-claude 集成**：以 banana-claude（v1.4.1）替代 generate_image.py 作为默认图像生成供应商。使用 MCP 工具（`gemini_generate_image`、`set_aspect_ratio`）、五组件提示词公式、9 种领域模式和品牌预设。
- **语气到风格映射**（`voice-to-style.md`）：将 6 个品牌语气轴映射到 banana 的 [STYLE] 提示词组件的视觉属性。供 creative-strategist 和 visual-designer 代理使用。
- **广告文案框架**（`copy-frameworks.md`）：6 个成熟框架（AIDA、PAS、BAB、4P、FAB、Star-Story-Solution），附平台专用模板、字符数和电商/SaaS 示例。
- **电商创意手册**（`ecommerce-creative.md`）：5 种广告系列类型（产品上线、促销、季节性、再营销、品牌认知），附 banana 领域模式、宽高比、文案框架和预算分配。
- **视觉一致性锚定**：visual-designer 先生成一张 "hero" 图像，再将其作为风格参考传给后续所有广告系列素材。
- **3 变体 A/B 策略**：visual-designer 现在每份简报生成 3 个变体（基础、替代角度、光照/氛围变化），而不是 2 个。
- **文案区域验证**：format-adapter 使用 Claude vision 检查生成图像在平台专属文案区域内是否有清晰留白。
- **框架驱动文案**：copy-writer 应用选定框架结构，为每个平台生成 2 个变体（主要版 + A/B 替代版）。
- **多截图品牌 DNA**：ads-dna 采集 3 张截图（首页、产品页、关于页面），以形成更丰富的品牌锚定。
- **自动创建品牌预设**：ads-generate 在生成前从 brand-profile.json 创建 banana 预设。
- **广告系列费用追踪**：读取 banana 的 `~/.banana/costs.json` 并汇总逐广告系列创意花费。
- **质量门禁**：ads-generate 通过 Claude vision 为每张图像打 1-10 分；低于 6 分时自动重新生成。

### 变更
- **ads-generate**：banana MCP 为主要方式；generate_image.py 为已弃用回退方式。
- **ads-photoshoot**：使用 banana Product 模式（Studio、Floating、Ingredient）和 Editorial 模式（In Use、Lifestyle），分辨率为 2K。
- **visual-designer 代理**：五组件 banana 公式替代 7 条预处理规则。
- **creative-strategist 代理**：读取 voice-to-style.md、copy-frameworks.md 和 ecommerce-creative.md；每个概念生成 2 个视觉方向变体（摄影 + 插画）。
- **copy-writer 代理**：基于框架的文案，附吸引词验证和动作动词 CTA。
- **format-adapter 代理**：新增文案区域验证和费用追踪。
- **requirements.txt**：google-genai 改为可选（banana 处理图像生成）。
- **install.sh / install.ps1**：移除 Playwright chromium 安装；新增 banana-claude 依赖检查。
- 参考文件数量：21 至 23（新增 voice-to-style.md、copy-frameworks.md）。

### 弃用
- `scripts/generate_image.py`：保留为未安装 banana-claude 环境的回退方式。应改用 banana MCP 工具。

## [1.3.0] - 2026-04-01

### 新增
- **marketplace.json**：用于插件系统发现和更新机制（Issue #14）。
- 6 个技能新增**验证门禁**；从 PR #12（Tessl）择取：
  - `ads/SKILL.md`：Task 工具编排清晰化 + 子代理 JSON 分数验证
  - `ads-audit`：平台数据可用性检查 + 子代理分数字段验证
  - `ads-budget`：停止/扩量决策至少 14-day 数据 + 20-click/$100 数据充足性
  - `ads-creative`：数据存在性检查 + 防止假设的门禁
  - `ads-google`：至少 30-day 数据 + 74 检查完整性验证
  - `ads-youtube`：活跃广告系列检查 + 广告系列类型完整性门禁
- **GAQL 兼容性参考资料**（`gaql-notes.md`）：已知字段不兼容、去重模式、过滤范围最佳实践、旧 BMM 检测启发式方法。
- ads-google 中新增 **Google Ads MCP 集成**：通过 [google-ads-mcp](https://github.com/googleads/google-ads-mcp) 可选自动采集数据，并可回退为手动导出。
- **共享否定关键词列表支持**（G14/G15）：由共享列表覆盖的广告系列不再标记为 "missing negatives"。
- **关键词级品牌检测**（G05/G07/G-PM3）：从账户名称推导品牌词元，按关键词组成而非广告系列命名约定分类。
- **G-SYS1 诊断**：报告 API 抓取失败的指引，而不是静默跳过检查。
- 为 Dependabot PR 自动化创建 **`dependencies` 标签**。

### 修复
- **G03**：零展示关键词、已暂停广告组、匹配类型重复和仅停用词关键词稀释一致性分数造成的误报（误报约减少 18%）。
- **G04**：多地点广告系列结构造成的误报；现在先剥离地理标识符，再计算目标数。
- **G12**：Search Partners 逻辑反转；将 OFF 标记为错失机会（此前错误地标记 ON）。
- **G16/G-WS1**：浪费花费阈值提高为 >$10 花费 + 0 转化（此前标记所有未转化词，包括长尾探索）。
- **G17/FL04**：旧 BMM 误报；BROAD + Manual CPC 属于旧 BMM（不是有意广泛匹配）。仅标记 Smart Bidding 广告系列中的 BROAD。
- **G19**：搜索词可见性从截断前全部已获取词计算（此前从截断子集计算）。
- **G48/CT-FL5**：将 Smart Campaign 系统管理转化排除在 DDA 和计数类型检查之外，避免误报。
- **G-CT1**：HIDDEN/REMOVED 转化操作造成的错误重复检测；现在仅检查 ENABLED 操作。
- **转化追踪**：新增重复检测准确性规则（排除 HIDDEN/REMOVED，排除 Smart Campaign 系统转化）。

### 变更
- Dependabot：actions/checkout v4 → v6、actions/setup-python v5 → v6、Pillow `<12.0.0` → `<13.0.0`。
- 版本统一为 1.3.0（plugin.json 曾错误地为 2.0.0）。
- 参考文件数量：20 → 21（新增 gaql-notes.md）。

### 社区
- 关闭 PR #4、#5、#13（超出范围：白标改名、广告系列系统、FastAPI Web 应用）。
- 从 PR #12（Tessl）择取验证改进；18 个文件中的 6 个。
- 回复 Discussion #11（"Does this really work?"）。
- 关闭 Issue #14（marketplace.json 已交付）。
- GAQL 准确性修复源自 akarls-web fork（44 个审计引擎改进提交）。
- MCP 集成源自 double-agency fork。

## [1.2.0] - 2026-03-12

### 新增
- **Apple Search Ads 子技能**（`/ads apple`）：35 项检查，涵盖广告系列结构（BOFU/MOFU/Search Match）、出价健康度（CPT 与安装率、CPA Goals）、Creative Sets（Custom Product Pages）、MMP 归因（AppsFlyer/Adjust/SKAdNetwork）、预算节奏、TAP 版位覆盖（Today/Search/Product Pages），以及按应用类别和国家层级划分的目标 CPA 基准。
- 主协调器新增 **Context Intake** 步骤：Claude 现在在任何审计前询问行业、月度广告花费、主要目标和活跃平台；确保基准和建议匹配用户真实情况，而不是默认通用行业平均值。
- README 新增 **Google Ads MCP 参考**：为需要线上 API 连接审计的用户链接 [google-ads-mcp](https://github.com/googleads/google-ads-mcp)。
- README 新增 **FAQ 章节**：回答社区主要问题（API 登录、基准准确性、手动发布广告、预算上下文、平台支持）。
- README 新增 **"How It Analyzes Your Ads"** 章节：清楚解释手动数据输入模式和数据导出工作流。

### 修复
- `install.ps1`：PowerShell 5.1 在 git clone 时崩溃：git 进度写入 stderr，而 PS 5.1 在 `$ErrorActionPreference = "Stop"` 下将其视为终止错误。通过在克隆调用周围暂设 `Continue` 并使用 `2>&1 | Out-Null` 修复。
- `uninstall.ps1`：非 UTF-8-BOM 系统上的解析失败；双引号字符串中的 Unicode `→` 和 `✓` 字符导致 `TerminatorExpectedAtEndOfString`。替换为 ASCII 等价表示。
- `ads-google/SKILL.md`：否定关键词指引现在默认强制 Exact Match `[kw]` 和 Phrase Match `"kw"` 类型；绝不使用 Broad Match 否定关键词。否定关键词必须来自 Search Terms Report 数据，并分组成主题化 Shared Lists。包含过度屏蔽审查步骤。
- `ads/SKILL.md`：依据 Anthropic 技能规范移除不支持的 `allowed-tools` frontmatter 字段。
- `ads/SKILL.md`：将 `apple` 加入 `argument-hint` 子命令列表。
- 安装脚本：子技能数量从 12 → 13，以反映新增 ads-apple。

## [1.1.1] - 2026-02-11

### 修复
- M-CR2 与 M37 频次阈值歧义：澄清 M-CR2 为广告组级（<3.0），M37 为广告系列级（<4.0）。
- 电商模板 PMax 图像数量与 G31 审计检查对齐（每个素材组 15 → 20 张图像）。
- 房地产模板预算百分比范围扩大以覆盖 100%（此前 90-105%，现在 80-110%）。
- 信息产品模板 TikTok 分配说明：新增最低 $50/day 广告系列预算限制。
- ads-tiktok（两个步骤 7）和 ads-creative（两个步骤 6）的重复步骤编号。

### 新增
- 主协调器技能新增 `argument-hint` 字段，用于 CLI 子命令提示。

## [1.1.0] - 2026-02-11

### 修复
- 审计检查数量从 186 纠正为 190（实际总数：Google 74 + Meta 46 + LinkedIn 25 + TikTok 25 + Microsoft 20）。
- TikTok 预算充足性阈值与权威检查清单对齐（Pass ≥50x CPA、Warning 20-49x、Fail <20x）。
- 基准笔误：Local Services CPC `$7.85-$15-$30` → `$7.85-$15.00`。
- Call Campaigns 上下文说明：澄清创建与投放截止日期（Feb 2026 / Feb 2027）。
- Flexible Ads 上下文说明：上线日期从 2025 纠正为 2024。
- 评分系统加权理由：将 "20-25%" 纠正为 "25-30%"，以匹配实际平台权重。
- G59 移动速度：LCP 现在在移动视口（375x812）而非桌面视口测量。
- G61 schema 检查：按审计参考资料验证 Product/FAQ/Service 类型（而不是任意 schema）。
- 从 requirements.txt 移除未使用的 beautifulsoup4 和 lxml。

### 新增
- `uninstall.ps1`，实现 Windows 对等支持（Unix 已有 `uninstall.sh`）。
- `.gitattributes`，修复 GitHub 语言检测（Markdown，而不是 PowerShell）。
- google-audit.md 中新增研究上下文说明（ECPC 弃用、Call Campaigns 终止、Power Pack、AI Max）。
- meta-audit.md 中新增研究上下文说明（详细定向移除、Flexible Ads、Financial Products SAC）。
- linkedin-audit.md 中新增研究上下文说明（Connected TV、BrandLink、Live Event Ads、Accelerate campaigns）。
- scoring-system.md 新增加权理由章节，解释评级区间设计。
- ads-tiktok 和 ads-creative 流程步骤中新增评分系统引用。
- 补齐创意、落地页、预算和竞争对手报告的 `.gitignore` 模式。

### 变更
- 从全部 6 个代理 frontmatter 文件移除非规范 `color` 字段。
- 代理 frontmatter 现在仅使用官方 Claude Code 规范字段（name、description、model、maxTurns、tools）。

## [1.0.0] - 2026-02-11

### 新增
- 主协调器技能（`/ads`），包含行业检测和质量门禁。
- 12 个子技能：audit、google、meta、youtube、linkedin、tiktok、microsoft、creative、landing、budget、plan、competitor。
- 6 个并行审计代理：audit-google、audit-meta、audit-creative、audit-tracking、audit-budget、audit-compliance。
- 12 个参考文件，包含 2026 基准、出价决策树、平台规格和合规要求。
- 11 个行业模板：saas、ecommerce、local-service、b2b-enterprise、info-products、mobile-app、real-estate、healthcare、finance、agency、generic。
- 全平台共 190 项审计检查（Google 74、Meta 46、LinkedIn 25、TikTok 25、Microsoft 20）。
- Ads Health Score（0-100），采用严重程度加权评分。
- 用于 Unix/macOS/Linux 的 install.sh 和 uninstall.sh。
- 用于 Windows PowerShell 的 install.ps1。
- 代理 frontmatter 使用 model sonnet、maxTurns 20，并附示例区块。
- 子技能设置 user-invocable false，避免菜单杂乱。
- 参考文件遵循 RAG 模式（按分析需要加载）。
- 质量门禁：Broad Match 安全、3x Kill Rule、预算充足性、学习期保护。
