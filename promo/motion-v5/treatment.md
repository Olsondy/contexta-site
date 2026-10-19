# v5 · 「荧光笔」— treatment

30 秒，1920×1080，30fps，无口播（配乐 + 音效）。用 huashu-motion 制作，与 v4（竖屏、学习伙伴角色故事、解说）完全不同的一支。

## 方向

```
A · 荧光笔        language: kinetic-type → continuous-morph（文字卷轴、索引行、小程序界面）   look: 纸面浅底 → 自习桌深底 → 薰衣草整屏
Palette:  ground #F1F2F0 / #252825 · surface #FBFCFA / #2E312E · ink #252825 / #F3F4EF · accent #584E78 / #9A90BA 3% · flood #9A90BA
          — from: contexta-site/assets/site.css（小程序 tokens.css 的浅色、深色两套），flood 取官网结尾「获取」段的 Drenched 策略
Logline:  一支荧光笔划过 prize。你背的是「奖项」，可三个真实句子里它分别是「重视」「珍视」「珍贵的」；意思在句子里——于是进小程序做这个词的语境题、看解析、盖上学完的章，最后整屏薰衣草落在语境透镜标志上。
Why it fits: 信息形状是 Transformation（背过的词义 → 语境里的词义）+ Workflow（一组语境题）；性格「精确、安静、偏人文、新」——像一本好词典，不像广告。
Feel:     hybrid：一条贯穿全片的荧光笔（品牌 Highlighter Ribbon）当主线，句子从它下面滑过；10 秒处索引行（KWIC concordance）连拍成一次 burst；12 秒一拍停顿；13 秒落拍进入小程序。120 BPM。静音时前 3 秒看到：荧光笔划出一个大词。
Sound:    作曲模式，D 大调钢琴动机 → 半拍律动 → 停 → 升全音到 E 大调全编制；关键音效：荧光笔 draw、索引行三连 hit、落拍 impact+subdrop、学完 stamp、结尾 chime。
Risk:     句子横向滑动时要读得清 → 落位时减速到近乎停住，并只在字落定后才画线索。
```

与 house style 的区别：浅灰绿纸面 + 冷调薰衣草（品牌原色），不是暖橙/青柠强调色；字体用品牌自己的 Satoshi + 仓耳渔阳体，词义注释用 Libre Baskerville 斜体（词典体）。

## 上屏文字出处

| 上屏 | 出处 |
| --- | --- |
| prize · [praɪz] · n. 奖项；奖品 / v. 珍视；高度重视 | contexta-client `src/domain/learning-content.ts` fixture `prize`（senses） |
| The committee decided to prize accuracy over speed … → value 重视 | 同上，`prize`（toefl）题目与 contextAnalysis「核心线索是 accuracy over speed」 |
| Local farmers continue to prize the traditional seed varieties … → treasure 珍视 | 同上，`prize`（ielts） |
| … researchers still consider them highly prized records … → valued 珍贵的 | 同上，`prized` |
| 题干、四个选项、中文辅助译文、解析、最强迷惑项 delay 对比 | 同上，`prize`（toefl）的 prompt / choices / translation / contextAnalysis / distractorComparison |
| 非官方内容 标签、题组完成 · 已计入学完、学完印章 | 官网首屏手机演示（`index.html`）、`assets/img/completion-stamp.webp` |
| 每个词，一组语境题 / 作答即有反馈 / 逐项解析，辨清易混项 / 学完一个词 / 下一个词，自己选 | PRODUCT.md「可以对外表述的现有能力」 |
| 结尾：语境透镜标志、「把单词放回语境里练。」 | `assets/contexta-mark-ink.svg`；PRODUCT.md Positioning 首句 |

不出现产品名（中文名会改），不出现考试名、用户数、AI 字样。

## 节奏单（120 BPM，1 拍 0.5 s，1 小节 2 s）

```
stretch       bars    time        energy  events/bar  route moves                                         music
hook          1–2     0–4         6       3           荧光笔大特写划过 → 1.0s 硬拉出全词 prize；音标、词义逐段落下      钢琴动机 + 底鼓/闭镲从第 1 拍
contexts      3–5     4–10        5→7     3–4         「n. 奖项」被划掉；三句真实句子依次横向滑过，目标词每次准确落进荧光笔槽位；释义斜体落下   半拍律动、拨弦、贝斯进入
burst         6       10–12       8       6           三句收成索引行（KWIC），八分音符三连砸入，荧光笔竖向贯通三行，三个释义同时亮       全鼓、和弦切分、三记 hit
stop          7(2/4)  12–13       1       1           地面翻到深色，只剩一句「意思，在句子里。」                          乐队停，只剩 riser
drop          8–9     13–17       9       3           荧光笔缩成题目里的 mark，镜头从 mark 大特写拉出整台手机；中文辅助打开；点选 value → 对     升 E 大调全编制，impact+subdrop
analysis      10–11   17–21       7       4           解析与最强迷惑项卡片升起；题号 2/5→5/5 每拍一跳                   弦乐唱动机，军鼓填充
peak          12      21–23       9       2           学完印章砸下（约 70% 处）                                      重拍 + stamp
next          13      23–25       6       3           手机后退，三张真实词卡横排滑入，选下一个词                          律动回落
resolve       14–16   25–30       4       1           印章处薰衣草整屏扩散，语境透镜标志与一句话落定，停 ≥3s             动机作为声音 logo，和弦延音收住
```

检查：3 秒内有钩子（0 s 就在动，1.0 s 硬拉出）；burst 在 33–40%；落拍在 43%，学完章在 70%；每段边界至少换两样（景别、地色、密度、音乐质感）；除 12–13 s 的计划停顿外，没有超过两小节没有新东西的段落。

## 四张关键帧

- 钩子 0.4 s：荧光笔大特写正在划过半个 prize。
- 主镜 9.2 s：第三句落位，prized 在槽里，下方斜体 valued · 珍贵的。
- 最密 11.2 s：三行索引行 + 竖向荧光笔 + 三个释义。
- 落版 28 s：薰衣草整屏，语境透镜 + 「把单词放回语境里练。」

## 衔接链

```
荧光笔（划过 prize）→ 同一支荧光笔停在槽位，句子从下面滑过 → 三个槽位叠成竖向荧光笔（索引行）
→ 收成一道细线（停顿）→ 细线变回题目里 prize 的 mark（镜头拉出手机）→ 选项的对勾 → 进度条 → 印章
→ 印章中心扩散成薰衣草整屏 → 标志
```
