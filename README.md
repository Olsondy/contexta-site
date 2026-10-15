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

15 秒 1080×1920 竖屏短片，成片在 `promo/out/contexta-15s.mp4`。

```bash
cd promo
python3 audio.py                              # 合成配乐与音效 → out/audio.wav
python3 render.py --audio out/audio.wav       # 逐帧渲染 → out/contexta-15s.mp4（需 playwright + 本机 Chrome + ffmpeg）
python3 render.py --stills 2,4.5,8.5,11.8     # 只导出指定时间点的静帧
```

`comp.html` 可直接在浏览器打开并加 `?play` 预览。修改字幕后，需要按 `comp.html` 的用字重新子集化 `promo/fonts/`（方法同 `scripts/subset-fonts.sh`）。
