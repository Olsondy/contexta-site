# 产品页自动部署

## 发布边界

本项目独立发布 `index.html` 和 `assets/`，不发布 `promo/`，不安装 Node、不构建 Server、不重启 Web/Worker，也不自动修改 Nginx。访问地址为 `https://mycontexta.com/product/`。

首次同域分流仍需按 [Server 产品页接入说明](../../contexta-server/docs/architecture/product-site-deployment.md)准备 Nginx：`/product` 补齐斜杠，`/product/` 和 `/product/assets/` 从 `/srv/contexta/site/current/` 下读取文件；根首页仍代理 Next.js。后续只更新静态版本，不 reload Nginx。

启用本仓库 `.github/workflows/deploy-site.yml` 后，`main` 的页面、资源或部署脚本变化会触发校验和部署，也支持 Actions 页面手动执行。手动执行也只允许 `main`。部署并发串行，不中途取消正在上传的版本。首次接入完成前，使用 GitHub 自带的禁用工作流功能暂停发布，不再配置额外的启用变量。

## 一次性准备

### 服务器

目标主机需要 Python 3、OpenSSH/SFTP 和 Nginx。当前复用 `olsond` 账号，使用 Site 专用密钥；部署公钥已追加到 `/home/olsond/.ssh/authorized_keys`，不复用本机管理员私钥。以运维账号创建发布目录：

```bash
sudo install -d -m 755 -o olsond -g olsond \
  /srv/contexta/site /srv/contexta/site/releases /srv/contexta/site/incoming
```

已有目录时先确认所有者，不直接覆盖正在使用的发布指针。Nginx 用户需要遍历 `/srv/contexta/site/current` 及父目录的权限。部署用户只需写入 `/srv/contexta/site`，不需要写 Nginx 配置目录。服务器只接收上传，不从 GitHub 拉代码；但 GitHub 托管 runner 必须能够访问服务器 SSH 端口。

### GitHub 仓库

服务器地址 `117.72.29.124`、SSH 端口 `2610` 和账号 `olsond` 直接写在工作流的 SSH 配置中，更换服务器时修改该文件。在 `Settings → Secrets and variables → Actions` 只保留以下两个 Repository secrets，不把私钥或主机公钥内容写入源码：

| Secret | 内容 |
| --- | --- |
| `SITE_SSH_PRIVATE_KEY` | 该账号专用部署私钥，对应公钥已安装在服务器 |
| `SITE_SSH_KNOWN_HOSTS` | 经可信渠道确认的服务器 SSH 主机公钥行；非 22 端口使用 `[主机]:端口` 格式 |

工作流强制校验已知主机，不使用 `StrictHostKeyChecking=no` 或在流水线中临时信任扫描结果。不要直接复用管理员私钥。

部署公钥只需装在服务器，不另存为 Secret。当前两个 Secrets 已配置。完成目录权限后，在 Actions 的 `Deploy product site` 页面启用工作流，再手动运行 `main`。首次上传通过后再切换、检查并 reload Nginx，然后验证公网产品页和资源。之后推送到 `main` 即自动发布，无额外人工构建。需要暂停时使用该页面菜单中的 `Disable workflow`；禁用期间校验与部署都不自动运行，需要本地检查。

GitHub CLI 也可以从本机设置这些值；私钥以文件输入，避免回显：

```bash
gh secret set SITE_SSH_PRIVATE_KEY --repo Olsondy/contexta-site < /path/to/dedicated-key
gh secret set SITE_SSH_KNOWN_HOSTS --repo Olsondy/contexta-site < /path/to/verified-known-hosts
gh workflow enable deploy-site.yml --repo Olsondy/contexta-site
gh workflow run deploy-site.yml --ref main --repo Olsondy/contexta-site
```

暂停后续触发使用 `gh workflow disable deploy-site.yml --repo Olsondy/contexta-site`。禁用工作流不会取消已经运行的发布，回退前先确认没有部署正在执行。

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

2026-11-06 首次实现已通过资源校验、17 个公开文件的打包范围检查、Shell/JavaScript 语法检查、工作流 YAML 与触发条件检查，以及 `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-deployment.py` 的 7 项部署测试。

同日配置简化为两个 Secrets，服务器连接信息改为工作流内固定值。专用部署公钥已安装到 `olsond` 账号并用配对私钥验证 SSH 登录，GitHub 已保存部署私钥和服务器主机公钥。工作流在首次接入前暂时禁用；尚未验证真实 GitHub 上传或切换目标主机 Nginx，不能把登录验证当作发布完成。
