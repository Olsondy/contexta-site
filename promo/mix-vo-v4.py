"""把 v4 解说逐句摆到时间轴上，与 out/audio-v4.wav 混音（人声说话时配乐自动压低），
再替换进 out/contexta-30s-v4.mp4 的音轨，画面不重新渲染。
输入 out/vo/<句号>-t<版本>.wav（GPU 主机上 qwen-zh-cn-narrator-v1 生成），输出 out/audio-v4-vo.wav 与 out/contexta-30s-v4-vo.mp4。
用法：python3 mix-vo-v4.py [--bed out/bgm-daw.wav]   需要 ffmpeg。换版本或挪时间只改下面的 CUES。
--bed 换用另一条 30 秒配乐（例如 DAW 里按 bgm-v4.mid 重做、已叠好 sfx-v4.wav 的混音），默认 out/audio-v4.wav。
"""
import argparse, subprocess, pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / 'out'

# (起始秒, 文件, 变速)。时间与 voiceover-v4.srt 一致；变速 >1 为加快且不变调。
CUES = [
    (0.20, '01-t1', 1.0),
    (2.55, '02-t1', 1.0),
    (3.55, '03-t1', 1.05),
    (5.75, '04-t0', 1.0),
    (8.95, '05-t4', 1.0),
    (11.00, '06-t1', 1.0),
    (13.40, '07-t1', 1.0),
    (16.70, '08-t1', 1.0),
    (18.70, '09-t1', 1.0),
    (22.45, '10-t1', 1.0),
    (24.90, '11-t1', 1.0),
    (27.40, '12-t1', 1.0),
]

ap = argparse.ArgumentParser()
ap.add_argument('--bed', type=pathlib.Path, default=OUT / 'audio-v4.wav')
bed = ap.parse_args().bed.resolve()
inputs, chains = ['-i', str(bed)], []
for k, (t, name, tempo) in enumerate(CUES, 1):
    inputs += ['-i', str(OUT / 'vo' / f'{name}.wav')]
    speed = f'atempo={tempo},' if tempo != 1.0 else ''
    chains.append(f'[{k}:a]aresample=48000,{speed}adelay={round(t * 1000)}:all=1[v{k}]')
vo = ''.join(f'[v{k}]' for k in range(1, len(CUES) + 1))
graph = ';'.join(chains + [
    f'{vo}amix=inputs={len(CUES)}:normalize=0,apad=whole_dur=30,atrim=0:30,'
    'loudnorm=I=-16:TP=-2:LRA=7,aformat=channel_layouts=stereo,asplit=2[vo][key]',
    # 说话时配乐压低约 5 dB（人声比配乐高 7–8 LU），句间 0.35 秒内恢复
    '[0:a]volume=0.8[bed]',
    '[bed][key]sidechaincompress=threshold=0.06:ratio=2.5:attack=15:release=350:makeup=1[ducked]',
    '[ducked][vo]amix=inputs=2:normalize=0,alimiter=limit=0.95[out]',
])
mix = OUT / 'audio-v4-vo.wav'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', graph,
                '-map', '[out]', '-ar', '48000', '-c:a', 'pcm_s16le', str(mix)], check=True)
video = OUT / 'contexta-30s-v4-vo.mp4'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(OUT / 'contexta-30s-v4.mp4'), '-i', str(mix),
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                '-movflags', '+faststart', str(video)], check=True)
print('wrote', mix)
print('wrote', video)
