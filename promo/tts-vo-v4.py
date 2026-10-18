"""逐句请求本地 GPU 语音服务（contexta-server/services/tts-provider）生成 v4 解说，
每句可生成多个版本（take），去首尾静音后存为 out/vo/<句号>-t<版本>.wav，并报告时长是否放得进时间窗。
服务需启用 qwen-zh-cn-narrator-v1 音色（contexta-server ADR 0073）。
用法：TTS_URL=http://<GPU 主机>:8808 TTS_API_KEY=... python3 tts-vo-v4.py [--takes 3] [--first-take 0]
      [--lines 3 5] [--text N=新台词 ...]
同一句、同一 take 的结果可复现；换 take 得到另一个版本。时间窗与 voiceover-v4.md 一致。
"""
import argparse, io, json, os, struct, urllib.request, wave
from pathlib import Path

LINES = [
    (0.2, 2.4, 'evidence，背了三十七遍。'),
    (2.5, 3.4, '稳了。'),
    (3.7, 5.4, '结果在论文里，它是个动词。'),
    (5.6, 7.3, '证据了……什么？'),
    (9.0, 10.9, '背的时候都认识，一读就懵。'),
    (11.0, 13.0, '不是没背，是没在语境里见过它。'),
    (13.3, 16.2, '语境自修，把单词放回真实句子里练。'),
    (16.7, 18.4, '再遇见它，秒懂。'),
    (18.7, 22.1, '实验记录、数据报告，都看得懂。'),
    (22.4, 24.6, '还有学习伙伴，陪你一起练。'),
    (24.9, 26.9, '背过的词，换个句子也认得。'),
    (27.4, 29.4, '微信搜索，语境自修。'),
]
OUT = Path(__file__).resolve().parent / 'out' / 'vo'
VOICE = 'qwen-zh-cn-narrator-v1'

ap = argparse.ArgumentParser()
ap.add_argument('--takes', type=int, default=3)
ap.add_argument('--first-take', type=int, default=0)
ap.add_argument('--lines', type=int, nargs='*')
ap.add_argument('--text', nargs='*', default=[], help='N=台词，替换第 N 句')
a = ap.parse_args()
override = {int(k): v for k, v in (t.split('=', 1) for t in a.text)}
url = os.environ['TTS_URL'].rstrip('/') + '/v1/audio/speech'
key = os.environ['TTS_API_KEY']
OUT.mkdir(parents=True, exist_ok=True)

for i, (t0, t1, text) in enumerate(LINES, 1):
    if a.lines and i not in a.lines:
        continue
    text = override.get(i, text)
    for take in range(a.first_take, a.first_take + a.takes):
        body = json.dumps({'text': text, 'voice': VOICE, 'format': 'wav', 'take': take}).encode()
        req = urllib.request.Request(url, body, {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
        try:
            data = urllib.request.urlopen(req, timeout=300).read()
        except urllib.error.HTTPError as e:
            print(f'{i:02d}-t{take} HTTP {e.code} {e.read()[:200]!r}')
            continue
        with wave.open(io.BytesIO(data)) as w:
            sr, n = w.getframerate(), w.getnframes()
            s = struct.unpack(f'<{n}h', w.readframes(n))
        loud = [k for k, v in enumerate(s) if abs(v) > 400]
        pad = int(0.03 * sr)
        s = s[max(0, loud[0] - pad): loud[-1] + pad] if loud else s
        path = OUT / f'{i:02d}-t{take}.wav'
        with wave.open(str(path), 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes(struct.pack(f'<{len(s)}h', *s))
        dur, room = len(s) / sr, t1 - t0
        fit = 'OK' if dur <= room else f'超 {dur - room:.2f}s'
        print(f'{i:02d}-t{take}  {dur:4.2f}s / {room:.1f}s  {fit:8} {text}', flush=True)
