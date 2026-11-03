"""Vertical 9:16 scenes (720x1280) for the FRB 20240304B Short. Ids x01..x16.
Only x09 can show real imagery (NASA/STScI Webb NIRCam image, downloaded at render time); every other scene is an original illustration or simulation and is labelled."""
import os, sys, types
os.environ.setdefault('SCENE_W', '720'); os.environ.setdefault('SCENE_H', '1280')
if 'engine' not in sys.modules:  # the stored engine draws 1280x720; load it at 720x1280 for this vertical module
    _p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'engine.py')
    _s = open(_p, encoding='utf-8').read().replace("W, H = 1280, 720", "W, H = 720, 1280")
    _m = types.ModuleType('engine'); _m.__file__ = _p; sys.modules['engine'] = _m
    exec(compile(_s, _p, 'exec'), _m.__dict__)
import numpy as np, cv2, math
from stlib import *

CX = W // 2
CY2 = (79, 216, 255); ICE = (191, 233, 255); WARM = (255, 179, 107)
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
def lerpc(a, b, f):
    return tuple(a[i] + (b[i] - a[i]) * f for i in range(3))
def badge(txt, a=1.0, col=GREY):
    return I(CX, 190, txt, 18, col, 0.9 * a, 'Medium')
def dashed(cv, xs, ys, c, w=2, a=0.7, seg=7, gap=6):
    i = 0
    while i < len(xs) - 1:
        j = min(i + seg, len(xs)); cv.line(np.stack([xs[i:j], ys[i:j]], 1), c, w, a, 0.2); i += seg + gap

# ---------- x01: flash in the dark ----------
_CL = [(-70, 30, 26, .10), (50, -40, 22, .09), (90, 50, 30, .08), (-20, -70, 20, .08), (10, 10, 40, .12)]
def x01(t, T, tg, cap):
    u = t / T
    c = cvz(1 + 0.04 * u, dim=0.55)
    fx, fy = CX, H * 0.50
    for dx, dy, r, a in _CL: c.blob(fx + dx, fy + dy, r, (150, 170, 255), a)
    k = math.exp(-t * 4.5)
    c.blob(fx, fy, 34 + 70 * k, (255, 255, 255), 0.95 * k + 0.05)
    c.blob(fx, fy, 16, WARM, 0.8 * math.exp(-t * 2.2))
    c.dot(fx, fy, 3 + 7 * k, (255, 255, 255), min(1.0, 0.5 + k))
    for i in range(3):
        tt = t - 0.12 * i
        if tt > 0: c.ring(fx, fy, tt * 430, (255, 255, 255) if i == 0 else ICE, 2, max(0, 1 - tt / 2.8) * 0.85, 0.9)
    te = t - 3.6
    if 0 < te < 2.4:
        c.ring(fx, fy, te * 300, CY2, 2, (1 - te / 2.4) * 0.55, 0.8); c.blob(fx, fy, 28, CY2, 0.4 * math.exp(-te * 4))
    its = [badge("ILLUSTRATION"), I(CX, H * 0.285, "10+ BILLION YEARS AGO", 32, WHITE, fin(u, 0.05, 0.14), 'Medium'),
           I(CX, H * 0.285 + 46, "LASTED A FEW MILLISECONDS", 24, CY2, fin(u, 0.62, 0.74), 'Medium')]
    return frame(c, its)

# ---------- x02/x03: riding the pulse through cosmic history ----------
_RT = np.random.default_rng(5); NG = 200
GX = _RT.uniform(-1.5, 1.5, NG); GY = _RT.uniform(-1.8, 1.8, NG); GZ = _RT.uniform(0, 1, NG); GCI = _RT.choice(3, NG, p=[.5, .35, .15]); GSZ = _RT.uniform(.6, 1.5, NG)
_GCOL = [(170, 200, 255), (255, 255, 255), (255, 200, 150)]
def _world(c, tt):
    for i in range(NG):
        z = ((GZ[i] - 0.075 * tt) % 1.0) + 0.05
        x = CX + GX[i] * 240 / z; y = H * 0.36 + GY[i] * 240 / z
        if x < -60 or x > W + 60 or y < -60 or y > H + 60: continue
        a = min(1.0, (1.08 - z) * 1.4) * 0.55
        r = min(38.0, GSZ[i] * 3.2 / z)
        c.blob(x, y, r, _GCOL[GCI[i]], a)
        if z < 0.5: c.dot(x, y, max(1.0, r * 0.25), _GCOL[GCI[i]], a)
