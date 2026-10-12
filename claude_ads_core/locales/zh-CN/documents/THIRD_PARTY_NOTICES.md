# 第三方声明

> 本译本仅供理解和参考，不是法律替代文本，也不替代原始许可证、声明或具有约束力的英文原文。绑定哈希的原始 `THIRD_PARTY_NOTICES.md` 保持不变；主协调器和语言包构建流程不得以此译本覆盖该原文。

Claude Ads 采用 MIT 许可证。产品名称、API、文档、公开 issue、拉取请求和引用的仓库仍归各自所有者所有，本仓库不对它们重新许可。

## 设计与研究出处

- Brainstein 采用 Apache-2.0。Claude Ads v2 对来源、能力、成熟度、编排和发布门禁思想采用原创领域专用实现；v2 控制面未复制 Brainstein 源代码。
- Anthropic 的公开 skill-creator 材料在技能层面采用 Apache-2.0。它为渐进式披露、触发评估和确定性辅助工具指引提供了参考；Claude Ads 提示词及实现均为原创。
- 私有 Fable 研究仅用作不再分发的设计输入。不包含任何原始或捕获的提示词、私有语料、近似改写或受限产物。
- GitHub issue 和拉取请求在生态处置台账中汇总并链接。未经仓库许可证及贡献者署名审查，不复制文本和补丁。

## 运行时与开发依赖

依赖从其发布者安装，并保留各自的许可证：

- Requests：Apache-2.0。
- urllib3：MIT。
- Playwright for Python：Apache-2.0。
- Cryptography：Apache-2.0 或 BSD-3-Clause。
- Pillow：MIT-CMU。
- ReportLab 和 WeasyPrint 代码：BSD-3-Clause。ReportLab wheel 还包含采用 GPL-2.0-or-later（附文档嵌入例外）的 DarkGarden，以及 Bitstream Vera 字体条款。
- Matplotlib：Matplotlib 1.3+ 许可证（`LicenseRef-Matplotlib-1.3`），以及随附的字体/样式/色图声明，包括 OFL-1.1、Apache-2.0、MIT 和 BSD 风格条款。
- PyYAML 和 pytest：MIT。

传递闭包是发行清单的一部分，本摘要未将其穷尽。特别是，Pyphen 代码提供 GPL-2.0-or-later OR LGPL-2.1-or-later OR MPL-1.1 许可选项，其词典具有按语言区分的条款。依赖清单保留全部 119 个选定 wheel 中发现的每个类似许可证/声明文件的精确路径、SHA-256、文本和产物归属。webencodings 0.5.1 wheel 不包含匹配的内嵌路径，因此明确记录为无文档，而不是分配编造的声明文本。

发行 SBOM 从已签入、由发布者元数据支持的依赖清单生成，并验证每项声明的直接依赖及锁定的传递边。本声明不能替代该机器生成的清单。

## 平台接口

Google、Meta、YouTube、LinkedIn、TikTok、Microsoft、Apple、Amazon、Reddit、Pinterest、Snapchat 和 X 的名称及 API 均为第三方产品。能力参考资料记录互操作性，不暗示关联、背书，或绕过平台条款、访问控制、政策及审查的许可。
