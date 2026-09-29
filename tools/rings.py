import io, os, re, sys, json
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from process import background_mask, pixel_size
from process2 import blobs, data_uri, pool
from process3 import RAMP, bayer8

ROOT = sys.argv[1]
R3 = os.path.join(ROOT, 'sprites/raw3'); OUT = os.path.join(ROOT, 'sprites/out3'); os.makedirs(OUT, exist_ok=True)
H = 150
RL = RAMP @ np.array([0.299, 0.587, 0.114]) / 255

def to_ramp_idx(rgb):
    l = rgb @ np.array([0.299, 0.587, 0.114]) / 255
    return np.abs(l[..., None] - RL[None, None, :] if l.ndim == 2 else l[..., None] - RL).argmin(axis=-1)

a = np.asarray(Image.open(os.path.join(R3, 'hand_bare.png')).convert('RGB'), float)
op = ~background_mask(a)
ys, xs = np.nonzero(op); a, op = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], op[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
scale = H / a.shape[0]; Wd = round(a.shape[1] * scale)
L = np.asarray(Image.fromarray((a @ np.array([0.299, 0.587, 0.114])).clip(0, 255).astype(np.uint8)).resize((Wd, H), Image.BOX), float) / 255
M = np.asarray(Image.fromarray((op * 255).astype(np.uint8)).resize((Wd, H), Image.BOX), float) / 255
soft = np.asarray(Image.fromarray((M * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3.2)), float) / 255
fade = np.clip((soft - 0.35) / 0.55, 0, 1) * np.clip((0.97 - np.linspace(0, 1, H)[:, None]) / 0.28, 0, 1)
lo, hi = np.percentile(L[M > 0.5], 3), np.percentile(L[M > 0.5], 99)
t = np.clip((L - lo) / (hi - lo), 0, 1) ** 0.75
v = 0.9 + (1.2 + t * 3.8 - 0.9) * fade ** 0.8
B = np.tile(bayer8(), (H // 8 + 1, Wd // 8 + 1))[:H, :Wd]
idx = np.clip(np.floor(v) + (np.mod(v, 1) > B), 0, 5).astype(int)
alpha = (fade > B * 0.999) & (M > 0.05)
hand = np.zeros((H, Wd, 4), np.uint8); hand[..., :3] = RAMP[idx].astype(np.uint8); hand[..., 3] = np.where(alpha, 255, 0)

mask = op.copy(); h0, w0 = mask.shape
top = np.array([np.argmax(mask[:, x]) if mask[:, x].any() else h0 for x in range(w0)])
tips = []
win = max(6, w0 // 40)
for x in range(w0):
    tv = top[x]
    if tv > h0 * 0.45: continue
    if tv == top[max(0, x - win):x + win + 1].min() and (not tips or x - tips[-1][0] > win * 2):
        tips.append((x, tv))
tips = sorted(tips, key=lambda p: p[0])[:4]
band = slice(int(h0 * 0.35), int(h0 * 0.8))
cols = np.nonzero(mask[band].any(axis=0))[0]; tx = cols.max(); ty = int(np.mean(np.nonzero(mask[band, tx])[0])) + band.start
palm = np.array(np.nonzero(mask[int(h0 * 0.55):int(h0 * 0.8)])).mean(axis=1) + [int(h0 * 0.55), 0]

def trace(tip, d0):
    p = np.array(tip, float); d = np.array(d0, float) / np.linalg.norm(d0)
    step = h0 * 0.012; pts = []; widths = []
    for _ in range(140):
        q = p + d * step
        perp = np.array([-d[1], d[0]])
        ext = []
        for sgn in (-1, 1):
            k = 0
            while k < h0 * 0.12:
                x, y = (q + perp * sgn * k).round().astype(int)
                if not (0 <= y < h0 and 0 <= x < w0 and mask[y, x]): break
                k += 1
            ext.append(k)
        wdt = ext[0] + ext[1]
        if wdt < 3: break
        c = q + perp * (ext[1] - ext[0]) / 2
        if len(widths) > 6 and wdt > 1.55 * np.median(widths[:8]): break
        nd = c - p; nd /= (np.linalg.norm(nd) + 1e-9)
        d = 0.75 * d + 0.25 * nd; d /= np.linalg.norm(d)
        pts.append(c.copy()); widths.append(wdt); p = c
    return pts, widths

names = ['Little Finger', 'Medicine Finger', 'Middle Finger', 'Index Finger']
fingers = []
for i, (x, y) in enumerate(tips):
    pts, wid = trace((x, y + 2), (0, 1))
    fingers.append((names[i] if len(tips) == 4 else f'Finger {i + 1}', pts, wid))
tp, tw = trace((tx - 2, ty), (palm[1] - tx, palm[0] - ty))
fingers.append(('Thumb', tp, tw))
F = []
for name, pts, wid in fingers:
    if len(pts) < 4: continue
    pts = pts[::-1]; wid = wid[::-1]
    step = max(1, len(pts) // 14)
    poly = [[round(p[0] * scale, 1), round(p[1] * scale, 1), round(w * scale, 1)] for p, w in zip(pts[::step], wid[::step])]
    poly.append([round(pts[-1][0] * scale, 1), round(pts[-1][1] * scale, 1), round(wid[-1] * scale, 1)])
    F.append({'name': name, 'axis': poly})
print('fingers', [(f['name'], len(f['axis']), f['axis'][0][2]) for f in F])

dbg = Image.fromarray(hand).resize((Wd * 4, H * 4), Image.NEAREST).convert('RGBA'); d = ImageDraw.Draw(dbg)
for f in F:
    for (x0, y0, w_), (x1, y1, _) in zip(f['axis'], f['axis'][1:]):
        d.line([(x0 * 4, y0 * 4), (x1 * 4, y1 * 4)], fill=(255, 40, 40, 255), width=2)
    for x_, y_, w_ in f['axis'][::3]: d.ellipse([x_ * 4 - w_ * 2, y_ * 4 - 2, x_ * 4 + w_ * 2, y_ * 4 + 2], outline=(40, 200, 255, 255))
dbg.save(os.path.join(OUT, 'fingers_debug.png'))

r = np.asarray(Image.open(os.path.join(R3, 'rings.png')).convert('RGB'), float)
rop = ~background_mask(r); px = pixel_size(r, rop) or 6
gh, gw = int(r.shape[0] / px), int(r.shape[1] / px)
ys = ((np.arange(gh) + 0.5) * px).astype(int); xs = ((np.arange(gw) + 0.5) * px).astype(int)
art, am = r[ys][:, xs], rop[ys][:, xs]
found = blobs(am, 8, 2)
meta = json.load(open(os.path.join(R3, 'ring_names.json')))
HEADS = {1, 2, 5}
rings = []
for i, (_, y0, y1, x0, x1) in enumerate(found):
    step = max(1, round((y1 - y0) / 18))
    ic = pool(art[y0:y1, x0:x1], am[y0:y1, x0:x1], step)
    ia = ic[..., 3] > 0
    ri = to_ramp_idx(ic[..., :3].astype(float)); icon = np.zeros_like(ic); icon[..., :3] = RAMP[ri].astype(np.uint8); icon[..., 3] = ic[..., 3]
    hh, ww = ia.shape
    band = []
    for x in range(ww):
        colm = np.nonzero(ia[:, x])[0]
        if len(colm): band.append(int(ri[colm.max() - 1 if len(colm) > 1 else colm.max(), x]))
    thick = int(np.clip(round(np.sum(ia[:, ww // 2]) / 3), 2, 3))
    head = None
    if i in HEADS:
        ht = int(hh * 0.5); cols_ = np.nonzero(ia[:ht].any(axis=0))[0]
        crop = icon[:ht, cols_.min():cols_.max() + 1]
        hs = Image.fromarray(crop).resize((max(3, crop.shape[1] // 2), max(3, crop.shape[0] // 2)), Image.NEAREST)
        head = {'src': data_uri(np.asarray(hs)), 'w': hs.size[0], 'h': hs.size[1]}
    Image.fromarray(icon).resize((ww * 6, hh * 6), Image.NEAREST).save(os.path.join(OUT, f'ring{i}_x6.png'))
    rings.append({'name': meta[i]['name'], 'desc': meta[i]['desc'], 'icon': data_uri(icon), 'w': ww, 'h': hh, 'band': band, 'thick': thick, 'head': head})
print('rings', [(x['name'], x['w'], x['h'], x['thick'], bool(x['head'])) for x in rings])

p = os.path.join(ROOT, 'index.html'); s = open(p).read()
g2 = json.loads(re.search(r'const GEN2 = (\{.*?\});\n', s, re.S).group(1))
g2['hand'] = {'src': data_uri(hand), 'w': Wd, 'h': H, 'n': 1, 'game': True}
s = re.sub(r'const GEN2 = \{.*?\};\n', lambda _: 'const GEN2 = ' + json.dumps(g2) + ';\n', s, flags=re.S)
block = 'const RINGS = ' + json.dumps({'fingers': F, 'rings': rings}) + ';\n'
if 'const RINGS = ' in s: s = re.sub(r'const RINGS = \{.*?\};\n', lambda _: block, s, flags=re.S)
else: s = s.replace('const GEN2 = ', block + 'const GEN2 = ', 1)
open(p, 'w').write(s); print('written hand', Wd, 'x', H)
