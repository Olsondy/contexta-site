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
| accent / accent-strong | `#D4B572` / `#E8CCA0` | 黄铜金强调色；浅色为 `#8C6D28` / `#695018` |
| on-accent | `#252825` | 深色主题金底深字；浅色主题为白字 `#FFFFFF` |
| surface-accent | `#3B3932` | 结尾与辨析的温暖中性底色；浅色为 `#EEEBE3` |
| positive / negative / favourite | `#7BC7A4` / `#E0A095` / accent | 表达正确、错误、收藏 |
| ivory | `#FCF9E8` | 仅用于 Logo |

颜色策略：整站沿用客户端黄铜金与灰绿中性色，金色集中于重点文字、操作与状态；结尾使用温暖中性底色。主按钮文字读取 on-accent，保持深浅主题对比度。

## 字体

- 中文标题与说明：仓耳渔阳体 400/700（按页面用字子集化，`scripts/subset-fonts.sh`）。
- 英文单词、题目与 UI：Satoshi 400–900。
- 品牌字标：Jaldi 700，`letter-spacing: 0.04em`。
- 标题 `clamp()` 流体字号，桌面最大 76px；正文 17–18px，移动端 16px。

## 页面结构

沿用「安静自习桌」的克制视觉；先演示一次完整练习，再用可操作题目与简短场景说明承接。维持零构建与零第三方脚本，不劫持滚动。

1. 首屏：左侧核心标题与入口；右侧按当前 client 结构演示 `construction`，约 28 秒一轮：三层叠卡正面 → 翻面与双语语境 → 语境题与对错 → 独立深入解析 → 学习收获弹窗 → 悬浮导航切换到今日目标。四个章节按钮可直接切换并暂停，播放按钮可继续；题目来自客户端 `learning-content.ts` 的 construction fixture，进度、时间、XP 与积分明确标注为示例。演示由独立本地 `assets/demo.css`、`assets/demo.js` 维护，彻底移除旧 prized 演示和盖章完成页。滚出视野或页面隐藏时冻结进度。桌面入口是小程序码，手机主入口是完整微信名称「奥尔森迪语境助手」及复制按钮。
2. 试一题（`canvas-outside` 底色）：保留原题与中文辅助、逐项解析、辨析和重答；内容区标注非官方。只为题目本身保留一次入场，文字默认可见。
3. 练习延续：左侧标题和去小程序入口，右侧无卡片的分行说明，分别讲词本切换、答案回看与需复习、收藏和学习记录；手机改为单列。
4. 结尾：surface-accent 温暖中性底色，完整微信名称与金色复制按钮；真实码图存在时桌面和手机都显示，手机提示长按识别。复制反馈就近显示。
5. 页脚：桌面单行品牌与法律信息，手机使用居中的品牌、版权、备案三行紧凑排列；不画横跨屏幕的分隔线，不把版权和备案撑到两端。Logo 24px、品牌字标 21px，移动端法律信息 11px，备案链接无常驻下划线。

动效只服务于说明产品：叠卡翻面、题目与解析横向交接、导航与操作栏原位切换、收获弹窗与一次性彩屑、今日目标刻度逐个点亮。手动章节切换可立即中断自动播放；只用本地 CSS 与原生 JavaScript。

演示与官网共享当前客户端黄铜金令牌（dark `#d4b572` / `#e8cca0`，light `#8c6d28` / `#695018`），演示内部别名直接读取页面令牌，保持主题切换一致。导航直接复用 client `src/static/tabbar/` 的心形、肱二头肌、靶心、用户、中央快捷头像与底座弧形素材，存放于 `assets/img/demo/`；答题操作栏沿用四个图标，不用文字主按钮代替。单词只展示美式音标、不演示音频播放；今日目标展示已存在的题数模式，不把待验收的三项目标或伙伴形态写成上线承诺。对照来源为 client 的 `index.vue`、`FloatingDock.vue`、`session/index.vue`、`SessionCompletionDialog.vue` 和 `today/index.vue`。

模拟手机导航为中央头像预留 48px 独立列，四侧图标列之间留 4px 间隔；头像 36px、容器 40px，上移 12px，选中底色收窄至最多 36px，避免与中央头像挤在一起。菜单高度 56px、上方间距 9px。

小程序码文件缺失时，首屏品牌展示配搜索说明，结尾隐藏空码框并明确显示完整搜索名称，避免用户尝试识别 Logo。`prefers-reduced-motion` 下关闭过渡与自动循环，默认显示 construction 的释义和语境，隐藏彩屑；章节仍可点击、内容完整可用。

## 组件规则

- 主按钮：accent 底、on-accent 文字、圆角 16px、高 52px（移动端 48px）。
- 顶栏：透明，页面滚动后变为半透明画布色 + 1px 分隔线。
- 不使用功能卡片网格；扩充能力使用场景分行说明，与核心演示形成主次。
- 马克笔高亮：`linear-gradient(180deg, transparent 70%, var(--highlight) 70%)`；深色黄铜金透明度 0.24，浅色 0.16，与小程序 Highlighter Ribbon 规则一致。
- 图标为内联 SVG，描边 1.7，圆角端点；不用 emoji。

## 内容边界

文案以 `PRODUCT.md` 为准：只描述已上线能力；雅思/托福内容标注「非官方内容」；不出现 AI 生成、真题、网页版入口或虚构数据。手机演示使用客户端 fixture 中的 `construction`，访客可操作的「试一题」保留 `prized`；两者都明确作为示例展示。
