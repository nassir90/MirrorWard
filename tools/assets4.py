import os, sys, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from common import *
ROOT = sys.argv[1]; OUT = os.path.join(ROOT, 'sprites/out4'); os.makedirs(OUT, exist_ok=True)
R = lambda *p: os.path.join(ROOT, 'sprites', *p)
H = Html(ROOT); g2 = H.get('GEN2'); rings = H.get('RINGS')
LUMW = np.array([0.299, 0.587, 0.114]); RL = RAMP @ LUMW / 255

K, D1, D2, M, L1 = [np.array(c + (255,), np.uint8) for c in [(22, 20, 22), (44, 40, 41), (74, 70, 74), (110, 106, 110), (160, 158, 164)]]
def put(img, x, y, c):
    if 0 <= y < img.shape[0] and 0 <= x < img.shape[1]: img[y, x] = c
def line_pts(x0, y0, x1, y1):
    n = max(abs(x1 - x0), abs(y1 - y0), 1); return [(round(x0 + (x1 - x0) * t / n), round(y0 + (y1 - y0) * t / n)) for t in range(n + 1)]
def leg(img, hx, hy, gy, fdx, kdx, lift, near):
    fill = L1 if near else D2; fy = gy - lift; ky = hy + (fy - hy) // 2
    for x, y in line_pts(hx, hy, hx + kdx, ky)[:-1] + line_pts(hx + kdx, ky, hx + fdx, fy - 1):
        put(img, x, y, fill)
    fx = hx + fdx
    for dx in range(0, 2): put(img, fx + dx, fy, K)
rgb, m = art_grid(R('raw4', 'kid.png')); bs = sorted(blobs(m, 4, 2), key=lambda b: b[3])
s = 12 / (bs[0][2] - bs[0][1]); base = pool_frac(*crop(rgb, m, bs[0]), s)
h, w = base.shape[:2]; HIP = round(h * 0.6); PAD = 3
body = np.zeros((h, w + PAD * 2, 4), np.uint8); body[:HIP + 1, PAD:PAD + w] = base[:HIP + 1]
cols = np.nonzero(body[HIP - 2:HIP + 1, :, 3] > 0)[1]; hx = int(round(cols.mean())) if len(cols) else PAD + w // 2
poses = [(0, 0, 0, -1, 0, 0, 0), (2, 1, 0, -2, -1, 0, 0), (1, 1, 0, -2, -1, 1, 1), (0, 1, 0, 1, 2, 1, 0), (-1, 0, 0, 2, 2, 1, 0),
         (-2, -1, 0, 2, 1, 0, 0), (-2, -1, 1, 1, 1, 0, 1), (1, 2, 1, 0, 1, 0, 0), (2, 2, 1, -1, 0, 0, 0)]
kid = []
for nf, nk, nl, ff, fk, fl, drop in poses:
    f = np.zeros_like(body); leg(f, hx - 1, HIP + drop, h - 1, ff, fk, fl, False)
    b = np.roll(body, drop, axis=0); f[b[..., 3] > 0] = b[b[..., 3] > 0]
    leg(f, hx, HIP + drop, h - 1, nf, nk, nl, True); kid.append(f)
tug = np.zeros_like(body); tug[1:] = kid[0][:-1]; tug[:HIP] = np.roll(tug[:HIP], -1, axis=1)
ax = min(tug.shape[1] - 1, hx + 3)
for dx in range(3): put(tug, ax + dx, HIP - 3, L1)
kid.append(tug)
hit = kid[1].copy(); hit[:HIP] = np.roll(hit[:HIP], 1, axis=1)
for dx in range(3): put(hit, min(hit.shape[1] - 1, hx + 3 + dx), HIP - 4 + dx, L1)
kid.append(hit)
g2['kid'], sh = meta_of(kid, 0); preview(sh, os.path.join(OUT, 'kid.png'))

rgb, m = art_grid(R('raw4', 'dog.png')); bs = sorted(blobs(m, 5, 0), key=lambda b: b[3])
s = 13 / (bs[0][4] - bs[0][3])
g2['dog'], sh = meta_of([pool_frac(*crop(rgb, m, b), s) for b in bs]); preview(sh, os.path.join(OUT, 'dog.png'))

