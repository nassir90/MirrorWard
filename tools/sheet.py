import glob, sys
from PIL import Image
SP = sys.argv[1]; fs = sorted(glob.glob(SP + '/fr/f*.png')); cols = 6; cw, ch = 270, 480
rows = (len(fs) + cols - 1) // cols; S = Image.new('RGB', (cw * cols, ch * rows))
for i, f in enumerate(fs): S.paste(Image.open(f).convert('RGB').resize((cw, ch)), ((i % cols) * cw, (i // cols) * ch))
S.save(SP + '/sheet.jpg', quality=85); print(len(fs))