def _pulse(c, tg, yc):
    for k in range(5):
        a = (1 - k / 5) * 0.85
        pts = [(CX + 95 * math.sin(an), yc - 38 * math.cos(an) + k * 30 + 3 * math.sin(tg * 6)) for an in np.linspace(-1.15, 1.15, 36)]
        c.line(pts, ICE if k else (255, 255, 255), 3 if k == 0 else 2, a, 1.0)
    c.blob(CX, yc, 34, CY2, 0.5); c.dot(CX, yc, 6, (255, 255, 255), 1.0)
def x02(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.3); _world(c, t); _pulse(c, tg, H * 0.36)
    v = 10.0 * sm(min(1.0, t / 11.5)); p = v / 10.0
    c.line([(CX - 200, H * 0.655), (CX + 200, H * 0.655)], GREY, 3, 0.5, 0)
    c.line([(CX - 200, H * 0.655), (CX - 200 + 400 * p, H * 0.655)], CY2, 3, 0.95, 1.0)
    its = [badge("ILLUSTRATION"), I(CX, H * 0.53, "TRAVEL TIME", 20, GREY, fin(u, 0.1, 0.3), 'Medium'),
           I(CX, H * 0.585, "10+" if v > 9.95 else "%.1f" % v, 62, WHITE, fin(u, 0.1, 0.3)), I(CX, H * 0.63, "BILLION YEARS", 24, CY2, fin(u, 0.1, 0.3), 'Medium'),
           I(CX, H * 0.69, "Radio waves are invisible — shown as a visual metaphor.", 16, GREY, fin(u, 0.15, 0.3) * (1 - fin(u, 0.7, 0.95)), 'Regular')]
    return frame(c, its)
def x03(t, T, tg, cap):
    u = t / T; tt = t + 5.2
    c = cvz(1.0, dim=0.3); _world(c, tt); _pulse(c, tg, H * 0.36)
    ul = fin(u, 0.15, 0.45)
    c.line([(CX - 150, H * 0.612), (CX - 150 + 300 * ul, H * 0.612)], CY2, 2, 0.9, 1.0)
    its = [badge("ILLUSTRATION"), I(CX, H * 0.55, "FRB 20240304B", 50, WHITE, fin(u, 0.05, 0.3)),
           I(CX, H * 0.645, "MOST DISTANT FAST RADIO BURST DETECTED", 19, CY2, fin(u, 0.3, 0.55), 'Medium'),
           I(CX, H * 0.68, "ANNOUNCED 8 OCT 2026 · SCIENCE", 19, GREY, fin(u, 0.45, 0.7), 'Medium')]
    return frame(c, its)

# ---------- x04: blink vs burst, Sun energy ----------
def x04(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.3)
    ap = 1 - fin(u, 0.42, 0.52)
    its = [badge("ILLUSTRATION")]
    if ap > 0.01:
        y1 = H * 0.34; y2 = H * 0.47; p = fin(u, 0.04, 0.22)
        c.line([(70, y1), (70 + 580 * p, y1)], WHITE, 9, 0.9 * ap, 0.5)
        its.append(I(CX, y1 - 36, "HUMAN BLINK: ABOUT 100-400 MS", 22, WHITE, fin(u, 0.0, 0.12) * ap, 'Medium'))
        q = fin(u, 0.2, 0.34)
        c.line([(70, y2 + 34), (70, y2 - 34)], CY2, 4, q * ap, 1.2); c.blob(70, y2, 16, CY2, 0.6 * q * ap)
        its.append(I(CX, y2 - 58, "FAST RADIO BURST: A FEW MS", 22, CY2, q * ap, 'Medium'))
    bp = fin(u, 0.5, 0.62)
    if bp > 0.01:
        sx, sy = 190, H * 0.44
        disk(c, sx, sy, 62, (255, 235, 170), (255, 150, 60), 0.95 * bp); c.blob(sx, sy, 70, WARM, 0.35 * bp)
        p2 = fin(u, 0.58, 0.82); ang = np.linspace(-math.pi / 2, -math.pi / 2 + 2 * math.pi * p2, max(2, int(80 * p2)))
        c.line(np.stack([sx + 96 * np.cos(ang), sy + 96 * np.sin(ang)], 1), WARM, 3, bp, 0.8)
        its += [I(470, sy - 14, "1 YEAR OF", 26, WHITE, bp, 'Medium'), I(470, sy + 22, "THE SUN'S OUTPUT", 26, WARM, bp, 'Medium')]
        a3 = fin(u, 0.78, 0.92)
        its += [I(CX, H * 0.60, "THE BURST HELD MORE ENERGY", 26, WHITE, a3, 'Medium'), I(CX, H * 0.60 + 36, "THAN THAT", 26, CY2, a3, 'Medium'),
                I(CX, H * 0.60 + 78, "isotropic-equivalent estimate", 15, GREY, a3, 'Regular')]
    return frame(c, its)

