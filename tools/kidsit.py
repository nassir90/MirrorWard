import os, sys, io, base64
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from common import *
ROOT = sys.argv[1]; H = Html(ROOT); g2 = H.get('GEN2'); kd = g2['kid']
im = np.asarray(Image.open(io.BytesIO(base64.b64decode(kd['src'].split(',')[1]))).convert('RGBA'))
cw, h = kd['w'], kd['h']; frames = [im[:, i * cw:(i + 1) * cw].copy() for i in range(12)]
f0 = frames[0]; HIP = round(h * 0.6)
cols = np.nonzero(f0[HIP - 2:HIP + 1, :, 3] > 0)[1]; hx = int(round(cols.mean()))
K, D2, L1 = (22, 20, 22, 255), (74, 70, 74, 255), (160, 158, 164, 255)
sit = np.zeros_like(f0); drop = h - 2 - HIP
sit[drop:drop + HIP + 1] = f0[:HIP + 1]
for dx in range(0, 4): sit[h - 1, min(cw - 1, hx + dx)] = D2 if dx < 3 else K
for dx in range(0, 4): sit[h - 2, min(cw - 1, hx + dx)] = L1 if dx < 3 else K
bow = sit.copy(); head = 5; bow[drop + 1:drop + 1 + head] = sit[drop:drop + head]; bow[drop] = 0
frames += [sit, bow]; sheet = np.concatenate(frames, axis=1)
g2['kid'] = {'src': data_uri(sheet), 'w': cw, 'h': h, 'n': 14}; g2['kid']['stats'] = stats(g2['kid'])
preview(sheet, os.path.join(ROOT, 'sprites/out4/kid14.png')); H.put('GEN2', g2); H.save(); print('kid', g2['kid']['n'])
