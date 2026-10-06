import sys, time
from gemini import read_key, image
key = read_key(sys.argv[1]); out = sys.argv[2]
BASE = ("Single object only, centred, whole object visible with margin, plain pure white background, soft even studio light, "
        "no ground, no shadow, no text. Realistic 3D clay-render style, clear readable silhouette, three-quarter view from slightly above. ")
JOBS = {
  "cottage_a": BASE + "A small medieval half-timbered cottage with a very steep gabled roof, a stone chimney, small windows and a wooden door.",
  "cottage_b": BASE + "A narrow two-storey medieval timber-framed house with a steep roof, an overhanging upper floor, a side dormer and a chimney.",
  "tower": BASE + "A tall round medieval stone watchtower, rough masonry blocks, crenellated top, a few narrow arrow-slit windows and an arched wooden door at its base.",
  "stone": BASE + "A tall weathered standing stone (menhir), roughly rectangular and slightly leaning, with a deep vertical crack splitting its upper half.",
  "cabin": BASE + "A small rough log cabin made of stacked round logs, with a sagging plank roof and a dark open doorway.",
}
for name, prompt in JOBS.items():
    print(name, image(key, prompt, "1:1", out, name, tries=5, wait=20)); time.sleep(6)
