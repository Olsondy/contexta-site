# contexta-site

Contexta｜语境自修 产品官网。纯静态单页，无构建步骤。

## 本地预览

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 部署

把仓库根目录（`index.html` 与 `assets/`）上传到任意静态托管即可。

## 待替换素材

- `assets/img/miniprogram-code.png`：微信小程序码（建议 ≥ 480×480，PNG）。文件缺失时页面自动显示品牌标志，并把说明文字改为「微信小程序 · 语境自修」。

## 修改文案后

中文字体是按页面用字生成的子集。修改 `index.html` 或 `assets/site.js` 里的中文后运行：

```bash
./scripts/subset-fonts.sh   # 需要 fonttools；读取 ../contexta-client 中的完整字体
```

## 文档

- `PRODUCT.md`：官网可以说什么、不能说什么。
- `DESIGN.md`：官网视觉系统（继承小程序设计令牌）。

## 宣传短片（promo/）

| 文件 | 内容 |
| --- | --- |
| `promo/out/contexta-30s-v4.mp4` | 30 秒主版本（学习伙伴）：读书机器人猛背 evidence 37 遍 → 论文里它是动词，当场懵掉 → 伙伴们“我也是” → 「不是没背，是没在语境里见过它」→ 小程序一道语境题（约 3.5 秒）→ 论文、实验记录、数据里都认得 → 伙伴们 → 落版 |
| `promo/out/contexta-30s.mp4` | 30 秒第三版：词卡学完 → 四点聚成「语境透镜」→ 三个语境世界 → 落版 |
| `promo/out/contexta-15s.mp4` | 15 秒版本：evidence 词性反差钩子 |
| `promo/out/contexta-15s-v1.mp4` | 15 秒第一版（流程演示，已不推荐） |

片中英文句子、词义与选项取自 `contexta-server` 本地库已审核的 evidence、analyze 内容；语境场景为宣传绘制的示意。v4 的角色是小程序学习伙伴的分层 SVG，复制自 `contexta-server/resources/buddies/bundles`，清单在 `promo/buddies/buddies.js`。这些词进入正式发布前如有修改，需要同步更新合成页。

```bash
cd promo
python3 audio-v4.py && python3 render.py --comp comp-v4.html --audio out/audio-v4.wav --out out/contexta-30s-v4.mp4
python3 audio.py                                                  # 第三版配乐与音效 → out/audio.wav
python3 render.py --audio out/audio.wav --out out/contexta-30s.mp4
python3 audio-15s.py && python3 render.py --comp comp-15s.html --audio out/audio-15s.wav --out out/contexta-15s.mp4
python3 render.py --stills 3.6,8,15                               # 只导出指定时间点的静帧
```

`comp-v4.html` / `comp.html` / `comp-15s.html` 可直接在浏览器打开并加 `?play` 预览；渲染需要 playwright、本机 Chrome 与 ffmpeg。修改字幕后，需要按合成页用字重新子集化 `promo/fonts/` 里的仓耳渔阳体（方法同 `scripts/subset-fonts.sh`）。`promo/fonts/` 中的 Libre Baskerville 与 Caveat 为 OFL 授权，许可文件随附。
