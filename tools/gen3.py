import json, base64, sys, urllib.request, urllib.error, os, time
import os
PROJECT = os.environ["GCP_PROJECT"]
key = open(sys.argv[1]).read().strip(); out = sys.argv[2]
BASE = "https://aiplatform.googleapis.com/v1/projects/" + PROJECT + "/locations/global/publishers/google/models/"
def call(model, body):
    for attempt in range(6):
        req = urllib.request.Request(BASE + model + ":generateContent", json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            return json.load(urllib.request.urlopen(req, timeout=240))
        except urllib.error.HTTPError as e:
            print(model, 'HTTP', e.code); time.sleep(15 * (attempt + 1))
    raise SystemExit('gave up')
def image(name, prompt, ar):
    d = call("gemini-3.1-flash-image", {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": ar}}})
    for p in d["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            open(os.path.join(out, name + ".png"), "wb").write(base64.b64decode(p["inlineData"]["data"])); print(name, 'ok'); return
    print(name, 'no image')
RINGS = ["plain worn gold-coloured band", "band set with one large round gemstone", "square signet ring with a crest", "twisted rope band",
         "band engraved with runes", "ring with a tiny skull", "band set with three small stones in a row", "thin braided band"]
if 'hand' in sys.argv[3:]:
    image("hand_bare", "Detailed greyscale pixel art of a single old weathered human hand seen from the back, fingers pointing up and slightly spread apart, "
          "thumb to the right, bare fingers with NO ring and no jewellery of any kind, wrist fading out at the bottom. Heavy ordered dithering, "
          "high detail like a dithered photograph, crisp pixels, no text. Plain flat solid pure magenta (#FF00FF) background.", "3:4")
if 'rings' in sys.argv[3:]:
    image("rings", "Retro pixel art item icon sheet, crisp hard-edged pixels, no anti-aliasing, no text. Muted greyscale palette only "
          "(near-black, dark grey, mid grey, light grey, off-white). Plain flat solid pure magenta (#FF00FF) background. Exactly 8 separate medieval rings "
          "in ONE horizontal row with wide magenta gaps, each seen at the same three-quarter angle and the same size: " + "; ".join(f"{i+1}) {r}" for i, r in enumerate(RINGS)) + ".", "16:9")
if 'names' in sys.argv[3:]:
    prompt = ("You write item text for a bleak, meditative medieval survival game about a weary traveller. For each of these rings give a short "
              "evocative name (2-3 words) and a one-sentence description under 60 characters, plain and melancholy, no exclamation marks. "
              "Return JSON only: a list of {\"name\":...,\"desc\":...} in the same order.\n" + "\n".join(f"{i+1}. {r}" for i, r in enumerate(RINGS)))
    d = call("gemini-2.5-flash", {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}})
    txt = d["candidates"][0]["content"]["parts"][0]["text"]; open(os.path.join(out, "ring_names.json"), "w").write(txt); print(txt)
