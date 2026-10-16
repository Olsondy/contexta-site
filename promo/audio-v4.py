"""合成 v4（学习伙伴版）30 秒短片的配乐与音效（纯 Python 标准库，全部原创合成，无第三方版权素材）。
输出 out/audio-v4.wav：48kHz 立体声 30 秒。事件时间与 comp-v4.html 的时间轴一致。
结构：120 BPM 轻快节拍 → 3.5 秒唱片急停（论文里懵了）→ 9 秒半速回来 → 11 秒四记重音 →
13 秒全速节拍一直到 27 秒 → 落版和弦。
"""
import math, random, struct, wave, pathlib

SR, DUR = 48000, 30.0
N = int(SR * DUR)
L = [0.0] * N
R = [0.0] * N
rng = random.Random(11)
TAU = 2 * math.pi
BEAT = 0.5


def add(t0, samples, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    gl, gr = gain * math.cos((pan + 1) * math.pi / 4), gain * math.sin((pan + 1) * math.pi / 4)
    for k, v in enumerate(samples):
        i = i0 + k
        if 0 <= i < N:
            L[i] += v * gl
            R[i] += v * gr


def env(n, a, d):
    na = max(1, int(a * SR))
    return [(k / na) if k < na else math.exp(-(k - na) / (d * SR)) for k in range(n)]


def tone(f, dur, a=0.005, d=0.3, harm=(1.0, 0.25, 0.08)):
    n = int(dur * SR)
    e = env(n, a, d)
    return [e[k] * sum(h * math.sin(TAU * f * (j + 1) * k / SR) for j, h in enumerate(harm)) for k in range(n)]


def glide(f0, f1, dur, d=0.4, square=False):
    n = int(dur * SR)
    out, ph = [], 0.0
    for k in range(n):
        u = k / n
        ph += TAU * (f0 * (f1 / f0) ** u) / SR
        s = math.sin(ph)
        if square:
            s = 0.6 * (1 if s > 0 else -1) + 0.4 * s
        out.append(s * math.exp(-k / (d * SR)) * min(1, k / 200))
    return out


def noise(dur, a, d, lp=0.2):
    n = int(dur * SR)
    e = env(n, a, d)
    out, y = [], 0.0
    for k in range(n):
        y += lp * (rng.uniform(-1, 1) - y)
        out.append(y * e[k])
    return out


def sweep(dur, lp0, lp1):
    n = int(dur * SR)
    out, y1, y2 = [], 0.0, 0.0
    for k in range(n):
        u = k / n
        lp = lp0 + (lp1 - lp0) * u
        y1 += lp * (rng.uniform(-1, 1) - y1)
        y2 += lp * 0.5 * (y1 - y2)
        out.append((y1 - y2) * math.sin(math.pi * u) ** 1.5)
    return out


def kick(dur=0.32, f0=55, depth=110):
    n = int(dur * SR)
    out, ph = [], 0.0
    for k in range(n):
        t = k / SR
        ph += TAU * (f0 + depth * math.exp(-t * 30)) / SR
        out.append(math.sin(ph) * math.exp(-t * 10))
    return out


def hat(dur=0.05):
    n = int(dur * SR)
    out, prev = [], 0.0
    for k in range(n):
        x = rng.uniform(-1, 1)
        out.append((x - prev) * math.exp(-k / SR * 80))
        prev = x
    return out


def clap():
    return [v for v in noise(0.18, 0.001, 0.05, 0.45)]


def pluck(f, dur=0.35, dec=9):
    n = int(dur * SR)
    return [math.exp(-k / SR * dec) * (math.sin(TAU * f * k / SR) + 0.35 * math.sin(TAU * 2 * f * k / SR) + 0.12 * math.sin(TAU * 3 * f * k / SR)) for k in range(n)]


def pop(f=900):
    # 气泡“啵”：快速上滑的正弦
    return glide(f * 0.5, f * 1.6, 0.09, d=0.04)


def scratch():
    # 唱片急停：带通噪声配合下滑音
    n = int(0.42 * SR)
    out, y1, y2, ph = [], 0.0, 0.0, 0.0
    for k in range(n):
        u = k / n
        lp = 0.35 * (1 - u) + 0.03
        y1 += lp * (rng.uniform(-1, 1) - y1)
        y2 += lp * 0.5 * (y1 - y2)
        ph += TAU * (420 * (1 - u) ** 2 + 60) / SR
        out.append(((y1 - y2) * 1.4 + 0.5 * math.sin(ph)) * (1 - u) ** 0.6)
    return out


# ---------- 和弦与节拍 ----------
CHORDS = [(130.81, 261.63, 329.63, 392.0), (110.0, 220.0, 261.63, 329.63), (87.31, 174.61, 220.0, 261.63), (98.0, 196.0, 246.94, 293.66)]  # C Am F G


def groove(start, stop, half=False, gain=1.0):
    t, i = start, 0
    while t < stop - 1e-6:
        bar = int((t - start) / (BEAT * 4)) % 4
        ch = CHORDS[bar]
        if not half or i % 2 == 0:
            add(t, kick(), 0.5 * gain)
        add(t + BEAT / 2, hat(), 0.09 * gain, pan=0.3)
        add(t, hat(0.03), 0.04 * gain, pan=-0.3)
        if i % 2 == 1:
            add(t, clap(), 0.16 * gain, pan=-0.05)
        # 跳跃低音：根音 + 八度
        add(t, pluck(ch[0], 0.3, 12), 0.16 * gain)
        add(t + BEAT / 2, pluck(ch[0] * 2, 0.22, 14), 0.08 * gain)
        # 切分和弦
        if i % 2 == 0:
            for j, f in enumerate(ch[1:]):
                add(t + BEAT * 0.75, pluck(f * 2, 0.25, 16), 0.035 * gain, pan=-0.4 + j * 0.4)
        t += BEAT
        i += 1


def pad(t0, t1, gain=0.010):
    i0, i1 = int(t0 * SR), int(t1 * SR)
    for k in range(i0, min(N, i1)):
        t = k / SR
        bar = int((t - t0) / 2.0) % 4
        f = min(1, (t - t0) / 0.3) * min(1, (t1 - t) / 0.3)
        v = sum(math.sin(TAU * x * t + j) for j, x in enumerate(CHORDS[bar][1:]))
        L[k] += v * gain * f
        R[k] += v * gain * f * 0.9


groove(0.0, 3.5)
groove(9.0, 11.0, half=True, gain=0.8)
groove(13.0, 27.0)
pad(13.0, 27.0, 0.008)
pad(3.6, 7.4, 0.006)

# ---------- 1. 猛背：越翻越快的书页声，第 37 遍得意 ----------
def count_at(t):
    u = min(1, max(0, (t - 0.45) / 1.9))
    return 1 + math.floor(36 * u ** 1.8)


prev, t = 1, 0.45
while t < 2.4:
    c = count_at(t)
    if c != prev:
        add(t, noise(0.04, 0.001, 0.012, 0.7), 0.16, pan=rng.uniform(-0.3, 0.3))
        prev = c
    t += 0.001
add(2.32, pop(1100), 0.25)
for k, f in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):
    add(2.5 + k * 0.05, tone(f, 0.7, d=0.22), 0.06, pan=-0.3 + k * 0.2)

