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
    s = sm(A(u, 0.45, 0.72)); p = fin(u, 0.08, 0.42)
    xs = x0 + (x1 - x0) * ((0.08 + 0.84 * tau) * (1 - s) + 0.52 * s); ys = y1 - fs * (y1 - y0)
    n = max(2, int(90 * p))
    c.line(np.stack([xs[:n], ys[:n]], 1), CY2, 5, 0.95, 1.3)
    px = np.linspace(x0, x1, 160); pk = x0 + (x1 - x0) * 0.52
    prof = s * 44 * np.exp(-((px - pk) / 5.0) ** 2) + rng.normal(0, 1.2, 160)
    c.line(np.stack([px, y0 - 12 - prof], 1), WARM, 2, 0.9, 0.8)
    if s > 0.9: c.blob(pk, y0 - 12 - 44, 12, WARM, 0.5 * (s - 0.9) * 10)
    its = [badge("ILLUSTRATIVE · NOT THE ACTUAL DATA"), I(x0 + 4, y0 + 14, "1.7 GHz", 14, GREY, 0.9, 'Regular', 'lm'), I(x0 + 4, y1 - 14, "0.9 GHz", 14, GREY, 0.9, 'Regular', 'lm'),
           I(x1 - 4, y1 + 16, "TIME", 14, GREY, 0.9, 'Regular', 'rm'),
           I(CX, H * 0.535, "DISPERSION MEASURE", 20, GREY, fin(u, 0.2, 0.4), 'Medium'), I(CX, H * 0.575, "2,458 pc/cm³", 40, WHITE, fin(u, 0.25, 0.45)),
           I(CX, H * 0.615, "MORE GAS = MORE DISTANCE", 22, CY2, fin(u, 0.55, 0.75), 'Medium'),
           I(CX, H * 0.65, "SMEARED BY ~10 SECONDS ACROSS THE BAND*", 17, WARM, fin(u, 0.62, 0.82), 'Medium'),
           I(CX, H * 0.68, "*calculated from the dispersion measure", 13, GREY, fin(u, 0.68, 0.85), 'Regular')]
    return frame(c, its)

# ---------- x07: empty sky ----------
def x07(t, T, tg, cap):
    u = t / T
    c = cvz(1 + 0.12 * u, dim=0.30)
    rng = np.random.default_rng(int(t * 24) % 53)
    c.im += np.clip(rng.normal(0.025, 0.02, c.im.shape), 0, 1).astype(np.float32)
    rr = lerp(170, 72, fin(u, 0.12, 0.45)); cy_ = H * 0.42; a = fin(u, 0.1, 0.3)
    for sx_, sy_ in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        x = CX + sx_ * rr; y = cy_ + sy_ * rr
        c.line([(x, y), (x - sx_ * 34, y)], CY2, 3, a, 1.0); c.line([(x, y), (x, y - sy_ * 34)], CY2, 3, a, 1.0)
    c.ring(CX, cy_, 4, CY2, 1, a * (0.5 + 0.5 * math.sin(tg * 4)), 0.5)
    its = [badge("ILLUSTRATION · SCHEMATIC OF A NON-DETECTION"), I(CX, H * 0.27, "KECK · MMT", 34, WHITE, fin(u, 0.0, 0.15), 'Medium'),
           I(CX, H * 0.56, "NOTHING DETECTED", 38, WARM, fin(u, 0.55, 0.75))]
    return frame(c, its)

