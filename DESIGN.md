# Design System: Contexta 官网

继承小程序的「安静自习桌」视觉系统（权威来源：`contexta-client/DESIGN.md` 与 `src/styles/tokens.css`），官网只增加营销页需要的规则。

## 场景与明暗

访客多在晚间或碎片时间用手机打开 → 只做 Dark：炭灰画布，与小程序默认深色一致。

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

## 签名交互：滚动词卡

首屏右侧（移动端为下方）是一张按小程序 1:1 复刻的词卡。叙事区 `.story` 高 560vh，内部 sticky；滚动进度决定阶段，`site.js` 的 `STAGE_STARTS` 控制起点：

0. 正面单词 + 首屏标题与主行动
1. 翻面（rotateY 180°）→ 音标、释义、词族搭配
2. 释义层模糊淡出，题目层上浮：语境段落（马克笔高亮）、题干、四个选项
3. 点击涟漪落在误选项 → 误选标红、正确项标绿、其余减淡，「最强迷惑项对比」与「下一道题」依次出现
4. 学完印章落下，状态栏计数 +1

左侧标题与卡片阶段同步切换；桌面端底部四段进度条可点击跳转。`prefers-reduced-motion` 下所有过渡瞬时完成，阶段切换仍然有效。

## 组件规则

- 主按钮：accent 底、画布色文字、圆角 16px、高 52px（移动端 48px）。
- 顶栏：透明，滚出叙事区后变为半透明画布色 + 1px 分隔线。
- 不使用卡片网格。「坚持」段用四栏发丝线分隔的定义列表，移动端为两栏或一栏。
- 马克笔高亮：`linear-gradient(180deg, transparent 70%, rgba(154,144,186,.42) 70%)`，与小程序 Highlighter Ribbon 规则一致。
- 图标为内联 SVG，描边 1.7，圆角端点；不用 emoji。

## 内容边界

文案以 `PRODUCT.md` 为准：只描述已上线能力；雅思/托福内容标注「非官方内容」；不出现 AI 生成、真题、网页版入口或虚构数据。词卡演示内容取自客户端 fixture 中的 `prized` 题目。
