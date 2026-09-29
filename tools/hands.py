import os, sys, io, base64
import numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from common import *
ROOT = sys.argv[1]; R4 = os.path.join(ROOT, 'sprites/raw4'); OUT = os.path.join(ROOT, 'sprites/out4')
H = Html(ROOT); g2 = H.get('GEN2')

def load(name):
    a = np.asarray(Image.open(os.path.join(R4, name + '.png')).convert('RGB'), float); op = ~background_mask(a)
    ys, xs = np.nonzero(op); return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], op[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
def forearm(op): row = op[int(op.shape[0] * 0.08)]; xs = np.nonzero(row)[0]; return xs.max() - xs.min() + 1

ARM = 34
def render(name, maxh, mirror=False):
    a, op = load(name)
    if mirror: a, op = a[:, ::-1], op[:, ::-1]
    s = ARM / forearm(op)
    Hh, Wd = round(a.shape[0] * s), round(a.shape[1] * s)
    L = np.asarray(Image.fromarray((a @ np.array([0.299, 0.587, 0.114])).clip(0, 255).astype(np.uint8)).resize((Wd, Hh), Image.BOX), float) / 255
    M = np.asarray(Image.fromarray((op * 255).astype(np.uint8)).resize((Wd, Hh), Image.BOX), float) / 255
    if Hh > maxh: L, M, Hh = L[:maxh], M[:maxh], maxh
    soft = np.asarray(Image.fromarray((M * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.3)), float) / 255
    rows = np.linspace(0, 1, Hh)[:, None] * Hh
    top = np.clip((rows - 4) / 60, 0, 1)
    bottom = np.clip((Hh - rows) / 14, 0, 1) if Hh >= maxh else 1
    fade = np.clip((soft - 0.25) / 0.5, 0, 1) * top * bottom
    lo, hi = np.percentile(L[M > 0.5], 3), np.percentile(L[M > 0.5], 99)
    t = np.clip((L - lo) / (hi - lo), 0, 1) ** 0.8
    v = 0.9 + (1.1 + t * 3.9 - 0.9) * fade ** 0.8
    B = np.tile(bayer8(), (Hh // 8 + 1, Wd // 8 + 1))[:Hh, :Wd]
    idx = np.clip(np.floor(v) + (np.mod(v, 1) > B), 0, 5).astype(int)
    alpha = (fade > B * 0.999) & (M > 0.05)
    out = np.zeros((Hh, Wd, 4), np.uint8); out[..., :3] = RAMP[idx].astype(np.uint8); out[..., 3] = np.where(alpha, 255, 0)
    Image.fromarray(out).resize((Wd * 3, Hh * 3), Image.NEAREST).save(os.path.join(OUT, name + '_x3.png'))
    return {'src': data_uri(out), 'w': Wd, 'h': Hh, 'n': 1}

g2['hand_idle'] = render('hand_idle', 200, mirror=True); g2['hand_sword'] = render('hand_sword', 200)
print({k: (g2[k]['w'], g2[k]['h']) for k in ['hand_idle', 'hand_sword']})

kd = g2['kid']; im = np.asarray(Image.open(io.BytesIO(base64.b64decode(kd['src'].split(',')[1]))).convert('RGBA'))
cw = kd['w']; frames = [im[:, i * cw:(i + 1) * cw] for i in range(11)]
f0 = frames[0]; ys, xs = np.nonzero(f0[..., 3]); body = np.rot90(f0[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 1)
cell = np.zeros_like(f0); hh, ww = body.shape[:2]; ww = min(ww, cw); cell[kd['h'] - hh:, (cw - ww) // 2:(cw - ww) // 2 + ww] = body[:, :ww]
frames.append(cell); sheet = np.concatenate(frames, axis=1)
g2['kid'] = {'src': data_uri(sheet), 'w': cw, 'h': kd['h'], 'n': 12}; g2['kid']['stats'] = stats(g2['kid'])
H.put('GEN2', g2); H.save(); print('kid frames', g2['kid']['n'])