# ---------- x05: MeerKAT at night (stylised) ----------
_RD = np.random.default_rng(9)
_DX = np.concatenate([_RD.normal(0, 55, 40), _RD.uniform(-300, 300, 24)]); _DZ = np.concatenate([_RD.uniform(30, 120, 40), _RD.uniform(60, 260, 24)])
_ORD = np.argsort(-_DZ)
def x05(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dy=-8 * u, dim=0.55)
    d = np.abs((_xx - CX) * 0.75 + (_yy - H * 0.30) * 0.66)
    band = np.exp(-(d / 95.0) ** 2) * 0.20 * (0.7 + 0.3 * np.sin(_xx * 0.05 + _yy * 0.03))
    c.im += band[..., None] * np.array([0.45, 0.55, 0.85], np.float32)
    hor = int(H * 0.52); c.im[hor:] *= 0.12
    f = 330.0; elev = 0.85 - 0.30 * u
    for i in _ORD:
        Z = _DZ[i] - 8 * u; X = _DX[i]
        sx = CX + X * f / Z; gy = hor + 9 * f / Z; s = 6.75 * f / Z; cy_ = gy - 8 * f / Z
        if sx < -40 or sx > W + 40: continue
        cv2.line(c.im, (int(sx), int(cy_ + s * elev * 0.7)), (int(sx), int(gy)), (0.07, 0.08, 0.11), max(1, int(s * 0.12)), cv2.LINE_AA)
        cv2.ellipse(c.im, (int(sx), int(cy_)), (max(2, int(s)), max(2, int(s * elev))), -35, 0, 360, (0.16, 0.19, 0.28), -1, cv2.LINE_AA)
        cv2.ellipse(c.im, (int(sx), int(cy_)), (max(2, int(s)), max(2, int(s * elev))), -35, 0, 360, (0.50, 0.58, 0.78), 1, cv2.LINE_AA)
    its = [badge("ILLUSTRATION"), I(CX, H * 0.285, "MeerKAT RADIO TELESCOPE", 28, CY2, fin(u, 0.05, 0.25), 'Medium'),
           I(CX, H * 0.32, "SOUTH AFRICA · 64 DISHES", 22, GREY, fin(u, 0.15, 0.35), 'Medium'),
           I(CX, H * 0.70, "4 MARCH 2024 · 00:50 UTC", 28, GOLD, fin(u, 0.45, 0.7), 'Medium')]
    return frame(c, its)

# ---------- x06: waterfall, dispersion ----------
def x06(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.3)
    x0, x1, y0, y1 = 80, 640, int(H * 0.285), int(H * 0.50)
    rng = np.random.default_rng(int(t * 24) % 97)
    pan = c.im[y0:y1, x0:x1]
    pan[:] = pan * 0.5 + np.clip(rng.normal(0.06, 0.035, pan.shape), 0, 1).astype(np.float32) * np.array([0.7, 0.85, 1.0], np.float32)
    c.line([(x0, y1), (x1, y1)], GREY, 2, 0.8, 0); c.line([(x0, y0), (x0, y1)], GREY, 2, 0.8, 0)
    fs = np.linspace(0, 1, 90); tau = ((0.9 + 0.8 * fs) ** -2 - 1.7 ** -2) / (0.9 ** -2 - 1.7 ** -2)
