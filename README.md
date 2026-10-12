<p align="center">
  <img src="assets/banner.svg" alt="Claude Ads，以 Claude 为优先、覆盖十二个广告平台的付费媒体运营" width="100%">
</p>

# Claude Ads 独立中文语言包

面向代理商、顾问和企业内部效果营销团队，以 Claude 为优先、可移植的付费媒体运营工具。本页是独立简体中文（`zh-CN`）语言包的介绍及完整产品说明。

中文资源的唯一维护源是 `claude_ads_core/locales/zh-CN`。文档按原始相对路径镜像保存在 `documents/` 下；派生文件由构建流程生成，不应分别手工维护。使用 `scripts/build_locale.py --check` 校验语言包与生成结果。输出默认使用中文；需要英文输出时，设置 `CLAUDE_ADS_LOCALE=en` 或使用 CLI 参数 `--locale en`。操作语言与广告创意的投放语言相互独立，机器字段、命令、标识符和原始证据保持原样。

### 中文阅读入口与升级

- [主技能与命令路由](ads/SKILL.md)、[设置流程](skills/ads-setup/SKILL.md)、[报告流程](skills/ads-report/SKILL.md)。
- [开发说明](CONTRIBUTING.md)、[安全策略](SECURITY.md)、[产品边界](control-plane/PRODUCT_BOUNDARIES.md)、[发布要求](control-plane/RELEASE_REQUIREMENTS.md)。
- [第三方说明中文译本](claude_ads_core/locales/zh-CN/documents/THIRD_PARTY_NOTICES.md)仅供阅读，不替代有法律效力的原文。英文完整基线保存在 `claude_ads_core/locales/en/documents/`。

修改中文语言包后运行 `python scripts/build_locale.py`，再运行 `python scripts/build_locale.py --check`。同步检查会报告新文档、删除或改名、英文基线变更、代码块变化、断链和生成视图漂移。升级上游时先合并英文基线，再逐项复核译文和清单中的 `source_sha256`；不要只更新哈希来跳过翻译复核。生成器遇到未合并的本地视图改动会停止，不会覆盖 `docs/` 等未管理文件。

原生插件使用随包提供的中文入口，无需先运行构建。修改此源码不会自动更新已经安装的插件缓存；重新安装或加载本地版本后，在新会话验证。安装到其他目录应使用原有安全安装器，而不是手工覆盖全局技能。中文资源不会回写已显示的历史消息。

Claude Ads 将获授权的导出文件或账户读取结果转化为有来源依据的审计、计划、创意工作流、实验、监控和报告。默认只读。在具体平台及操作通过批准、幂等性、验证、审计和回滚门禁之前，线上变更保持禁用。

