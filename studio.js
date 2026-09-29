
(() => {
  const R = window.__rot, VW = 1080, VH = 1920, FPS = 30, SR = 48000;
  const W = () => R.W(), K = () => R.W().knight, G = () => R.game();
  const gameCanvas = document.querySelector('canvas');
  const comp = document.createElement('canvas'); comp.width = VW; comp.height = VH; const cx = comp.getContext('2d');
  const INK = '#f0e7d4', DIM = '#9d908f', BG = '#0b090b', MID = '#41393e';
  const clear = () => { let n = 0; while (R.dialog() && n++ < 20) R.advance(); };
  const aim = (x, y, z) => { const v = new THREE.Vector3(x, y, z).project(W().cam), r = gameCanvas.getBoundingClientRect(); gameCanvas.dispatchEvent(new MouseEvent('mousemove', { clientX: r.left + (v.x * 0.5 + 0.5) * r.width, clientY: r.top + (1 - (v.y * 0.5 + 0.5)) * r.height })); };
  const once = (st, key, t, at, f) => { if (t >= at && !st[key]) { st[key] = 1; f(); } };
  const img = src => new Promise(res => { const i = new Image(); i.onload = () => res(i); i.onerror = () => res(null); i.src = src; });

  function bg() { cx.fillStyle = BG; cx.fillRect(0, 0, VW, VH); }
  let bgCache = null;
  function base() { if (!bgCache) { bg(); bgCache = cx.getImageData(0, 0, VW, VH); } else cx.putImageData(bgCache, 0, 0); }
  function game(alpha = 1, y = 420) { cx.save(); cx.globalAlpha = alpha; cx.imageSmoothingEnabled = true; cx.drawImage(gameCanvas, 0, y, VW, VW); cx.restore(); }
  function text(s, x, y, font, col = INK, align = 'center', alpha = 1, max = 960) {
    cx.save(); cx.globalAlpha = alpha; cx.font = font; cx.fillStyle = col; cx.textAlign = align; cx.textBaseline = 'middle';
    const words = String(s).split(' '); let line = '', lines = [];
    for (const w of words) { const t = line ? line + ' ' + w : w; if (cx.measureText(t).width > max && line) { lines.push(line); line = w; } else line = t; }
    lines.push(line); const lh = parseInt(font.match(/(\d+)px/)[1]) * 1.18;
    lines.forEach((l, i) => { cx.shadowColor = 'rgba(0,0,0,0.8)'; cx.shadowBlur = 12; cx.fillText(l, x, y + (i - (lines.length - 1) / 2) * lh); });
    cx.restore();
  }
  const BL = n => `${n}px "UnifrakturMaguntia", serif`, PX = n => `${n}px "Pixelify Sans", monospace`, MONO = n => `${n}px Menlo, "SF Mono", monospace`;
  const ease = t => t < 0 ? 0 : t > 1 ? 1 : t * t * (3 - 2 * t);
  const fadeIn = (t, d = 0.35) => ease(t / d);
  function bubble(label, s, y, alpha = 1) {
    cx.save(); cx.globalAlpha = alpha; cx.font = PX(40); const w = Math.min(980, Math.max(cx.measureText(s).width, 400) + 80), x = (VW - w) / 2, lines = Math.ceil(cx.measureText(s).width / 900), h = 110 + (lines - 1) * 48;
    cx.fillStyle = 'rgba(27,22,25,0.94)'; cx.fillRect(x, y, w, h); cx.fillStyle = MID; for (let i = 0; i < w; i += 8) cx.fillRect(x + i, y, 4, 3);
    cx.restore(); text(label, VW / 2, y + 26, PX(26), DIM, 'center', alpha); text(s, VW / 2, y + 70 + (lines - 1) * 24, PX(40), INK, 'center', alpha, 900);
  }

  const shot = (dur, setup, tick, over) => ({ dur, setup, tick: tick || (() => {}), over: over || (() => {}) });
  const cap = (s, y = 1640, size = 64) => (t) => text(s, VW / 2, y, BL(size), INK, 'center', fadeIn(t - 0.2));
  const top = (s, size = 92) => (t) => text(s, VW / 2, 250, BL(size), INK, 'center', fadeIn(t - 0.1));
  const both = (...fs) => (t, d) => fs.forEach(f => f(t, d));
  const S = {};
  S.inscription = (d = 5.5) => shot(d, () => { R.newGame(); clear(); R.walkTo(-1.5, 1.2); }, (t, st) => once(st, 'a', t, 3.0, () => R.act()));
  S.fall = (d = 4.6) => shot(d, () => { R.jump(0, true); clear(); K().pos.set(2.2, 0, 2.9); }, (t, st) => once(st, 'a', t, 0.2, () => R.act()));
  S.ring = (d = 5.2) => shot(d, () => { R.jump(1, true); clear(); const p = W().along(23.5, 0); K().pos.copy(p); const r = W().along(28, 0); R.walkTo(r.x, r.z); },
    (t, st) => { once(st, 'a', t, 2.2, () => R.act()); once(st, 'b', t, 3.4, () => R.advance()); });
  S.wake = (d = 4.6) => shot(d, () => { R.jump(2, true); clear(); const g = G(); g.hp = 55; g.bleed = 30; K().lying = 2.4; }, (t, st) => once(st, 'a', t, 4.2, () => clear()));
  S.dogs = (d = 6.5) => shot(d, () => { R.jump(3, true); clear(); const w = W(), k = K(); G().hp = 100; [5.5, 9].forEach((dx, i) => { const e = w.enemies[i]; e.a.pos.set(k.pos.x + dx, k.pos.y, k.pos.z + (i ? 1.2 : -0.6)); e.home.copy(e.a.pos); e.state = 'chase'; }); },
    (t, st) => { const w = W(), k = K(); const near = w.enemies.filter(e => !e.dead && e.a.pos.distanceTo(k.pos) < 1.5); if (near.length && t - (st.last || 0) > 0.33) { st.last = t; k.flip = near[0].a.pos.clone().sub(k.pos).dot(w.rightH) < 0; R.swing(); } });
  S.snow = (d = 4.2) => shot(d, () => { R.jump(4, true); clear(); const k = K(); R.walkTo(k.pos.x + 8, k.pos.z - 3); });
  S.name = (d = 6.2) => shot(d, () => { R.jump(5, true); clear(); K().pos.set(2.2, 0, 4.2); },
    (t, st) => { once(st, 'a', t, 0.3, () => R.act()); 'Burt'.split('').forEach((ch, i) => once(st, 'k' + i, t, 1.2 + i * 0.28, () => R.key('Key' + ch.toUpperCase()))); once(st, 'e', t, 3.0, () => R.key('Enter')); once(st, 'w', t, 3.3, () => R.walkTo(-3, 6)); });
  S.bury = (d = 6.4) => shot(d, () => { R.jump(5, true); clear(); const g = G(), w = W(); Object.assign(g.flags, { pulled: true, shovel: true }); g.kid = true; g.kidName = 'Burt'; w.kidHome = false; w.kid.pos.set(-4.6, 0, -5.0); K().pos.set(-6.2, 0, -5.4); },
    (t, st) => once(st, 'a', t, 0.3, () => R.act()));
  S.ravens = (d = 6.5) => shot(d, () => { R.jump(6, true); clear(); G().hp = 100; },
    (t, st) => { const w = W(), g = G(); if (t > 0.6 && t - (st.last || 0) > 0.7) { const e = w.enemies.filter(e => !e.dead).sort((a, b) => a.a.pos.distanceTo(K().pos) - b.a.pos.distanceTo(K().pos))[0]; if (e) { st.last = t; aim(e.a.pos.x, e.a.pos.y + e.a.lift + 0.35, e.a.pos.z); g.mana = 100; R.castFire(); } } });
  S.burnTree = (d = 5.5) => shot(d, () => { R.jump(4, true); clear(); const g = G(); g.owned.push(1); g.kid = true; g.kidName = 'Burt'; R.enter('snowfield', 'west'); clear(); },
    (t, st) => { once(st, 'a', t, 0.4, () => { const w = W(), k = K(); let best = 99, q = null; w.sets.filter(S => S.key === 'pine').forEach(S => S.pts.forEach(p => { const dd = Math.hypot(p[0] - k.pos.x, p[1] - k.pos.z); if (dd > 2.5 && dd < best) { best = dd; q = p; } })); aim(q[0], 0.7, q[1]); G().mana = 100; R.castFire(); }); once(st, 'b', t, 2.4, () => clear()); });
  S.houses = (d = 7.5) => shot(d, () => { R.jump(8, true); clear(); const g = G(); g.kidName = 'Burt'; g.housesBurned = 3; const w = W(), h = w.houses.find(h => Math.abs(h.x) < 8); st0.h = h; K().pos.set(h.x - 3.2, 0, h.z + 1.8); w.walk(K().pos); w.kid.pos.copy(K().pos).add(new THREE.Vector3(-1, 0, 0.3)); },
    (t, st) => { once(st, 'a', t, 0.4, () => { aim(st0.h.x, 0.7, st0.h.z); G().mana = 100; R.castFire(); }); once(st, 'b', t, 3.2, () => { const kd = W().kid; R.walkTo(kd.pos.x + 0.9, kd.pos.z); }); once(st, 'c', t, 4.6, () => R.act()); });
  const st0 = {};
  S.lake = (d = 5.5) => shot(d, () => { R.jump(9, true); clear(); K().pos.set(-9.5, 0, 2.5); R.walkTo(-4.5, 1.5); });
  S.city = (d = 4.4) => shot(d, () => { R.jump(7, true); clear(); const k = K(); R.walkTo(k.pos.x + 9, k.pos.z - 1); });
  S.tower = (d = 8) => shot(d, () => { R.jump(10, true); clear(); K().pos.set(0.6, 0, 6.5); W().kid.pos.set(-0.8, 0, 7.2); },
    (t, st) => { once(st, 'a', t, 0.3, () => R.walkTo(0, 4.5)); once(st, 'b', t, 1.4, () => R.act()); once(st, 'c', t, 3.2, () => R.walkTo(0, 4.1)); });
  S.inventory = (d = 7) => shot(d, () => { R.jump(6, true); clear(); R.rings.equip(2, 0.35, 0); R.inv(true); },
    (t, st) => { once(st, 'a', t, 2.0, () => { G().wield = false; R.inv(true); }); once(st, 'b', t, 3.3, () => { G().wield = true; R.inv(true); }); once(st, 'c', t, 4.4, () => R.key('KeyH')); once(st, 'd', t, 5.6, () => { R.rings.equip(0, 0.45, 1); }); });
  S.gallery = (d = 6) => shot(d, () => { R.jump(11); },
    (t, st) => [[3, 0.3, 4], [2, 0.2, 5], [0, 0.35, 6], [3, 0.55, 7], [4, 0.4, 8], [2, 0.5, 9]].forEach(([f, s, r], i) => once(st, 'r' + i, t, 0.6 + i * 0.8, () => R.rings.equip(f, s, r))));
  S.dither = (d = 5) => Object.assign(shot(d, () => { R.jump(4, true); clear(); R.walkTo(K().pos.x + 6, K().pos.z - 2); },
    (t, st) => { const on = Math.floor(t / 0.9) % 2 === 0, btn = document.getElementById('ditherBtn'); if ((btn.getAttribute('aria-pressed') === 'true') !== on) btn.click(); }),
    { after: () => { const btn = document.getElementById('ditherBtn'); if (btn.getAttribute('aria-pressed') !== 'true') btn.click(); } });
  S.sun = (d = 5) => Object.assign(shot(d, () => { R.jump(9, true); clear(); const b = document.getElementById('spinBtn'); if (b.getAttribute('aria-pressed') !== 'true') b.click(); }),
    { after: () => { const b = document.getElementById('spinBtn'); if (b.getAttribute('aria-pressed') === 'true') b.click(); } });

  const slide = (dur, draw) => ({ dur, slide: true, setup: () => {}, tick: () => {}, over: draw });
  const fit = (s, size) => { cx.font = BL(size); while (cx.measureText(s).width > 960 && size > 40) cx.font = BL(size -= 6); return size; };
  const titleCard = (a, b, c) => slide(3, t => { text(a, VW / 2, VH / 2 - 60, BL(fit(a, 150)), INK, 'center', fadeIn(t), 2000); if (b) text(b, VW / 2, VH / 2 + 90, PX(44), DIM, 'center', fadeIn(t - 0.5)); if (c) text(c, VW / 2, VH / 2 + 160, PX(34), DIM, 'center', fadeIn(t - 0.9)); });
  let IM = {};
  const pipeline = (rawKey, outKey, label, frames = 1) => slide(3.4, t => {
    const a = IM[rawKey], b = IM[outKey]; text(label, VW / 2, 250, BL(78), INK, 'center', fadeIn(t));
    if (a) { const s = Math.min(900 / a.width, 560 / a.height); cx.globalAlpha = fadeIn(t - 0.2); cx.drawImage(a, (VW - a.width * s) / 2, 420, a.width * s, a.height * s); cx.globalAlpha = 1; text('Gemini image', VW / 2, 1010, PX(34), DIM, 'center', fadeIn(t - 0.2)); }
    text('\u2193', VW / 2, 1080, PX(64), INK, 'center', fadeIn(t - 1.0));
    if (b) { cx.imageSmoothingEnabled = false; const sw = b.width * Math.min(1, 4 / frames), k = Math.min(1000 / sw, 460 / b.height); cx.globalAlpha = fadeIn(t - 1.2); cx.drawImage(b, 0, 0, sw, b.height, (VW - sw * k) / 2, 1160 + (460 - b.height * k) / 2, sw * k, b.height * k); cx.globalAlpha = 1; cx.imageSmoothingEnabled = true; text('palette-locked game sprite', VW / 2, 1690, PX(34), DIM, 'center', fadeIn(t - 1.2)); }
  });
  const CODE = [
    '// vegetation shivers in whole pixels near anything moving',
    'for (int i = 0; i < 6; i++)',
    '  amp += uMov[i].w * (1.0 - smoothstep(0.25,',
    '         0.5 + sx * 0.55, length(uMov[i].xz - org.xz)));',
    'float off = floor(amp * 1.7 * sin(uRT * 15.0',
    '         + ph + band * 4.0) * (0.2 + band) + 0.5);',
    'transformed.x += off * uPx / sx;'];
  const codeSlide = (label) => slide(4, t => {
    text(label, VW / 2, 250, BL(78), INK, 'center', fadeIn(t));
    cx.fillStyle = 'rgba(27,22,25,0.95)'; cx.fillRect(40, 520, 1000, 560);
    const n = Math.floor(clamp01((t - 0.3) / 2.4) * CODE.join('\n').length); let used = 0;
    CODE.forEach((l, i) => { const show = l.slice(0, Math.max(0, n - used)); used += l.length + 1; text(show, 70, 590 + i * 70, MONO(25), i ? INK : DIM, 'left', 1, 2000); });
    text('three.js \u00b7 custom dither + CRT shaders', VW / 2, 1200, PX(40), DIM, 'center', fadeIn(t - 0.8));
  });
  const clamp01 = v => Math.max(0, Math.min(1, v));
  const grid = (label, keys) => slide(3.6, t => {
    text(label, VW / 2, 250, BL(78), INK, 'center', fadeIn(t));
    keys.forEach((k, i) => { const im = IM[k]; if (!im) return; const c = i % 2, r = Math.floor(i / 2), x = 120 + c * 430, y = 400 + r * 430; cx.globalAlpha = fadeIn(t - 0.2 - i * 0.18); cx.drawImage(im, x, y, 410, 410); cx.globalAlpha = 1; });
    text('scripted runs, stone to tower', VW / 2, 1720, PX(40), DIM, 'center', fadeIn(t - 1.2));
  });

  const mtof = m => 440 * Math.pow(2, (m - 69) / 12);
  const THEMES = {

    story: { bpm: 72, lead: [[62,1],[65,1],[69,1],[67,1.5],[65,0.5],[64,1],[62,2],[60,1],[62,1],[64,1],[65,1.5],[64,0.5],[62,1],[69,2],[72,1],[71,1],[69,1],[67,1],[65,1.5],[64,0.5],[62,3]], bass: [38, 36, 34, 36], chords: [[62,65,69],[60,64,67],[58,62,65],[60,64,67]], drum: 'slow' },

    jig: { bpm: 132, lead: [[62,.5],[64,.5],[65,.5],[69,.5],[65,.5],[64,.5],[62,.5],[69,.5],[74,.5],[72,.5],[69,.5],[67,.5],[65,.5],[67,.5],[69,.5],[65,.5],[64,.5],[62,.5],[60,.5],[62,.5],[64,.5],[62,1.5],[69,.5],[71,.5],[72,.5],[74,1],[72,.5],[71,.5],[69,.5],[67,.5],[65,1],[64,.5],[62,1.5]], bass: [38, 38, 36, 36], chords: [[62,65,69],[62,65,69],[60,64,67],[60,64,67]], drum: 'jig' },

    make: { bpm: 100, lead: [[74,1],[72,.5],[69,.5],[67,1],[69,1],[65,1],[64,.5],[62,.5],[64,2],[69,1],[72,1],[71,.5],[69,.5],[67,1],[65,1],[64,1],[62,2]], bass: [38, 36, 34, 36], chords: [[62,65,69],[60,64,67],[58,62,65],[60,64,67]], drum: 'soft', arp: true }
  };
  async function music(themeName, dur) {
    const th = THEMES[themeName], ctx = new OfflineAudioContext(2, Math.ceil(dur * SR), SR), out = ctx.createGain(); out.gain.value = 0.9;
    const comp2 = ctx.createDynamicsCompressor(); out.connect(comp2); comp2.connect(ctx.destination);
    const beat = 60 / th.bpm, bar = beat * (th.drum === 'jig' ? 3 : 4);
    const rev = ctx.createConvolver(); { const n = SR * 1.8, b = ctx.createBuffer(2, n, SR); for (let c = 0; c < 2; c++) { const d = b.getChannelData(c); for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, 3); } rev.buffer = b; }
    const wet = ctx.createGain(); wet.gain.value = 0.25; rev.connect(wet); wet.connect(out);
    const voice = (type, f, t0, d, g, cutoff, send = 0.5) => {
      const o = ctx.createOscillator(), a = ctx.createGain(), lp = ctx.createBiquadFilter(); o.type = type; o.frequency.value = f; lp.type = 'lowpass'; lp.frequency.value = cutoff;
      a.gain.setValueAtTime(0, t0); a.gain.linearRampToValueAtTime(g, t0 + 0.012); a.gain.exponentialRampToValueAtTime(Math.max(1e-4, g * 0.35), t0 + d * 0.7); a.gain.exponentialRampToValueAtTime(1e-4, t0 + d + 0.08);
      o.connect(lp); lp.connect(a); a.connect(out); const s = ctx.createGain(); s.gain.value = send; a.connect(s); s.connect(rev); o.start(t0); o.stop(t0 + d + 0.1); return o;
    };
    const pluck = (f, t0, g) => { const o = ctx.createOscillator(), a = ctx.createGain(), lp = ctx.createBiquadFilter(); o.type = 'sawtooth'; o.frequency.value = f; lp.type = 'lowpass'; lp.frequency.setValueAtTime(3200, t0); lp.frequency.exponentialRampToValueAtTime(400, t0 + 0.35); a.gain.setValueAtTime(g, t0); a.gain.exponentialRampToValueAtTime(1e-4, t0 + 0.6); o.connect(lp); lp.connect(a); a.connect(out); const s = ctx.createGain(); s.gain.value = 0.6; a.connect(s); s.connect(rev); o.start(t0); o.stop(t0 + 0.65); };
    const noise = (() => { const b = ctx.createBuffer(1, SR, SR), d = b.getChannelData(0); for (let i = 0; i < SR; i++) d[i] = Math.random() * 2 - 1; return b; })();
    const drum = (t0, g) => { const o = ctx.createOscillator(), a = ctx.createGain(); o.frequency.setValueAtTime(110, t0); o.frequency.exponentialRampToValueAtTime(45, t0 + 0.18); a.gain.setValueAtTime(g, t0); a.gain.exponentialRampToValueAtTime(1e-4, t0 + 0.3); o.connect(a); a.connect(out); o.start(t0); o.stop(t0 + 0.32);
      const n = ctx.createBufferSource(), bp = ctx.createBiquadFilter(), na = ctx.createGain(); n.buffer = noise; bp.type = 'bandpass'; bp.frequency.value = 180; na.gain.setValueAtTime(g * 0.6, t0); na.gain.exponentialRampToValueAtTime(1e-4, t0 + 0.12); n.connect(bp); bp.connect(na); na.connect(out); n.start(t0); n.stop(t0 + 0.14); };
    const tamb = (t0, g) => { const n = ctx.createBufferSource(), hp = ctx.createBiquadFilter(), a = ctx.createGain(); n.buffer = noise; hp.type = 'highpass'; hp.frequency.value = 6000; a.gain.setValueAtTime(g, t0); a.gain.exponentialRampToValueAtTime(1e-4, t0 + 0.09); n.connect(hp); hp.connect(a); a.connect(out); n.start(t0, Math.random() * 0.5); n.stop(t0 + 0.1); };

    [38, 45].forEach(m => { const o = ctx.createOscillator(), lp = ctx.createBiquadFilter(), a = ctx.createGain(); o.type = 'sawtooth'; o.frequency.value = mtof(m); lp.type = 'lowpass'; lp.frequency.value = 420; a.gain.setValueAtTime(0, 0); a.gain.linearRampToValueAtTime(0.05, 1.2); a.gain.setValueAtTime(0.05, Math.max(1.3, dur - 1.2)); a.gain.linearRampToValueAtTime(0, dur); o.connect(lp); lp.connect(a); a.connect(out); o.start(0); o.stop(dur); });

    for (let t = 0, b = 0; t < dur; t += bar, b++) {
      voice('triangle', mtof(th.bass[b % th.bass.length]), t, bar * 0.95, 0.22, 900, 0.2);
      const ch = th.chords[b % th.chords.length];
      if (th.arp) for (let i = 0; i < 8; i++) pluck(mtof(ch[i % 3] + (i >= 3 && i < 6 ? 12 : 0)), t + i * bar / 8, 0.07);
      else ch.forEach((m, i) => pluck(mtof(m), t + i * 0.03, 0.06));
      const beats = th.drum === 'jig' ? 6 : 4, step = bar / beats;
      for (let i = 0; i < beats; i++) {
        if (th.drum === 'jig') { if (i === 0 || i === 3) drum(t + i * step, 0.5); tamb(t + i * step, i % 3 === 1 ? 0.08 : 0.04); }
        else if (th.drum === 'slow') { if (i === 0) drum(t, 0.45); if (i === 2) drum(t + i * step, 0.25); }
        else { if (i % 2 === 0) drum(t + i * step, 0.25); tamb(t + i * step + step / 2, 0.03); }
      }
    }
    const lead0 = th.drum === 'slow' ? bar : 0;
    for (let t = lead0, i = 0; t < dur - 0.3; i++) { const [m, bt] = th.lead[i % th.lead.length], d = bt * beat; const o = voice('square', mtof(m), t, d * 0.92, 0.07, 2400, 0.5); o.detune.setValueAtTime(0, t); t += d; }
    const master = ctx.createGain();
    out.gain.setValueAtTime(0.9, Math.max(0, dur - 1.5)); out.gain.linearRampToValueAtTime(0, dur);
    return ctx.startRendering();
  }

  async function record(name, shots, themeName, badge) {
    await document.fonts.load(BL(80)); await document.fonts.load(PX(40));
    IM.kidRaw = IM.kidRaw || await img('sprites/raw4/kid.png'); IM.kidOut = IM.kidOut || await img('sprites/out4/kid14.png');
    IM.handRaw = IM.handRaw || await img('sprites/raw4/hand_sword.png'); IM.handOut = IM.handOut || await img('sprites/out4/hand_sword_x3.png');
    IM.dogRaw = IM.dogRaw || await img('sprites/raw4/gallop.png'); IM.dogOut = IM.dogOut || await img('sprites/out4/dog_gallop.png');
    for (const k of ['g_01_stone', 'g_08_fight', 'g_15_tug', 'g_20_fire', 'g_24_village', 'g_29_end']) IM[k] = IM[k] || await img('docs/playtest/' + k + '.jpg');
    const dur = shots.reduce((a, s) => a + s.dur, 0);
    const target = new Mp4Muxer.ArrayBufferTarget();
    const mux = new Mp4Muxer.Muxer({ target, video: { codec: 'avc', width: VW, height: VH }, audio: { codec: 'aac', numberOfChannels: 2, sampleRate: SR }, fastStart: 'in-memory' });
    const ve = new VideoEncoder({ output: (c, m) => mux.addVideoChunk(c, m), error: e => { throw e; } });
    ve.configure({ codec: 'avc1.640028', width: VW, height: VH, bitrate: 9e6, framerate: FPS });
    let f = 0;
    for (const sh of shots) {
      const st = {}; sh.setup(st); if (!sh.slide && G().kidName) G().kidName = 'Burt';
      const n = Math.round(sh.dur * FPS);
      for (let i = 0; i < n; i++, f++) {
        const t = i / FPS; sh.tick(t, st);
        if (!sh.slide) R.run(1 / FPS);
        base(); if (!sh.slide) game(1); sh.over(t, sh.dur);
        if (badge) { cx.fillStyle = 'rgba(27,22,25,0.85)'; cx.fillRect(VW / 2 - 250, 1800, 500, 64); text('Made by Claude Opus 5.5', VW / 2, 1832, PX(36), INK, 'center', 1); }
        const edge = Math.min(i, n - 1 - i); if (edge < 6) { cx.fillStyle = `rgba(11,9,11,${1 - edge / 6})`; cx.fillRect(0, 0, VW, VH); }
        const vf = new VideoFrame(comp, { timestamp: Math.round(f * 1e6 / FPS), duration: Math.round(1e6 / FPS) });
        ve.encode(vf, { keyFrame: f % 60 === 0 }); vf.close();
        while (ve.encodeQueueSize > 4) await new Promise(r => setTimeout(r, 2));
      }
      if (sh.after) sh.after();
    }
    await ve.flush();
    const buf = await music(themeName, dur);
    const ae = new AudioEncoder({ output: (c, m) => mux.addAudioChunk(c, m), error: e => { throw e; } });
    ae.configure({ codec: 'mp4a.40.2', sampleRate: SR, numberOfChannels: 2, bitrate: 192000 });
    const L = buf.getChannelData(0), Rr = buf.getChannelData(1), CH = 1024;
    for (let i = 0; i < buf.length; i += CH) {
      const n = Math.min(CH, buf.length - i), data = new Float32Array(n * 2); data.set(L.subarray(i, i + n), 0); data.set(Rr.subarray(i, i + n), n);
      const ad = new AudioData({ format: 'f32-planar', sampleRate: SR, numberOfFrames: n, numberOfChannels: 2, timestamp: Math.round(i / SR * 1e6), data }); ae.encode(ad); ad.close();
    }
    await ae.flush(); mux.finalize();
    const res = await fetch('/save?name=' + name + '.mp4', { method: 'POST', body: new Blob([target.buffer], { type: 'video/mp4' }) });
    return { name, seconds: +dur.toFixed(1), bytes: target.buffer.byteLength, saved: await res.text() };
  }

  const V = {

    promo_story: () => [titleCard('Mirror Ward', 'a dithered pilgrimage'),
      Object.assign(S.inscription(), { over: cap('Read the stone.') }), Object.assign(S.fall(), { over: cap('Descend.') }),
      Object.assign(S.ring(), { over: cap('Find the ring.') }), Object.assign(S.wake(), { over: cap('Wake beside the abyss.') }),
      Object.assign(S.name(), { over: cap('Name the boy.') }), Object.assign(S.bury(), { over: cap('Bury the dead.') }), Object.assign(S.lake(), { over: cap('See yourself.') }),
      Object.assign(S.tower(), { over: cap('Reach the tower.') }), titleCard('Mirror Ward')],

    promo_combat: () => [titleCard('Mirror Ward', 'steel \u00b7 fire \u00b7 grief'),
      Object.assign(S.dogs(), { over: top('Steel.') }), Object.assign(S.ravens(), { over: top('Fire.') }),
      Object.assign(S.burnTree(), { over: top('Everything burns.') }), Object.assign(S.houses(), { over: top('He is watching.') }),
      titleCard('Mirror Ward')],

    promo_rings: () => [titleCard('Mirror Ward', 'every ring, any finger'),
      Object.assign(S.inventory(), { over: top('Your hand.') }), Object.assign(S.gallery(), { over: top('Ten rings.') }),
      Object.assign(S.snow(), { over: top('One colour: red.') }), titleCard('Mirror Ward')],

    claude_pipeline: () => [titleCard('Opus 5.5', 'from a source game\'s art style', 'to a playable game'),
      Object.assign(S.dither(), { over: both(top('1. Study the style', 76), cap('dither \u00b7 CRT \u00b7 one colour', 1680, 54)) }),
      codeSlide('2. Write the engine'),
      pipeline('kidRaw', 'kidOut', '3. Generate the art', 14), pipeline('dogRaw', 'dogOut', '\u2026and animate it', 5),
      Object.assign(S.sun(), { over: both(top('4. Light it', 76), cap('sprites that stand, cast and receive shadow', 1680, 44)) }),
      Object.assign(S.dogs(5), { over: both(top('5. Write the game', 76), cap('11 areas \u00b7 combat \u00b7 a companion \u00b7 a story', 1680, 44)) }),
      grid('6. Playtest it itself', ['g_01_stone', 'g_08_fight', 'g_15_tug', 'g_20_fire', 'g_24_village', 'g_29_end']),
      titleCard('Claude Opus 5.5', 'built in one Claude Code session', '~1,900 lines \u00b7 28 generated images \u00b7 138 sprite frames')],

    claude_requests: () => {
      const req = (s, shotObj) => Object.assign(shotObj, { over: (t) => bubble('you asked', s, 150, fadeIn(t)) });
      return [titleCard('You describe it.', 'Opus 5.5 builds it.'),
        req('"Dogs should gallop, not walk."', S.dogs(5)),
        req('"Fire should shoot where the mouse points."', S.ravens(5.5)),
        req('"Show my rings on the inventory hand."', S.inventory(6)),
        req('"Burn more than three houses and Burt sits down and cries."', S.houses(7.5)),
        req('"Let me name the boy."', S.name(5.5)),
        req('"Put the standing stone in the middle of a lake where you can see your reflection."', S.lake(6)),
        titleCard('Claude Opus 5.5', 'a custom game, derived from a source game', 'one request at a time')];
    }
  };
  window.STUDIO = { record, V, music, S, status: {} };
  window.STUDIO.run = (name, theme) => { const st = window.STUDIO.status[name] = { state: 'running' }; R.pause(true);
    record(name, V[name](), theme, name.startsWith('claude')).then(r => Object.assign(st, { state: 'done' }, r)).catch(e => Object.assign(st, { state: 'error', error: String(e && e.stack || e) })); return st; };
})();
