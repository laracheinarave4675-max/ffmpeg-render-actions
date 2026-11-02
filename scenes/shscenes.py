"""Vertical 9:16 scenes (720x1280) for the black-hole-star Short. Ids w01..w13. All visuals are original schematics / artist concepts."""
import os
os.environ.setdefault('SCENE_W', '720'); os.environ.setdefault('SCENE_H', '1280')
import numpy as np, cv2, math
from stlib import *

CX = W // 2
HOT = (255, 90, 55); AMB = (255, 175, 90)
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)

def zbg(z=1.0, dx=0.0, dy=0.0, dim=0.5):
    M = np.float32([[z, 0, (1 - z) * W / 2 + dx], [0, z, (1 - z) * H / 2 + dy]])
    return cv2.warpAffine((BG * 0.6 * dim).astype(np.float32), M, (W, H), flags=cv2.INTER_LINEAR)
def cvz(z=1.0, dx=0.0, dy=0.0, dim=0.5):
    c = Cv(); c.im = zbg(z, dx, dy, dim); return c
def disk(cv, x, y, R, c0, c1, a=1.0, edge=0.04):
    r = np.sqrt((_xx - x) ** 2 + (_yy - y) ** 2) / max(R, 1.0)
    m = np.clip((1 - r) / edge, 0, 1)[..., None] * a
    tt = np.clip(r, 0, 1)[..., None]
    col = np.array(c0, np.float32) / 255 * (1 - tt) + np.array(c1, np.float32) / 255 * tt
    cv.im = cv.im * (1 - m) + col * m
def badge(txt="ARTIST'S CONCEPT", a=1.0):
    return I(CX, 70, txt, 22, GREY, 0.85 * a, 'Medium')
def lerpc(a, b, k): return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))
def dashed(cv, xs, ys, c, w=3, a=0.8, seg=7, gap=5):
    i = 0
    while i < len(xs) - 1:
        j = min(i + seg, len(xs))
        cv.line(np.stack([xs[i:j], ys[i:j]], 1), c, w, a, 0.2); i += seg + gap

# ---- w01: the red dot emerges (hook) ----
def w01(t, T, tg, cap):
    u = t / T
    c = cvz(1 + 0.35 * sm(u), dx=-10 * u)
    r = 5 + 62 * sm(u) ** 1.6; x, y = CX, H * 0.40
    pulse = 0.5 + 0.5 * math.sin(tg * 3.2)
    c.blob(x, y, r * 4, (255, 50, 40), 0.26 + 0.12 * pulse)
    c.blob(x, y, r * 1.7, (255, 110, 70), 0.5)
    disk(c, x, y, r, (255, 190, 120), (255, 70, 40), 0.95)
    its = [badge("ILLUSTRATION"), I(CX, H * 0.14, "SOMETHING THAT", 40, WHITE, fin(u, 0.08, 0.25), 'Medium'), I(CX, H * 0.14 + 52, "SHOULDN'T EXIST", 52, GOLD, fin(u, 0.14, 0.32))]
    a = fin(u, 0.55, 0.75)
    its += [I(CX, H * 0.74 + (1 - a) * 16, "NOT A STAR?", 84, WHITE, a), I(CX, H * 0.74 + 86, "A BLACK HOLE IN DISGUISE", 30, RED, fin(u, 0.7, 0.9), 'Medium')]
    return frame(c, its)

