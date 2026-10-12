# 为 Claude Ads 做出贡献

Claude Ads 接受聚焦、有来源依据的变更，并要求保留隐私、能力如实披露、确定性验证和默认只读原则。

## 修改代码或指引之前

1. 阅读 `AGENTS.md`、控制面边界，以及相关技能、实现、固定测试数据和测试。
2. 搜索生态处置台账及当前 issue，避免重复已经审查的工作。
3. 对平台、政策、API、法规、基准或规格变更，收集当前官方或一手证据，并更新来源/声明覆盖情况。
4. 对来自外部仓库的想法，记录许可证和出处。公开不等于可以复用。

绝不提交凭据、客户/账户导出文件、客户数据、私有提示词、原始私有研究、本地绝对路径或代理会话记录。

## 开发环境设置

```bash
git clone https://github.com/AgriciDaniel/claude-ads.git
cd claude-ads
python -m venv .venv
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements.lock
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r .github/requirements-schema-tests.lock
.venv/bin/python -m pip check
.venv/bin/python -m pytest -q
```

仅在需要时将当前检出安装到宿主：

```bash
bash install.sh --source=local
```

不要使用 curl-to-shell 安装，也不要静默修改全局 Python。

## 拉取请求

- 创建聚焦的分支，排除无关变更。
- 说明问题、证据、公开契约变更、风险和验证情况。
- 添加从失败案例或预期能力推导的回归测试。
- 保持 JSON schema 兼容性，或声明主版本契约变更。
- 仅在实现、固定测试数据、测试和证据足以支持新状态时更新能力清单。
- 运行仓库审计和完整测试套件。

```bash
python scripts/release.py audit
python -m pytest -q
```

必需远程 CI 必须通过；本地成功不能替代跳过或因计费受阻的检查。

## 技能和代理

- 技能目录使用小写 kebab-case 和 `ads-` 名称。
- `SKILL.md` frontmatter 仅包含 `name` 和全面的 `description`。
- 在描述中说明技能做什么、何时触发。
- 将 `SKILL.md` 控制在约 500 行/5,000 tokens 以下。
- 将详细事实、控制项、示例和 schema 放到渐进式披露资源中。
- 使用有序检查、明确优先级、操作原因、不可信输入边界、输出契约和恢复行为。
- 工作代理返回符合 schema 的结果；一个主协调器拥有最终产物。
- 代理获得最小权限工具，不具有隐含变更权限。

为新路由范围添加正例、近似但不匹配、歧义及冲突案例。高风险行为也应加入 `evals/v2-behavior-evals.json`。

## 平台控制项和来源

- 发布后保留稳定的控制项 ID。
- 建模适用性、可用性、地域、账户成熟度、所需输入、严重程度、来源 ID、稳定性和评分行为。
- 可选、测试版、付费高级、不可用及不符合资格的功能保持不计分。
- 不对同一根本问题重复扣分。
- 没有来源、范围、方法和到期信息时，不添加精确阈值。
- 未知和不适用是有效结果，不是需要隐藏的失败。

## 适配器和账户变更

每个适配器实现能力发现、读取快照、草稿、执行、验证和回滚接口。新适配器从只读开始。

写入能力需要沙箱固定测试数据、幂等性、精确对象范围、批准、上限、验证、审计、回滚和对抗测试。v2 不支持永久删除。

## 安全报告

不要为漏洞创建公开 issue。使用仓库私密的 [GitHub Security Advisory](https://github.com/AgriciDaniel/claude-ads/security/advisories/new) 渠道，并包含受影响版本、复现步骤及影响。

## 发布工作

发布候选项必须通过来源时效性、确定性/模型评估、安全/隐私/许可证扫描、安装矩阵、可重复打包、SBOM/校验和生成和全新上下文验证。在独立公开发布门禁获得明确批准之前，仓库可见性保持私有。