> [!NOTE]
> Claude Ads 有两个发布渠道：位于 [`AgriciDaniel/claude-ads`](https://github.com/AgriciDaniel/claude-ads) 的**公开发行版**（MIT，无需会员资格），以及位于 `AI-Marketing-Hub/claude-ads` 的**社区镜像**；[AI Marketing Hub Pro](https://www.skool.com/ai-marketing-hub-pro) 会员可在后者获得提前访问和直接协作机会。

<p align="center">
  <img src="assets/diagrams/how-it-works.svg" alt="经过验证的输入由有界工作代理处理，形成符合 schema 的发现和确定性报告" width="100%">
</p>

## 功能

- 使用注明日期的证据及明确的置信度审计付费媒体账户。
- 规划广告系列、渠道、预算、衡量方案和实验。
- 创建文案、图像、视频及产品照片的简报和素材。
- 监控预算节奏、投放、追踪、疲劳、政策和表现。
- 生成版本化 JSON，再渲染为 Markdown、HTML 和可选 PDF。
- 起草安全的账户变更，默认不执行。
- 报告缺失数据、过期来源、矛盾和部分失败。

## 平台

<p align="center">
  <img src="assets/diagrams/platform-coverage.svg" alt="十二个一等支持的付费广告平台范围" width="100%">
</p>

| 领域 | 平台 |
| --- | --- |
| 搜索、视频和社交 | Google Ads, Meta Ads, YouTube Ads, LinkedIn Ads, TikTok Ads, Microsoft Advertising, Reddit Ads, Snapchat Ads, X Ads |
| 商务和零售媒体 | Apple Ads, Amazon Ads, Pinterest Ads |

每个平台都具有专项技能、审计工作代理、控制项参考资料、能力声明和可测试的路由接口。[能力清单](control-plane/manifests/capability-manifest.json) 是线上读取和写入能力的权威记录。

## 命令

独立安装使用 `/ads`。Claude Code 插件采用命名空间，使用 `/claude-ads:ads`。两者加载同一个 `ads/SKILL.md` 契约。

| 命令 | 结果 |
| --- | --- |
| `/ads setup` | 创建客户、账户、KPI、隐私和防护规则配置 |
| `/ads audit [all\|platform\|scope]` | 运行完整或限定范围、以证据为依据的审计 |
| `/ads plan` | 制定渠道、广告系列、预算、竞争对手和衡量计划 |
| `/ads create` | 制作文案、图像、视频或产品照片素材 |
| `/ads launch --draft` | 起草广告系列变更计划，不修改账户 |
| `/ads monitor` | 审查预算节奏、投放、追踪、疲劳、政策和表现 |
| `/ads optimize --draft` | 起草以证据为依据的优化变更 |
| `/ads experiment` | 设计或解读对照实验 |
| `/ads report` | 渲染已验证的 JSON 运行包 |
| `/ads research refresh` | 刷新平台、政策、API、基准和生态证据 |
| `/ads validate` | 验证契约、运行、能力、成熟度或发布准备情况 |
| `/ads status`, `/ads next` | 显示当前状态和最高优先级阻碍项 |

`/ads google`、`/ads meta`、`/ads amazon` 和 `/ads reddit` 等平台快捷命令会路由到对应平台审计。

宿主界面中的 `Skip`、`Submit`、`Other` 等控件由宿主应用提供，不属于本项目，中文语言包不会修改这些控件。

## 演示

<p align="center">
  <img src="assets/demo.gif" alt="英文历史演示：Claude Code 内的 Claude Ads 命令发现体验" width="800">
</p>

此 GIF 是**英文历史演示**，展示最初的命令发现体验，不代表当前中文交互。上方 v2 命令表及平台表才是当前的权威说明。

## 安装

Claude Code 是规范运行时。Codex、Gemini、Cursor、Windsurf、Goose 和兼容的 Agent Skills 宿主可在其运行时支持范围内使用同一套技能文件。

优先使用宿主原生插件流程，或具有已验证 SHA-256 校验和的带标签发行归档。绝不要将远程安装程序直接通过管道传给 shell。

Claude Code 的原生插件流程如下：

```text
/plugin marketplace add agricidaniel/claude-ads
/plugin install claude-ads@ai-marketing-hub-claude-ads
```

如果在 v2.0.0 之前添加过此市场，Claude Code 仍可能以过期本地别名 `agricidaniel-claude-ads` 保存它。移除该别名，然后重新添加并安装：

```text
/plugin marketplace remove agricidaniel-claude-ads
/plugin marketplace add agricidaniel/claude-ads
/plugin install claude-ads@ai-marketing-hub-claude-ads
```

也可从公开仓库的本地克隆安装：

```bash
git clone https://github.com/AgriciDaniel/claude-ads.git
cd claude-ads
bash install.sh --source=local
```

显式选择其他独立宿主：

```bash
bash install.sh --target=codex --source=local
bash install.sh --target=gemini --source=local --no-deps
```

PowerShell 使用同一套受管所有权模型：

```powershell
git clone https://github.com/AgriciDaniel/claude-ads.git
Set-Location claude-ads
.\install.ps1 -Source local
```

受管依赖支持声明的 Linux、macOS 和 Windows wheel 矩阵上的 CPython 3.11 和 3.12。不支持的解释器会在目标目录发生变更之前失败。仅安装技能时，使用 `--no-deps` 或 `-NoDeps`。

浏览器采集需要操作者安装 Playwright 浏览器载荷。PDF 渲染需要宿主的 WeasyPrint 和 Pango 系统库。详情见[外部运行时依赖清单](control-plane/manifests/external-runtime-dependencies.json)。

仅卸载清单记录为本项目所有的文件：

```bash
bash uninstall.sh --target=claude
```

PowerShell 对应脚本为 `uninstall.ps1`。

## 架构

<p align="center">
  <img src="assets/diagrams/architecture.svg" alt="一个主协调器分派平台和跨平台工作代理，然后验证并渲染规范 JSON 运行包" width="100%">
</p>

由一个主协调器负责范围、策略、汇总和最终产物。工作代理分析有界任务片段，返回符合 schema 的发现。必需工作代理失败会使本次运行标记为部分完成，绝不会被悄然呈现为完整审计。

规范结果采用版本化 JSON。Markdown、HTML 和 PDF 均由同一个经过验证的运行包渲染而来。

## 评分和证据

<p align="center">
  <img src="assets/diagrams/ads-health-score.svg" alt="健康度与证据覆盖率保持独立；评分需要已批准的平台配置" width="100%">
</p>

控制项使用 `pass`、`fail`、`unknown` 或 `not_applicable`。

- 健康度、证据覆盖率、监管风险敞口和机会保持独立。
- 未知控制项降低证据覆盖率，但不改变已知健康度。
- 覆盖率达到 80% 或以上可评级，60 至 79% 为暂定，低于 60% 表示证据不足。
- 可选、测试版、付费高级、不可用及不符合资格的功能不参与评分。
- 已禁用或未批准的平台配置不会产生健康度分数。
- 失败的平台从组合评分中排除，并使本次运行标记为部分完成。

参见[评分参考资料](ads/references/scoring-system.md) 和 `claude_ads_core/scoring.py` 中的生产实现。

## 账户安全

所有适配器默认只读。执行变更需要：

1. 具体操作具有经过测试且已启用的能力。
2. 明确的账户和对象 ID。
3. 可供人阅读的变更前后差异及影响范围。
4. 所有者在账户定义的上限内批准。
5. 幂等键、审计目标、回滚方案及验证窗口。
6. 验证远程状态仍符合变更前置条件。

没有上限就不能写入。v2 不支持永久删除。凭据应保存在环境变量、操作系统钥匙串或批准的密钥管理器中，绝不能保存在仓库、配置、报告或日志中。

## 证据和发布控制

可安全公开的 `control-plane/` 记录产品边界、注明日期的来源、声明、能力、安全规则、隐私规则、生态决策和发布要求。

- 没有来源，就没有当前平台声明。
- 没有实现、固定测试数据和测试，就没有能力声明。
- 没有批准和回滚，就没有账户变更。
- 没有独立验证，就不能发布。

参见[发布要求](control-plane/RELEASE_REQUIREMENTS.md)和[公开发布策略](control-plane/PUBLISHING_POLICY.md)。

## 开发

创建虚拟环境并运行完整套件：

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements.lock
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r .github/requirements-schema-tests.lock
.venv/bin/python -m pip check
.venv/bin/python -m pytest -q
```

常用专项检查：

```bash
python -m claude_ads_core --version
python -m claude_ads_core validate finding path/to/finding.json
bash -n install.sh uninstall.sh
```

中文语言包维护与输出切换：

```bash
python scripts/build_locale.py --check
CLAUDE_ADS_LOCALE=en python -m claude_ads_core --help
python -m claude_ads_core --locale en --help
```

## 仓库地图

```text
ads/                  main skill, interface metadata, and shared references
skills/               platform and lifecycle skills
agents/               platform, cross-platform, research, and verifier workers
claude_ads_core/      typed contracts, adapters, validation, and scoring
control-plane/        evidence, capability, safety, maturity, and release state
scripts/              browser, creative, reporting, and release helpers
evals/                routing and behavioral evaluation cases
tests/                deterministic, security, installer, and adapter tests
```

上述目录依次承载主技能与共享参考资料、平台与生命周期技能、各类工作代理、类型化契约与评分、控制面状态、辅助脚本、行为评估以及确定性和安全测试。中文唯一维护源位于 `claude_ads_core/locales/zh-CN`。

## 贡献者与致谢

Claude Ads 得益于社区的问题报告、功能请求和修复提案。感谢以下贡献者，他们的工作为 v2.0.2 提供了参考。部分提案已独立实现或被后续方案取代；这些致谢认可贡献，并不表示每份提交的补丁均已合并。

| 贡献者 | 贡献 | 讨论 |
| --- | --- | --- |
| [@principisimone-sys](https://github.com/principisimone-sys) | Search 与 DSA 重叠检查请求 | [#65](https://github.com/AgriciDaniel/claude-ads/issues/65) |
| [@HarKro753](https://github.com/HarKro753) | Meta 账户、Pixel 和转化冷启动请求 | [#53](https://github.com/AgriciDaniel/claude-ads/issues/53) |
| [@plcosta](https://github.com/plcosta) | 市场名称大小写规范化报告和文档修复提案 | [#17](https://github.com/AgriciDaniel/claude-ads/issues/17), [#18](https://github.com/AgriciDaniel/claude-ads/pull/18) |
| [@ulises2k](https://github.com/ulises2k) | 过期市场别名安装报告 | [#56](https://github.com/AgriciDaniel/claude-ads/issues/56) |
| [@kutzki](https://github.com/kutzki) | Windows 依赖锁定及旧安装更新报告 | [#57](https://github.com/AgriciDaniel/claude-ads/issues/57) |
| [@SamaEducationalCo](https://github.com/SamaEducationalCo) | 落地页分析失败后出现误导性评级的报告 | [#61](https://github.com/AgriciDaniel/claude-ads/issues/61) |
| [@Bortlesboat](https://github.com/Bortlesboat) | 落地页分析失败修复提案 | [#66](https://github.com/AgriciDaniel/claude-ads/pull/66) |
| [@gabbyran2026-gif](https://github.com/gabbyran2026-gif) | 目标锁定测试子进程修复提案 | [#58](https://github.com/AgriciDaniel/claude-ads/pull/58) |
| [@AbundantASG](https://github.com/AbundantASG) | 限定范围的目标锁定测试子进程修复提案 | [#59](https://github.com/AgriciDaniel/claude-ads/pull/59) |
| [@hendrixfreire](https://github.com/hendrixfreire) | 敏感文件忽略模式报告 | [#32](https://github.com/AgriciDaniel/claude-ads/issues/32) |
| [@josefresco](https://github.com/josefresco) | 不可执行的 Smart Conversions 移除建议报告 | [#50](https://github.com/AgriciDaniel/claude-ads/issues/50) |
| [@dead-simba](https://github.com/dead-simba) | 重新审视 Meta 架构指引的请求 | [#15](https://github.com/AgriciDaniel/claude-ads/issues/15) |
| [@c6zks4gssn-droid](https://github.com/c6zks4gssn-droid) | 包含 CodeQL 的仓库工具提案 | [#29](https://github.com/AgriciDaniel/claude-ads/pull/29) |

报告问题或提出变更请参见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 隐私

客户数据、原始私有研究、捕获的提示词、凭据、账户导出文件和代理会话记录绝不能进入 Git 历史、报告或发行归档。将凭据保存在环境变量、操作系统钥匙串或批准的密钥管理器中。

## 许可证

Claude Ads 的原创代码和文档采用 MIT License。第三方 API、商标、文档和被引用产物仍受各自条款约束。在引入外部工作成果前，请审查[来源台账](control-plane/manifests/source-ledger.json)及[第三方声明](THIRD_PARTY_NOTICES.md)。中文法律声明译本仅供理解，不替代原始法律文本。
