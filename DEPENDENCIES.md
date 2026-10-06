# Dependencies

## The game (`index.html`)

| Dependency | Version | Loaded from | Notes |
|---|---|---|---|
| three.js | r128 | cdnjs | Current release is r186. r128 works and every scene is tuned against it. Upgrading is a project, not a bump: r152 turned colour management on by default, which would shift the palette, and light intensities changed in r155. Re-check the baseline takes frame by frame if you upgrade. |
| Pixelify Sans, UnifrakturMaguntia | — | Google Fonts | HUD and titles. |

Everything else in the game is its own code: the CRT and dither shaders, the deterministic `mulberry32` RNG, value noise, the sprite sheets (embedded as data URIs).

## Deploy

| Dependency | Version | Notes |
|---|---|---|
| wrangler | ^4.144.0 (4.148.0 available) | `npm run deploy`. `worker.js` only strips the `/games/mirrorward` prefix before serving `dist/`. |

## Video maker (`video-maker.html`, `studio.js`)

| Dependency | Version | Loaded from | Notes |
|---|---|---|---|
| mp4-muxer | 5.1.3 | jsDelivr | Deprecated by its author in favour of **Mediabunny** (same author, actively maintained). |

## Asset tools (`tools/`)

| Dependency | Version | Notes |
|---|---|---|
| numpy | >= 2.0 | `tools/requirements.txt` |
| Pillow | >= 11.0 | `tools/requirements.txt` |
| Gemini on Vertex AI | REST | `tools/gemini.py`; needs `GCP_PROJECT` and a key file. |
| AVFoundation, AppKit | macOS | `tools/frames.swift` |

## Reimplemented here, with maintained alternatives

| Ours | Alternative | Recommendation |
|---|---|---|
| `clamp`, `smoothstep` in the game | `THREE.MathUtils.clamp` / `smoothstep` | Optional; ours are one line each. |
| Value noise / `fbm` | `simplex-noise` (npm) | Keep ours: scenes are laid out against its exact output. |
| Manual post-processing chain (low-res target, CRT pass) | three.js `EffectComposer` | Keep ours: it is two passes and pixel-exact. |
| `tools/gemini.py` (urllib + retry) | `google-genai` SDK + `tenacity` | Worth it if the tools grow; today it is 40 lines and has no dependencies. |
| `blobs()` flood fill in `tools/process2.py` | `scipy.ndimage.label` | Much faster; adds SciPy. Only matters when re-processing sprite sheets. |
| `mp4-muxer` | Mediabunny | Migrate when the video maker is next touched. |
| `worker.js` prefix router | Workers static assets alone, with `dist/games/mirrorward/` as the layout | Removes the worker; the route and URL stay the same. |