# ---- w02: the paper ----
def w02(t, T, tg, cap):
    u = t / T
    c = cvz(1 + 0.1 * u, dim=0.45)
    c.blob(CX, H * 0.5, 260, (80, 120, 255), 0.10)
    c.blob(CX, H * 0.20, 34, (255, 70, 50), 0.45 + 0.15 * math.sin(tg * 3)); c.dot(CX, H * 0.20, 8, (255, 150, 100))
    pa = fin(u, 0.05, 0.25); y0 = int(H * 0.34); y1 = int(H * 0.62)
    its = [{'k': 'rect', 'x1': 60, 'y1': y0, 'x2': W - 60, 'y2': y1, 'c': (10, 16, 32), 'a': 0.80 * pa},
           {'k': 'line', 'x1': 60, 'y1': y0, 'x2': int(60 + (W - 120) * fin(u, 0.1, 0.4)), 'y2': y0, 'c': GOLD, 'a': pa, 'wd': 4},
           I(CX, H * 0.395, "PUBLISHED IN", 26, GREY, fin(u, 0.2, 0.4), 'Medium'), I(CX, H * 0.465, "NATURE", 110, WHITE, fin(u, 0.25, 0.45)),
           I(CX, H * 0.545, "AUG 12, 2026", 44, GOLD, fin(u, 0.4, 0.6)), I(CX, H * 0.59, "TEAM LED BY ROHAN NAIDU", 26, CYAN, fin(u, 0.5, 0.7), 'Medium')]
    return frame(c, its)

# ---- w03: when we are looking ----
def w03(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.4)
    x0 = CX - 130; y0 = int(H * 0.24); y1 = int(H * 0.82); p = fin(u, 0.05, 0.35)
    c.line([(x0, y0), (x0, y0 + (y1 - y0) * p)], CYAN, 4, 0.9)
    my = y0 + (y1 - y0) * 0.048; mp = fin(u, 0.35, 0.5)
    c.blob(x0, my, 30, (255, 70, 50), 0.6 * mp); c.dot(x0, my, 9, (255, 150, 100), mp)
    n = int(660 * sm(A(u, 0.42, 0.75)))
    its = [I(CX, H * 0.10, "JAMES WEBB SPACE TELESCOPE", 28, CYAN, fin(u, 0.0, 0.15), 'Medium'), I(x0 + 28, y0, "BIG BANG", 28, WHITE, fin(u, 0.1, 0.3), 'Bold', 'lm'),
           I(x0 + 28, y1, "TODAY · 13.8 BILLION YEARS", 24, GREY, fin(u, 0.2, 0.4), 'Medium', 'lm'),
           I(CX + 60, H * 0.44, str(n), 150, GOLD, fin(u, 0.4, 0.55)), I(CX + 60, H * 0.44 + 100, "MILLION YEARS", 40, WHITE, fin(u, 0.5, 0.7)),
           I(CX + 60, H * 0.44 + 148, "AFTER THE BIG BANG", 30, GREY, fin(u, 0.55, 0.75), 'Medium')]
    return frame(c, its)

# ---- w04: the Balmer break (schematic) ----
def w04(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.35)
    bx0, bx1 = 80, W - 70; by0, by1 = int(H * 0.32), int(H * 0.64)
    c.line([(bx0, by1), (bx1, by1)], GREY, 2, 0.8, 0); c.line([(bx0, by0), (bx0, by1)], GREY, 2, 0.8, 0)
    xs = np.linspace(bx0, bx1, 220); xb = bx0 + (bx1 - bx0) * 0.42
    def curve(lo, hi, sharp): return by1 - (lo + (hi - lo) / (1 + np.exp(-(xs - xb) / sharp))) * (by1 - by0)
    yn = curve(0.30, 0.55, 18); yr = curve(0.04, 0.90, 3)
    n = int(220 * A(u, 0.12, 0.5))
    if n > 3: dashed(c, xs[:n], yn[:n], GREY, 3, 0.85)
    m = int(220 * A(u, 0.30, 0.75))
    if m > 3: c.line(np.stack([xs[:m], yr[:m]], 1), (255, 90, 70), 6, 1.0, 1.0)
    ba = fin(u, 0.55, 0.72)
    c.line([(xb, by0 - 10), (xb, by1)], GOLD, 2, 0.6 * ba, 0.3)
    its = [badge("SCHEMATIC · NOT REAL DATA"), I(CX, H * 0.14, "THE LIGHT DROPS", 52, WHITE, fin(u, 0.0, 0.18)), I(CX, H * 0.14 + 62, "SHARPLY", 66, RED, fin(u, 0.08, 0.26)),
           I(xb, by0 - 38, "BALMER BREAK", 34, GOLD, ba), I(bx1 - 10, by1 + 44, "WAVELENGTH →", 22, GREY, fin(u, 0.1, 0.3), 'Medium', 'rm'),
           I(bx0 + 8, by0 - 14, "BRIGHTNESS", 22, GREY, fin(u, 0.1, 0.3), 'Medium', 'lm'),
           I(bx1 - 20, by0 + 44, "THIS OBJECT", 28, (255, 110, 90), fin(u, 0.6, 0.78), 'Bold', 'rm'),
           I(bx0 + 16, by1 - (by1 - by0) * 0.18 - 36, "NORMAL STARS", 26, GREY, fin(u, 0.4, 0.6), 'Medium', 'lm'),
           I(CX, H * 0.78, "STRONGER THAN ANY ORDINARY", 32, WHITE, fin(u, 0.7, 0.85), 'Medium'), I(CX, H * 0.78 + 44, "GROUP OF STARS CAN MAKE", 32, WHITE, fin(u, 0.74, 0.9), 'Medium')]
    return frame(c, its)

