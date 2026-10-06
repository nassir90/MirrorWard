import sys, concurrent.futures as cf
from gemini import read_key, image
key = read_key(sys.argv[1]); out = sys.argv[2]; only = set(sys.argv[3:])
STYLE = ("Retro pixel art game asset sheet, crisp hard-edged pixels, no anti-aliasing, no text, no labels, no grid, "
         "no ground shadows, no ground plane. Muted greyscale palette only (near-black, dark grey, mid grey, light grey, "
         "off-white), bleak medieval winter mood. Plain flat solid pure magenta (#FF00FF) background filling the whole image. ")
ROW = "All items in ONE horizontal row, evenly spaced with wide clear magenta gaps, bottoms aligned on the same baseline. "
HAND = ("Detailed greyscale pixel art of a single old weathered human right hand and forearm seen from the side, the arm hanging straight down "
        "from the top edge of the image so the forearm is cut off at the top. Heavy ordered dithering, high detail like a dithered photograph, "
        "crisp pixels, no text, no ring. Plain flat solid pure magenta (#FF00FF) background. ")
JOBS = {
  "gallop": (STYLE + ROW + "A gaunt, dark, feral wild dog with a long snout, seen exactly from the side facing right. Exactly 4 frames of one full-speed "
             "GALLOP cycle (not a walk or trot), same dog, same size, each frame clearly different: 1) fully stretched out in mid-air, front legs "
             "reaching far forward and hind legs kicked far back, no feet touching the ground; 2) front feet striking the ground, body starting to "
             "compress; 3) fully gathered in mid-air, all four legs bunched together under the belly, back strongly arched; 4) hind legs planted "
             "and pushing off, front legs lifting forward.", "16:9"),
  "hand_idle": (HAND + "The hand hangs down relaxed and empty, fingers loosely curled, holding nothing.", "9:16"),
  "hand_sword": (HAND + "The hand grips the hilt of a plain medieval longsword; the sword hangs straight down from the fist, blade pointing to the ground, "
                 "the whole sword visible below the hand.", "9:16"),
  "kid": (STYLE + ROW + "A single small peasant boy of about eight years old, messy hair, ragged dark tunic, bare legs and worn boots, "
          "seen from the side facing right. Exactly 4 frames of a walk cycle, all the same size.", "16:9"),
  "dog": (STYLE + ROW + "A gaunt, dark, feral wild dog with a long snout, seen from the side facing right. Exactly 5 separate items: "
          "frames 1-4 are a running gallop cycle of the same dog at the same size; item 5 is the same dog lying dead on its side.", "16:9"),
  "bodies": (STYLE + ROW + "Exactly 2 separate dead figures lying flat on their backs on the ground, seen from the side, heads to the left, "
             "arms at their sides, eyes closed: 1) a peasant woman in a long dark dress and pale shawl, 2) a young boy in a ragged tunic.", "16:9"),
  "sword": (STYLE.replace("Retro pixel art game asset sheet", "Detailed retro pixel art game item icon") +
            "Exactly 1 medieval longsword, large, vertical, point up, filling the image height: straight double-edged steel blade with a "
            "dark fuller, simple crossguard, leather-wrapped grip, round pommel. Soft shading from light to dark, no black outline.", "9:16"),
  "shovel": (STYLE + ROW + "Exactly 2 separate items: 1) an old grave-digger's shovel with a long wooden handle and a worn iron blade, "
             "standing upright; 2) a rough wooden grave cross made of two lashed branches.", "16:9"),
  "rings2": (STYLE + ROW + "Exactly 2 separate finger rings, each in a 3/4 view like a game inventory icon, soft shading, no black outline: "
             "1) the Ring of Knowledge: a plain pale silver band with a small engraved open eye on its face; "
             "2) the Ring of Fire: a dark iron band holding a small flame-shaped setting on top.", "16:9"),
}
names = [n for n in JOBS if not only or n in only]
with cf.ThreadPoolExecutor(3) as ex:
    for n, r in zip(names, ex.map(lambda n: image(key, JOBS[n][0], JOBS[n][1], out, n), names)): print(n, r, flush=True)
