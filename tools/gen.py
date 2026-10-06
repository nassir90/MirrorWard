import sys, concurrent.futures as cf
from gemini import read_key, image
key = read_key(sys.argv[1]); out = sys.argv[2]
STYLE = ("Retro pixel art sprite sheet, crisp hard-edged pixels, no anti-aliasing, no text, no labels, no grid lines, no shadows on the ground. "
         "Muted greyscale palette only (near-black outlines, dark grey, mid grey, light grey, off-white), bleak medieval winter mood. "
         "Plain flat solid pure magenta (#FF00FF) background filling the whole image. ")
JOBS = {
  "knight": STYLE + "A single armoured knight in a great helm with a dark cloak and a sword, seen from the side facing right. "
            "Exactly 4 frames of a walk cycle in one horizontal row, evenly spaced with clear magenta gaps between frames, all the same size and aligned at the feet.",
  "pilgrim": STYLE + "A single hooded pilgrim in long pale ragged robes holding a wooden staff, seen from the side facing right. "
            "Exactly 4 frames of a slow walk cycle in one horizontal row, evenly spaced with clear magenta gaps, same size, aligned at the feet.",
  "crow": STYLE + "A black crow seen from the side facing right. Exactly 3 frames in one horizontal row with clear magenta gaps: "
            "1) standing, 2) head down pecking the ground, 3) wings spread in flight.",
  "pine": STYLE + "Three separate snow-dusted dark pine trees of different heights side by side in one row with clear magenta gaps, each with a short trunk.",
  "roses": STYLE.replace("Muted greyscale palette only (near-black outlines, dark grey, mid grey, light grey, off-white)",
            "Dark grey-green foliage with vivid blood-red roses as the ONLY colour") +
            "Four separate small low rose bushes in one horizontal row with clear magenta gaps, each dotted with several small red blooms.",
}
with cf.ThreadPoolExecutor(5) as ex:
    for n, r in zip(JOBS, ex.map(lambda n: image(key, JOBS[n], "16:9", out, n), JOBS)): print(n, r)
