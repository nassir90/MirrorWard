import os, sys, re, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import process2 as P2
from process import background_mask, pixel_size
from process3 import stats
ROOT = sys.argv[1]
SRC = {'deadtrees': ('raw2', 4, 33), 'birches': ('raw2', 5, 33), 'shrubs': ('raw2', 6, 9), 'grass': ('raw2', 6, 10), 'pine': ('raw', 3, 22)}
p = os.path.join(ROOT, 'index.html'); s = open(p).read()
g2 = json.loads(re.search(r'const GEN2 = (\{.*?\});\n', s, re.S).group(1))
for name, (folder, n, th) in SRC.items():
    P2.RAW = os.path.join(ROOT, 'sprites', folder)
    cells, px, step = P2.items(name, n, th)
    sheet, cw, ch, sizes = P2.pack(cells)
    meta = {'src': P2.data_uri(sheet), 'w': cw, 'h': ch, 'n': len(cells)}; meta['stats'] = stats(meta)
    g2[name + '_s'] = meta; print(name + '_s', len(cells), cw, ch, 'step', step)
s = re.sub(r'const GEN2 = \{.*?\};\n', lambda _: 'const GEN2 = ' + json.dumps(g2) + ';\n', s, flags=re.S)
open(p, 'w').write(s)
