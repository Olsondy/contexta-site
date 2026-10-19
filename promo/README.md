# 宣传短片

Contexta 的竖屏宣传短片（1080×1920，30fps）。画面、配乐与音效全部由本目录的代码生成，没有使用第三方版权素材。

## 成片

| 文件 | 时长 | 内容 |
| --- | --- | --- |
| `out/contexta-30s-v4-vo.mp4` | 30 秒 | **主版本**：v4 画面，加中文解说 |
| `out/contexta-30s-v4.mp4` | 30 秒 | 无解说版，也是混入解说时的画面底片。故事：读书机器人猛背 evidence 37 遍 → 论文里它是动词，当场懵掉 → 伙伴们“我也是” → 「不是没背，是没在语境里见过它」→ 小程序一道语境题（约 3.5 秒）→ 论文、实验记录、数据里都认得 → 伙伴们 → 落版「一个单词，一次语境练习。」。画面和解说都不出现产品名 |
| `motion-v5/out/motion-v5-v3.mp4` | 30 秒 | **v5「荧光笔」**：横屏 16:9，无口播，与 v4 互不相关的另一支。一支荧光笔划过 prize → 三个真实句子里它分别是「重视」「珍视」「珍贵的」→ 索引行 → 「意思，在句子里。」→ 小程序里做这个词的语境题、看解析、学完盖章 → 薰衣草整屏落在语境透镜标志上。同样不出现产品名 |
| `motion-v6/out/motion-v6-v1.mp4` | 30 秒 | **v6「书桌拼贴」**（v5 的方向 B）：横屏 16:9，无口播。俯拍书桌：词卡上 prize = 奖项被铅笔划掉 → 三张句子纸条滑进来，荧光笔涂过、圈出线索、手写真正的意思 → 手写「意思，在句子里。」→ 手机滑上书桌做这道题、看最强迷惑项 → 镜头甩回词卡盖上学完印章 → 纸张收拢，新卡片上画出语境透镜标志。不出现产品名 |

## 工作方式

- **画面**：每个版本是一张合成页（`comp-v4.html`、`comp.html`、`comp-15s.html`）。每一帧都是时间 t 的纯函数 `window.__seek(t)`；在浏览器里打开并加 `?play` 可以直接预览。
- **渲染**：`render.py` 用 Playwright 驱动本机 Chrome 逐帧截图，ffmpeg 编码成 mp4，同时混入指定的音轨。
- **配乐与音效**：`audio-v4.py`、`audio.py`、`audio-15s.py` 只用 Python 标准库合成，事件时间与对应合成页的时间轴一一对应。
- **解说**（仅 v4）：本地 GPU 语音服务逐句生成，`mix-vo-v4.py` 把它们摆到时间轴上，与配乐混音后换进 mp4 的音轨。

依赖：Python 3、`playwright`（使用本机 Chrome）、ffmpeg。生成解说时还需要能访问运行 `qwen-zh-cn-narrator-v1` 音色的语音服务。

## 制作 v5 / v6（huashu-motion）

