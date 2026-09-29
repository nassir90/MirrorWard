import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from common import *
ROOT = sys.argv[1]; OUT = os.path.join(ROOT, 'sprites/out4'); os.makedirs(OUT, exist_ok=True)
H = Html(ROOT); gen, g2 = H.get('GEN'), H.get('GEN2')
R = lambda *p: os.path.join(ROOT, 'sprites', *p)

rgb, m = art_grid(R('raw', 'crow.png')); bs = sorted(blobs(m, 3, 2), key=lambda b: b[3])
s = 5 / (bs[0][2] - bs[0][1]); gen['crow'], sh = meta_of([pool_frac(*crop(rgb, m, b), s) for b in bs]); preview(sh, os.path.join(OUT, 'crow.png'))

rgb, m = art_grid(R('raw2', 'crowflap.png')); bs = sorted(blobs(m, 4, 2), key=lambda b: b[3])
s = 12 / max(b[4] - b[3] for b in bs); cells = [pool_frac(*crop(rgb, m, b), s) for b in bs]
beak = [np.nonzero(c[:, np.nonzero((c[..., 3] > 0).any(axis=0))[0][-1], 3])[0].mean() for c in cells]
top = max(beak); bot = max(c.shape[0] - b for c, b in zip(cells, beak)); Hh = int(np.ceil(top + bot)) + 1
al = []
for c, b in zip(cells, beak):
    f = np.zeros((Hh, c.shape[1], 4), np.uint8); oy = int(round(top - b)); f[oy:oy + c.shape[0]] = c[:Hh - oy]; al.append(f)
g2['crowfly'], sh = meta_of(al); preview(sh, os.path.join(OUT, 'crowfly.png'))

rgb, m = art_grid(R('raw', 'roses.png')); bs = blobs(m, 4, 2); tall = max(b[2] - b[1] for b in bs)
gen['roses_s'], sh = meta_of([pool_frac(*crop(rgb, m, b), 10 / tall, red_first=True) for b in bs]); preview(sh, os.path.join(OUT, 'roses_s.png'))
gen['bushes'], sh = meta_of([pool_frac(*crop(rgb, m, b), 15 / tall, grey=True) for b in bs]); preview(sh, os.path.join(OUT, 'bushes.png'))

rgb, m = art_grid(R('raw2', 'props.png')); bs = blobs(m, 6, 2)
T = [10, 9, 8, 13, 8, 20]
g2['props'], sh = meta_of([pool_frac(*crop(rgb, m, b), t / (b[2] - b[1])) for b, t in zip(bs, T)]); preview(sh, os.path.join(OUT, 'props.png'))
for k in ['crow', 'roses_s', 'bushes']: print(k, gen[k]['w'], gen[k]['h'], [x['fh'] for x in gen[k]['stats']])
for k in ['crowfly', 'props']: print(k, g2[k]['w'], g2[k]['h'], [x['fh'] for x in g2[k]['stats']])
H.put('GEN', gen); H.put('GEN2', g2); H.save()
