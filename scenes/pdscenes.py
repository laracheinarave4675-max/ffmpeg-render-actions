"""Vertical 9:16 scenes (720x1280) for the Short 'A Planet Born From a Dead Star' (white dwarf HS 0209+0832). Ids y01..y08.
All scenes are original illustrations/simulations (labelled); niobium line positions are taken from Williams et al., Nature Astronomy 2026 (Extended Data Table 2)."""
from frscenes import *
_Y, _X = np.mgrid[0:H, 0:W].astype(np.float32)
_GCOL = [(170, 200, 255), (255, 255, 255), (255, 200, 150)]

def sphere(cx, cy, R, L, ca, cb, t, bands=8.0, spin=0.2, dark=0.03, rim=(0.5, 0.7, 1.0), gran=0.0):
    x0, x1 = int(max(cx - R - 2, 0)), int(min(cx + R + 3, W)); y0, y1 = int(max(cy - R - 2, 0)), int(min(cy + R + 3, H))
    if x1 <= x0 or y1 <= y0: return None
    nx = (_X[y0:y1, x0:x1] - cx) / R; ny = (_Y[y0:y1, x0:x1] - cy) / R; r2 = nx ** 2 + ny ** 2
    m = (r2 < 1.0).astype(np.float32); nz = np.sqrt(np.clip(1 - r2, 0, 1))
    Ld = np.array(L, np.float32); Ld /= np.linalg.norm(Ld)
    dif = np.clip(nx * Ld[0] + ny * Ld[1] + nz * Ld[2], 0, 1)
    lon = np.arctan2(nx, nz) + spin * t
    b = np.sin(ny * bands + 0.8 * np.sin(lon * 3 + ny * 4) + 0.4 * np.sin(lon * 7 - ny * 2 + t))
    tone = (0.5 + 0.5 * b)[..., None]
    col = np.array(ca, np.float32) * (1 - tone) + np.array(cb, np.float32) * tone
    if gran: col = col * (1 + gran * (np.sin(lon * 14 + ny * 11 + t) * np.sin(ny * 17 - lon * 9 + t * 0.7)))[..., None]
    out = col * (dark + (dif ** 0.9) * (1 - dark))[..., None]
    out += np.array(rim, np.float32) * (((1 - nz) ** 3) * dif * 0.8)[..., None]
    return out, m, (y0, y1, x0, x1)
def paste(img, sp, a=1.0):
    if sp is None: return
    o, m, (y0, y1, x0, x1) = sp; mm = (m * a)[..., None]
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - mm) + o * mm
def star(img, cx, cy, R, k, t):  # k: 0 sun-like yellow-white .. 1 red giant
    ca = lerpc((1.0, 0.92, 0.6), (1.0, 0.42, 0.14), k); cb = lerpc((1.0, 0.72, 0.30), (0.75, 0.16, 0.05), k)
    o = sphere(cx, cy, R, (0, 0, 1), ca, cb, t, bands=3.0, spin=0.15, dark=0.55, rim=(1.0, 0.6, 0.3), gran=0.10 + 0.10 * k)
    if o is not None:
        s, m, box = o; y0, y1, x0, x1 = box
        nz = np.sqrt(np.clip(1 - ((_X[y0:y1, x0:x1] - cx) / R) ** 2 - ((_Y[y0:y1, x0:x1] - cy) / R) ** 2, 0, 1))
        s = np.array(ca, np.float32) * (0.42 + 0.58 * nz[..., None]) * (1 + 0.14 * (s.mean(axis=2, keepdims=True) - 0.5))
        paste(img, (s * 1.25, m, box))
def wd(c, cx, cy, a=1.0, s=1.0):
    c.blob(cx, cy, 46 * s, (170, 205, 255), 0.7 * a); c.blob(cx, cy, 16 * s, (255, 255, 255), 0.9 * a); c.dot(cx, cy, 4.5 * s, (255, 255, 255), a)
    c.line([(cx - 110 * s, cy), (cx + 110 * s, cy)], (200, 225, 255), 1, 0.45 * a, 0.5); c.line([(cx, cy - 110 * s), (cx, cy + 110 * s)], (200, 225, 255), 1, 0.45 * a, 0.5)
def layer(px, py, w, blur=1.4, gain=3.0):
    ix = px.astype(np.int32); iy = py.astype(np.int32); ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
    out = np.zeros((H, W, 3), np.float32)
    for ch in range(3): out[:, :, ch] = np.bincount(iy[ok] * W + ix[ok], weights=w[ok, ch], minlength=W * H).reshape(H, W)
    return 1 - np.exp(-cv2.GaussianBlur(out, (0, 0), blur) * gain - out * 0.6)

