import base64, json, os, time, urllib.error, urllib.request

BASE = "https://aiplatform.googleapis.com/v1/projects/%s/locations/global/publishers/google/models/"
RETRY = {429, 500, 502, 503, 504}

def read_key(path):
    return open(path).read().strip()

def call(key, model, body, tries=6, wait=10, timeout=240):
    url = BASE % os.environ["GCP_PROJECT"] + model + ":generateContent"
    for attempt in range(tries):
        req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            return json.load(urllib.request.urlopen(req, timeout=timeout))
        except urllib.error.HTTPError as e:
            if e.code not in RETRY or attempt == tries - 1: raise
            print(model, "HTTP", e.code, "retrying", flush=True); time.sleep(wait * (attempt + 1))

def image(key, prompt, aspect, out, name, model="gemini-3.1-flash-image", **kw):
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}}}
    try:
        d = call(key, model, body, **kw)
    except urllib.error.HTTPError as e:
        return "HTTP %d %s" % (e.code, e.read()[:200])
    for p in d["candidates"][0]["content"].get("parts", []):
        if "inlineData" in p:
            ext = p["inlineData"].get("mimeType", "image/png").split("/")[-1]
            open(os.path.join(out, name + "." + ext), "wb").write(base64.b64decode(p["inlineData"]["data"]))
            return "ok"
    return "no image"

def text(key, prompt, model="gemini-2.5-flash", mime="application/json", **kw):
    d = call(key, model, {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": mime}}, **kw)
    return d["candidates"][0]["content"]["parts"][0]["text"]
