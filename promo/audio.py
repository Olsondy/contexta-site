"""合成 30 秒短片的配乐与音效（纯 Python 标准库，全部原创合成，无第三方版权素材）。
输出 out/audio.wav：48kHz 立体声 30 秒。事件时间与 comp.html 的时间轴一致。
结构：词卡段只有轻音效 → 穿过第一枚透镜时节拍进入（100 BPM）→ 作品集后节拍停下 → 落版和弦。
"""
import math, random, struct, wave, pathlib

SR, DUR = 48000, 30.0
N = int(SR * DUR)
L = [0.0] * N
R = [0.0] * N
rng = random.Random(7)
TAU = 2 * math.pi


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


def kick(dur=0.35):
    n = int(dur * SR)
    out, ph = [], 0.0
    for k in range(n):
        t = k / SR
        f = 48 + 90 * math.exp(-t * 28)
        ph += TAU * f / SR
        out.append(math.sin(ph) * math.exp(-t * 9))
    return out


def hat(dur=0.06):
    n = int(dur * SR)
    out, prev = [], 0.0
    for k in range(n):
        x = rng.uniform(-1, 1)
        out.append((x - prev) * math.exp(-k / SR * 70))
        prev = x
    return out


def pluck(f, dur=0.5):
    n = int(dur * SR)
    return [math.exp(-k / SR * 7) * (math.sin(TAU * f * k / SR) + 0.3 * math.sin(TAU * 2 * f * k / SR)) for k in range(n)]


# ---------- 铺底：温暖和弦，全片低音量 ----------
CHORDS = [(146.83, 220.0, 277.18, 369.99), (123.47, 185.0, 246.94, 293.66), (98.0, 196.0, 246.94, 293.66), (110.0, 164.81, 220.0, 277.18)]  # D Bm G A
BEAT = 0.6
START, STOP = 4.3, 27.25
for k in range(N):
    t = k / SR
    bar = int(max(0.0, t - START) / (BEAT * 4)) % 4 if t >= START else 0
    ch = CHORDS[bar]
    fade = min(1, t / 1.2) * min(1, (DUR - t) / 1.5)
    lift = 0.6 if t < START else 1.0
    v = sum(math.sin(TAU * f * t + i) for i, f in enumerate(ch))
    w = sum(math.sin(TAU * f * 1.004 * t + i * 1.3) for i, f in enumerate(ch))
    L[k] += v * 0.012 * fade * lift
    R[k] += w * 0.012 * fade * lift

# ---------- 节拍：穿过第一枚透镜时进入，作品集结束时停下 ----------
t = START
i = 0
while t < STOP:
    bar = int((t - START) / (BEAT * 4)) % 4
    add(t, kick(), 0.42)
    add(t + BEAT / 2, hat(), 0.08, pan=0.25)
    if i % 2 == 1:
        add(t, noise(0.12, 0.001, 0.05, 0.5), 0.10, pan=-0.1)   # 轻拍
    root = CHORDS[bar][0]
    add(t, pluck(root / 2 if root > 120 else root, 0.55), 0.10)
    if i % 4 == 2:
        add(t + BEAT * 0.5, pluck(CHORDS[bar][2] * 2, 0.4), 0.05, pan=0.3)
    t += BEAT
    i += 1

# ---------- 词卡段 ----------
for tt in [1.2, 11.95]:                                       # 轻触翻面
    add(tt, noise(0.05, 0.001, 0.01, 0.6), 0.3)
    add(tt + 0.05, sweep(0.4, 0.03, 0.2), 0.16)
for tt in [2.3, 12.7, 19.85]:                                 # 选中正确项
    add(tt, noise(0.05, 0.001, 0.01, 0.6), 0.3)
    add(tt + 0.05, tone(1046.5, 0.6, d=0.18), 0.07)
    add(tt + 0.12, tone(1567.98, 0.6, d=0.18), 0.05)

# 学完：四个点依次飞起（上行四音）→ 圆弧画出
for d, fast in [(2.85, 1.0), (13.0, 0.7), (20.05, 0.7)]:
    for k, f in enumerate([587.33, 739.99, 880.0, 1174.66]):
        add(d + k * 0.06 * fast + 0.3 * fast, tone(f, 0.8, d=0.25), 0.06, pan=-0.3 + k * 0.2)
    add(d + 0.1 * fast, sweep(0.7 * fast, 0.01, 0.12), 0.12)
    add(d + 0.75 * fast, tone(146.83, 1.4, a=0.02, d=0.6, harm=(1, 0.5, 0.2)), 0.12)

# 穿过透镜
for z in [4.3, 13.85, 20.75]:
    add(z - 0.05, sweep(0.95, 0.005, 0.45), 0.34)

# ---------- 世界内的动作 ----------
add(4.3 + 1.9, tone(1318.5, 0.5, d=0.15), 0.035)                 # 声纹变色
for k in range(3):
    add(4.0 + 3.3 + k * 0.03, noise(0.25, 0.01, 0.08, 0.3), 0.06)  # 圈出 evidence（笔触）
for i in range(3):
    add(13.55 + 0.5 + i * 0.12, tone(196 + i * 40, 0.35, d=0.1, harm=(1, 0.4)), 0.12)  # 试管落下
add(13.55 + 1.4, sweep(0.8, 0.05, 0.3), 0.12)                   # 扫描
for i in range(10):                                              # 数据点落下
    add(20.15 + 0.3 + i * 0.07, noise(0.03, 0.001, 0.01, 0.8), 0.06, pan=-0.5 + i * 0.1)

# 收进缩略图
for e in [11.0, 19.0, 24.6]:
    add(e, sweep(0.5, 0.03, 0.15), 0.18)

# ---------- 作品集与落版 ----------
add(25.2, sweep(0.8, 0.01, 0.25), 0.2)
add(27.25, sweep(0.7, 0.005, 0.2), 0.2)
for k, f in enumerate([587.33, 739.99, 880.0, 1174.66]):
    add(27.8 + k * 0.07, tone(f, 1.2, d=0.4), 0.06, pan=-0.3 + k * 0.2)
for k, f in enumerate([73.42, 146.83, 220.0, 277.18, 369.99, 440.0]):
    add(28.0 + k * 0.025, tone(f, 2.0, a=0.02, d=1.0), 0.07, pan=-0.4 + k * 0.16)

peak = max(max(abs(x) for x in L), max(abs(x) for x in R))
g = 0.89 / peak
out = pathlib.Path(__file__).resolve().parent / 'out' / 'audio.wav'
out.parent.mkdir(exist_ok=True)
with wave.open(str(out), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<hh', int(L[k] * g * 32767), int(R[k] * g * 32767)) for k in range(N)))
print('wrote', out)