# ---- w05: cutaway ----
def w05(t, T, tg, cap):
    u = t / T
    c = cvz(1 + 0.2 * u, dim=0.4)
    x, y = CX, H * 0.46; z = 1 + 0.9 * sm(u); R = 250 * z
    c.blob(x, y, R * 0.75, (255, 60, 40), 0.30)
    disk(c, x, y, R, (255, 200, 130), (200, 40, 25), 0.85)
    for k in range(5):
        c.ring(x, y, R * (0.25 + 0.15 * k) * (1 + 0.012 * math.sin(tg * 2 + k)), (255, 170, 110), 2, 0.35, 0.4)
    c.blob(x, y, R * 0.10, (255, 210, 150), 0.4)
    disk(c, x, y, max(6, R * 0.045), (0, 0, 0), (0, 0, 0), 1.0, 0.2)
    c.ring(x, y, R * 0.075, GOLD, 3, 0.9, 1.0)
    its = [badge("ARTIST'S CONCEPT · CUTAWAY"), I(CX, H * 0.13, "INSIDE THE OBJECT", 42, WHITE, fin(u, 0.05, 0.2)),
           I(x, y + R * 0.20, "BLACK HOLE", 30, GOLD, fin(u, 0.4, 0.55)), I(x, y + R * 0.62, "DENSE HYDROGEN GAS", 30, (255, 225, 190), fin(u, 0.55, 0.72))]
    return frame(c, its)

