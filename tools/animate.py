import base64, io, json, os, re, sys
import numpy as np
from PIL import Image

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, 'sprites/out')

K, D1, D2, M, L1, L2 = [np.array(c + (255,), np.uint8) for c in
                         [(22, 20, 22), (44, 40, 41), (74, 70, 74), (110, 106, 110), (160, 158, 164), (205, 200, 192)]]

def frames_of(name, n):
    im = np.asarray(Image.open(os.path.join(OUT, name + '.png')).convert('RGBA'))
    cw = im.shape[1] // n
    return [im[:, i * cw:(i + 1) * cw].copy() for i in range(n)]

def put(img, x, y, c):
    if 0 <= y < img.shape[0] and 0 <= x < img.shape[1]:
        img[y, x] = c

def line_pts(x0, y0, x1, y1):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    return [(round(x0 + (x1 - x0) * t / n), round(y0 + (y1 - y0) * t / n)) for t in range(n + 1)]

THIN = False

def leg(img, hip_x, hip_y, ground_y, foot_dx, knee_dx, lift, near):
    fill, shade = (L1, M) if near else (D2, D1)
    foot_y = ground_y - lift
    knee_y = hip_y + (foot_y - hip_y) // 2
    pts = line_pts(hip_x, hip_y, hip_x + knee_dx, knee_y)[:-1] + line_pts(hip_x + knee_dx, knee_y, hip_x + foot_dx, foot_y - 1)
    for x, y in pts:
        put(img, x - 1, y, K)
        if THIN:
            put(img, x, y, fill); put(img, x + 1, y, K)
        else:
            put(img, x, y, shade); put(img, x + 1, y, fill); put(img, x + 2, y, K)
    fx = hip_x + foot_dx
    for dx in range(-1, 2 if THIN else 3):
        put(img, fx + dx, foot_y, K)
    put(img, fx, foot_y - 1, K if not near else M)

def sc(v, k):
    return 0 if v == 0 else int(np.sign(v) * max(1, round(abs(v) * k)))

def knight():
    global THIN
    base = frames_of('knight', 4)[0]
    h, w = base.shape[:2]
    k = h / 26
    THIN = h < 24
    HIP = round(h * 19 / 26)
    PAD = 4
    body = np.zeros((h, w + PAD * 2, 4), np.uint8)
    body[:HIP + 1, PAD:PAD + w] = base[:HIP + 1]
    torso = body[HIP - 5:HIP + 1, :, 3] > 0
    hip_x = int(round(np.nonzero(torso)[1].mean())) if torso.any() else PAD + w // 2
    body[HIP - 1:HIP + 1, hip_x + 3:] = 0
    ground = h - 1
    poses = [
        (1, 0, 0, -1, 0, 0, 0),
        (3, 2, 0, -3, -1, 0, 0),
        (2, 2, 0, -3, -2, 1, 1),
        (0, 1, 0, 1, 3, 2, 0),
        (-2, 0, 0, 3, 3, 1, 0),
        (-3, -1, 0, 3, 2, 0, 0),
        (-3, -2, 1, 2, 2, 0, 1),
        (1, 3, 2, 0, 1, 0, 0),
        (3, 3, 1, -2, 0, 0, 0),
    ]
    out = []
    poses = [tuple(sc(v, k) if i < 6 else v for i, v in enumerate(p)) for p in poses]
    for nf, nk, nl, ff, fk, fl, drop in poses:
        f = np.zeros_like(body)
        leg(f, hip_x - 1, HIP + drop, ground, ff, fk, fl, near=False)
        b = np.roll(body, drop, axis=0)
        f[b[..., 3] > 0] = b[b[..., 3] > 0]
        leg(f, hip_x + 1, HIP + drop, ground, nf, nk, nl, near=True)
        out.append(f)
    return out

def pilgrim():
    base = frames_of('pilgrim', 4)[0]
    h, w = base.shape[:2]
    k = h / 24
    HEM = round(h * 21 / 24)
    PAD = 3
    body = np.zeros((h, w + PAD * 2, 4), np.uint8)
    body[:HEM + 1, PAD:PAD + w] = base[:HEM + 1]
    ground = h - 1
    cols = np.nonzero(body[HEM - 3:HEM + 1, :, 3] > 0)[1]
    cx = int(round(cols.mean())) - 1 if len(cols) else PAD + w // 2
    poses = [(1, -2, 0, 0, 0, 0),
             (3, -3, 0, 0, 1, 0), (2, -2, 0, 1, 1, 1), (0, 0, 1, 0, 0, 0), (-1, 2, 0, 1, -1, 0),
             (-3, 3, 0, 0, -1, 0), (-2, 2, 1, 0, -1, 1), (0, 0, 0, 1, 0, 0), (2, -1, 1, 0, 1, 0)]
    poses = [(sc(a, k), sc(b, k), c, d, e, g) for a, b, c, d, e, g in poses]
    out = []
    for fx, bx, fl, bl, sway, bob in poses:
        f = np.zeros_like(body)
        for x0, lift, c in ((bx, bl, D1), (fx, fl, K)):
            y = ground - lift
            for dx in range(3):
                put(f, cx + x0 + dx, y, c)
            put(f, cx + x0, y - 1, c)
        b = np.roll(body, bob, axis=0)
        hem = b[HEM - 2 + bob:HEM + 1 + bob].copy()
        b[HEM - 2 + bob:HEM + 1 + bob] = np.roll(hem, sway, axis=1)
        f[b[..., 3] > 0] = b[b[..., 3] > 0]
        out.append(f)
    return out

def sheet_meta(frames, name):
    cw, h = frames[0].shape[1], frames[0].shape[0]
    sheet = np.concatenate(frames, axis=1)
    im = Image.fromarray(sheet)
    im.save(os.path.join(OUT, name + '_anim.png'))
    im.resize((im.width * 8, im.height * 8), Image.NEAREST).save(os.path.join(OUT, name + '_anim_x8.png'))
    buf = io.BytesIO(); im.save(buf, 'PNG')
    return {'src': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode(), 'w': cw, 'h': h, 'n': len(frames)}

html_path = os.path.join(ROOT, 'prototypes', 'sprites.html')
html = open(html_path).read()
gen = json.loads(re.search(r'const GEN = (\{.*?\});\n', html, re.S).group(1))
gen['knight'] = sheet_meta(knight(), 'knight')
gen['pilgrim'] = sheet_meta(pilgrim(), 'pilgrim')
html = re.sub(r'const GEN = \{.*?\};\n', lambda m: 'const GEN = ' + json.dumps(gen) + ';\n', html, flags=re.S)
open(html_path, 'w').write(html)
print({k: (v['w'], v['h'], v['n']) for k, v in gen.items()})
