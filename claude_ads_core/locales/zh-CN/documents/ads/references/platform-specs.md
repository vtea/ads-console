# 创意规格解析

**已核验：** 2026-08-25
**刷新到期：** 2026-09-24
**证据状态：** 来源索引和验证工作流，而非通用规格表

创意要求因格式、版位、目标、地理区域、账户资格和产品发布而异。验证素材前，先确定精确格式。单一“平台规格”表不安全，因为它会悄然合并不适用于同一版位的要求。

## 解析顺序

1. 记录平台、目标、格式、版位、目标页面、地理区域，以及当前账户 UI 选择。
2. 打开匹配的平台专属创意参考文档。
3. 根据当前官方帮助页面或 API schema 核实易变限制。
4. 当素材必须跨版位投放时，优先采用更严格的要求。
5. 在账户 UI 中预览，并验证渲染后的裁切、叠加层、文字、字幕、音频、CTA、披露和目标页面。
6. 记录来源 ID、检索日期、观察到的 UI/API 版本和例外。

来源不一致时，不要猜测。将检查标记为 `unknown`，保留两个值，并请求当前预览或 API 验证。

## 当前来源入口

| 平台 | 第一方来源 | 范围 |
| --- | --- | --- |
| Google / YouTube | `google-rsa-official` — [响应式搜索广告](https://support.google.com/google-ads/answer/7684791) 和 [Google Ads 素材要求](https://support.google.com/adspolicy/answer/6368661) | 搜索文字和通用素材政策 |
| Meta | `meta-video-ads-official`：[Meta Reels 广告](https://www.facebook.com/business/ads/facebook-instagram-reels-ads) | Reels 创意指导和格式发现 |
| LinkedIn | `linkedin-ads-guide-official`：[LinkedIn 广告指南](https://business.linkedin.com/advertise/ads/ads-guide) | 当前格式入口 |
| TikTok | `tiktok-ad-format-policy-official`：[广告格式和功能](https://ads.tiktok.com/resources/help/article/tiktok-ads-policy-ad-format-and-functionality) | 创意和编辑规范要求 |
| Microsoft | `microsoft-ad-types-official`：[ResponsiveSearchAd schema](https://learn.microsoft.com/en-us/advertising/campaign-management-service/responsivesearchad?view=bingads-13) | 当前 v13 响应式搜索广告行为 |
| Apple | `apple-ads-creative-official`：[Apple Ads 资源](https://ads.apple.com/app-store/resources) | Apple Ads 资源和创意入口 |
| Amazon | `amazon-creative-acceptance-official`：[通用要求](https://advertising.amazon.com/help/GDG2CCTRU55BYY2Y) | Amazon Ads 通用创意要求 |
| Reddit | `reddit-ads-help-official` — [Reddit Ads 帮助](https://business.reddithelp.com/s/) | 当前 Reddit 帮助和政策发现 |
| Pinterest | `pinterest-ad-specs-official` — [Pinterest 广告规格](https://help.pinterest.com/en/business/article/pinterest-product-specs) | Pinterest 格式和素材 |
| Snapchat | `snap-creative-specs-official` — [Snap 创意规格](https://forbusiness.snapchat.com/advertising/ad-formats) | Snap 广告格式入口 |
| X | `x-creative-specs-official` — [X Ads 创意规格](https://business.x.com/en/help/campaign-setup/creative-ad-specifications) | X 格式和素材 |

这些页面是发现入口，不能证明每种格式在特定账户中都可用。给出通过结果或执行变更前，重新检查活跃 UI/API。

## 精确保留的事实

Google 当前的响应式搜索广告文档指出，RSA 最多接受 15 个标题和四条描述，标题字段最多支持 30 个字符。Microsoft 当前 v13 schema 指出，其 RSA 接受三到 15 个标题和两到四条描述。这些事实仅适用于所指明的格式；不能确立跨平台文字标准。

## 验证输出

为每项素材返回：

- `platform`、`format`、`placement`、`objective` 和 `geography`。
- 观察到的尺寸、时长、文件类型、文件大小、文字字段、音频、字幕、目标页面、CTA 和披露。
- 每项适用要求的 `pass`、`fail`、`unknown` 或 `not_applicable`。
- 每项精确限制的官方来源 ID 和检索日期。
- 预览证据及任何裁切或叠加风险。
- 保留创意概念的补救措施。

## 非通用规则

- 不存在通用竖屏视频安全区域。依据当前版位预览和平台叠加层指导验证。
- 建议尺寸并不总是最低接受要求；须标注区别。
- 平台上传成功不能证明政策批准或良好渲染。
- 字符计数可能使用平台专属标准化；当精确接受条件重要时，通过平台 API/UI 验证。
- 不要将“最佳实践”素材数量或时长转化为合规失败。
