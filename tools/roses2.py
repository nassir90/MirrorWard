import base64, io, json, os, re, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from process import background_mask, pixel_size, quantise
from process2 import blobs, pack, data_uri
ROOT = sys.argv[1]
a = np.asarray(Image.open(os.path.join(ROOT, 'sprites/raw/roses.png')).convert('RGB'), float)
op = ~background_mask(a); px = pixel_size(a, op) or 6
gh, gw = int(a.shape[0] / px), int(a.shape[1] / px)
ys = ((np.arange(gh) + 0.5) * px).astype(int); xs = ((np.arange(gw) + 0.5) * px).astype(int)
art, m = a[ys][:, xs], op[ys][:, xs]
found = blobs(m, 4, 2)
step = max(1, round(max(b[2] - b[1] for b in found) / 14))
cells = []
for _, y0, y1, x0, x1 in found:
    rgb, mm = art[y0:y1, x0:x1], m[y0:y1, x0:x1]
    h, w = mm.shape; oh, ow = -(-h // step), -(-w // step)
    orgb = np.zeros((oh, ow, 3)); oa = np.zeros((oh, ow))
    red = (rgb[..., 0] > 90) & (rgb[..., 0] > 1.6 * rgb[..., 1])
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    for by in range(oh):
        yb1 = h - by * step; yb0 = max(0, yb1 - step)
        for bx in range(ow):
            xb0 = bx * step; xb1 = min(w, xb0 + step)
            bm = mm[yb0:yb1, xb0:xb1]
            if bm.sum() < 0.25 * bm.size: continue
            br = red[yb0:yb1, xb0:xb1] & bm
            if br.any():
                k = np.argwhere(br)[0]
            else:
                idx = np.argwhere(bm); k = idx[np.argsort(lum[yb0:yb1, xb0:xb1][bm])[len(idx) // 2]]
            orgb[oh - 1 - by, bx] = rgb[yb0 + k[0], xb0 + k[1]]; oa[oh - 1 - by, bx] = 1
    cells.append(quantise(orgb, oa))
sheet, cw, ch, sizes = pack(cells)
Image.fromarray(sheet).save(os.path.join(ROOT, 'sprites/out2/roses.png'))
meta = {'src': data_uri(sheet), 'w': cw, 'h': ch, 'n': len(cells)}
r = sheet[..., 0].astype(int); g = sheet[..., 1].astype(int)
print('step', step, 'cell', cw, ch, 'red px', int(((r > 1.4 * g) & (sheet[..., 3] > 0)).sum()), 'of', int((sheet[..., 3] > 0).sum()))
for f in ['index.html', 'prototypes/sprites.html']:
    p = os.path.join(ROOT, f); s = open(p).read()
    gen = json.loads(re.search(r'const GEN = (\{.*?\});\n', s, re.S).group(1)); gen['roses'] = meta
    s = re.sub(r'const GEN = \{.*?\};\n', lambda _: 'const GEN = ' + json.dumps(gen) + ';\n', s, flags=re.S)
    open(p, 'w').write(s)
print('updated')
