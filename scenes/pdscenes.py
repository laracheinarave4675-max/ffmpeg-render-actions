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
def y03(t, T, tg, cap):
    u = t / T; sweep = fin(u, 0.05, 0.75); c = cvz(1.0, dim=0.3); _spec(c, sweep, 0.0, t)
    n = int(100 * sm(A(u, 0.08, 0.8)))
    its = [badge("ILLUSTRATIVE · LINES SCHEMATIC"), I(CX, H * 0.265, "HUBBLE · STIS · FAR-ULTRAVIOLET · 1999", 16, GREY, fin(u, 0.0, 0.12), 'Medium'),
           I(_PX0, _PY1 + 18, "1150 Å", 13, GREY, 0.9, 'Regular', 'lm'), I(_PX1, _PY1 + 18, "1710 Å", 13, GREY, 0.9, 'Regular', 'rm'),
           I(CX, H * 0.60, "%d" % n, 66, WHITE, fin(u, 0.1, 0.25)), I(CX, H * 0.655, "UNIDENTIFIED SPECTRAL LINES", 20, WARM, fin(u, 0.2, 0.4), 'Medium')]
    return frame(c, its)
def y04(t, T, tg, cap):
    u = t / T; c = cvz(1.0, dim=0.3); hl = sm(A(u, 0.15, 0.6)); _spec(c, 1.0, hl, t)
    tx, ty = CX, H * 0.585; ta = fin(u, 0.3, 0.5)
    c.line([(tx - 55, ty - 55), (tx + 55, ty - 55), (tx + 55, ty + 55), (tx - 55, ty + 55), (tx - 55, ty - 55)], CY2, 2, ta, 1.0); c.blob(tx, ty, 70, CY2, 0.18 * ta)
    its = [badge("ILLUSTRATIVE · LINE POSITIONS FROM THE PAPER"), I(CX, H * 0.265, "HUBBLE · STIS · FAR-ULTRAVIOLET · 1999", 16, GREY, 0.9, 'Medium'),
           I(tx - 40, ty - 36, "41", 18, GREY, ta, 'Medium', 'lm'), I(tx, ty + 4, "Nb", 54, WHITE, ta), I(tx, ty + 38, "NIOBIUM", 14, CY2, ta, 'Medium'),
           I(CX, H * 0.70, "MANY LINES MATCH NIOBIUM", 22, CY2, fin(u, 0.35, 0.55), 'Medium'), I(CX, H * 0.735, "AN ELEMENT FORGED IN DYING STARS", 17, GREY, fin(u, 0.55, 0.75), 'Medium')]
    return frame(c, its)

# ---------- y05: debris disk gathers into a gas giant ----------
_RD = np.random.default_rng(12); NPD = 2200
_DR = 70 + 190 * _RD.random(NPD) ** 0.8; _DT = _RD.uniform(0, 2 * math.pi, NPD); _DF = _RD.random(NPD); _DW = 0.5 + 0.8 * _RD.random(NPD)
def y05(t, T, tg, cap):
    u = t / T; cx, cy = CX, H * 0.40; acc = sm(A(u, 0.35, 0.92))
    th = _DT + tg * 2.6 * (100.0 / _DR) ** 1.5 * 0.5
    px = cx + _DR * np.cos(th); py = cy + 0.34 * _DR * np.sin(th)
    ang = tg * 0.7; ccx = cx + 190 * math.cos(ang); ccy = cy + 0.34 * 190 * math.sin(ang)
    k = np.clip((acc - _DF * 0.8) * 3.0, 0, 1) ** 1.5
    px = px * (1 - k) + (ccx + np.random.default_rng(3).normal(0, 6, NPD)) * k; py = py * (1 - k) + (ccy + np.random.default_rng(4).normal(0, 6, NPD)) * k
    w = (_DW * (1.0 - 0.7 * k * (u > 0.8)))[:, None] * np.array([1.0, 0.72, 0.45], np.float32)[None] * 0.5
    c = cvz(1.0, dim=0.35); wd(c, cx, cy, 1.0)
    img = screen(c.out(), layer(px, py, w, 1.3, 2.4))
    Rp = 36 * fin(u, 0.62, 0.95)
    if Rp > 2:
        d = np.array([cx - ccx, cy - ccy, 0.8 * math.hypot(cx - ccx, cy - ccy)], np.float32)
        paste(img, sphere(ccx, ccy, Rp, d, (0.86, 0.72, 0.52), (0.58, 0.40, 0.30), tg, bands=7.0, spin=0.5, dark=0.04, rim=(0.6, 0.8, 1.0)))
    its = [badge("SIMULATION · ARTIST CONCEPT"), I(CX, H * 0.66, "DEBRIS FROM THE DEAD STAR", 24, WHITE, fin(u, 0.05, 0.2) * (1 - fin(u, 0.58, 0.68)), 'Medium'),
           I(CX, H * 0.66, "A NEW GAS GIANT?", 36, WHITE, fin(u, 0.74, 0.9)), I(CX, H * 0.705, "SECOND-GENERATION PLANET · CANDIDATE", 16, GREY, fin(u, 0.82, 0.95), 'Medium')]
    return frame(img, its)

