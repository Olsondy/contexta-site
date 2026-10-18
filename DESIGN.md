# Design System: Contexta 官网

继承小程序的「安静自习桌」视觉系统（权威来源：`contexta-client/DESIGN.md` 与 `src/styles/tokens.css`），官网只增加营销页需要的规则。

## 场景与明暗

深色、浅色两套主题，色值都沿用小程序 `tokens.css`。默认跟随系统 `prefers-color-scheme`；顶栏按钮可手动切换，选择存在 `localStorage`（`ctxa-theme`），`<head>` 内联脚本在渲染前确定主题，避免闪烁。手动切换时用 View Transitions API：新主题以按钮为圆心、0.65 秒圆形扩散铺满整屏；不支持该 API 或开启减少动态效果时直接切换。下表为深色值；浅色值见 `site.css` 的 `:root[data-theme="light"]`。Logo 深色主题用 ivory 版 `contexta-mark.svg`，浅色主题用小程序同款 ink 版 `contexta-mark-ink.svg`。

## 颜色

| 角色 | 值 | 用途 |
| --- | --- | --- |
| canvas / canvas-outside | `#252825` / `#1C1F1C` | 页面底色；词本段落与页脚用更深的外部底色分隔节奏 |
| surface / surface-muted | `#2E312E` / `#363A36` | 词卡、选项、辨析面板 |
| ink / ink-2 / ink-3 | `#F3F4EF` / `#C7CBC4` / `#A5ACA3` | 正文三级 |
| accent / accent-strong | `#9A90BA` / `#B8B0D4` | 主按钮、进度、强调文字；结尾「获取」段整屏铺满 accent |
| positive / negative / favourite | `#7BC7A4` / `#E0A095` / `#E5A05C` | 仅在词卡演示中表达正确、错误、收藏 |
| ivory | `#FCF9E8` | 仅用于 Logo |

颜色策略：Restrained，最后一屏 Drenched（accent 整屏，文字用画布色）。

## 字体

- 中文标题与说明：仓耳渔阳体 400/700（按页面用字子集化，`scripts/subset-fonts.sh`）。
- 英文单词、题目与 UI：Satoshi 400–900。
- 品牌字标：Jaldi 700，`letter-spacing: 0.04em`。
- 标题 `clamp()` 流体字号，桌面最大 76px；正文 17–18px，移动端 16px。

## 页面结构

产品一句话说得清，所以官网短：不写长文，不做滚动动画，不列功能清单。

1. 首屏：左侧标题「一个单词，就是一次语境练习。」+ 一句说明 + 入口；右侧手机循环演示 prized 的一次闭环：正面 → 轻触翻面看释义 → 开始学习 → 语境题点选、对错与最强迷惑项 → 学完印章、计数 +1（约 12 秒一轮，`site.js` 的 `TIMELINE`）。手机滚出视野或页面隐藏时暂停。桌面入口是小程序码，手机端改为「在微信搜索 语境助手 + 复制名称」（访客无法扫自己屏幕上的码）。配置了跳转地址（`ctxa-miniprogram-link`）时，手机端在搜索入口上方和结尾再加一个整宽的「打开小程序」按钮，顶栏按钮在手机上也直接打开。
2. 试一题（`canvas-outside` 底色）：同一个词的一道语境题，可开关中文辅助；作答后选项标出对错，展开逐项解析、最强迷惑项对比与「去小程序继续」，可重新作答。下方一行列出小程序里的其他能力，并标注非官方内容说明。
3. 结尾：accent 整屏，小程序码 + 微信搜索与复制名称。

动效只服务于说明产品：首屏文字与手机依次进场；后续段落滚动到时淡入上移；试一题答对的选项轻弹、答错的轻抖，解析逐条出现。

小程序码文件缺失时，两处都显示品牌标志，说明改为「微信小程序 · 语境助手」。`prefers-reduced-motion` 下关闭所有过渡与循环，手机停在释义页。

## 组件规则

- 主按钮：accent 底、画布色文字、圆角 16px、高 52px（移动端 48px）。
- 顶栏：透明，页面滚动后变为半透明画布色 + 1px 分隔线。
- 不使用功能卡片网格；其他能力只用一行圆点列表。
- 马克笔高亮：`linear-gradient(180deg, transparent 70%, rgba(154,144,186,.42) 70%)`，与小程序 Highlighter Ribbon 规则一致。
- 图标为内联 SVG，描边 1.7，圆角端点；不用 emoji。

## 内容边界

文案以 `PRODUCT.md` 为准：只描述已上线能力；雅思/托福内容标注「非官方内容」；不出现 AI 生成、真题、网页版入口或虚构数据。词卡与试一题内容取自客户端 fixture 中的 `prized` 题目。