v5 和 v6 各是一个 [huashu-motion](https://github.com/alchaincyf/huashu-motion) 工程（技能不放在仓库里，装在 `~/.agents/skills/huashu-motion`）：合成页 `motion-v5/index.html`、`motion-v6/index.html`（HTML + GSAP，配乐是写在页内的 ABC 乐谱），方向、节奏单与上屏文字出处见各自的 `treatment.md`；三个方向的关键帧与方向卡在 `motion-v5/directions/`。下面的命令把 `motion-v5` 换成 `motion-v6` 即可用于 v6。依赖 Node 22+、Chrome、ffmpeg + ffprobe；真乐器音色第一次需要运行 `om samples build`（约 50MB，CC0/CC-BY）。

```bash
OM=~/.agents/skills/huashu-motion/bin/om
$OM studio motion-v5 --no-open   # 浏览器里预览，可在画面上点选、改文案变量
$OM check motion-v5              # 版式与运动规则检查
$OM render motion-v5 --blur      # 配乐与音效自动重新生成 → motion-v5/out/motion-v5-vN.mp4
$OM qa motion-v5                 # 检查成片
```

字幕、停顿句、落版一句话都是合成页变量（studio 右侧可直接改）；改了中文后运行 `motion-v5/tools/subset-fonts.sh` 重新生成仓耳渔阳体子集。

## 制作 v4

```bash
cd promo
python3 audio-v4.py                                                         # 配乐与音效 → out/audio-v4.wav
python3 render.py --comp comp-v4.html --audio out/audio-v4.wav --out out/contexta-30s-v4.mp4
TTS_URL=http://<GPU 主机>:8808 TTS_API_KEY=... python3 tts-vo-v4.py --takes 3   # 解说 → out/vo/
python3 mix-vo-v4.py                                                        # → out/audio-v4-vo.wav、out/contexta-30s-v4-vo.mp4
```

只改了解说或混音时，跑最后一步就够了：`mix-vo-v4.py` 只替换音轨，不重新渲染画面。

### 解说

- 台词、每句的画面与时间见 [voiceover-v4.md](voiceover-v4.md)；字幕文件是 [voiceover-v4.srt](voiceover-v4.srt)，可以导入剪辑软件，也可以烧进画面。
- `tts-vo-v4.py` 逐句请求 `contexta-server/services/tts-provider` 的 `/v1/audio/speech`，使用宣传专用的中文音色 `qwen-zh-cn-narrator-v1`（contexta-server ADR 0073）。服务的 `TTS_VOICES` 必须列出这个音色。每句可以生成多个版本（`--takes`、`--first-take`）；在同一台主机、同一模型和音色版本下，同一个版本号的结果可以复现。脚本会报告每个版本能不能放进时间窗。
- `mix-vo-v4.py` 里的 `CUES` 记录每句采用的版本、起始时间和变速。换版本或挪时间只改这里，同时更新 `voiceover-v4.md` 和 SRT。人声统一到 -16 LUFS；说话时配乐自动压低约 5 dB，人声比配乐高 7–8 LU。

### 用 DAW 重做配乐（可选）

现在的配乐是代码合成的，音色偏电子。要换成真实乐器的音色，可以在 Studio One 等 DAW 里按同一套音符重新编配，卡点不变。

```bash
python3 bgm-midi-v4.py          # 配乐 MIDI → out/bgm-v4.mid
python3 audio-v4.py --sfx-only  # 只含音效的分轨 → out/sfx-v4.wav
```

`bgm-v4.mid` 速度为 120 BPM、4/4 拍，30 秒正好 15 小节。音符与 `audio-v4.py` 的节拍、和弦、点缀一一对应。第 1 轨包含速度、拍号和 12 个场景标记；其余各轨：

| 轨道 | 内容 | 建议音色 |
| --- | --- | --- |
| Drums（第 10 通道，GM 映射） | 底鼓 36、拍手 39、闭镲 42、落版吊镲 49 | 任意 GM 映射的鼓组 |
| Bass | 跳跃低音：根音 + 八度 | 电贝斯或合成贝斯 |
| Chord Stabs | 切分和弦；11.95 秒一记重和弦 | 电钢、拨弦合成器 |
| Pad | 3.6–7.4 秒、13–27 秒的铺底 | 柔和 Pad |
| Bells | 第 37 遍、“我也是”、学完、伙伴九宫格、结尾上行等点缀 | 钟琴、马林巴 |
| Hits | 11 秒开始的四记重音 | 打击乐或 impact 音色 |
| Ending Chord | 27 秒的落版和弦 | 钢琴 + Pad |

`sfx-v4.wav` 包含唱片急停、气泡、嗖声、方波卡顿等音效，节拍、铺底和旋律点缀都已去掉，和新配乐叠在一起就是完整的音轨。分轨导出时被放大到满电平，需要在 DAW 里重新调音量。不加 `--sfx-only` 时，`audio-v4.py` 的输出保持不变。

流程：DAW 项目设为 120 BPM，在第 1 小节导入 `bgm-v4.mid` 和 `sfx-v4.wav`，给各轨挂音色。3.5、9、11、13、27 秒是画面的结构点，不要移动。混好后导出 48kHz、30 秒的 WAV，例如 `out/bgm-daw.wav`，然后：

```bash
python3 mix-vo-v4.py --bed out/bgm-daw.wav
```

## 早期版本

v3（`comp.html` + `audio.py`，30 秒「语境透镜」）和 15 秒版（`comp-15s.html` + `audio-15s.py`）的合成页与配乐脚本保留在目录里，成片不再随仓库保存，需要时重新渲染：

```bash
python3 audio.py && python3 render.py --audio out/audio.wav --out out/contexta-30s.mp4
python3 audio-15s.py && python3 render.py --comp comp-15s.html --audio out/audio-15s.wav --out out/contexta-15s.mp4
python3 render.py --comp comp-v4.html --stills 3.6,8,15   # 只导出指定时间点的静帧 → out/still-*.png
```

## 素材与授权

- 片中的英文句子、词义与选项取自 `contexta-server` 本地库中已审核的 evidence、analyze 内容；语境场景是为宣传绘制的示意。这些内容在正式发布前如有修改，需要同步更新合成页。
- v4 的角色是小程序学习伙伴的分层 SVG，复制自 `contexta-server/resources/buddies/bundles`，清单在 `buddies/buddies.js`。
- `fonts/` 中的 Libre Baskerville 与 Caveat 为 OFL 授权，许可文件随附。仓耳渔阳体是按三个合成页用字生成的子集；修改合成页中文后运行 `./subset-fonts.sh` 重新生成。
- 生成的 WAV（包括 `out/vo/` 里的解说）和静帧都被 Git 忽略，成片 mp4 和 MIDI 随仓库保存。在新环境里重新混音之前，先用 `tts-vo-v4.py` 生成 `CUES` 里用到的版本。
