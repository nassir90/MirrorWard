import os, sys
from gemini import read_key, image, text
key = read_key(sys.argv[1]); out = sys.argv[2]
def img(name, prompt, ar): print(name, image(key, prompt, ar, out, name, wait=15))
RINGS = ["plain worn gold-coloured band", "band set with one large round gemstone", "square signet ring with a crest", "twisted rope band",
         "band engraved with runes", "ring with a tiny skull", "band set with three small stones in a row", "thin braided band"]
if 'hand' in sys.argv[3:]:
    img("hand_bare", "Detailed greyscale pixel art of a single old weathered human hand seen from the back, fingers pointing up and slightly spread apart, "
          "thumb to the right, bare fingers with NO ring and no jewellery of any kind, wrist fading out at the bottom. Heavy ordered dithering, "
          "high detail like a dithered photograph, crisp pixels, no text. Plain flat solid pure magenta (#FF00FF) background.", "3:4")
if 'rings' in sys.argv[3:]:
    img("rings", "Retro pixel art item icon sheet, crisp hard-edged pixels, no anti-aliasing, no text. Muted greyscale palette only "
          "(near-black, dark grey, mid grey, light grey, off-white). Plain flat solid pure magenta (#FF00FF) background. Exactly 8 separate medieval rings "
          "in ONE horizontal row with wide magenta gaps, each seen at the same three-quarter angle and the same size: " + "; ".join(f"{i+1}) {r}" for i, r in enumerate(RINGS)) + ".", "16:9")
if 'names' in sys.argv[3:]:
    prompt = ("You write item text for a bleak, meditative medieval survival game about a weary traveller. For each of these rings give a short "
              "evocative name (2-3 words) and a one-sentence description under 60 characters, plain and melancholy, no exclamation marks. "
              "Return JSON only: a list of {\"name\":...,\"desc\":...} in the same order.\n" + "\n".join(f"{i+1}. {r}" for i, r in enumerate(RINGS)))
    txt = text(key, prompt, wait=15); open(os.path.join(out, "ring_names.json"), "w").write(txt); print(txt)
