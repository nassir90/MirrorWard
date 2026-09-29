import base64, io, json, os, re, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from process import background_mask, pixel_size, quantise
from process2 import blobs, data_uri, pool

ROOT = sys.argv[1] if __name__ == '__main__' else ''
HTML = os.path.join(ROOT, 'index.html')

def ramp(t):
    c = np.array([0.065, 0.052, 0.07]) + (np.array([0.94, 0.905, 0.83]) - np.array([0.065, 0.052, 0.07])) * t
    c = c + np.array([0.025, 0.0, 0.035]) * np.sin(t * np.pi)
    return np.clip(c * 255, 0, 255)

RAMP = np.array([ramp(k / 5) for k in range(6)])

def decode(src):
    return np.asarray(Image.open(io.BytesIO(base64.b64decode(src.split(',', 1)[1]))).convert('RGBA'))

def crowfly():
    a = np.asarray(Image.open(os.path.join(ROOT, 'sprites/raw2/crowflap.png')).convert('RGB'), float)
    op = ~background_mask(a); px = pixel_size(a, op) or 6
    gh, gw = int(a.shape[0] / px), int(a.shape[1] / px)
    ys = ((np.arange(gh) + 0.5) * px).astype(int); xs = ((np.arange(gw) + 0.5) * px).astype(int)
    art, m = a[ys][:, xs], op[ys][:, xs]
    found = sorted(blobs(m, 4, 2), key=lambda b: b[3])
    step = max(1, round(max(b[4] - b[3] for b in found) / 22))
    frames = []
    for _, y0, y1, x0, x1 in found:
        c = pool(art[y0:y1, x0:x1], m[y0:y1, x0:x1], step); mm = c[..., 3] > 0
        cols = np.where(mm.any(axis=0))[0]; beak_row = np.where(mm[:, cols[-1]])[0].mean()
        frames.append((c, beak_row))
    top = max(f[1] for f in frames); bot = max(f[0].shape[0] - f[1] for f in frames)
    H = int(np.ceil(top + bot)) + 1; cw = max(f[0].shape[1] for f in frames) + 2
    sheet = np.zeros((H, cw * len(frames), 4), np.uint8)
    for i, (c, br) in enumerate(frames):
        oy = int(round(top - br)); h, w = c.shape[:2]; ox = i * cw + (cw - w) // 2
        sheet[oy:oy + h, ox:ox + w] = c
    Image.fromarray(sheet).resize((sheet.shape[1] * 8, sheet.shape[0] * 8), Image.NEAREST).save(os.path.join(ROOT, 'sprites/out2/crowfly_x8.png'))
    print('crowfly', len(frames), 'frames', cw, 'x', H, 'step', step)
    return {'src': data_uri(sheet), 'w': cw, 'h': H, 'n': len(frames)}

def stats(meta):
    im = decode(meta['src']); n = meta['n']; cw = im.shape[1] // n
    out = []
    for i in range(n):
        f = im[:, i * cw:(i + 1) * cw]; op = f[..., 3] > 0
        if not op.any():
            out.append({'cov': 0, 'lum': 0, 'fw': 0, 'fh': 0}); continue
        lum = (f[..., :3] @ np.array([0.299, 0.587, 0.114]))[op].mean() / 255
        ys, xs = np.nonzero(op)
        out.append({'cov': int(op.sum()), 'lum': round(float(lum), 3), 'fw': int(xs.max() - xs.min() + 1), 'fh': int(ys.max() - ys.min() + 1)})
    return out

def bayer8():
    b = np.array([[0, 2], [3, 1]])
    for _ in range(2):
        b = np.block([[4 * b, 4 * b + 2], [4 * b + 3, 4 * b + 1]])
    return (b + 0.5) / 64

def hand(meta):
    im = decode(meta['src']).astype(float)
    op = im[..., 3] > 0
    lum = im[..., :3] @ np.array([0.299, 0.587, 0.114]) / 255
    ramp_l = RAMP @ np.array([0.299, 0.587, 0.114]) / 255
    t = np.interp(lum, [lum[op].min(), lum[op].max()], [ramp_l[0] + 0.02, ramp_l[-1]])
    v = np.interp(t, ramp_l, np.arange(6))
    B = bayer8(); th = np.tile(B, (im.shape[0] // 8 + 1, im.shape[1] // 8 + 1))[:im.shape[0], :im.shape[1]]
    idx = np.clip(np.floor(v) + (np.mod(v, 1) > th), 0, 5).astype(int)
    out = np.zeros(im.shape, np.uint8); out[..., :3] = RAMP[idx].astype(np.uint8); out[..., 3] = np.where(op, 255, 0)
    Image.fromarray(out).save(os.path.join(ROOT, 'sprites/out2/hand_ramp.png'))
    used = {tuple(c) for c in out[op][:, :3]}
    print('hand colours now', len(used), 'all on ramp:', all(any((np.abs(np.array(c) - r) < 1).all() for r in RAMP.astype(np.uint8)) for c in used))
    return {'src': data_uri(out), 'w': meta['w'], 'h': meta['h'], 'n': 1}

if __name__ == '__main__':
    html = open(HTML).read()
    gen = json.loads(re.search(r'const GEN = (\{.*?\});\n', html, re.S).group(1))
    gen2 = json.loads(re.search(r'const GEN2 = (\{.*?\});\n', html, re.S).group(1))
    gen2['crowfly'] = crowfly()
    if '--hand' in sys.argv: gen2['hand'] = hand(gen2['hand'])
    for d in (gen, gen2):
        for k, m in d.items():
            if k != 'hand':
                m['stats'] = stats(m)
    print('stats e.g. grass', [(s['cov'], s['lum']) for s in gen2['grass']['stats']])
    print('ramp hex', ['#%02x%02x%02x' % tuple(int(round(x)) for x in c) for c in RAMP])
    html = re.sub(r'const GEN = \{.*?\};\n', lambda _: 'const GEN = ' + json.dumps(gen) + ';\n', html, flags=re.S)
    html = re.sub(r'const GEN2 = \{.*?\};\n', lambda _: 'const GEN2 = ' + json.dumps(gen2) + ';\n', html, flags=re.S)
    open(HTML, 'w').write(html)
    print('written')
