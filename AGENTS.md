# AGENTS.md

contexta-site 的维护说明：Contexta｜语境助手的产品官网（纯静态单页）和宣传短片源码。

## 目录

| 路径 | 内容 |
| --- | --- |
| `index.html` | 官网单页 |
| `assets/` | 页面 `site.css` / `site.js`、客户端演示 `demo.css` / `demo.js`、Logo、字体与图片 |
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

正式入口保留 `mycontexta.com/product`，由 Nginx 补齐末尾斜杠到 `/product/`，直接提供本项目静态文件；不要再把页面复制进 `contexta-server` 的 Next.js 路由。首次接入、目录权限、独立上传与回退统一见[产品页独立部署](../contexta-server/docs/architecture/product-site-deployment.md)。页面调整无需 Server 构建或应用重启。

自动部署以 [docs/deployment.md](docs/deployment.md) 为准：启用 GitHub 工作流后，`main` 的页面和资源改动先校验，再上传并切换静态目录。连接地址、端口、账号、专用部署私钥和服务器主机公钥统一从 Repository secrets 读取，不在源码或文档中写真实连接信息，不另设启用变量；暂停发布使用 GitHub 自带的禁用工作流功能。部署配置属于本仓库，不引入 Server 构建；不把密钥写入代码或在流水线中关闭 SSH 主机校验。提交前可运行 `python3 scripts/package-site.py` 检查静态资源。

部署公钥必须通过 `restrict,command="…"` 绑定管理员安装的固定接收脚本，只接收静态归档，不允许任意 Shell、Python、SFTP 或转发。`scripts/receive-site.py` 与 `scripts/activate-site.py` 在服务器的副本及其目录归 root 所有，自动部署密钥不能更新它们；修改这两个脚本后，管理员必须另行同步服务器副本，详见部署文档。

## 文案

- 范围以 `PRODUCT.md` 为准：只描述小程序当前已有的能力，不写用户数、证言或效果数据。
- 官网品牌当前使用「语境助手」；微信搜索、复制名称与打开说明使用完整登记名「奥尔森迪语境助手」。「奥尔森迪」是必带的个体户主体名前缀，后续计划改为「奥尔森迪语境自修」，官网随小程序实际更名同步，见 `PRODUCT.md`。
- 中文字体（仓耳渔阳体）是按页面用字生成的子集。改了 `index.html` 或 `assets/*.js` 里的中文后要重新生成：

  ```bash
  ./scripts/subset-fonts.sh   # 需要 fonttools 与 brotli；完整字体读取自 ../contexta-client/resources/fonts/full
  ```

## 小程序入口

- **小程序码**：首屏和结尾各一处，路径 `assets/img/miniprogram-code.png`，建议不小于 480×480 的 PNG。结尾码位在手机端也显示，支持长按识别；仓库里还没有这张图，缺失时结尾改为明确搜索提示，不把品牌标志伪装成小程序码。首屏缺码时品牌标志仅作品牌展示。
- **微信搜索**：手机端始终提供「在微信搜索 奥尔森迪语境助手」和复制完整名称的入口，复制结果在当前段落显示。
- **打开小程序按钮**（仅手机端）：跳转地址写在 `index.html` `<head>` 的 `<meta name="ctxa-miniprogram-link" content="">`，可填微信 URL Link（`https://wxaurl.cn/...`）或明文 URL Scheme（`weixin://dl/business/?...`）；留空时不显示按钮。填写后首屏、结尾和顶栏的「打开小程序」在手机上直接跳转；桌面端顶栏按钮仍跳到结尾的小程序码。URL Link 有有效期，过期前要重新生成替换。

## 宣传短片

主版本是 `promo/out/contexta-30s-v4-vo.mp4`（30 秒竖屏，中文解说）。各版本说明、制作流程、解说生成和用 DAW 重做配乐的方法见 [promo/README.md](promo/README.md)。
