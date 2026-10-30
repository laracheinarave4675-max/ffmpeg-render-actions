import numpy as np, cv2, math
from engine import *
GOLD = (255, 214, 120); CYAN = (120, 220, 255); WHITE = (240, 245, 255); RED = (255, 120, 110); GREEN = (140, 235, 170); VIOLET = (190, 150, 255); GREY = (150, 160, 180)
TAGS = {'ill': 'ILLUSTRATION', 'sim': 'SIMULATION', 'sch': 'SCHEMATIC'}
def A(u, a, b): return float(np.clip((u - a) / (b - a), 0, 1))
def fin(u, a, b): return sm(A(u, a, b))
def I(x, y, t, s=34, c=WHITE, a=1.0, w='Bold', an='mm'): return {'k': 'text', 'x': x, 'y': y, 't': t, 's': s, 'c': c, 'a': a, 'w': w, 'an': an}
def col01(c): return np.array(c, np.float32)[::-1][::-1] / 255.0
class Cv:
    """float canvas with additive glowing primitives"""
    def __init__(s, bg=0.6, bgdim=0.5):
        s.im = (BG * bg * bgdim).astype(np.float32).copy()
        s.gl = np.zeros((H, W, 3), np.float32)
    def _c(s, c, a): return tuple(float(v) * a / 255.0 for v in c)
    def line(s, pts, c=CYAN, w=2, a=1.0, glow=1.0):
        p = np.round(np.array(pts, np.float32) * 16).astype(np.int32).reshape(-1, 1, 2)
        cc = s._c(c, a)
        cv2.polylines(s.im, [p], False, cc, w, cv2.LINE_AA, shift=4)
        if glow > 0: cv2.polylines(s.gl, [p], False, tuple(v * glow for v in cc), w + 3, cv2.LINE_AA, shift=4)
    def dot(s, x, y, r=6, c=WHITE, a=1.0, glow=1.0):
        cc = s._c(c, a)
        cv2.circle(s.im, (int(x), int(y)), int(max(r, 1)), cc, -1, cv2.LINE_AA)
        if glow > 0: cv2.circle(s.gl, (int(x), int(y)), int(max(r * 2.2, 2)), tuple(v * glow for v in cc), -1, cv2.LINE_AA)
    def ring(s, x, y, r, c=CYAN, w=2, a=1.0, glow=1.0):
        cc = s._c(c, a)
        cv2.circle(s.im, (int(x), int(y)), int(max(r, 1)), cc, w, cv2.LINE_AA)
        if glow > 0: cv2.circle(s.gl, (int(x), int(y)), int(max(r, 1)), tuple(v * glow for v in cc), w + 3, cv2.LINE_AA)
    def poly(s, pts, c, a=0.3):
        cv2.fillPoly(s.im, [np.round(np.array(pts)).astype(np.int32)], s._c(c, a))
    def blob(s, x, y, r, c, a=0.5):
        """soft radial glow"""
        x0, x1 = int(max(x - r * 3, 0)), int(min(x + r * 3, W)); y0, y1 = int(max(y - r * 3, 0)), int(min(y + r * 3, H))
        if x1 <= x0 or y1 <= y0: return
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        g = np.exp(-(((xx - x) ** 2 + (yy - y) ** 2) / (2 * r * r)))[:, :, None]
        s.gl[y0:y1, x0:x1] += g * np.array(s._c(c, a), np.float32)
    def out(s, k=1.0):
        g = cv2.GaussianBlur(s.gl, (0, 0), 7) * 1.6 + cv2.GaussianBlur(s.gl, (0, 0), 2.2) * 0.8 + s.gl * 0.2
        return np.clip(1 - (1 - np.clip(s.im, 0, 1)) * np.exp(-g * k), 0, 1)
def frame(cv_or_img, items=(), cap=None, tag=None, fade=1.0, k=1.0):
    img = cv_or_img.out(k) if isinstance(cv_or_img, Cv) else cv_or_img
    return overlay(vignette(img), list(items), caption=cap, tag=tag, fade=fade)
def title_items(lines, u, y0=360, sizes=None, cols=None, gap=70, start=0.05, step=0.12, dur=0.2):
    its = []
    n = len(lines)
    for i, ln in enumerate(lines):
        a = fin(u, start + i * step, start + i * step + dur)
        sz = (sizes or [54] * n)[i]; cc = (cols or [WHITE] * n)[i]
        its.append(I(640, y0 + (i - (n - 1) / 2) * gap + (1 - a) * 12, ln, sz, cc, a))
    return its
# ---------- string primitives ----------
def string_open(cv, x1, x2, y, mode, t, amp=40, c=CYAN, w=3, n=240, speed=2.2, a=1.0):
    xs = np.linspace(x1, x2, n); L = x2 - x1
    ys = y + amp * np.sin(mode * np.pi * (xs - x1) / L) * np.cos(speed * mode * 0.6 * t)
    cv.line(np.stack([xs, ys], 1), c, w, a)
    cv.dot(x1, y, 5, c, a); cv.dot(x2, y, 5, c, a)