# ---------- y01: Sun-like star in the dark (hook) ----------
def y01(t, T, tg, cap):
    u = t / T; sw = sm(A(u, 0.5, 1.0)); R = 118 + 40 * sw; cx, cy = CX, H * 0.42
    c = cvz(1 + 0.02 * u, dim=0.45)
    for k, (s_, a_) in enumerate(((R * 2.4, 0.22), (R * 1.5, 0.35), (R * 1.15, 0.5))): c.blob(cx, cy, s_, lerpc((255, 215, 140), (255, 120, 60), sw), a_)
    for i in range(5):
        an = tg * 0.15 + i * 1.3
        pts = [(cx + (R + 6 + 24 * math.sin(math.pi * q)) * math.cos(an + q * 0.35), cy + (R + 6 + 24 * math.sin(math.pi * q)) * math.sin(an + q * 0.35)) for q in np.linspace(0, 1, 14)]
        c.line(pts, (255, 190, 110), 2, 0.5, 0.8)
    img = c.out(); star(img, cx, cy, R, sw * 0.8, tg)
    its = [badge("ILLUSTRATION"), I(CX, H * 0.68, "A STAR DIED…", 46, WHITE, fin(u, 0.1, 0.28)), I(CX, H * 0.68 + 46, "…BUT SOMETHING MAY HAVE BEEN BORN", 20, CY2, fin(u, 0.5, 0.68), 'Medium')]
    return frame(img, its)

# ---------- y02: red giant, shed layers, white dwarf ----------
def y02(t, T, tg, cap):
    u = t / T; cx, cy = CX, H * 0.42
    gp = sm(A(u, 0.0, 0.45)); R = 160 + 230 * gp; fade = 1 - fin(u, 0.52, 0.68)
    c = cvz(1.0, dim=0.4)
    c.blob(cx, cy, R * 1.3, (255, 90, 40), 0.35 * fade)
    for k, col in enumerate(((255, 150, 90), (255, 110, 190), (110, 210, 230))):
        te = u - 0.40 - 0.07 * k
        if te > 0:
            r = 130 + te * 1050; a = max(0.0, 1 - te / 0.55) * 0.8
            c.ring(cx, cy, r, col, 12, a * 0.35, 1.0); c.ring(cx, cy, r, col, 2, a, 0.8)
    wa = fin(u, 0.64, 0.82); wd(c, cx, cy, wa, 1.0 + 0.1 * math.sin(tg * 5))
    img = c.out()
    if fade > 0.02: star(img, cx, cy, max(R * (0.3 + 0.7 * fade), 4), 1.0, tg)
    its = [badge("ILLUSTRATION"), I(CX, H * 0.70, "RED GIANT", 30, (255, 150, 110), fin(u, 0.08, 0.22) * (1 - fin(u, 0.36, 0.46)), 'Medium'),
           I(CX, H * 0.70, "OUTER LAYERS EXPELLED", 24, CY2, fin(u, 0.44, 0.56) * (1 - fin(u, 0.66, 0.74)), 'Medium'),
           I(CX, H * 0.70, "WHITE DWARF", 36, WHITE, fin(u, 0.76, 0.9)), I(CX, H * 0.74, "THE DEAD CORE · ABOUT EARTH-SIZED", 16, GREY, fin(u, 0.85, 1.0), 'Medium')]
    return frame(img, its)

# ---------- y03/y04: Hubble spectrum, unidentified lines -> niobium ----------
_NB = [1316.906, 1330.601, 1349.634, 1363.762, 1369.762, 1379.492, 1386.238, 1418.884, 1420.662, 1424.368, 1434.140, 1434.223, 1444.491, 1447.491, 1451.628, 1456.692, 1466.015, 1472.246, 1472.664, 1476.974, 1487.218, 1487.260, 1500.579, 1508.721, 1510.832, 1513.831, 1517.461, 1524.383, 1524.927, 1532.606, 1532.981, 1534.059, 1639.512]
_RS = np.random.default_rng(77); _OTH = np.sort(_RS.uniform(1160, 1700, 67)); _DEP = _RS.uniform(0.25, 0.9, 100)
_PX0, _PX1, _PY0, _PY1 = 70, 650, int(H * 0.30), int(H * 0.52)
def _wx(w): return _PX0 + (w - 1150.0) / (1710.0 - 1150.0) * (_PX1 - _PX0)
def _spec(c, sweep, hl, t):
    rng = np.random.default_rng(int(t * 24) % 61)
    pan = c.im[_PY0:_PY1, _PX0:_PX1]; pan[:] = pan * 0.6 + 0.03 * np.array([0.6, 0.8, 1.0], np.float32)
    c.line([(_PX0, _PY1), (_PX1, _PY1)], GREY, 2, 0.8, 0); c.line([(_PX0, _PY0), (_PX0, _PY1)], GREY, 2, 0.8, 0)
    xs = np.linspace(_PX0, _PX1, 180); base = _PY0 + 0.28 * (_PY1 - _PY0)
    c.line(np.stack([xs, base + rng.normal(0, 1.0, 180)], 1), (150, 175, 220), 1, 0.7, 0.4)
    allw = [(w, False) for w in _OTH] + [(w, True) for w in _NB]
    for i, (w, isnb) in enumerate(allw):
        x = _wx(w)
        if x > _PX0 + (_PX1 - _PX0) * sweep: continue
        d = _DEP[i % 100] * (_PY1 - _PY0) * 0.62
        if isnb and hl > 0: c.line([(x, base), (x, base + d)], CY2, 2, 0.95 * hl, 1.2)
        else: c.line([(x, base), (x, base + d)], (170, 180, 200), 1, 0.75 * (1 - 0.55 * hl), 0.3)
        if (not isnb) and i % 7 == 0 and hl < 0.5: c.dot(x, base - 12, 1.6, (255, 200, 140), 0.8 * (1 - hl))
