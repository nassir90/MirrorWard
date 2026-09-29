import base64, io, json, os, re
import numpy as np
from PIL import Image
from process import background_mask, pixel_size, quantise
from process2 import blobs, data_uri
from process3 import stats, RAMP, bayer8

def art_grid(path):
    a = np.asarray(Image.open(path).convert('RGB'), float)
    op = ~background_mask(a); px = pixel_size(a, op) or 6
    gh, gw = int(a.shape[0] / px), int(a.shape[1] / px)
    ys = ((np.arange(gh) + 0.5) * px).astype(int); xs = ((np.arange(gw) + 0.5) * px).astype(int)
    return a[ys][:, xs], op[ys][:, xs]

def pool_frac(rgb, m, scale, red_first=False, grey=False):
    h, w = m.shape; oh, ow = max(1, round(h * scale)), max(1, round(w * scale))
    sy, sx = h / oh, w / ow
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    red = (rgb[..., 0] > 90) & (rgb[..., 0] > 1.6 * rgb[..., 1])
    orgb = np.zeros((oh, ow, 3)); oa = np.zeros((oh, ow))
    for oy in range(oh):
        y1 = h - int(round(oy * sy)); y0 = max(0, h - int(round((oy + 1) * sy)))
        for ox in range(ow):
            x0 = int(round(ox * sx)); x1 = max(x0 + 1, min(w, int(round((ox + 1) * sx))))
            bm = m[y0:y1, x0:x1]
            if bm.size == 0 or bm.sum() < 0.25 * bm.size: continue
            br = red[y0:y1, x0:x1] & bm
            if red_first and br.any(): k = np.argwhere(br)[0]
            else:
                idx = np.argwhere(bm); k = idx[np.argsort(lum[y0:y1, x0:x1][bm])[len(idx) // 2]]
            c = rgb[y0 + k[0], x0 + k[1]]
            if grey: c = np.full(3, c @ np.array([0.299, 0.587, 0.114]) * (2.6 if red[y0 + k[0], x0 + k[1]] else 1.25))
            orgb[oh - 1 - oy, ox] = c; oa[oh - 1 - oy, ox] = 1
    return quantise(orgb, oa)

def crop(rgb, m, b):
    _, y0, y1, x0, x1 = b
    return rgb[y0:y1, x0:x1], m[y0:y1, x0:x1]

def pack(cells, pad=2):
    cw = max(c.shape[1] for c in cells) + pad; ch = max(c.shape[0] for c in cells)
    sheet = np.zeros((ch, cw * len(cells), 4), np.uint8)
    for i, c in enumerate(cells):
        h, w = c.shape[:2]; ox = i * cw + (cw - w) // 2
        sheet[ch - h:ch, ox:ox + w] = c
    return sheet, cw, ch

def meta_of(cells, pad=2):
    sheet, cw, ch = pack(cells, pad)
    m = {'src': data_uri(sheet), 'w': cw, 'h': ch, 'n': len(cells)}; m['stats'] = stats(m)
    return m, sheet

class Html:
    def __init__(self, root):
        self.p = os.path.join(root, 'index.html'); self.s = open(self.p).read()
    def get(self, tag):
        return json.loads(re.search(r'const %s = (\{.*?\});\n' % tag, self.s, re.S).group(1))
    def put(self, tag, d):
        blk = 'const %s = ' % tag + json.dumps(d) + ';\n'
        if 'const %s = ' % tag in self.s: self.s = re.sub(r'const %s = \{.*?\};\n' % tag, lambda _: blk, self.s, flags=re.S)
        else: self.s = self.s.replace('const GEN2 = ', blk + 'const GEN2 = ', 1)
    def save(self):
        open(self.p, 'w').write(self.s)

def preview(sheet, path, k=8):
    Image.fromarray(sheet).resize((sheet.shape[1] * k, sheet.shape[0] * k), Image.NEAREST).save(path)
