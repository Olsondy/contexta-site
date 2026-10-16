"""合成短片配乐与音效（纯 Python 标准库，全部原创合成，无第三方版权素材）。
输出 out/audio.wav：48kHz 立体声 15 秒。事件时间与 comp.html 的时间轴一致。
"""
import math, random, struct, wave, pathlib

SR, DUR = 48000, 15.0
N = int(SR * DUR)
L = [0.0] * N
R = [0.0] * N
rng = random.Random(7)


def add(t0, samples, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    gl, gr = gain * math.cos((pan + 1) * math.pi / 4), gain * math.sin((pan + 1) * math.pi / 4)
    for k, v in enumerate(samples):
        i = i0 + k
        if 0 <= i < N:
            L[i] += v * gl
            R[i] += v * gr


def env(n, a, d):
    """线性起音 a 秒，指数衰减时间常数 d 秒。"""
    na = max(1, int(a * SR))
    return [(k / na) if k < na else math.exp(-(k - na) / (d * SR)) for k in range(n)]


def tone(f, dur, a=0.005, d=0.3, harm=(1.0, 0.25, 0.08)):
    n = int(dur * SR)
    e = env(n, a, d)
    return [e[k] * sum(h * math.sin(2 * math.pi * f * (j + 1) * k / SR) for j, h in enumerate(harm)) for k in range(n)]


def noise(dur, a, d, lp=0.2):
    n = int(dur * SR)
    e = env(n, a, d)
    out, y = [], 0.0
    for k in range(n):
        y += lp * (rng.uniform(-1, 1) - y)
        out.append(y * e[k])
    return out


def sweep_noise(dur, lp0, lp1):
    """带通扫频的风声，用于划走与收尾铺色。"""
    n = int(dur * SR)
    out, y1, y2 = [], 0.0, 0.0
    for k in range(n):
        u = k / n
        lp = lp0 + (lp1 - lp0) * u
        y1 += lp * (rng.uniform(-1, 1) - y1)
        y2 += lp * 0.5 * (y1 - y2)
        out.append((y1 - y2) * math.sin(math.pi * u) ** 1.5)
    return out


# 背景：低音量温暖和弦铺底（Dmaj9 声位），整体淡入淡出
pad_notes = [146.83, 220.0, 277.18, 329.63, 369.99]
for k in range(N):
    t = k / SR
    fade = min(1, t / 1.5) * min(1, (DUR - t) / 1.2)
    swell = 0.75 + 0.25 * math.sin(2 * math.pi * t / 7.5)
    v = sum(math.sin(2 * math.pi * f * t + i) * (0.5 + 0.5 * math.sin(2 * math.pi * (0.11 + i * 0.03) * t)) for i, f in enumerate(pad_notes))
    L[k] += v * 0.018 * fade * swell
    R[k] += sum(math.sin(2 * math.pi * f * 1.003 * t + i * 1.7) for i, f in enumerate(pad_notes)) * 0.016 * fade * swell

# 开场：低沉一击，evidence 出现
add(0.0, tone(55.0, 1.2, a=0.01, d=0.35, harm=(1, 0.4, 0.15)), 0.4)
add(0.0, noise(0.5, 0.002, 0.12, 0.05), 0.25)
add(0.62, tone(987.77, 0.5, d=0.15), 0.06)              # n. 证据 标签
add(1.15, sweep_noise(1.1, 0.01, 0.3), 0.3)             # 镜头拉远
add(2.05, tone(1318.5, 0.6, d=0.2, harm=(1, 0.1)), 0.04)  # 马克笔高亮

# 3 秒倒计时与揭晓
for i, tt in enumerate([2.8, 3.3, 3.8]):
    add(tt, tone(880.0 if i < 2 else 1046.5, 0.12, d=0.03, harm=(1, 0.3)), 0.12)
    add(tt, noise(0.04, 0.001, 0.008, 0.7), 0.25)
for i, f in enumerate([783.99, 1174.66, 1567.98]):
    add(4.3 + i * 0.07, tone(f, 1.0, d=0.35), 0.08)
add(4.55, sweep_noise(0.35, 0.05, 0.25), 0.1)           # 主语宾语下划线

# 快切：每张色块一次铺开 + 一个上行音
for i, (tt, f) in enumerate([(6.1, 587.33), (7.25, 739.99), (8.35, 880.0)]):
    add(tt, sweep_noise(0.5, 0.03, 0.45), 0.28, pan=(-0.3, 0.3, 0)[i])
    add(tt + 0.35, tone(f, 0.7, d=0.22), 0.09)
    add(tt + 0.35, tone(f * 1.5, 0.5, d=0.15), 0.035)

add(9.0, sweep_noise(0.7, 0.02, 0.2), 0.2)              # 收进小程序

# 作答
add(10.42, noise(0.06, 0.001, 0.012, 0.6), 0.35)
add(10.43, tone(196.0, 0.4, d=0.09, harm=(1, 0.5, 0.2)), 0.22)
for i, f in enumerate([783.99, 1174.66]):
    add(10.8 + i * 0.08, tone(f, 0.9, d=0.3), 0.08)
add(11.3, sweep_noise(0.4, 0.03, 0.12), 0.12)

# 收尾
add(12.15, sweep_noise(0.9, 0.01, 0.35), 0.28)
for i, f in enumerate([293.66, 440.0, 554.37, 659.26, 880.0]):
    add(12.55 + i * 0.03, tone(f, 2.2, a=0.02, d=1.0), 0.07, pan=-0.4 + i * 0.2)

peak = max(max(abs(x) for x in L), max(abs(x) for x in R))
g = 0.89 / peak
out = pathlib.Path(__file__).resolve().parent / 'out' / 'audio-15s.wav'
out.parent.mkdir(exist_ok=True)
with wave.open(str(out), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<hh', int(L[k] * g * 32767), int(R[k] * g * 32767)) for k in range(N)))
print('wrote', out)