rgb, m = art_grid(R('raw4', 'bodies.png')); bs = blobs(m, 4, 2)
top = sorted(sorted(bs, key=lambda b: b[1])[:2], key=lambda b: b[3])
s = 16 / (top[0][4] - top[0][3])
g2['bodies'], sh = meta_of([pool_frac(*crop(rgb, m, b), s) for b in top]); preview(sh, os.path.join(OUT, 'bodies.png'))

rgb, m = art_grid(R('raw4', 'shovel.png')); bs = sorted(blobs(m, 2, 2), key=lambda b: b[3])
g2['shovel'], sh = meta_of([pool_frac(*crop(rgb, m, bs[0]), 11 / (bs[0][2] - bs[0][1])), pool_frac(*crop(rgb, m, bs[1]), 10 / (bs[1][2] - bs[1][1]))])
preview(sh, os.path.join(OUT, 'shovel.png'))

def soft_icon(rgb, m, height, lift=0.0):
    lum = rgb @ LUMW
    edge = m & ~np.pad(m, 1)[2:, 1:-1] | m & ~np.pad(m, 1)[:-2, 1:-1] | m & ~np.pad(m, 1)[1:-1, 2:] | m & ~np.pad(m, 1)[1:-1, :-2]
    mm = m & ~(edge & (lum < 70))
    s = height / mm.shape[0]; W2, H2 = max(1, round(mm.shape[1] * s)), height
    a = np.asarray(Image.fromarray((mm * 255).astype(np.uint8)).resize((W2, H2), Image.BOX), float) / 255
    l = np.asarray(Image.fromarray((lum * mm).clip(0, 255).astype(np.uint8)).resize((W2, H2), Image.BOX), float) / 255
    l = l / np.maximum(a, 1e-3)
    B = np.tile(bayer8(), (H2 // 8 + 1, W2 // 8 + 1))[:H2, :W2]
    v = np.interp(np.clip(l + lift, 0, 1), [0, 1], [RL[0], RL[-1]]); v = np.interp(v, RL, np.arange(6))
    v = 0.6 + v * 0.88
    idx = np.clip(np.floor(v) + (np.mod(v, 1) > B), 1, 5).astype(int)
    out = np.zeros((H2, W2, 4), np.uint8); out[..., :3] = RAMP[idx].astype(np.uint8)
    out[..., 3] = np.where(a > 0.35 + B * 0.4, 255, 0)
    return out, idx, out[..., 3] > 0

def ring_entry(rgb, m, b, name, desc, head):
    c_rgb, c_m = crop(rgb, m, b)
    icon, idx, op = soft_icon(c_rgb, c_m, 18)
    big, _, _ = soft_icon(c_rgb, c_m, 32)
    hh, ww = op.shape
    band = []
    for x in range(ww):
        colm = np.nonzero(op[:, x])[0]
        if len(colm): band.append(int(idx[colm.max() - 1 if len(colm) > 1 else colm.max(), x]))
    hd = None
    if head:
        ht = int(hh * 0.5); cs = np.nonzero(op[:ht].any(axis=0))[0]
        cropi = icon[:ht, cs.min():cs.max() + 1]
        hs = Image.fromarray(cropi).resize((max(3, cropi.shape[1] // 2), max(3, cropi.shape[0] // 2)), Image.NEAREST)
        hd = {'src': data_uri(np.asarray(hs)), 'w': hs.size[0], 'h': hs.size[1]}
    return {'name': name, 'desc': desc, 'icon': data_uri(icon), 'w': ww, 'h': hh, 'big': data_uri(big), 'bw': big.shape[1], 'bh': big.shape[0],
            'band': band, 'thick': 3, 'head': hd}

old = rings['rings']; meta = json.load(open(R('raw3', 'ring_names.json')))
rgb, m = art_grid(R('raw3', 'rings.png')); bs = blobs(m, 8, 2)
new = [ring_entry(rgb, m, b, meta[i]['name'], meta[i]['desc'], i in {1, 2, 5}) for i, b in enumerate(bs)]
rgb, m = art_grid(R('raw4', 'rings2.png')); bs = sorted(blobs(m, 2, 2), key=lambda b: b[3])
story = [ring_entry(rgb, m, bs[0], 'Ring of Knowledge', 'It holds no power. It only remembers that you went down into the dark, and came back.', False),
         ring_entry(rgb, m, bs[1], 'Ring of Fire', "Taken from a dead boy's hand. It burns for the one who carries grief.", True)]
for r in story: r['story'] = True
rings['rings'] = story + new

rgb, m = art_grid(R('raw4', 'sword.png')); b = blobs(m, 1, 2)[0]; c_rgb, c_m = crop(rgb, m, b)
icon, _, _ = soft_icon(c_rgb, c_m, 40, lift=0.05); small, _, _ = soft_icon(c_rgb, c_m, 18, lift=0.05)
rings['sword'] = {'src': data_uri(icon), 'w': icon.shape[1], 'h': icon.shape[0], 'icon': data_uri(small), 'iw': small.shape[1], 'ih': small.shape[0]}
hh, ww = c_m.shape; grip = (hh * 0.83, ww / 2)
S = int(np.ceil(np.hypot(hh, ww))) * 2 + 4; cy = cx = S // 2
canvas = np.zeros((S, S, 4), np.uint8)
oy, ox = int(cy - grip[0]), int(cx - grip[1])
canvas[oy:oy + hh, ox:ox + ww, :3] = c_rgb.clip(0, 255).astype(np.uint8); canvas[oy:oy + hh, ox:ox + ww, 3] = c_m * 255
k = 10 / hh; out_px = int(np.ceil(S * k)); out_px += (out_px + 1) % 2
frames = []
for ang in [-150, 30, -30, -80, -120]:
    rot = np.asarray(Image.fromarray(canvas).rotate(ang, resample=Image.NEAREST, center=(cx, cy)))
    cell = pool_frac(rot[..., :3].astype(float), rot[..., 3] > 0, out_px / S)
    frames.append(cell)
cw = max(f.shape[1] for f in frames); ch = max(f.shape[0] for f in frames)
sheet = np.zeros((ch, cw * len(frames), 4), np.uint8)
for i, f in enumerate(frames): sheet[:f.shape[0], i * cw:i * cw + f.shape[1]] = f
g2['sword'] = {'src': data_uri(sheet), 'w': cw, 'h': ch, 'n': len(frames)}; g2['sword']['stats'] = stats(g2['sword'])
preview(sheet, os.path.join(OUT, 'sword_frames.png')); preview(icon, os.path.join(OUT, 'sword_icon.png'), 6)
prev = [Image.open(__import__('io').BytesIO(__import__('base64').b64decode(r['big'].split(',')[1]))) for r in rings['rings']]
wall = Image.new('RGBA', (sum(p.width + 6 for p in prev), max(p.height for p in prev)), (90, 80, 84, 255)); x = 0
for p in prev: wall.paste(p, (x, 0), p); x += p.width + 6
wall.resize((wall.width * 4, wall.height * 4), Image.NEAREST).save(os.path.join(OUT, 'rings_soft.png'))
for k2 in ['kid', 'dog', 'bodies', 'shovel', 'sword']: print(k2, g2[k2]['w'], g2[k2]['h'], g2[k2]['n'], [x['fh'] for x in g2[k2]['stats']])
gen = H.get('GEN'); kn = gen['knight']
import base64 as b64, io as _io
im = np.asarray(Image.open(_io.BytesIO(b64.b64decode(kn['src'].split(',')[1]))).convert('RGBA'))
cw = kn['w']; frames = [im[:, i * cw:(i + 1) * cw] for i in range(9)]
f0 = frames[0]; ys, xs = np.nonzero(f0[..., 3]); body = f0[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
lie = np.rot90(body, 1); cell = np.zeros_like(f0); h2_, w2_ = lie.shape[:2]; w2_ = min(w2_, cw); ox = (cw - w2_) // 2
cell[kn['h'] - h2_:, ox:ox + w2_] = lie[:, :w2_]
frames.append(cell); sheet = np.concatenate(frames, axis=1)
gen['knight'] = {'src': data_uri(sheet), 'w': cw, 'h': kn['h'], 'n': 10}; gen['knight']['stats'] = stats(gen['knight'])
preview(sheet, os.path.join(OUT, 'knight10.png')); H.put('GEN', gen)
H.put('GEN2', g2); H.put('RINGS', rings); H.save(); print('rings', len(rings['rings']))