# ---------- y06: TESS brightness cycle + orbit size ----------
def y06(t, T, tg, cap):
    u = t / T; c = cvz(1.0, dim=0.3); cx, cy, ro = CX, H * 0.34, 100
    phi = 2 * math.pi * (tg / 3.0); th = np.linspace(0, 2 * math.pi, 120)
    dashed(c, cx + ro * np.cos(th), cy + ro * np.sin(th), GREY, 2, 0.55 * fin(u, 0.0, 0.1))
    wd(c, cx, cy, 1.0, 0.6); pxx, pyy = cx + ro * math.cos(phi), cy + ro * math.sin(phi)
    c.blob(pxx, pyy, 14, (255, 200, 140), 0.6); c.dot(pxx, pyy, 6, (240, 200, 150), 1.0)
    la = fin(u, 0.08, 0.25); c.line([(cx, cy), (pxx, pyy)], CY2, 1, 0.4 * la, 0.3)
    x0, x1, yc = 80, 640, H * 0.50; xs = np.linspace(x0, x1, 200); p = fin(u, 0.2, 0.55)
    ys = yc + 24 * np.sin(2 * math.pi * (xs - x0) / (x1 - x0) * 2.4); n = max(2, int(200 * p))
    c.line(np.stack([xs[:n], ys[:n]], 1), CY2, 3, 0.95, 1.0)
    mx = x0 + (x1 - x0) * (((tg / 3.0) % 2.4) / 2.4); my = yc + 24 * math.sin(2 * math.pi * 2.4 * (mx - x0) / (x1 - x0))
    if p > 0.5: c.blob(mx, my, 10, WARM, 0.7); c.dot(mx, my, 4, WARM, 1.0)
    ba = fin(u, 0.58, 0.8); wb = 58 * 1.0
    c.line([(80, H * 0.655), (80 + wb, H * 0.655)], CY2, 8, ba, 0.8); c.line([(80, H * 0.705), (640, H * 0.705)], GREY, 8, 0.8 * ba, 0.3)
    its = [badge("SIMULATION · ILLUSTRATIVE"), I(cx + ro * 0.5, cy - ro - 18, "6 MILLION KM", 16, CY2, la, 'Medium'),
           I(CX, H * 0.455, "BRIGHTNESS · TESS", 15, GREY, p, 'Medium'), I(CX, H * 0.555, "VARIES EVERY 4.4 DAYS", 22, WHITE, p, 'Medium'), I(CX, H * 0.578, "(variation exaggerated: really ~0.1%)", 13, GREY, p, 'Regular'),
           I(80, H * 0.625, "THIS PLANET: 6 MILLION KM FROM ITS STAR", 15, CY2, ba, 'Medium', 'lm'), I(80, H * 0.735, "MERCURY TO THE SUN: 58 MILLION KM", 15, GREY, ba, 'Medium', 'lm')]
    return frame(c, its)