# ---------- 2. 论文：唱片急停 → 懵 ----------
add(3.48, scratch(), 0.42)
add(3.6, noise(0.3, 0.02, 0.1, 0.25), 0.07)               # 纸张
add(3.9, pop(700), 0.18, pan=0.4)                         # 探头
add(4.3, sweep(0.35, 0.1, 0.3), 0.08)                     # 荧光笔
add(5.48, kick(0.5, 45, 140), 0.6)                        # 重击
add(5.5, glide(1400, 180, 0.7, d=0.5), 0.12)              # 下滑哨音
for k in range(3):
    add(5.75 + k * 0.22, pop(600 + k * 180), 0.2, pan=-0.4 + k * 0.4)   # 问号
add(6.0, glide(1800, 900, 0.12, d=0.06), 0.08, pan=0.5)    # 汗滴

# ---------- 3. 大脑加载 → 卡在 99% ----------
t = 7.6
while t < 8.25:
    f = 600 + (t - 7.6) * 900
    add(t, glide(f, f, 0.03, d=0.02, square=True), 0.05)
    t += 0.05
add(8.3, glide(110, 105, 0.35, d=0.3, square=True), 0.16)
add(8.68, glide(110, 98, 0.32, d=0.3, square=True), 0.16)

# ---------- 4. 你也这样 ----------
for k, t0 in enumerate([9.0, 9.66, 10.33]):
    add(t0, pop(500 + k * 220), 0.28)
    add(t0 + 0.02, tone([523.25, 659.25, 784.0][k], 0.4, d=0.12), 0.06)

