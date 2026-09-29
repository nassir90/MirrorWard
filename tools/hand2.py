import io, os, re, sys, json, base64
import numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from process import background_mask
from process2 import data_uri
from process3 import RAMP, bayer8

ROOT = sys.argv[1]
H = int(sys.argv[2]) if len(sys.argv) > 2 else 150
BG_LEVEL = 0.9
a = np.asarray(Image.open(os.path.join(ROOT, 'sprites/raw2/hand.png')).convert('RGB'), float)
op = ~background_mask(a)
ys, xs = np.nonzero(op); a, op = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], op[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
Wd = round(a.shape[1] * H / a.shape[0])
lum = Image.fromarray((a @ np.array([0.299, 0.587, 0.114])).astype(np.uint8)).resize((Wd, H), Image.BOX)
mask = Image.fromarray((op * 255).astype(np.uint8)).resize((Wd, H), Image.BOX)
L = np.asarray(lum, float) / 255; M = np.asarray(mask, float) / 255
soft = np.asarray(Image.fromarray((M * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3.2)), float) / 255
edge = np.clip((soft - 0.35) / 0.55, 0, 1)
rows = np.linspace(0, 1, H)[:, None]; wrist = np.clip((0.97 - rows) / 0.28, 0, 1)
fade = edge * wrist
lo, hi = np.percentile(L[M > 0.5], 3), np.percentile(L[M > 0.5], 99)
t = np.clip((L - lo) / (hi - lo), 0, 1) ** 0.75
v = BG_LEVEL + (1.2 + t * 3.8 - BG_LEVEL) * fade ** 0.8
B = np.tile(bayer8(), (H // 8 + 1, Wd // 8 + 1))[:H, :Wd]
idx = np.clip(np.floor(v) + (np.mod(v, 1) > B), 0, 5).astype(int)
alpha = (fade > B * 0.999) & (M > 0.05)
out = np.zeros((H, Wd, 4), np.uint8); out[..., :3] = RAMP[idx].astype(np.uint8); out[..., 3] = np.where(alpha, 255, 0)
Image.fromarray(out).save(os.path.join(ROOT, 'sprites/out2/hand_game.png'))
Image.fromarray(out).resize((Wd * 4, H * 4), Image.NEAREST).save(os.path.join(ROOT, 'sprites/out2/hand_game_x4.png'))
p = os.path.join(ROOT, 'index.html'); s = open(p).read()
g2 = json.loads(re.search(r'const GEN2 = (\{.*?\});\n', s, re.S).group(1))
g2['hand'] = {'src': data_uri(out), 'w': Wd, 'h': H, 'n': 1, 'game': True}
s = re.sub(r'const GEN2 = \{.*?\};\n', lambda _: 'const GEN2 = ' + json.dumps(g2) + ';\n', s, flags=re.S)
open(p, 'w').write(s); print('hand', Wd, 'x', H, 'colours', len({tuple(c) for c in out[alpha][:, :3]}))
