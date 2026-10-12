# 安全策略

## 报告漏洞

如果发现安全漏洞，请通过**私密 GitHub Security Advisory 渠道**负责任地报告：

1. **不要创建公开 issue**（公开 issue 会在漏洞修复前暴露漏洞）。
2. 在公开仓库上创建 [GitHub Security Advisory](https://github.com/AgriciDaniel/claude-ads/security/advisories/new)。这是唯一受支持的私密披露渠道——请勿发送电子邮件或私信。
3. 包含：受影响版本（例如 v2.0.0）、复现步骤和影响评估。

我们力争在 **48 小时**内确认收到报告，并在 **7 天**内提供预计解决时间表。

## 支持的版本

仅最新版本接收安全更新。

## 安全实践

- 本仓库不存储凭据或 API 密钥。
- 安装脚本仅写入配置的宿主根目录，规范化目标路径，拒绝链接逃逸和非本项目所有的文件冲突，并记录所有权清单。Windows 安装程序在首次写入目标之前预检完整计划，并拒绝重解析点、受管环境和后期文件冲突。
- Python 依赖安装到隔离的虚拟环境中。
- 共享 SSRF 验证（`scripts/url_utils.py`）拒绝非公开 IPv4/IPv6，将 Requests 固定到经过验证的数字地址，同时保留 Host/SNI/TLS 验证，并在每次重定向时重新进入防护。Playwright 无法固定 Chromium 的套接字解析，因此浏览器执行默认被拒绝，除非外部操作系统/容器出口沙箱提供绑定当前环境、短期有效的 Ed25519 签名证明。截图采集会写入与摘要绑定的回执，注明证明、签发者、信任密钥、环境和产物。
- PDF 报告文本（包括健康度分数说明）在 ReportLab 标记解析前统一经过一个转义辅助函数，因此报告值无法注入标记。
- 错误消息在到达 stdout、JSON 输出或审计报告前经 `sanitize_error()` 清理——移除 `key=`、`token=`、`secret=`、`password=` 和裸 `Bearer <token>` 子串。
- GitHub Actions 固定到完整提交 SHA。Dependabot 工作流只读，不能批准或合并自身的拉取请求。必需分支检查之后，由人工拥有合并决定权。
- 每次 CI 构建运行精确版本的 `pip-audit`。新的、未处理、过期或与执行路径相关的安全公告均失败即关闭。已报告公告只有通过带到期时间、精确版本的 `not_affected` 记录，并具备经过验证的代码路径证据，才可通过。

## 出站网络目标

运行时可能联系以下端点。所有用户提供的 URL 在任何抓取尝试之前都经过 SSRF 阻止列表；可信供应商端点为硬编码，用户无法影响。

| 端点 | 用途 | 脚本 | 门禁 |
|----------|---------|--------|----------|
| `generativelanguage.googleapis.com` | Gemini 图像生成（回退路径） | `generate_image.py` | API 密钥（环境变量） |
| `api.openai.com` | OpenAI 图像生成（回退路径） | `generate_image.py` | API 密钥（环境变量） |
| `api.stability.ai` | Stability AI 图像生成（回退路径） | `generate_image.py` | API 密钥（环境变量） |
| `api.replicate.com` | Replicate 模型调用（回退路径） | `generate_image.py` | API 密钥（环境变量） |
| Replicate 返回的结果 URL | 获取生成图像字节 | `generate_image.py` | HTTPS 检查 + 经 `url_utils.validate_url` 再次验证 SSRF（v1.7.0+） |
| 用户提供的 URL | 落地页分析、截图采集、页面抓取 | `analyze_landing.py`, `capture_screenshot.py`, `fetch_page.py` | DNS 固定 HTTP；浏览器默认拒绝，除非外部出口沙箱具有证明，并逐请求验证 |
| `github.com`（只读，通过 git clone） | 技能安装 | `install.sh`, `install.ps1` | 硬编码仓库 URL |
| PyPI（`pypi.org`, `files.pythonhosted.org`） | Python 依赖安装 | `install.sh`, `install.ps1` | 硬编码；由 `pip` 信任 |

如果发现上述列表以外的出站目标，请通过前述披露渠道报告。

## 浏览器出口证明

不支持布尔形式的 `--egress-sandbox-attested` 逃生开关。浏览器执行仅接受符合 `control-plane/schemas/egress-sandbox-attestation.schema.json` 且使用 Ed25519 认证的 JSON 文档。签名覆盖省略 `authentication.signature_b64url` 后的规范 JSON 对象：UTF-8、键按字典序排序、无无意义空白、不使用 ASCII 转义。证明必须：

- 指定 `claude-ads-browser-egress` 受众及精确环境；
- 在签发后 24 小时内到期；
- 声明所有必需的 IPv4、IPv6、DNS 重绑定、重定向、子资源、元数据、私有地址和失败即关闭控制；
- 包含测试或策略证据引用；以及
- 由密钥签名，其公钥部分、密钥 ID 和环境 ID 通过文档外部的 `CLAUDE_ADS_EGRESS_ATTESTATION_PUBLIC_KEY_B64URL`、`CLAUDE_ADS_EGRESS_ATTESTATION_KEY_ID` 和 `CLAUDE_ADS_EGRESS_ENVIRONMENT_ID` 提供。

运行时仅接收 Ed25519 公钥，因此无法制造证明。缺失依赖、信任材料、控制项、证据、签名、环境绑定或时效性时，在 Chromium 启动前失败即关闭。schema 和签名认证签发者的声明；操作者仍须独立配置和测试指定网络边界。

截图及其回执属于机密。它们使用同目录原子替换，在可用 POSIX 权限的地方设置为 `0600`，回执中省略 URL 路径和查询，不得提交、附加到公开 issue 或放入发行包。采集需要经过验证的机密 `data-lifecycle` 契约；回执包含该契约的生命周期字段，且仅使用相对仓库/运行的产物定位信息。

## 数据生命周期

每个持久化运行和工作流产物声明 `claude_ads_core/schemas/v1/data-lifecycle.schema.json` 中的版本化契约。产品策略为 `control-plane/manifests/data-lifecycle-policy.json`。它记录分类、明确的零秒产品最短保留期加上操作者定义的用途约束截止日期或例外、非公开数据的已验证加密证据、最小权限角色、删除和独立验证，以及私密事件处理。这些是操作防护措施，不是法律保留要求或合规声明。

创意生成 JSON 仅存储提示词 SHA-256 值和规范脱敏摘要。截图和生成 JSON 仅存储相对定位信息。原始提示词、私有供应商载荷和解析后的本地路径保留在发布产物之外，并应通过获批准的临时/私密证据渠道处理。
