"""把 v4 配乐导出成多轨 MIDI（out/bgm-v4.mid），在 Studio One 等 DAW 里换成 VST 音色重做。
音符与 audio-v4.py 的节拍、和弦、点缀一一对应，时间轴与 comp-v4.html 一致：120 BPM、4/4、30 秒 = 15 小节。
第 1 轨含速度、拍号和场景标记；鼓轨走第 10 通道 GM 映射（36 底鼓 / 39 拍手 / 42 闭镲 / 49 吊镲）。
音效（唱片急停、气泡、嗖声等）不在 MIDI 里，用 `python3 audio-v4.py --sfx-only` 导出分轨。
"""
import pathlib, struct

PPQ, BEAT = 480, 0.5
tick = lambda t: round(t / BEAT * PPQ)

CHORDS = [(48, (72, 76, 79)), (45, (69, 72, 76)), (41, (65, 69, 72)), (43, (67, 71, 74))]  # C Am F G
PAD = [(60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62)]
MARKERS = [(0, '1 猛背'), (3.5, '2 论文：懵'), (7.5, '3 大脑加载'), (9.0, '4 我也是'), (11.0, '5 不是没背'),
           (13.0, '6 小程序'), (16.5, '7 再遇见：论文'), (18.5, '8 实验记录'), (20.25, '9 数据'),
           (22.25, '10 伙伴们'), (24.75, '11 换个句子也认得'), (27.0, '12 落版')]

tracks = {k: [] for k in ['Drums', 'Bass', 'Chord Stabs', 'Pad', 'Bells', 'Hits', 'Ending Chord']}
CH = {'Drums': 9, 'Bass': 0, 'Chord Stabs': 1, 'Pad': 2, 'Bells': 3, 'Hits': 4, 'Ending Chord': 5}


def note(trk, t, dur, n, vel):
    tracks[trk].append((t, dur, n, vel))


def groove(start, stop, half=False, vel=1.0):
    t, i = start, 0
    while t < stop - 1e-6:
        root, stab = CHORDS[int((t - start) / (BEAT * 4)) % 4]
        if not half or i % 2 == 0:
            note('Drums', t, 0.25, 36, int(110 * vel))
        note('Drums', t, 0.1, 42, int(50 * vel))
        note('Drums', t + BEAT / 2, 0.1, 42, int(85 * vel))
        if i % 2 == 1:
            note('Drums', t, 0.15, 39, int(100 * vel))
        note('Bass', t, 0.3, root, int(105 * vel))
        note('Bass', t + BEAT / 2, 0.2, root + 12, int(80 * vel))
        if i % 2 == 0:
            for n in stab:
                note('Chord Stabs', t + BEAT * 0.75, 0.22, n, int(80 * vel))
        t += BEAT
        i += 1


def pad(t0, t1, vel):
    t = t0
    while t < t1 - 1e-6:
        for n in PAD[int((t - t0) / 2.0) % 4]:
            note('Pad', t, min(2.0, t1 - t), n, vel)
        t += 2.0


groove(0.0, 3.5)
groove(9.0, 11.0, half=True, vel=0.8)
groove(13.0, 27.0)
pad(3.6, 7.4, 55)
pad(13.0, 27.0, 65)

# 旋律性点缀
for k, n in enumerate([84, 88, 91, 96]):
    note('Bells', 2.5 + k * 0.05, 0.6, n, 70)                 # 第 37 遍：稳了
for k, t0 in enumerate([9.0, 9.66, 10.33]):
    note('Bells', t0 + 0.02, 0.35, [72, 76, 79][k], 80)       # 我也是
for k, n in enumerate([79, 84, 88, 91]):
    note('Bells', 15.55 + k * 0.06, 0.6, n, 70)               # 学完
for k, n in enumerate([72, 74, 76, 79, 81, 84, 86, 88, 91]):
    note('Bells', 22.37 + k * 0.25, 0.25, n, 75)              # 伙伴们：五声音阶上行
for k, n in enumerate([72, 76, 79, 84, 88]):
    note('Bells', 25.8 + k * 0.05, 0.7, n, 70)                # 换个句子也认得

# 11 秒四记重音（第三记最重，带和弦）；Hits 轨可挂打击乐 / 电影感 impact 音色
for t0, heavy in [(11.0, 0), (11.6, 0), (11.95, 1), (12.4, 0)]:
    note('Drums', t0, 0.3, 36, 127 if heavy else 110)
    note('Hits', t0, 0.4, 36, 127 if heavy else 100)
    if heavy:
        for n in (60, 64, 67, 72):
            note('Chord Stabs', t0, 0.9, n, 100)

# 落版
note('Drums', 27.0, 2.0, 49, 100)
for k, n in enumerate([36, 48, 55, 60, 64, 67, 72]):
    note('Ending Chord', 27.05 + k * 0.02, 2.8, n, 90)


def vlq(n):
    out = [n & 0x7F]
    while n > 127:
        n >>= 7
        out.insert(0, (n & 0x7F) | 0x80)
    return bytes(out)


def chunk(events):
    # events: (tick, order, bytes)；同一时刻先关后开
    data, last = b'', 0
    for t, _, b in sorted(events, key=lambda e: (e[0], e[1])):
        data += vlq(t - last) + b
        last = t
    data += b'\x00\xff\x2f\x00'
    return b'MTrk' + struct.pack('>I', len(data)) + data


def meta(kind, payload):
    return b'\xff' + bytes([kind]) + vlq(len(payload)) + payload


conductor = [(0, 0, meta(0x03, 'Contexta v4 · 30s'.encode())), (0, 0, meta(0x51, (500000).to_bytes(3, 'big'))),
             (0, 0, meta(0x58, bytes([4, 2, 24, 8])))]
conductor += [(tick(t), 1, meta(0x06, name.encode())) for t, name in MARKERS]
chunks = [chunk(conductor)]
for name, notes in tracks.items():
    ch = CH[name]
    ev = [(0, 0, meta(0x03, name.encode()))]
    for t, dur, n, vel in notes:
        ev.append((tick(t), 2, bytes([0x90 | ch, n, max(1, min(127, vel))])))
        ev.append((tick(t + dur), 1, bytes([0x80 | ch, n, 0])))
    chunks.append(chunk(ev))

out = pathlib.Path(__file__).resolve().parent / 'out' / 'bgm-v4.mid'
out.parent.mkdir(exist_ok=True)
out.write_bytes(b'MThd' + struct.pack('>IHHH', 6, 1, len(chunks), PPQ) + b''.join(chunks))
print('wrote', out)
