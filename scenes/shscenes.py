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