# ---------- x08: Webb ----------
_HEX = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1), (2, 0), (2, -1), (2, -2), (1, -2), (0, -2), (-1, -1), (-2, 0), (-2, 1), (-2, 2), (-1, 2), (0, 2), (1, 1)]
def x08(t, T, tg, cap):
    u = t / T; a = fin(u, 0.0, 0.3)
    c = cvz(1.0, dim=0.3)
    ph = 0.18 + 0.35 * u
    def tf(x, y, cx, cy):
        xr = x * math.cos(ph) - y * math.sin(ph); yr = x * math.sin(ph) + y * math.cos(ph)
        return (cx + xr, cy + yr * 0.82)
    for k, (wd, al) in enumerate([(300, 0.30), (270, 0.28), (240, 0.26), (210, 0.24), (180, 0.22)]):
        pts = [tf(-wd, -20 + k * 14, CX, H * 0.52), tf(wd, -20 + k * 14, CX, H * 0.52), tf(wd * 0.55, 150 + k * 14, CX, H * 0.52), tf(-wd * 0.55, 150 + k * 14, CX, H * 0.52)]
        c.poly(pts, (150, 170, 215), al * a); c.line(pts + [pts[0]], (190, 205, 240), 1, 0.5 * a, 0.3)
    s = 40.0
    for q, r in _HEX:
        x = s * 1.5 * q; y = s * math.sqrt(3) * (r + q / 2.0)
        hp = [tf(x + s * 0.94 * math.cos(math.radians(60 * i)), y + s * 0.94 * math.sin(math.radians(60 * i)), CX, H * 0.40) for i in range(6)]
        c.poly(hp, (255, 200, 90), 0.85 * a); c.line(hp + [hp[0]], (255, 232, 170), 1, 0.9 * a, 0.5)
    c.blob(CX, H * 0.40, 150, WARM, 0.12 * a)
    its = [badge("ILLUSTRATION"), I(CX, H * 0.68, "JAMES WEBB SPACE TELESCOPE", 24, CY2, fin(u, 0.3, 0.55), 'Medium'), I(CX, H * 0.705, "NIRCam + NIRSpec", 19, GREY, fin(u, 0.4, 0.65), 'Medium')]
    return frame(c, its)

