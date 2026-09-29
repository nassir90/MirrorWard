import base64, io, json, os, re, sys
from collections import deque
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from process import background_mask, pixel_size, quantise

ROOT = sys.argv[1] if __name__ == '__main__' else ''
RAW, OUT = os.path.join(ROOT, 'sprites/raw2'), os.path.join(ROOT, 'sprites/out2')

SPECS = {'deadtrees': (4, 44), 'birches': (5, 44), 'shrubs': (6, 12), 'grass': (6, 14), 'houses': (3, 80),
         'hut': (1, 60), 'fire': (4, 30), 'stones': (3, 112), 'ruins': (4, 50), 'props': (6, 13)}

def blobs(mask, n, grow):
    h, w = mask.shape
    g = np.zeros_like(mask)
    ys, xs = np.nonzero(mask)
    for dy in range(-grow, grow + 1):
        for dx in range(-grow, grow + 1):
            g[np.clip(ys + dy, 0, h - 1), np.clip(xs + dx, 0, w - 1)] = True
    lab = np.zeros((h, w), np.int32); cur = 0; found = []
    for y0, x0 in zip(*np.nonzero(g)):
        if lab[y0, x0]:
            continue
        cur += 1; q = deque([(y0, x0)]); lab[y0, x0] = cur; pts = []
        while q:
            y, x = q.popleft(); pts.append((y, x))
            for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= ny < h and 0 <= nx < w and g[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = cur; q.append((ny, nx))
        pts = np.array(pts)
        real = mask[pts[:, 0], pts[:, 1]].sum()
        found.append((real, pts[:, 0].min(), pts[:, 0].max() + 1, pts[:, 1].min(), pts[:, 1].max() + 1))
    found.sort(key=lambda b: -b[0])
    keep = found[:n]
    rows = sorted(keep, key=lambda b: b[2])
    out, band = [], []
    for b in rows:
        if band and b[2] - band[-1][2] > (b[2] - b[1]) * 0.5:
            out += sorted(band, key=lambda c: c[3]); band = []
        band.append(b)
    out += sorted(band, key=lambda c: c[3])
    return out

def pool(rgb, m, step):
    if step == 1:
        return quantise(rgb, m.astype(float))
    h, w = m.shape
    oh, ow = -(-h // step), -(-w // step)
    out_rgb = np.zeros((oh, ow, 3)); out_a = np.zeros((oh, ow))
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    for by in range(oh):
        y1 = h - by * step; y0 = max(0, y1 - step)
        for bx in range(ow):
            x0 = bx * step; x1 = min(w, x0 + step)
            bm = m[y0:y1, x0:x1]
            if bm.sum() < 0.25 * bm.size:
                continue
            idx = np.argwhere(bm)
            ls = lum[y0:y1, x0:x1][bm]
            k = idx[np.argsort(ls)[len(ls) // 2]]
            out_rgb[oh - 1 - by, bx] = rgb[y0 + k[0], x0 + k[1]]; out_a[oh - 1 - by, bx] = 1
    return quantise(out_rgb, out_a)

def load(name):
    return np.asarray(Image.open(os.path.join(RAW, name + '.png')).convert('RGB'), float)

def items(name, n, target_h):
    a = load(name)
    opaque = ~background_mask(a)
    px = pixel_size(a, opaque) or 6.0
    gh, gw = int(a.shape[0] / px), int(a.shape[1] / px)
    ys = ((np.arange(gh) + 0.5) * px).astype(int); xs = ((np.arange(gw) + 0.5) * px).astype(int)
    art = a[ys][:, xs]; amask = opaque[ys][:, xs]
    found = blobs(amask, n, grow=1 if name == 'ruins' else 2)
    tallest = max(b[2] - b[1] for b in found)
    step = max(1, round(tallest / target_h))
    cells = []
    for _, y0, y1, x0, x1 in found:
        cells.append(pool(art[y0:y1, x0:x1], amask[y0:y1, x0:x1], step))
    return cells, px, step

def pack(cells):
    cw = max(c.shape[1] for c in cells) + 2; ch = max(c.shape[0] for c in cells)
    sheet = np.zeros((ch, cw * len(cells), 4), np.uint8)
    sizes = []
    for i, c in enumerate(cells):
        h, w = c.shape[:2]; ox = i * cw + (cw - w) // 2
        sheet[ch - h:ch, ox:ox + w] = c
        sizes.append([int(w), int(h)])
    return sheet, cw, ch, sizes

def data_uri(arr):
    buf = io.BytesIO(); Image.fromarray(arr).save(buf, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

if __name__ == '__main__':
    gen = {}
    for name, (n, th) in SPECS.items():
        cells, px, step = items(name, n, th)
        sheet, cw, ch, sizes = pack(cells)
        Image.fromarray(sheet).save(os.path.join(OUT, name + '.png'))
        Image.fromarray(sheet).resize((sheet.shape[1] * 6, sheet.shape[0] * 6), Image.NEAREST).save(os.path.join(OUT, name + '_x6.png'))
        gen[name] = {'src': data_uri(sheet), 'w': cw, 'h': ch, 'n': len(cells), 'sizes': sizes}
        print(f'{name}: {len(cells)} items, px {px:.2f}, step {step}, cell {cw}x{ch}')

    a = load('hand'); opaque = ~background_mask(a)
    ys, xs = np.nonzero(opaque); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    TH = 300; sc = TH / (y1 - y0)
    crop = Image.fromarray(a[y0:y1, x0:x1].astype(np.uint8)).resize((round((x1 - x0) * sc), TH), Image.NEAREST)
    cm = Image.fromarray((opaque[y0:y1, x0:x1] * 255).astype(np.uint8)).resize(crop.size, Image.NEAREST)
    hand = quantise(np.asarray(crop, float), np.asarray(cm, float) / 255)
    Image.fromarray(hand).save(os.path.join(OUT, 'hand.png'))
    gen['hand'] = {'src': data_uri(hand), 'w': hand.shape[1], 'h': hand.shape[0], 'n': 1}
    print('hand', hand.shape)

    target = os.path.join(ROOT, 'index.html')
    if os.path.exists(target):
        html = open(target).read()
        html = re.sub(r'const GEN2 = \{.*?\};\n', lambda m: 'const GEN2 = ' + json.dumps(gen) + ';\n', html, flags=re.S)
        open(target, 'w').write(html)
        print('injected into index.html')
    json.dump({k: {kk: vv for kk, vv in v.items() if kk != 'src'} for k, v in gen.items()}, open(os.path.join(OUT, 'meta.json'), 'w'))