# ---- w06: the physics ----
_R6 = np.random.default_rng(6); P_R = _R6.random(1500); P_A = _R6.random(1500) * 2 * math.pi; P_S = 0.6 + _R6.random(1500) * 0.8
def w06(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.35)
    x, y = CX, H * 0.46; R = 300
    disk(c, x, y, R, (150, 40, 30), (90, 15, 12), 0.55)
    c.blob(x, y, R * 0.7, (255, 60, 40), 0.22)
    ph = (P_R - tg * 0.045 * P_S) % 1.0
    r = R * 0.95 * ph ** 0.8 + 10
    ang = P_A + tg * (0.5 / (0.2 + ph))
    ix = (x + r * np.cos(ang)).astype(np.int32); iy = (y + r * np.sin(ang)).astype(np.int32)
    ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
    lay = np.bincount(iy[ok] * W + ix[ok], weights=(0.25 + 0.75 * (1 - ph))[ok], minlength=H * W).reshape(H, W).astype(np.float32)
    lay = cv2.GaussianBlur(lay, (0, 0), 1.6) * 6
    col = np.array([1.0, 0.7, 0.35], np.float32)
    c.gl += lay[..., None] * col * 0.5; c.im += lay[..., None] * col * 0.6
    ra = fin(u, 0.25, 0.4)
    for k in range(12):
        a_ = k * math.pi / 6 + 0.2
        for j in range(4):
            s = ((tg * 0.16 + j / 4 + k * 0.083) % 1.0) * R * 0.98 + 24
            col2 = lerpc((170, 210, 255), (255, 70, 50), min(1, s / R))
            c.line([(x + s * math.cos(a_), y + s * math.sin(a_)), (x + (s + 34) * math.cos(a_), y + (s + 34) * math.sin(a_))], col2, 3, ra * (1 - 0.55 * s / R), 0.8)
    c.blob(x, y, 30, (255, 230, 180), 0.8)
    disk(c, x, y, 13, (0, 0, 0), (0, 0, 0), 1.0, 0.2)
    its = [badge("ARTIST'S CONCEPT"), I(CX, H * 0.13, "GAS FALLS IN", 52, AMB, fin(u, 0.05, 0.2)), I(CX, H * 0.13 + 52, "ENERGY POURS OUT", 40, WHITE, fin(u, 0.15, 0.3), 'Medium'),
           I(CX, H * 0.80, "THE COCOON ABSORBS THE LIGHT", 30, WHITE, fin(u, 0.45, 0.6), 'Medium'), I(CX, H * 0.80 + 50, "AND GLOWS RED", 52, RED, fin(u, 0.55, 0.72))]
    return frame(c, its)

# ---- w07: title ----
def w07(t, T, tg, cap):
    u = t / T
    c = cvz(1 + 0.1 * u, dim=0.4)
    x, y = CX, H * 0.38; R = 200 * (1 + 0.25 * (1 - fin(u, 0, 0.35)) ** 2)
    c.blob(x, y, R * 0.8, (255, 60, 40), 0.30)
    disk(c, x, y, R, (255, 190, 110), (210, 45, 28), 0.9)
    disk(c, x, y, R * 0.08, (0, 0, 0), (0, 0, 0), 1.0, 0.2); c.ring(x, y, R * 0.12, GOLD, 3, 0.9, 1.0)
    img = np.clip(c.out() + max(0, 1 - u / 0.12) * 0.5, 0, 1)
    a = fin(u, 0.05, 0.3)
    its = [badge("ARTIST'S CONCEPT"), I(CX, H * 0.66 + (1 - a) * 20, "BLACK HOLE", 92, WHITE, a), I(CX, H * 0.66 + 112, "STAR", 140, GOLD, fin(u, 0.2, 0.45)),
           I(CX, H * 0.66 + 215, "A PROPOSED NEW TYPE OF OBJECT", 26, GREY, fin(u, 0.45, 0.7), 'Medium')]
    return frame(img, its)

# ---- w08: scale ----
AU = [(0.72, "V"), (1.0, "E"), (1.52, "M"), (5.2, "J"), (9.5, "S"), (19.2, "U"), (30.1, "N")]
def w08(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.35)
    x, y = CX, H * 0.47; k = 10.0
    env = 300 * sm(A(u, 0.15, 0.5))
    if env > 4:
        disk(c, x, y, env, (255, 120, 70), (190, 40, 25), 0.38, 0.10); c.blob(x, y, env * 0.6, (255, 60, 40), 0.22)
    ro = fin(u, 0.05, 0.3)
    for au, _ in AU:
        c.ring(x, y, au * k, CYAN, 1, 0.55 * ro, 0.2)
        a_ = tg * 0.9 / au ** 1.5 + au
        c.dot(x + au * k * math.cos(a_), y + au * k * math.sin(a_), 3 if au < 10 else 5, (190, 225, 255), ro, 0.6)
    c.blob(x, y, 14, (255, 220, 120), 0.9); c.dot(x, y, 5, (255, 240, 180))
    its = [badge("SCHEMATIC · MODEL ESTIMATE"), I(CX, H * 0.13, "HOW BIG?", 56, WHITE, fin(u, 0.0, 0.15)),
           I(CX, H * 0.86, "≈ SOLAR SYSTEM SCALE", 46, GOLD, fin(u, 0.5, 0.7)), I(CX, H * 0.86 + 46, "NEPTUNE'S ORBIT ≈ 30 AU", 24, GREY, fin(u, 0.6, 0.8), 'Medium'),
           I(x + 18, y + 14, "SUN", 20, (255, 235, 170), ro, 'Medium', 'lm')]
    return frame(c, its)