# ---------- x09: the host galaxy (real NASA/STScI image when downloadable) ----------
_URL = 'https://assets.science.nasa.gov/content/dam/science/missions/webb/science/2026/10/STScI-01KKCJGBWX6TE4ABRTFWE9B8SQ.jpg/jcr:content/renditions/2000x1742.jpg'
_ST = {'img': None, 'box': None, 'tried': False}
def _find_box(im):
    m = (im.min(axis=2) >= 245).astype(np.uint8) * 255
    hh = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (101, 1)))
    vv = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 101)))
    L = cv2.dilate(hh | vv, np.ones((7, 7), np.uint8))
    cs, _ = cv2.findContours(L, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    for ct in cs:
        x, y, w, h = cv2.boundingRect(ct)
        if w < 260 or h < 260 or w > 0.85 * im.shape[1] or h > 0.85 * im.shape[0]: continue
        if best is None or w * h > best[2] * best[3]: best = (x, y, w, h)
    return best
def _load():
    if _ST['tried']: return
    _ST['tried'] = True
    try:
        import urllib.request
        data = urllib.request.urlopen(urllib.request.Request(_URL, headers={'User-Agent': 'Mozilla/5.0'}), timeout=90).read()
        im = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        assert im is not None and im.shape[1] >= 800
        _ST['box'] = _find_box(im)
        _ST['img'] = (im[:, :, ::-1].astype(np.float32) / 255.0)
        print('x09: real image', im.shape, 'inset box', _ST['box'], flush=True)
    except Exception as e:
        print('x09: image unavailable ->', repr(e), flush=True)
_RF = np.random.default_rng(21)
def x09(t, T, tg, cap):
    u = t / T; _load()
    im = _ST['img']; its = []
    if im is not None:
        ih, iw = im.shape[:2]; s0 = W / iw; box = _ST['box']; k = sm(A(u, 0.12, 0.85))
        if box: bx, by, bw, bh = box; fx, fy = bx + bw / 2.0, by + bh / 2.0; zmax = min(5.0, 0.88 * W / (bw * s0))
        else: fx, fy = iw * 0.5, ih * 0.40; zmax = 1.5
        z = math.exp(math.log(max(zmax, 1.0)) * k); s = s0 * z
        fxm = lerp(iw / 2.0, fx, k); fym = lerp(ih / 2.0, fy, k); cyc = H * 0.46
        M = np.float32([[s, 0, CX - s * fxm], [0, s, cyc - s * fym]])
        wi = cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
        mk = cv2.warpAffine(np.ones((ih, iw), np.float32), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)[..., None]
        if s < 0.6: wi = cv2.GaussianBlur(wi, (0, 0), 0.6)
        img = np.clip(zbg(1.0, dim=0.25) * (1 - mk) + wi * mk * 1.05, 0, 1)
        if box:
            ba = fin(u, 0.38, 0.62)
            xa = s * (bx - fxm) + CX; xb = s * (bx + bw - fxm) + CX; ya = s * (by - fym) + cyc; yb = s * (by + bh - fym) + cyc
            for (xx, yy, dx, dy) in ((xa, ya, 1, 1), (xb, ya, -1, 1), (xa, yb, 1, -1), (xb, yb, -1, -1)):
                its.append({'k': 'line', 'x1': xx, 'y1': yy, 'x2': xx + dx * 34, 'y2': yy, 'c': CY2, 'a': ba, 'wd': 3})
                its.append({'k': 'line', 'x1': xx, 'y1': yy, 'x2': xx, 'y2': yy + dy * 34, 'c': CY2, 'a': ba, 'wd': 3})
        its += [badge("REAL IMAGE · JAMES WEBB SPACE TELESCOPE", 1.0, GOLD), I(CX, H * 0.255, "THE HOST GALAXY", 26, WHITE, fin(u, 0.1, 0.25)), I(CX, H * 0.255 + 34, "FRB 20240304B", 20, CY2, fin(u, 0.15, 0.3), 'Medium'),
                I(CX, H * 0.705, "WHITE CROSS: WHERE THE BURST CAME FROM", 17, WHITE, fin(u, 0.5, 0.7), 'Medium'),
                I(CX, H * 0.74, "NASA · ESA · CSA · STScI · T. NANAYAKKARA (USYD) · J. DEPASQUALE (STScI)", 12, GREY, 0.9, 'Regular')]
        return frame(img, its)
    c = cvz(1 + 0.2 * sm(u), dim=0.45)
    for i in range(70): c.blob(_RF.uniform(40, W - 40), _RF.uniform(300, 900), _RF.uniform(2, 6), (170, 200, 255), 0.35)
    c.blob(CX + 30, H * 0.46, 7, CY2, 0.7 * fin(u, 0.4, 0.7)); c.ring(CX + 30, H * 0.46, 26 + 4 * math.sin(tg * 3), WHITE, 2, fin(u, 0.5, 0.8), 0.8)
    its = [badge("ILLUSTRATION"), I(CX, H * 0.255, "A TINY, FAINT GALAXY", 28, WHITE, fin(u, 0.1, 0.3)), I(CX, H * 0.705, "RIGHT WHERE THE BURST BEGAN", 20, CY2, fin(u, 0.5, 0.7), 'Medium')]
    return frame(c, its)

# ---------- x10: redshift + cosmic timeline ----------
def x10(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.3); its = [badge("ILLUSTRATION")]
    pa = 1 - fin(u, 0.44, 0.54)
    if pa > 0.01:
        k = min(1.0, u / 0.34); xs = np.linspace(60, 660, 240)
        lam = 24 + 62 * sm(np.clip((xs - 60) / 600.0, 0, 1)) * k
        phi = np.cumsum(2 * math.pi / lam) * (xs[1] - xs[0])
        ys = H * 0.37 + 58 * np.sin(phi - tg * 5)
        for j in range(12):
            a_, b_ = j * 20, min(240, j * 20 + 21); f = j / 11.0
            col = lerpc((170, 215, 255), (255, 80, 60), f)
            c.line(np.stack([xs[a_:b_], ys[a_:b_]], 1), col, 3, 0.95 * pa, 1.0)
        z = 2.148 * sm(A(u, 0.1, 0.4))
        its += [I(CX, H * 0.285, "LIGHT STRETCHED BY EXPANDING SPACE", 19, CY2, fin(u, 0.0, 0.12) * pa, 'Medium'),
                I(CX, H * 0.50, "z = %.3f" % z, 46, WHITE, fin(u, 0.1, 0.25) * pa),
                I(CX, H * 0.545, "H-ALPHA: 0.656 µm TO ~2.07 µm (CALCULATED)", 15, GREY, fin(u, 0.3, 0.42) * pa, 'Regular')]
    tb = fin(u, 0.5, 0.62)
    if tb > 0.01:
        x0_, x1_, y = 90, 630, H * 0.42; mx = x0_ + (x1_ - x0_) * 3.0 / 13.8
        c.line([(x0_, y), (x1_, y)], GREY, 3, 0.7 * tb, 0); c.line([(x0_, y), (mx, y)], WARM, 3, 0.95 * tb, 1.0)
        c.blob(mx, y, 16, WARM, 0.8 * tb); c.dot(mx, y, 7, WARM, tb)
        pp = fin(u, 0.7, 0.97); px = lerp(mx, x1_, pp)
        c.line([(mx, y), (px, y)], CY2, 3, 0.9 * tb * (pp > 0), 1.0); c.dot(px, y, 6, ICE, tb * (pp > 0))
        its += [I(x0_, y + 34, "BIG BANG", 15, GREY, tb, 'Medium', 'lm'), I(x1_, y + 34, "TODAY · 13.8 BILLION YEARS", 15, GREY, tb, 'Medium', 'rm'),
                I(mx + 20, y - 66, "UNIVERSE: ABOUT 3 BILLION YEARS OLD", 19, WHITE, fin(u, 0.55, 0.7), 'Medium', 'lm'),
                I(mx + 20, y - 38, "ABOUT 22% OF ITS AGE TODAY", 15, GREY, fin(u, 0.62, 0.78), 'Regular', 'lm'),
                I(CX, y + 90, "TRAVEL TIME: 10+ BILLION YEARS", 21, CY2, fin(u, 0.8, 0.95), 'Medium')]
    return frame(c, its)

# ---------- shared: young dwarf galaxy (particles) ----------
_RG = np.random.default_rng(31)
_KN = [(-0.30, -0.14, 1.0), (0.26, -0.30, 0.9), (0.34, 0.22, 0.8), (-0.18, 0.34, 0.7)]
_PX = []; _PY = []; _PW = []; _PK = []; _PC = []
for ki, (kx, ky, ks) in enumerate(_KN):
    n = 420; _PX.append(kx + _RG.normal(0, 0.09 * ks, n)); _PY.append(ky + _RG.normal(0, 0.09 * ks, n)); _PW.append(_RG.uniform(0.5, 1.2, n) * ks); _PK.append(np.full(n, ki)); _PC.append(_RG.random(n) < 0.18)
_PX.append(_RG.normal(0, 0.55, 1100)); _PY.append(_RG.normal(0, 0.40, 1100)); _PW.append(_RG.uniform(0.12, 0.35, 1100)); _PK.append(np.full(1100, -1)); _PC.append(np.zeros(1100, bool))
_PX = np.concatenate(_PX); _PY = np.concatenate(_PY); _PW = np.concatenate(_PW); _PK = np.concatenate(_PK); _PC = np.concatenate(_PC)
def dwarf_layer(cx, cy, scale, ang, tg, gain=1.0):
    ca, sa = math.cos(ang), math.sin(ang)
    xr = _PX * ca - _PY * sa; yr = (_PX * sa + _PY * ca) * 0.8
    fl = np.where(_PK >= 0, 1.0 + 0.45 * np.sin(tg * 3.1 + _PK * 1.7), 1.0)
    sx = (xr * scale + cx).astype(np.int32); sy = (yr * scale + cy).astype(np.int32)
    ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
    idx = sy[ok] * W + sx[ok]; wgt = (_PW * fl)[ok] * gain
    cols = np.where(_PC[ok, None], np.array([1.0, 0.72, 0.42], np.float32), np.array([0.62, 0.80, 1.0], np.float32))
    layer = np.zeros((H, W, 3), np.float32)
    for ch in range(3): layer[:, :, ch] = np.bincount(idx, weights=wgt * cols[:, ch], minlength=W * H).reshape(H, W)
    k = float(np.clip(110.0 / max(scale, 1.0), 0.6, 6.0))
    g = cv2.GaussianBlur(layer, (0, 0), max(1.2, scale * 0.025)) * 3.2 * k + layer * 0.9
    return 1 - np.exp(-g)
def x11(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.3); cx_, cy_ = CX, H * 0.42
    gh = fin(u, 0.1, 0.35)
    th = np.linspace(0, 2 * math.pi, 140)
    dashed(c, cx_ + 255 * np.cos(th), cy_ + 105 * np.sin(th), GREY, 2, 0.55 * gh)
    img = screen(c.out(), dwarf_layer(cx_, cy_, 150, 0.5 * u, tg) * fin(u, 0.0, 0.2))
    its = [badge("SIMULATION · ILLUSTRATIVE SCALE"), I(CX, cy_ - 150, "TYPICAL FRB HOST (EXPECTED)", 16, GREY, gh, 'Medium'),
           I(CX, H * 0.585, "1,000 TIMES LESS MASSIVE THAN EXPECTED", 20, WHITE, fin(u, 0.4, 0.6), 'Medium'),
           I(CX, H * 0.625, "METAL-POOR · STARBURST", 19, CY2, fin(u, 0.55, 0.75), 'Medium')]
    return frame(img, its)

# ---------- x12: magnetar concept ----------
def x12(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.3); cx_, cy_ = CX, H * 0.40
    dim = 1 - 0.5 * fin(u, 0.72, 0.88); pul = 0.55 + 0.45 * math.sin(tg * 7.5)
    tilt = math.radians(28) + 0.12 * math.sin(tg * 0.9)
    rng = np.random.default_rng(int(t * 24) % 31)
    for L in (55, 95, 140):
        th = np.linspace(0.12, math.pi - 0.12, 60); r = L * np.sin(th) ** 2
        for sgn in (1, -1):
            x = sgn * r * np.sin(th); y = -L * 0.0 - r * np.cos(th) * 0 + (L * np.sin(th) ** 2) * 0
            px = sgn * r * np.sin(th) * 1.0; py = r * np.cos(th) * 1.0
            xr = px * math.cos(tilt) - py * math.sin(tilt); yr = px * math.sin(tilt) + py * math.cos(tilt)
            fl = 1.0 if u < 0.72 else (0.6 + 0.4 * rng.random())
            c.line(np.stack([cx_ + xr, cy_ + yr], 1), CY2, 2, 0.7 * dim * fl, 1.0)
    for sgn in (1, -1):
        ax = sgn * math.sin(tilt) * -1; ay = sgn * math.cos(tilt)
        c.poly([(cx_, cy_), (cx_ + ax * 230 - ay * 55, cy_ + ay * 230 + ax * 55), (cx_ + ax * 230 + ay * 55, cy_ + ay * 230 - ax * 55)], CY2, 0.07 * dim * pul)
    c.blob(cx_, cy_, 22, (200, 225, 255), 0.7 * dim * (0.6 + 0.4 * pul)); c.dot(cx_, cy_, 8, (255, 255, 255), dim)
    a1 = fin(u, 0.1, 0.3) * (1 - fin(u, 0.68, 0.78)); a2 = fin(u, 0.74, 0.9)
    its = [badge("ARTIST CONCEPT"), I(CX, H * 0.60, "LEADING IDEA: YOUNG MAGNETAR", 26, WHITE, a1, 'Medium'),
           I(CX, H * 0.60, "ORIGIN NOT CONFIRMED", 30, WARM, a2), I(CX, H * 0.665, "?", 84, WARM, fin(u, 0.8, 0.95) * 0.9)]
    return frame(c, its)

# ---------- cosmic web helpers ----------
_RW = np.random.default_rng(41)
def _filaments(n=12, steps=28):
    fl = []
    for _ in range(n):
        x = _RW.uniform(-300, 300); y = _RW.uniform(-700, 700); ang = _RW.uniform(0, 2 * math.pi); pts = [(x, y)]
        for _ in range(steps):
            ang += _RW.normal(0, 0.28); x += 38 * math.cos(ang); y += 38 * math.sin(ang); pts.append((x, y))
        fl.append(np.array(pts, np.float32))
    return fl
_FIL = _filaments()
def _web(c, zoom, cx, cy, a=1.0, lit=None):
    for f in _FIL:
        pts = f * zoom + np.array([cx, cy], np.float32)
        al = 0.30 * a
        if lit is not None:
            for i in range(len(pts) - 1):
                mx, my = (pts[i] + pts[i + 1]) / 2
                w = lit(mx, my)
                if w > 0.02: c.line(pts[i:i + 2], (140, 175, 255), 2, al * w * 2.2, 0.8)
        else: c.line(pts, (120, 150, 235), 2, al, 0.6)
        for p in pts[::5]: c.blob(p[0], p[1], 8 * zoom ** 0.5, (130, 170, 255), 0.10 * a)

# ---------- x13: cosmic flashlight ----------
def x13(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.28); ax, ay = CX, H * 0.64
    sw = math.radians(-22 + 44 * sm(u)); rv = fin(u, 0.0, 0.5)
    def cone(x, y):
        dx = x - ax; dy = ay - y
        if dy < 10: return 0.0
        d = math.atan2(dx, dy) - sw
        return math.exp(-(d / 0.30) ** 2) * min(1.0, dy / (rv * 560 + 1))
    _web(c, 1.0, CX, H * 0.40, 1.0, lit=cone)
    L = rv * 560
    c.poly([(ax, ay), (ax + L * math.sin(sw - 0.30), ay - L * math.cos(sw - 0.30)), (ax + L * math.sin(sw + 0.30), ay - L * math.cos(sw + 0.30))], ICE, 0.10)
    c.blob(ax, ay, 26, (255, 255, 255), 0.6); c.dot(ax, ay, 5, (255, 255, 255), 1.0)
    its = [badge("ILLUSTRATION"), I(CX, H * 0.72, "COSMIC FLASHLIGHT", 34, WHITE, fin(u, 0.35, 0.6))]
    return frame(c, its)

# ---------- x14: fingerprints on the signal ----------
def x14(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.28); zm = 1.0 + 0.25 * u
    _web(c, zm, CX, H * 0.38, 1.0)
    py = lerp(H * 0.52, H * 0.26, sm(u)); n = int(u * 4.0 + 0.0001) if u < 0.75 else 3
    n = min(3, int(max(0, (u - 0.2)) / 0.22) + (1 if u > 0.2 else 0)) if u > 0.2 else 0
    for ev in (0.25, 0.5, 0.75):
        te = u - ev
        if 0 < te < 0.16: c.ring(CX, lerp(H * 0.52, H * 0.26, sm(ev)), te / 0.16 * 70, ICE, 2, (1 - te / 0.16) * 0.8, 0.9); c.blob(CX, lerp(H * 0.52, H * 0.26, sm(ev)), 24, CY2, 0.4 * (1 - te / 0.16))
    c.blob(CX, py, 18, CY2, 0.8); c.dot(CX, py, 5, (255, 255, 255), 1.0)
    y0 = H * 0.70; w = 5 + n * 15; xs = np.linspace(100, 620, 160)
    for off, col in ((-n * 4, (255, 110, 90)), (0, (150, 235, 160)), (n * 4, (110, 160, 255))):
        ys = y0 - 40 * np.exp(-(((xs - 360 + off) / w) ** 2)) / (1 + 0.5 * n)
        c.line(np.stack([xs, ys], 1), col, 2, 0.75, 0.6)
    its = [badge("SIMULATION · NOT TO SCALE"), I(CX, H * 0.575, "GAS ADDS DELAY —", 22, WHITE, fin(u, 0.1, 0.3), 'Medium'), I(CX, H * 0.61, "AND LEAVES A FINGERPRINT", 22, CY2, fin(u, 0.2, 0.4), 'Medium'),
           I(CX, H * 0.74, "TOTAL DM 2,458 pc/cm³", 17, GREY, fin(u, 0.4, 0.6), 'Medium')]
    return frame(c, its)

# ---------- x15: the whole sightline ----------
def x15(t, T, tg, cap):
    u = t / T
    c = cvz(1.0, dim=0.28); ex, ey = 110, H * 0.60; gx_, gy_ = 610, H * 0.28
    _web(c, 0.8, CX, H * 0.40, 0.8)
    p = fin(u, 0.0, 0.45); ts = np.linspace(0, 1, 60)
    px = lerp(gx_, ex, ts) + 40 * np.sin(ts * math.pi); py = lerp(gy_, ey, ts) - 30 * np.sin(ts * math.pi)
    for i in range(0, 60, 4): c.blob(px[i], py[i], 22, (120, 160, 255), 0.07 * p)
    n = max(2, int(60 * p)); c.line(np.stack([px[:n], py[:n]], 1), ICE, 3, 0.95, 1.2)
    c.blob(gx_, gy_, 16, WARM, 0.7); c.dot(gx_, gy_, 5, WARM, 1.0)
    c.dot(ex, ey, 7, CY2, 1.0); c.ring(ex, ey, 14 + 3 * math.sin(tg * 3), CY2, 2, 0.8, 0.8)
    vm = 0.80; vx, vy = px[int(vm * 59)], py[int(vm * 59)]; va = fin(u, 0.45, 0.65)
    c.ring(vx, vy, 20, WARM, 2, va, 0.8)
    y = H * 0.665; xa, xb = 90, 630; xm = xa + (xb - xa) * 3.0 / 13.8; hp = fin(u, 0.3, 0.6)
    c.line([(xa, y), (xb, y)], GREY, 4, 0.6, 0); c.line([(xm, y), (xm + (xb - xm) * hp, y)], CY2, 4, 0.95, 1.0)
    its = [badge("SIMULATION · NOT TO SCALE"), I(ex, ey + 34, "EARTH", 15, CY2, 0.9, 'Medium'), I(gx_ - 6, gy_ - 28, "HOST GALAXY", 15, WARM, 0.9, 'Medium', 'rm'),
           I(vx + 26, vy + 4, "VIRGO CLUSTER", 16, WARM, va, 'Medium', 'lm'),
           I(CX, H * 0.62, "ABOUT 80% OF COSMIC HISTORY", 22, CY2, fin(u, 0.35, 0.6), 'Medium'),
           I(xa, y + 28, "BIG BANG", 14, GREY, 0.9, 'Medium', 'lm'), I(xb, y + 28, "TODAY", 14, GREY, 0.9, 'Medium', 'rm')]
    return frame(c, its)

# ---------- x16: pull back into the Universe + the question ----------
_RP = np.random.default_rng(51); NP = 160
_PXW = _RP.uniform(-34, 34, NP); _PYW = _RP.uniform(-50, 50, NP); _PCI = _RP.choice(3, NP, p=[.5, .35, .15]); _PSZ = _RP.uniform(0.6, 1.6, NP)
_SIG = [(80.0, 400.0, 0.5, -0.3), (640.0, 260.0, -0.4, 0.2), (150.0, 980.0, 0.3, 0.4), (600.0, 880.0, -0.5, -0.2), (330.0, 300.0, 0.0, 0.5), (60.0, 620.0, 0.45, 0.1)]
def x16(t, T, tg, cap):
    u = t / T
    k = sm(A(u, 0.0, 0.85)); sc = math.exp(lerp(math.log(250.0), math.log(11.0), k))
    c = cvz(1 + 0.05 * u, dim=0.3); cx_, cy_ = CX, H * 0.44
    for i in range(NP):
        x = cx_ + _PXW[i] * sc; y = cy_ + _PYW[i] * sc
        if x < -30 or x > W + 30 or y < -30 or y > H + 30: continue
        a = 0.55 * fin(u, 0.04, 0.4)
        c.blob(x, y, max(1.5, _PSZ[i] * 2.4), _GCOL[_PCI[i]], a)
    for sx, sy, vx, vy in _SIG:
        a = fin(u, 0.40, 0.6)
        if a < 0.02: continue
        x = sx + vx * 40 * (u - 0.4) * 3; y = sy + vy * 40 * (u - 0.4) * 3
        c.blob(x, y, 7, CY2, 0.5 * a); c.dot(x, y, 2.5, (255, 255, 255), a); c.ring(x, y, 10 + 5 * math.sin(tg * 3 + sx), CY2, 1, 0.5 * a, 0.4)
    img = screen(c.out(), dwarf_layer(cx_, cy_, sc * 0.9, 0.5 + 0.3 * u, tg) * (1 - 0.6 * k))
    y1 = H * 0.215; qa = fin(u, 0.33, 0.43); oa = 1 - fin(u, 0.26, 0.32)
    its = [badge("SIMULATION"),
           I(CX, y1, "1 FLASH", 38, WHITE, fin(u, 0.0, 0.05) * oa), I(CX, y1 + 44, "MILLISECONDS", 38, WHITE, fin(u, 0.05, 0.1) * oa), I(CX, y1 + 84, "10+ BILLION YEARS IN TRANSIT", 22, CY2, fin(u, 0.1, 0.17) * oa, 'Medium'),
           I(CX, H * 0.30, "HOW MANY MORE MESSAGES", 34, ICE, qa * 0.92, 'Regular'), I(CX, H * 0.30 + 46, "ARE STILL CROSSING THE DARK?", 34, ICE, fin(u, 0.37, 0.47) * 0.92, 'Regular')]
    return frame(img, its)

IDS = ['x01_flash', 'x02_travel', 'x03_title', 'x04_blink', 'x05_dishes', 'x06_waterfall', 'x07_empty', 'x08_webb', 'x09_host', 'x10_redshift', 'x11_dwarf', 'x12_magnetar', 'x13_flashlight', 'x14_web', 'x15_sightline', 'x16_pullback']
_F = [x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12, x13, x14, x15, x16]
FUNCSX = dict(zip(IDS, _F)); STARTX = {k: 0.0 for k in IDS}
