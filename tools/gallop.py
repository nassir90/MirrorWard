import os, sys, io, base64
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from common import *
ROOT = sys.argv[1]; H = Html(ROOT); g2 = H.get('GEN2'); rings = H.get('RINGS')
rgb, m = art_grid(os.path.join(ROOT, 'sprites/raw4/gallop.png'))
bs = blobs(m, 4, 1)
s = 15 / (bs[0][4] - bs[0][3])
cells = [pool_frac(*crop(rgb, m, b), s) for b in bs]
old = g2['dog']; im = np.asarray(Image.open(io.BytesIO(base64.b64decode(old['src'].split(',')[1]))).convert('RGBA'))
dead = im[:, 4 * old['w']:5 * old['w']]; ys, xs = np.nonzero(dead[..., 3]); dead = dead[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
def nose(c):
    a = c[..., 3] > 0; x = np.nonzero(a.any(axis=0))[0][-1]; return x, int(np.nonzero(a[:, x])[0].mean())
N = [nose(c) for c in cells]
top = max(n[1] for n in N); bot = max(c.shape[0] - n[1] for c, n in zip(cells, N)); Hh = top + bot
cw = max(n[0] for n in N) + 3
frames = []
for c, (nx, ny) in zip(cells, N):
    f = np.zeros((Hh, cw, 4), np.uint8); oy, ox = top - ny, cw - 2 - nx
    h, w = c.shape[:2]; y0, x0 = max(0, oy), max(0, ox)
    f[y0:oy + h, x0:ox + w] = c[y0 - oy:, x0 - ox:]; frames.append(f)
Hh = max(Hh, dead.shape[0]); frames = [np.vstack([np.zeros((Hh - f.shape[0], cw, 4), np.uint8), f]) for f in frames]
d = np.zeros((Hh, cw, 4), np.uint8); dh, dw = dead.shape[:2]; dw = min(dw, cw); d[Hh - dh:, (cw - dw) // 2:(cw - dw) // 2 + dw] = dead[:, :dw]; frames.append(d)
sheet = np.concatenate(frames, axis=1)
g2['dog'] = {'src': data_uri(sheet), 'w': int(cw), 'h': int(Hh), 'n': 5}; g2['dog']['stats'] = stats(g2['dog'])
preview(sheet, os.path.join(ROOT, 'sprites/out4/dog_gallop.png'))
for f in rings['fingers']:
    if f['name'] == 'Medicine Finger': f['name'] = 'Ring Finger'
H.put('GEN2', g2); H.put('RINGS', rings); H.save(); print('dog', cw, Hh, [x['fh'] for x in g2['dog']['stats']], [f['name'] for f in rings['fingers']])
