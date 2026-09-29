import json, base64, sys, urllib.request, urllib.error, os, time
import os
PROJECT = os.environ["GCP_PROJECT"]
key = open(sys.argv[1]).read().strip(); out = sys.argv[2]
BASE = ("Single object only, centred, whole object visible with margin, plain pure white background, soft even studio light, "
        "no ground, no shadow, no text. Realistic 3D clay-render style, clear readable silhouette, three-quarter view from slightly above. ")
JOBS = {
  "cottage_a": BASE + "A small medieval half-timbered cottage with a very steep gabled roof, a stone chimney, small windows and a wooden door.",
  "cottage_b": BASE + "A narrow two-storey medieval timber-framed house with a steep roof, an overhanging upper floor, a side dormer and a chimney.",
  "tower": BASE + "A tall round medieval stone watchtower, rough masonry blocks, crenellated top, a few narrow arrow-slit windows and an arched wooden door at its base.",
  "stone": BASE + "A tall weathered standing stone (menhir), roughly rectangular and slightly leaning, with a deep vertical crack splitting its upper half.",
  "cabin": BASE + "A small rough log cabin made of stacked round logs, with a sagging plank roof and a dark open doorway.",
}
URL = "https://aiplatform.googleapis.com/v1/projects/" + PROJECT + "/locations/global/publishers/google/models/gemini-3.1-flash-image:generateContent"
for name, prompt in JOBS.items():
    for attempt in range(5):
        body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "1:1"}}}
        req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=240))
            for p in d["candidates"][0]["content"]["parts"]:
                if "inlineData" in p:
                    open(os.path.join(out, name + ".png"), "wb").write(base64.b64decode(p["inlineData"]["data"])); print(name, "ok"); break
            break
        except urllib.error.HTTPError as e:
            print(name, "HTTP", e.code); time.sleep(20 * (attempt + 1))
    time.sleep(6)