# ---------- y07: radiation strips the planet's atmosphere ----------
_RS7 = np.random.default_rng(23); N7 = 1500
_A0 = _RS7.random(N7); _PSI = _RS7.uniform(-1.2, 1.2, N7); _FB = _RS7.random(N7) < 0.18; _WG = _RS7.uniform(-1, 1, N7)
def y07(t, T, tg, cap):
    u = t / T; px, py, R = 470.0, H * 0.43, 96.0; sx, sy = 40.0, H * 0.43
    c = cvz(1.0, dim=0.3); c.blob(sx, sy, 85, (170, 205, 255), 0.75); c.blob(sx, sy, 30, (255, 255, 255), 0.9)
    ag = (_A0 + tg * 0.22) % 1.0
    x = np.where(_FB, px - R * 0.8 - 280 * ag ** 1.2, px + R * 0.6 + 520 * ag ** 1.35)
    y = py + R * np.sin(_PSI) * (1 + 0.5 * ag) + 22 * _WG * ag * np.sin(ag * 6 + tg) + np.where(_FB, 60 * ag * _WG, 0)
    w = ((1 - ag) ** 1.3 * 0.9)[:, None] * np.where(_FB[:, None], np.array([0.7, 0.85, 1.0]), np.array([1.0, 0.82, 0.6]))
    img = screen(c.out(), layer(x, y, w.astype(np.float32) * 1.6, 3.0, 3.8) * fin(u, 0.08, 0.3))
    paste(img, sphere(px, py, R, (-1.0, 0.0, 0.45), (0.86, 0.72, 0.52), (0.58, 0.40, 0.30), tg, bands=7.0, spin=0.3, dark=0.03, rim=(0.6, 0.8, 1.0)))
    its = [badge("ARTIST CONCEPT"), I(CX, H * 0.66, "THE STAR: 6 TIMES HOTTER THAN THE SUN", 20, WHITE, fin(u, 0.05, 0.22), 'Medium'),
           I(CX, H * 0.70, "ATMOSPHERE BEING STRIPPED AWAY", 22, CY2, fin(u, 0.3, 0.5), 'Medium'), I(CX, H * 0.735, "POSSIBLE COMET-LIKE TAIL", 16, GREY, fin(u, 0.52, 0.72), 'Medium')]
    return frame(img, its)

# ---------- y08: unconfirmed + the question ----------
_RF8 = np.random.default_rng(88); NF8 = 150
_FX8 = _RF8.uniform(-34, 34, NF8); _FY8 = _RF8.uniform(-50, 50, NF8); _FC8 = _RF8.choice(3, NF8, p=[.5, .35, .15]); _FS8 = _RF8.uniform(0.6, 1.6, NF8)
def y08(t, T, tg, cap):
    u = t / T; sc = lerp(26.0, 12.0, sm(u)); cx, cy = CX, H * 0.50
    c = cvz(1 + 0.04 * u, dim=0.35)
    for i in range(NF8):
        x = cx + _FX8[i] * sc; y = cy + _FY8[i] * sc
        if -20 < x < W + 20 and -20 < y < H + 20: c.blob(x, y, max(1.5, _FS8[i] * 2.4), _GCOL[_FC8[i]], 0.5)
    wd(c, cx - 30, cy, 1.0, 0.8); an = tg * 1.8; qx, qy = cx - 30 + 70 * math.cos(an), cy + 24 * math.sin(an)
    c.line([(cx - 30 + 70 * math.cos(a_), cy + 24 * math.sin(a_)) for a_ in np.linspace(0, 2 * math.pi, 60)], GREY, 1, 0.4, 0.2)
    c.blob(qx, qy, 9, (255, 210, 150), 0.6); c.dot(qx, qy, 3.5, (240, 200, 150), 1.0)
    its = [badge("SIMULATION · ARTIST CONCEPT"), I(CX, H * 0.255, "UNCONFIRMED", 36, WARM, fin(u, 0.0, 0.08) * (1 - fin(u, 0.2, 0.28))),
           I(CX, H * 0.255, "HOW MANY DEAD STARS", 34, ICE, fin(u, 0.22, 0.34) * 0.95, 'Regular'), I(CX, H * 0.255 + 46, "MIGHT BE HIDING NEW WORLDS?", 34, ICE, fin(u, 0.3, 0.42) * 0.95, 'Regular'),
           I(CX, H * 0.74, "HS 0209+0832 · SECOND-GENERATION PLANET CANDIDATE", 14, GREY, fin(u, 0.1, 0.3), 'Medium')]
    return frame(c, its)

IDS = ['y01_star', 'y02_giant', 'y03_lines', 'y04_niobium', 'y05_disk', 'y06_orbit', 'y07_strip', 'y08_final']
FUNCSY = dict(zip(IDS, [y01, y02, y03, y04, y05, y06, y07, y08])); STARTY = {k: 0.0 for k in IDS}
