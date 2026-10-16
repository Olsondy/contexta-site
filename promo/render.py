"""把 comp.html 逐帧渲染成 1080×1920 视频。
用法：python3 render.py [--fps 60] [--out out/contexta-15s.mp4] [--stills 0,3,6,9,12,14.5]
60fps 抓帧后两两混合成 30fps，得到轻微的快门运动模糊。需要 playwright（使用本机 Chrome）与 ffmpeg。
"""
import argparse, asyncio, subprocess, pathlib
from playwright.async_api import async_playwright

HERE = pathlib.Path(__file__).resolve().parent

async def main(a):
    out = HERE / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chrome', args=['--allow-file-access-from-files', '--disable-lcd-text', '--font-render-hinting=none'])
        pg = await b.new_page(viewport={'width': 1080, 'height': 1920}, device_scale_factor=1)
        await pg.goto((HERE / a.comp).as_uri())
        pg.on('pageerror', lambda e: print('PAGE ERROR', e))
        await pg.evaluate('window.__ready')
        await pg.wait_for_timeout(300)
        if a.stills:
            for t in [float(x) for x in a.stills.split(',')]:
                await pg.evaluate(f'window.__seek({t})')
                await pg.screenshot(path=str(out.parent / f'still-{t:05.2f}.png'))
            await b.close(); return
        dur = await pg.evaluate('window.__duration')
        n = int(round(dur * a.fps))
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(a.fps), '-i', '-',
            *(['-i', str(HERE / a.audio)] if a.audio else []),
            '-vf', 'tmix=frames=2,fps=30,scale=out_range=tv,format=yuv420p' if a.fps == 60 else 'scale=out_range=tv,format=yuv420p',
            '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-profile:v', 'high', '-movflags', '+faststart',
            *(['-c:a', 'aac', '-b:a', '192k', '-shortest'] if a.audio else []), str(out)], stdin=subprocess.PIPE)
        for i in range(n):
            await pg.evaluate(f'window.__seek({i / a.fps})')
            ff.stdin.write(await pg.screenshot(type='jpeg', quality=95))
            if i % 60 == 0: print(f'frame {i}/{n}', flush=True)
        ff.stdin.close(); ff.wait()
        await b.close()
    print('wrote', out)

ap = argparse.ArgumentParser()
ap.add_argument('--fps', type=int, default=60)
ap.add_argument('--out', default='out/contexta-15s.mp4')
ap.add_argument('--audio', default='')
ap.add_argument('--stills', default='')
ap.add_argument('--comp', default='comp.html')
asyncio.run(main(ap.parse_args()))
