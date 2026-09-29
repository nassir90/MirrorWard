import json, base64, sys, urllib.request, os, concurrent.futures as cf
import os
PROJECT = os.environ["GCP_PROJECT"]
key = open(sys.argv[1]).read().strip(); out = sys.argv[2]
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
URL = "https://aiplatform.googleapis.com/v1/projects/" + PROJECT + "/locations/global/publishers/google/models/gemini-3.1-flash-image:generateContent"
def run(name):
    body = {"contents": [{"role": "user", "parts": [{"text": JOBS[name]}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        return name, "HTTP %d %s" % (e.code, e.read()[:300])
    for p in d["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            ext = p["inlineData"]["mimeType"].split("/")[-1]
            open(os.path.join(out, name + "." + ext), "wb").write(base64.b64decode(p["inlineData"]["data"]))
            return name, "ok " + ext
    return name, "no image: " + json.dumps(d)[:300]
with cf.ThreadPoolExecutor(5) as ex:
    for n, r in ex.map(run, JOBS): print(n, r)
