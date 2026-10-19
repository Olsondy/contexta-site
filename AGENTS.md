# AGENTS.md

contexta-site 的维护说明：Contexta｜语境助手的产品官网（纯静态单页）和宣传短片源码。

## 目录

| 路径 | 内容 |
| --- | --- |
| `index.html` | 官网单页 |
| `assets/` | 样式 `site.css`、交互 `site.js`、Logo、字体与图片 |
| `scripts/subset-fonts.sh` | 按页面用字重新生成中文字体子集 |
| `promo/` | 宣传短片：合成页、配乐、解说与渲染脚本，以及成片，见 [promo/README.md](promo/README.md) |
| `PRODUCT.md` | 官网可以说什么、不能说什么 |
| `DESIGN.md` | 视觉系统（沿用小程序的设计令牌）与页面结构 |

页面没有构建步骤，也不依赖第三方脚本或外部字体服务；保持这一点。

## 本地预览与部署

```bash
python3 -m http.server 8000   # 打开 http://localhost:8000
```

部署只需上传 `index.html` 和 `assets/` 到任意静态托管；`promo/` 不部署。

## 文案

- 范围以 `PRODUCT.md` 为准：只描述小程序当前已有的能力，不写用户数、证言或效果数据。
- 中文产品名暂用「语境助手」，与小程序登记名称「奥尔森迪语境助手」对应；计划 2027 年改回「语境自修」，见 `PRODUCT.md` 的“产品名”。
- 中文字体（仓耳渔阳体）是按页面用字生成的子集。改了 `index.html` 或 `assets/site.js` 里的中文后要重新生成：

  ```bash
  ./scripts/subset-fonts.sh   # 需要 fonttools 与 brotli；完整字体读取自 ../contexta-client/resources/fonts/full
  ```

## 小程序入口

- **小程序码**：首屏和结尾各一处，路径 `assets/img/miniprogram-code.png`，建议不小于 480×480 的 PNG。仓库里还没有这张图；文件不存在时页面显示品牌标志，说明文字改为「微信小程序 · 语境助手」。
- **微信搜索**：手机端访客扫不了自己屏幕上的码，所以始终提供「在微信搜索 语境助手」和复制名称的入口。
- **打开小程序按钮**（仅手机端）：跳转地址写在 `index.html` `<head>` 的 `<meta name="ctxa-miniprogram-link" content="">`，可填微信 URL Link（`https://wxaurl.cn/...`）或明文 URL Scheme（`weixin://dl/business/?...`）；留空时不显示按钮。填写后首屏、结尾和顶栏的「打开小程序」在手机上直接跳转；桌面端顶栏按钮仍跳到结尾的小程序码。URL Link 有有效期，过期前要重新生成替换。

## 宣传短片

主版本是 `promo/out/contexta-30s-v4-vo.mp4`（30 秒竖屏，中文解说）。各版本说明、制作流程、解说生成和用 DAW 重做配乐的方法见 [promo/README.md](promo/README.md)。huashu-motion 做的 v5/v6 实验未采用，放在分支 `promo/huashu-motion-experiments`。
