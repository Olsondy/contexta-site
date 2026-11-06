# 产品页自动部署

## 发布边界

本项目独立发布 `index.html` 和 `assets/`，不发布 `promo/`，不安装 Node、不构建 Server、不重启 Web/Worker，也不自动修改 Nginx。访问地址为 `https://mycontexta.com/product/`。

首次同域分流仍需按 [Server 产品页接入说明](../../contexta-server/docs/architecture/product-site-deployment.md)准备 Nginx：`/product` 补齐斜杠，`/product/` 和 `/product/assets/` 从 `/srv/contexta/site/current/` 下读取文件；根首页仍代理 Next.js。后续只更新静态版本，不 reload Nginx。

本仓库 `.github/workflows/deploy-site.yml` 在 `main` 的页面、资源或部署脚本变化时运行，也支持 Actions 页面手动执行。流程先校验资源引用，然后仅在仓库变量 `SITE_DEPLOY_ENABLED=true` 时部署；默认不部署。手动执行也只允许 `main`。部署并发串行，不中途取消正在上传的版本。

## 一次性准备

### 服务器

目标主机需要 Python 3、OpenSSH/SFTP 和 Nginx。使用专用静态部署用户更方便隔离目录权限，无需为该用户提供 sudo 或应用数据库凭据。运维账号先创建用户、配置专用 SSH 公钥，再创建发布目录；以下使用 `contexta-site` 作为部署账号示例：

```bash
sudo install -d -m 755 -o contexta-site -g contexta-site \
  /srv/contexta/site /srv/contexta/site/releases /srv/contexta/site/incoming
```

已有目录时先确认所有者，不直接覆盖正在使用的发布指针。Nginx 用户需要遍历 `/srv/contexta/site/current` 及父目录的权限。部署用户只需写入 `/srv/contexta/site`，不需要写 Nginx 配置目录。服务器只接收上传，不从 GitHub 拉代码；但 GitHub 托管 runner 必须能够访问服务器 SSH 端口。

### GitHub 仓库

在 `Settings → Secrets and variables → Actions` 配置以下 Repository secrets，不把私钥或主机指纹写入源码：

| Secret | 内容 |
| --- | --- |
| `SITE_SSH_HOST` | 可从 GitHub runner 访问的服务器域名或 IP |
| `SITE_SSH_PORT` | SSH 端口 |
| `SITE_SSH_USER` | 静态发布账号，例如 `contexta-site` |
| `SITE_SSH_PRIVATE_KEY` | 该账号专用部署私钥，对应公钥已安装在服务器 |
| `SITE_SSH_KNOWN_HOSTS` | 经可信渠道确认的服务器 SSH 主机公钥行；非 22 端口使用 `[主机]:端口` 格式 |

工作流强制校验已知主机，不使用 `StrictHostKeyChecking=no` 或在流水线中临时信任扫描结果。不要直接复用管理员私钥。

先不设置启用变量；完成目录、公钥和 Secrets 后，将 Repository variable `SITE_DEPLOY_ENABLED` 设为字符串 `true`，手动执行一次 `Deploy product site`。首次上传通过后再切换、检查并 reload Nginx，然后验证公网产品页和资源。之后推送到 `main` 即自动发布，无额外人工构建。将该变量改为 `false` 可以暂停后续自动部署，资源校验仍运行。

GitHub CLI 也可以从本机设置这些值；私钥以文件输入，避免回显：

```bash
gh secret set SITE_SSH_PRIVATE_KEY < /path/to/dedicated-key
gh secret set SITE_SSH_KNOWN_HOSTS < /path/to/verified-known-hosts
# 其余 Secrets 可在设置页面填写，最后才启用。
gh variable set SITE_DEPLOY_ENABLED --body true
gh workflow run deploy-site.yml --ref main
```

平台依据：[GitHub Actions 部署与并发控制](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments)。

## 日常修改

1. 修改 `index.html`、`assets/site.css` 或 `assets/site.js`，按原流程本地预览。中文文案变化时，先运行 `./scripts/subset-fonts.sh`，把生成的字体子集一并提交；CI 不依赖相邻 Client 仓库完整字体，也不会自动补字。
2. 运行 `python3 scripts/package-site.py` 校验引用。尚未提供的小程序码是明确允许的缺失项，保留页面既有品牌回退；其他缺失的 HTML/CSS 资源会阻止发布。
3. 提交推送 `main`，查看 Actions 的校验和部署结果。只改文档或宣传短片不会自动部署；需要时可手动触发。

工作流不使用 `git archive` 打包整个仓库，只打包经过校验的页面与资源。版本名由完整 commit SHA、run ID 和 attempt 组成。远端核对 SHA-256 和归档路径，拒绝越界文件、链接、重复成员及缺少必要文件的归档，上传或校验失败不会改变当前指针。

## 目录与回退

```text
/srv/contexta/site/
├── incoming/                         待校验的归档；成功激活后删除
├── releases/<commit>-<run>-<attempt>/
│   ├── release.txt                   commit/run 与归档 SHA-256
│   └── product/
│       ├── index.html
│       └── assets/
└── current -> releases/<commit>-<run>-<attempt>
```

文件先解压到新的临时目录，必要文件齐全后登记版本，最后原子替换 `current` 符号链接；激活期间使用主机文件锁。保留历史版本，不自动删除已验收版本。切换只保证目录指针原子更新，不保证跨切换时刻的多个浏览器请求来自同一版本，资源更新保持兼容。

需要回退时，在目标 Linux 主机以部署用户选定上一份已验收版本，并切换 `current`；先暂停自动部署，避免下一次 push 又更新：

```bash
cd /srv/contexta/site
previous='<上一份已验收的发布目录名>'
test -s "releases/$previous/product/index.html"
ln -s "releases/$previous" current.rollback
mv -Tf current.rollback current
```

不需要回滚 Server 镜像或 reload Nginx。Nginx 应为未带哈希文件名的页面、CSS、JS 和字体配置 `Cache-Control: no-cache`。成功上传只证明静态目录已切换，不等于 DNS、TLS、Nginx 分流或页面视觉已验收；首次接通后仍需验证真实网址。失败的上传归档、未启用版本和历史目录由运维按需要清理。

## 验证记录

2026-11-06 本地已通过资源校验、17 个公开文件的打包范围检查、Shell/JavaScript 语法检查、工作流 YAML 与触发条件检查，以及 `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-deployment.py` 的 7 项部署测试。尚未配置远端部署 Secrets、安装服务器部署公钥、启用发布变量或验证真实 SSH 上传；不能把工作流提交视为自动部署已经接通。