def string_loop(cv, cx, cy, r, mode, t, amp=0.18, c=CYAN, w=3, n=260, speed=2.0, a=1.0, tilt=1.0, rot=0.0):
    th = np.linspace(0, 2 * np.pi, n)
    rr = r * (1 + amp * np.sin(mode * th + rot) * np.cos(speed * t))
    pts = np.stack([cx + rr * np.cos(th), cy + rr * np.sin(th) * tilt], 1)
    cv.line(pts, c, w, a)
def project(P, ax, ay, f=700, d=4.0, cx=640, cy=360):
    ca, sa = math.cos(ax), math.sin(ax); cb, sb = math.cos(ay), math.sin(ay)
    X, Y, Z = P[..., 0], P[..., 1], P[..., 2]
    y1 = Y * ca - Z * sa; z1 = Y * sa + Z * ca
    x2 = X * cb + z1 * sb; z2 = -X * sb + z1 * cb
    k = f / (d + z2)
    return np.stack([cx + x2 * k, cy + y1 * k], -1), z2
def grid_well(cv, cx, cy, depth, t=0.0, span=520, n=21, c=(110, 170, 255), a=0.7, tiltk=0.42, sig=140):
    """spacetime grid with gravity well, perspective-ish"""
    xs = np.linspace(-1, 1, n); m = 90
    ts = np.linspace(-1, 1, m)
    def pt(u, v):
        X = u * span; Z = v * span * 0.75
        r2 = X * X + Z * Z
        h = depth * np.exp(-r2 / (2 * sig * sig))
        sx = cx + X * (1 + 0.0004 * Z); sy = cy + Z * tiltk + h
        return np.stack([sx, sy], -1)
    for u in xs:
        cv.line(pt(np.full(m, u), ts), c, 1, a, 0.4)
    for v in xs:
        cv.line(pt(ts, np.full(m, v)), c, 1, a, 0.4)
    return lambda X, Z: (cx + X, cy + Z * tiltk + depth * np.exp(-(X * X + Z * Z) / (2 * sig * sig)))
def ladder(cv, items_u, levels, y0=600, y1=130, x=300, hi=None, ulog=True):
    pass
def checker_wave(cv, x, y, r, t, c=CYAN):
    for k in range(4):
        ph = (t * 0.6 + k * 0.25) % 1.0
        cv.ring(x, y, r * ph, c, 2, (1 - ph) * 0.8)
def particle(cv, x, y, r, c, a=1.0, label=None, items=None, ls=20):
    cv.blob(x, y, r * 1.6, c, 0.5 * a); cv.dot(x, y, r, c, a)
    if label is not None and items is not None: items.append(I(x, y + r + 26, label, ls, WHITE, a))
def starsbg(cv_dim=0.5): return Cv(0.6, cv_dim)
def poincare_geodesic(a, b, R, cx, cy):
    """arc orthogonal to boundary circle between boundary angles a,b"""
    d = (b - a + math.pi) % (2 * math.pi) - math.pi
    if abs(d) < 1e-3: return np.array([[cx + R * math.cos(a), cy + R * math.sin(a)]] * 2)
    if abs(abs(d) - math.pi) < 1e-3:
        return np.array([[cx + R * math.cos(a), cy + R * math.sin(a)], [cx + R * math.cos(b), cy + R * math.sin(b)]])
    m = a + d / 2; h = abs(d) / 2
    rc = R * math.tan(h); dc = R / math.cos(h)
    ccx = cx + dc * math.cos(m); ccy = cy + dc * math.sin(m)
    a0 = math.atan2(cy + R * math.sin(a) - ccy, cx + R * math.cos(a) - ccx)
    a1 = math.atan2(cy + R * math.sin(b) - ccy, cx + R * math.cos(b) - ccx)
    dd = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    tt = np.linspace(0, 1, 60)
    ang = a0 + dd * tt
    return np.stack([ccx + rc * np.cos(ang), ccy + rc * np.sin(ang)], 1)
def calabi_yau(n=5, na=9, nb=9, res=14):
    """Hanson Calabi-Yau 2D cross-section -> list of 3D polylines"""
    lines = []
    a = np.linspace(-1, 1, res)
    b = np.linspace(0, math.pi / 2, res)
    def pt(k1, k2, aa, bb):
        z = aa + 1j * bb
        z1 = np.exp(2j * math.pi * k1 / n) * np.cosh(z) ** (2.0 / n)
        z2 = np.exp(2j * math.pi * k2 / n) * (1j * np.sinh(z)) ** (2.0 / n)
        z2 = np.exp(2j * math.pi * k2 / n) * (-1j * np.sinh(z)) ** (2.0 / n)
        return z1, z2
    al = 0.6
    for k1 in range(n):
        for k2 in range(n):
            for ai in a:
                z1, z2 = pt(k1, k2, np.full(res, ai), b)
                lines.append(np.stack([z1.real, z2.real, z1.imag * math.cos(al) + z2.imag * math.sin(al)], 1))
            for bi in b:
                z1, z2 = pt(k1, k2, a, np.full(res, bi))
                lines.append(np.stack([z1.real, z2.real, z1.imag * math.cos(al) + z2.imag * math.sin(al)], 1))
    return lines
_CY = {}
def cy_lines(n=5):
    if n not in _CY: _CY[n] = calabi_yau(n)
    return _CY[n]
