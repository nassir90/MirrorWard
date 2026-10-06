import sys, concurrent.futures as cf
from gemini import read_key, image
key = read_key(sys.argv[1]); out = sys.argv[2]
only = set(sys.argv[3:])
STYLE = ("Retro pixel art game asset sheet, crisp hard-edged pixels, no anti-aliasing, no text, no labels, no grid, "
         "no ground shadows, no ground plane. Muted greyscale palette only (near-black outlines, dark grey, mid grey, light grey, "
         "off-white), bleak medieval winter mood. Plain flat solid pure magenta (#FF00FF) background filling the whole image. "
         "All items in ONE horizontal row, evenly spaced with wide clear magenta gaps, bottoms aligned on the same baseline. ")
TOPDOWN = "Each item drawn in a 3/4 top-down view, as seen from a high isometric game camera. "
JOBS = {
    "deadtrees": STYLE + "Exactly 4 separate bare, leafless, gnarled dead winter trees of different heights and shapes, twisted branches, dark bark.",
    "birches": STYLE + "Exactly 5 separate items: 3 bare silver birch trees with pale bark and dark marks, 1 broken tree stump, 1 short fallen log.",
    "shrubs": STYLE + "Exactly 5 separate low winter shrubs and heather clumps of different shapes, some dusted with snow.",
    "grass": STYLE + "Exactly 6 separate small ground plants: dry grass tuft, tall reeds, thistle, bracken fern, bare twigs, snowy weed clump.",
    "houses": STYLE + TOPDOWN + "Exactly 3 separate medieval half-timbered cottages with steep snow-covered roofs, dark timber frames, small dark windows, a chimney.",
    "hut": STYLE + TOPDOWN + "Exactly 1 small rough wooden log cabin with a sagging dark roof and a dark doorway.",
    "fire": STYLE.replace("Muted greyscale palette only (near-black outlines, dark grey, mid grey, light grey, off-white)",
                          "Greyscale only: white-hot white and pale grey flames with dark grey smoke") +
            "Exactly 4 animation frames of a tall roaring bonfire flame, each frame a slightly different flicker, same size.",
    "stones": STYLE + TOPDOWN + "Exactly 3 separate tall weathered standing stones (menhirs), rough and cracked, one split down its face.",
    "ruins": STYLE + TOPDOWN + "Exactly 4 separate ruined grey stone buildings of a bleak cliff-top town: blocky, broken roofs, dark window holes, one tall tower.",
    "props": STYLE + TOPDOWN + "Exactly 6 separate small props: wooden hand cart, short wooden fence section, barrel, stone well, old gravestone, lantern on a post.",
    "crowflap": STYLE + "A single black crow in flight seen from the side, facing right. Exactly 4 animation frames of one wingbeat, "
                "same body size and position in every frame: 1) wings raised high above the body, 2) wings level and spread, "
                "3) wings pushed down below the body, 4) wings half folded mid-recovery.",
    "hand": ("Detailed greyscale pixel art of a single old weathered human hand seen from the back, fingers pointing up and slightly spread, "
             "thumb to the right, a plain worn ring on the second finger from the left, wrist fading out at the bottom. Heavy ordered dithering, "
             "high detail like a dithered photograph, crisp pixels, no text. Plain flat solid pure magenta (#FF00FF) background."),
}
names = [n for n in JOBS if not only or n in only]
with cf.ThreadPoolExecutor(6) as ex:
    for n, r in zip(names, ex.map(lambda n: image(key, JOBS[n], "3:4" if n == "hand" else "16:9", out, n), names)):
        print(n, r)