# ---- w09: luminosity ----
def w09(t, T, tg, cap):
    u = t / T
    c = cvz(1 + 0.05 * u, dim=0.4)
    g = sm(u); x, y = CX, H * 0.28
    c.blob(x, y, 80 + 70 * g, (255, 70, 45), 0.5); c.blob(x, y, 190 * g + 20, (255, 120, 70), 0.25)
    disk(c, x, y, 36 + 26 * g, (255, 215, 160), (255, 90, 50), 0.95)
    c.blob(110, y + 10, 14, (255, 225, 140), 0.8); c.dot(110, y + 10, 5, (255, 245, 190))
    n = int(100 * sm(A(u, 0.1, 0.62)))
    its = [badge("ARTIST'S CONCEPT"), I(110, y + 44, "OUR SUN", 20, GREY, fin(u, 0.1, 0.3), 'Medium'),
           I(CX, H * 0.56, ">" + str(n), 190, GOLD, fin(u, 0.08, 0.25)), I(CX, H * 0.56 + 112, "BILLION ×", 64, WHITE, fin(u, 0.4, 0.6)),
           I(CX, H * 0.56 + 172, "THE SUN'S LUMINOSITY", 32, GREY, fin(u, 0.55, 0.75), 'Medium')]
    return frame(c, its)

# ---- w10: mass (model dependent) ----
def w10(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.35)
    xa, xb2, y = 130, 426, int(H * 0.50); pg = A(u, 0.15, 0.55)
    c.line([(100, y), (W - 60, y)], GREY, 2, 0.5, 0)
    nseg = 40
    for i in range(int(nseg * pg)):
        k = i / nseg
        c.line([(xa + (xb2 - xa) * k, y), (xa + (xb2 - xa) * (k + 1 / nseg), y)], lerpc((255, 190, 100), (255, 90, 70), k), 18, 1.0 - 0.75 * k, 0.5)
    for xx in (130, 330, 530): c.line([(xx, y - 22), (xx, y + 22)], GREY, 2, 0.8, 0)
    its = [badge("SCHEMATIC · LOG SCALE"), I(CX, H * 0.15, "HOW HEAVY IS", 48, WHITE, fin(u, 0.0, 0.15)), I(CX, H * 0.15 + 58, "THE BLACK HOLE?", 56, GOLD, fin(u, 0.08, 0.25)),
           I(130, y + 54, "100,000", 28, WHITE, fin(u, 0.2, 0.4)), I(330, y + 54, "1 MILLION", 28, WHITE, fin(u, 0.3, 0.5)), I(530, y + 54, "10 MILLION", 28, GREY, fin(u, 0.35, 0.55), 'Medium'),
           I(CX, y + 100, "TIMES THE SUN'S MASS", 24, GREY, fin(u, 0.4, 0.6), 'Medium'),
           I(CX, H * 0.74, "DEPENDS ON THE MODEL", 50, RED, fin(u, 0.62, 0.82))]
    return frame(c, its)

