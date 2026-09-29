import base64, io, json, os, re, sys
import numpy as np
from PIL import Image

ROOT = sys.argv[1] if __name__ == '__main__' else ''
RAW, OUT = os.path.join(ROOT, 'sprites/raw'), os.path.join(ROOT, 'sprites/out')
if __name__ == '__main__': os.makedirs(OUT, exist_ok=True)

SPECS = {'knight': (4, 16), 'pilgrim': (4, 15), 'crow': (3, 13), 'pine': (3, 33), 'roses': (4, 11)}

GREYS = np.array([[22, 20, 22], [44, 40, 41], [74, 70, 74], [110, 106, 110], [160, 158, 164], [205, 200, 192], [236, 232, 224]], float)
REDS = np.array([[138, 10, 20], [208, 16, 28], [240, 60, 60]], float)

def load(name):
    for ext in ('png', 'jpeg', 'jpg', 'webp'):
        p = os.path.join(RAW, f'{name}.{ext}')
        if os.path.exists(p):
            return Image.open(p).convert('RGB')
    return None

def background_mask(a):
    corners = np.concatenate([a[:8, :8].reshape(-1, 3), a[:8, -8:].reshape(-1, 3), a[-8:, :8].reshape(-1, 3), a[-8:, -8:].reshape(-1, 3)])
    bg = np.median(corners, axis=0)
    d_bg = np.linalg.norm(a - bg, axis=2)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    magenta = (r > 150) & (b > 150) & (g < 0.6 * np.minimum(r, b))
    return (d_bg < 60) | magenta

def segments(opaque, n):
    cols = opaque.sum(axis=0) > 0
    runs, start = [], None
    for x, c in enumerate(list(cols) + [False]):
        if c and start is None:
            start = x
        elif not c and start is not None:
            runs.append([start, x]); start = None
    w = opaque.shape[1]
    runs = [r for r in runs if r[1] - r[0] > w * 0.015]
    while len(runs) > n:
        gaps = [runs[i + 1][0] - runs[i][1] for i in range(len(runs) - 1)]
        i = int(np.argmin(gaps)); runs[i] = [runs[i][0], runs[i + 1][1]]; del runs[i + 1]
    if len(runs) < n:
        step = w / n
        runs = [[int(i * step), int((i + 1) * step)] for i in range(n)]
    return runs

def pixel_size(a, opaque):
    d = (np.abs(np.diff(a, axis=1)).max(axis=2) > 40) & opaque[:, 1:]
    gaps = []
    for row in d[::3]:
        xs = np.where(row)[0]
        if len(xs) > 2:
            g = np.diff(xs); gaps.extend(g[(g >= 3) & (g <= 60)])
    if len(gaps) < 50:
        return None
    gaps = np.array(gaps, float)
    ps = np.arange(4, 16.01, 0.05)
    score = np.array([np.cos(2 * np.pi * gaps / p).mean() for p in ps])
    good = ps[score >= 0.85 * score.max()]
    return float(good.max()) if score.max() > 0.3 else None

def quantise(rgb, alpha):
    out = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    is_red = (r > 70) & (r > 1.4 * g) & (r > 1.4 * b)
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    gi = np.abs(lum[..., None] - GREYS.mean(axis=1)[None, None, :]).argmin(axis=2)
    ri = np.linalg.norm(rgb[..., None, :] - REDS[None, None], axis=3).argmin(axis=2)
    out[..., :3] = np.where(is_red[..., None], REDS[ri], GREYS[gi]).astype(np.uint8)
    out[..., 3] = np.where(alpha > 0.5, 255, 0)
    return out

def process(name, n, target_h):
    img = load(name)
    if img is None:
        return None
    a = np.asarray(img, float)
    opaque = ~background_mask(a)
    frames = []
    for x0, x1 in segments(opaque, n):
        sub = opaque[:, x0:x1]
        ys = np.where(sub.any(axis=1))[0]
        if len(ys) == 0:
            continue
        frames.append((x0, x1, ys[0], ys[-1] + 1))
    tallest = max(f[3] - f[2] for f in frames)
    px = pixel_size(a, opaque)
    if px:
        step = max(1, round(tallest / px / target_h))
        scale = 1 / (px * step)
    else:
        scale = target_h / tallest
    cells = []
    for x0, x1, y0, y1 in frames:
        crop_rgb = a[y0:y1, x0:x1]
        crop_a = opaque[y0:y1, x0:x1].astype(float)
        w, h = max(1, round((x1 - x0) * scale)), max(1, round((y1 - y0) * scale))
        rs = Image.NEAREST if px else Image.BOX
        pm = Image.fromarray((crop_rgb * crop_a[..., None]).astype(np.uint8)).resize((w, h), rs)
        al = Image.fromarray((crop_a * 255).astype(np.uint8)).resize((w, h), rs)
        al_n = np.asarray(al, float) / 255
        rgb = np.asarray(pm, float) / np.maximum(al_n[..., None], 1e-3)
        cells.append(quantise(np.clip(rgb, 0, 255), al_n))
    cw = max(c.shape[1] for c in cells) + 2
    target_h = max(c.shape[0] for c in cells)
    sheet = np.zeros((target_h, cw * len(cells), 4), np.uint8)
    for i, c in enumerate(cells):
        h, w = c.shape[:2]
        ox = i * cw + (cw - w) // 2
        sheet[target_h - h:target_h, ox:ox + w] = c
    im = Image.fromarray(sheet, 'RGBA')
    im.save(os.path.join(OUT, f'{name}.png'))
    im.resize((im.width * 8, im.height * 8), Image.NEAREST).save(os.path.join(OUT, f'{name}_x8.png'))
    buf = io.BytesIO(); im.save(buf, 'PNG')
    print('  pixel size', px)
    return {'src': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode(), 'w': cw, 'h': target_h, 'n': len(cells)}

if __name__ == '__main__':
    gen = {}
    for name, (n, th) in SPECS.items():
        meta = process(name, n, th)
        print(name, 'missing' if meta is None else f"{meta['n']} frames, {meta['w']}x{meta['h']}")
        if meta:
            gen[name] = meta

    html_path = os.path.join(ROOT, 'prototypes', 'sprites.html')
    html = open(html_path).read()
    block = 'const GEN = ' + json.dumps(gen) + ';\n'
    html = re.sub(r'const GEN = \{.*?\};\n', lambda m: block, html, flags=re.S)
    open(html_path, 'w').write(html)
    print('injected', list(gen))