# ---------- 5. 不是没背，是没在语境里见过它 ----------
for t0, heavy in [(11.0, 0), (11.6, 0), (11.95, 1), (12.4, 0)]:
    add(t0, kick(0.45, 48, 130), 0.55 + heavy * 0.15)
    add(t0, noise(0.25, 0.001, 0.08, 0.35), 0.12 + heavy * 0.08)
    if heavy:
        for j, f in enumerate((261.63, 329.63, 392.0, 523.25)):
            add(t0, tone(f, 0.9, d=0.4, harm=(1, 0.5, 0.25)), 0.05, pan=-0.3 + j * 0.2)

# ---------- 6. 小程序 ----------
add(12.85, sweep(0.5, 0.01, 0.35), 0.25)                  # 手机上滑
add(14.2, noise(0.03, 0.001, 0.01, 0.8), 0.25)            # 轻点
add(14.3, tone(1046.5, 0.6, d=0.18), 0.08)
add(14.38, tone(1568.0, 0.7, d=0.22), 0.07)
for k, f in enumerate([783.99, 1046.5, 1318.5, 1568.0]):  # 学完
    add(15.55 + k * 0.06, tone(f, 0.7, d=0.22), 0.05, pan=-0.3 + k * 0.2)

# ---------- 7–8. 再遇见：论文 / 实验记录 / 数据 ----------
for w in [16.42, 18.42, 20.17, 22.17, 24.67]:
    add(w, sweep(0.28, 0.03, 0.4), 0.18)                  # 切镜嗖声
add(16.75, sweep(0.3, 0.15, 0.4), 0.07)                   # 红笔下划线
add(17.0, tone(2093.0, 0.9, d=0.3, harm=(1, 0.2)), 0.08)  # 秒懂：叮
add(17.0, tone(2637.0, 0.9, d=0.25, harm=(1,)), 0.04, pan=0.3)
add(18.95, sweep(0.3, 0.1, 0.35), 0.07)
add(19.25, pop(900), 0.2)
for k in range(8):
    add(20.3 + k * 0.06, noise(0.02, 0.001, 0.006, 0.9), 0.06, pan=-0.5 + k * 0.14)
add(20.95, glide(1500, 3000, 0.25, d=0.2), 0.06)          # 放大镜：闪
add(21.15, pop(650), 0.22)

# ---------- 9. 伙伴们：每个格子一声，五声音阶上行 ----------
PENTA = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5, 1174.66, 1318.5, 1568.0]
for k in range(9):
    add(22.35 + k * 0.25, pop(700 + k * 60), 0.16, pan=-0.4 + (k % 3) * 0.4)
    add(22.37 + k * 0.25, pluck(PENTA[k], 0.3, 10), 0.05, pan=-0.4 + (k % 3) * 0.4)

# ---------- 10. 换个句子也认得 ----------
add(25.27, pop(800), 0.2)
add(25.52, pop(950), 0.2)
add(25.75, sweep(0.2, 0.2, 0.5), 0.1)                     # 划掉 ×37
for k, f in enumerate([523.25, 659.25, 783.99, 1046.5, 1318.5]):
    add(25.8 + k * 0.05, tone(f, 0.8, d=0.3), 0.05, pan=-0.4 + k * 0.2)
for k in range(40):                                       # 彩纸
    add(25.8 + rng.uniform(0, 0.9), noise(0.015, 0.001, 0.005, 0.9), 0.04, pan=rng.uniform(-0.8, 0.8))

# ---------- 11. 落版 ----------
add(26.95, sweep(0.4, 0.01, 0.2), 0.15)
for k, f in enumerate([65.41, 130.81, 196.0, 261.63, 329.63, 392.0, 523.25]):
    add(27.05 + k * 0.02, tone(f, 2.8, a=0.02, d=1.2), 0.065, pan=-0.4 + k * 0.13)
add(27.8, pop(700), 0.15, pan=0.4)
add(28.0, pop(800), 0.15, pan=-0.4)

# 结尾淡出
for k in range(int(29.2 * SR), N):
    g = max(0.0, (DUR - k / SR) / 0.8)
    L[k] *= g
    R[k] *= g

peak = max(max(abs(x) for x in L), max(abs(x) for x in R))
g = 0.89 / peak
out = pathlib.Path(__file__).resolve().parent / 'out' / 'audio-v4.wav'
out.parent.mkdir(exist_ok=True)
with wave.open(str(out), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<hh', int(L[k] * g * 32767), int(R[k] * g * 32767)) for k in range(N)))
print('wrote', out)