# ---- w11: rival explanation ----
def w11(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.35)
    x1, y1_, x2, y2_ = CX, H * 0.27, CX, H * 0.62; a1 = fin(u, 0.05, 0.3); a2 = fin(u, 0.4, 0.6)
    disk(c, x1, y1_, 120, (255, 190, 110), (210, 45, 28), 0.9 * a1); disk(c, x1, y1_, 10, (0, 0, 0), (0, 0, 0), a1, 0.2); c.ring(x1, y1_, 17, GOLD, 2, a1, 0.8)
    c.blob(x1, y1_, 110, (255, 60, 40), 0.25 * a1)
    disk(c, x2, y2_, 120, (255, 215, 150), (255, 110, 50), 0.9 * a2); c.blob(x2, y2_, 110, (255, 120, 50), 0.28 * a2)
    its = [badge("SCHEMATIC"), I(CX, y1_ + 168, "BLACK HOLE STAR", 38, WHITE, a1), I(CX, (y1_ + y2_) / 2 + 12, "OR?", 64, GOLD, fin(u, 0.3, 0.5)),
           I(CX, y2_ + 168, "A GIANT STAR", 38, WHITE, a2), I(CX, H * 0.86, "CANDIDATE — NOT SETTLED", 36, RED, fin(u, 0.65, 0.85))]
    return frame(c, its)

# ---- w12: little red dots ----
_R12 = np.random.default_rng(12); DX = _R12.uniform(40, W - 40, 46); DY = _R12.uniform(180, H - 200, 46); DT = np.sort(_R12.uniform(0.05, 0.7, 46)); DR = _R12.uniform(3, 8, 46)
def w12(t, T, tg, cap):
    u = t / T
    c = cvz(1 + 0.15 * sm(u), dim=0.5)
    for i in range(46):
        a = fin(u, DT[i], DT[i] + 0.1) * (0.7 + 0.3 * math.sin(tg * 2 + i))
        if a > 0.02: c.blob(DX[i], DY[i], DR[i] * 3, (255, 60, 40), 0.35 * a); c.dot(DX[i], DY[i], DR[i], (255, 130, 90), a)
    hx, hy = DX[10], DY[10]; ha = fin(u, 0.72, 0.85)
    c.ring(hx, hy, 26 + 4 * math.sin(tg * 3), GOLD, 2, ha, 0.8)
    its = [badge("ILLUSTRATION"), I(CX, H * 0.12, "LITTLE RED DOTS?", 58, WHITE, fin(u, 0.25, 0.42)), I(CX, H * 0.12 + 56, "A PUZZLE OF THE EARLY UNIVERSE", 26, GREY, fin(u, 0.5, 0.7), 'Medium')]
    return frame(c, its)

# ---- w13: pullback and question ----
def w13(t, T, tg, cap):
    u = t / T
    c = cvz(1 + 0.12 * u, dim=0.5)
    gs = lerp(900, 260, sm(u)); ga = fin(u, 0.15, 0.55)
    img = c.out()
    if ga > 0.02:
        gl = gal_layer(G, CX, H * 0.40, gs, 62, tg, 0.9)
        img = screen(img, np.clip(gl * ga * 0.85, 0, 1))
    mark = H * 0.40
    img = img.copy()
    cv2.circle(img, (CX, int(mark)), int(max(2, 18 - 12 * sm(u))), (1.0, 0.35, 0.25), -1, cv2.LINE_AA)
    its = [badge("ILLUSTRATION"), I(CX, H * 0.74, "HOW MANY OF THE FIRST GIANTS", 32, WHITE, fin(u, 0.35, 0.5), 'Medium'), I(CX, H * 0.74 + 50, "BEGAN HIDING INSIDE", 32, WHITE, fin(u, 0.42, 0.57), 'Medium'),
           I(CX, H * 0.74 + 110, "A STAR THAT WAS", 46, GOLD, fin(u, 0.5, 0.65)), I(CX, H * 0.74 + 166, "NEVER A STAR?", 56, GOLD, fin(u, 0.56, 0.72))]
    return frame(img, its)

IDS = ['w01_dot', 'w02_paper', 'w03_time', 'w04_break', 'w05_cut', 'w06_phys', 'w07_title', 'w08_scale', 'w09_lum', 'w10_mass', 'w11_rival', 'w12_dots', 'w13_final']
_F = [w01, w02, w03, w04, w05, w06, w07, w08, w09, w10, w11, w12, w13]
FUNCSW = dict(zip(IDS, _F)); STARTW = {k: 0.0 for k in IDS}
