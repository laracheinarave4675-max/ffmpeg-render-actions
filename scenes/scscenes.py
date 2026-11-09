"""Vertical 9:16 scenes (720x1280) for the Short 'How Small We Really Are': one continuous pull-back from a human to the observable universe. Ids z01..z08.
All scenes are original illustrations/simulations (labelled). Facts: Sun = 1.3 million Earths by volume; Moon = 30 Earth-widths away; Neptune = 30 AU; Milky Way ~100,000 ly across, Sun ~26,000 ly from the centre; Andromeda 2.5 Mly; observable universe ~93 billion ly across."""
from pdscenes import *
_Y, _X = np.mgrid[0:H, 0:W].astype(np.float32)
_GCOL = [(170, 200, 255), (255, 255, 255), (255, 200, 150)]

def earth_sp(cx, cy, R, t, tex):
    x0, x1 = int(max(cx - R - 2, 0)), int(min(cx + R + 3, W)); y0, y1 = int(max(cy - R - 2, 0)), int(min(cy + R + 3, H))
    if x1 <= x0 or y1 <= y0: return None
    nx = (_X[y0:y1, x0:x1] - cx) / R; ny = (_Y[y0:y1, x0:x1] - cy) / R; r2 = nx ** 2 + ny ** 2
    m = (r2 < 1.0).astype(np.float32); nz = np.sqrt(np.clip(1 - r2, 0, 1))
    lon = np.arctan2(nx, nz) + 0.18 * t; lat = np.arcsin(np.clip(-ny, -1, 1))
    land = np.sin(2.1 * lon + 1.7 * lat) + 0.7 * np.sin(4.3 * lat - 1.9 * lon + 1.0) + 0.5 * np.sin(6.7 * lon + 3.1 * lat + 2.0) + 0.3 * np.sin(11 * lon - 5 * lat)
    isl = np.clip((land - 0.55) * 4, 0, 1)[..., None]
    ocean = np.array([0.04, 0.18, 0.46], np.float32) * (0.7 + 0.3 * nz[..., None]); ground = np.array([0.22, 0.42, 0.20], np.float32) * (0.8 + 0.4 * np.sin(lat * 9)[..., None] ** 2)
    col = ocean * (1 - isl) + ground * isl
    cl = np.clip(np.sin(3 * lon + 2 * lat + t * 0.3) * np.sin(5 * lat - 2 * lon) * 2.2 - 0.2, 0, 1)[..., None]
    col = col * (1 - 0.7 * cl) + 0.7 * cl
    Ld = np.array([-0.5, -0.55, 0.65], np.float32); Ld /= np.linalg.norm(Ld)
    dif = np.clip(nx * Ld[0] + ny * Ld[1] + nz * Ld[2], 0, 1)
    out = col * (0.04 + 0.96 * dif[..., None] ** 0.8) + np.array([0.3, 0.55, 1.0], np.float32) * (((1 - nz) ** 2.5) * (0.25 + 0.75 * dif))[..., None]
    out = np.array([0.02, 0.03, 0.06], np.float32) * (1 - tex) + out * tex
    return out * m[..., None], m, (y0, y1, x0, x1)
def land_sky(dim=0.55, mw=0.18):
    c = cvz(1.0, dim=dim); d = np.abs((_X - CX) * 0.8 + (_Y - H * 0.25) * 0.6)
    c.im += (np.exp(-(d / 110.0) ** 2) * mw)[..., None] * np.array([0.5, 0.6, 0.9], np.float32); return c
def human(img, hx, hy, fs):
    pts = (np.array([(-5, 0), (-6, -30), (-3, -46), (3, -46), (6, -30), (5, 0)], np.float32) * fs * 1.4 + np.array([hx, hy], np.float32)).astype(np.int32)
    cv2.fillPoly(img, [pts], (0.0, 0.0, 0.0)); cv2.circle(img, (int(hx), int(hy - 52 * fs * 1.4)), max(1, int(6 * fs * 1.4)), (0.0, 0.0, 0.0), -1)

# ---------- z01: a human, then the whole Earth ----------
def z01(t, T, tg, cap):
    u = t / T; k = sm(A(u, 0.38, 1.0)); R = math.exp(lerp(math.log(1800.0), math.log(40.0), k)); ylimb = lerp(H * 0.64, H * 0.44 - 40, k); cy = ylimb + R
    c = land_sky(0.55, 0.18 * (1 - k)); c.blob(CX, ylimb, 170, (60, 90, 160), 0.35 * (1 - k)); img = c.out()
    paste(img, earth_sp(CX, cy, R, tg, fin(u, 0.30, 0.55)))
    if u < 0.6: human(img, CX, ylimb + 2, lerp(1.0, 0.06, min(1.0, k * 2.0)))
    its = [badge("ILLUSTRATION"), I(CX, H * 0.70, "EARTH · 12,742 KM ACROSS", 22, WHITE, fin(u, 0.75, 0.92), 'Medium')]
    return frame(img, its)

# ---------- z02: the Moon is 30 Earths away; the Sun holds 1.3 million Earths ----------
def z02(t, T, tg, cap):
    u = t / T; cx, cy = CX, H * 0.44; a1 = 1 - fin(u, 0.42, 0.52); a2 = fin(u, 0.48, 0.6)
    Re = 40.0 * (1 / 8.0) ** sm(A(u, 0.0, 0.4)); c = land_sky(0.5, 0.0); its = [badge("ILLUSTRATION")]
    if a1 > 0.01:
        ro = 60 * Re; th = np.linspace(0, 2 * math.pi, 160)
        if ro < 520: dashed(c, cx + ro * np.cos(th), cy + ro * np.sin(th), GREY, 1, 0.5 * a1)
        ang = -0.6 + 0.4 * tg; mx, my = cx + ro * math.cos(ang), cy + ro * math.sin(ang)
        c.blob(mx, my, max(2, 0.6 * Re), (200, 200, 205), 0.7 * a1); c.dot(mx, my, max(1.5, 0.27 * Re), (210, 210, 215), a1)
        img = c.out(); paste(img, earth_sp(cx, cy, Re, tg, 1.0), a1)
        if Re < 7.0: its += [I(CX, H * 0.62, "THE MOON · 384,000 KM", 22, WHITE, a1 * fin(u, 0.25, 0.4), 'Medium'), I(CX, H * 0.655, "30 EARTHS SIDE BY SIDE", 18, CY2, a1 * fin(u, 0.3, 0.42), 'Medium')]
    else: img = c.out()
    if a2 > 0.01:
        sx, sy, SR = 215, H * 0.40, 220.0; pa = a2
        c2 = cvz(1.0, dim=0.5); c2.blob(sx, sy, SR * 1.7, (255, 200, 120), 0.4 * pa); img2 = c2.out(); star(img2, sx, sy, SR, 0.0, tg)
        ex, ey = 600, H * 0.40; c2b = Cv(); c2b.im = img2; c2b.dot(ex, ey, 2.2, (120, 190, 255), 1.0); c2b.ring(ex, ey, 9, CY2, 1, 0.9, 0.5); img2 = c2b.out()
        img = img * (1 - pa) + img2 * pa
        n = int(1300000 * sm(A(u, 0.55, 0.92)))
        its += [I(CX, H * 0.60, "{:,}".format(n), 54, WHITE, pa * fin(u, 0.55, 0.7)), I(CX, H * 0.655, "EARTHS FIT INSIDE THE SUN (BY VOLUME)", 17, CY2, pa * fin(u, 0.6, 0.75), 'Medium'),
                I(ex, ey + 26, "EARTH", 13, CY2, pa, 'Medium'), I(CX, H * 0.69, "sizes to scale · not distances", 13, GREY, pa * fin(u, 0.7, 0.85), 'Regular')]
    return frame(img, its)

# ---------- z03: the Solar System shrinks to one star among many ----------
_AU = [(0.39, (190, 180, 170)), (0.72, (230, 200, 150)), (1.0, (110, 170, 255)), (1.52, (230, 120, 90)), (5.2, (230, 190, 150)), (9.58, (230, 215, 160)), (19.2, (150, 220, 230)), (30.05, (90, 130, 255))]
_RS3 = np.random.default_rng(5); _SX = _RS3.normal(0, 1, 7000); _SY = _RS3.normal(0, 1, 7000)
def z03(t, T, tg, cap):
    u = t / T; cx, cy = CX, H * 0.44
    ppa = 150.0 * (9.3 / 150.0) ** sm(A(u, 0.0, 0.45)); s2 = math.exp(lerp(0.0, math.log(70.0), sm(A(u, 0.45, 1.0))))
    c = cvz(1.0, dim=0.4); its = [badge("SIMULATION · ILLUSTRATIVE")]; k = 1.0 / s2
    a_orb = 1 - fin(u, 0.55, 0.8)
    for i, (au, col) in enumerate(_AU):
        r = au * ppa * k; th = np.linspace(0, 2 * math.pi, 120)
        if 1.0 < r < 700: c.line(np.stack([cx + r * np.cos(th), cy + r * np.sin(th)], 1), col, 1, 0.45 * a_orb, 0.3)
        ang = tg * (0.9 / math.sqrt(au)) + i; px, py = cx + r * math.cos(ang), cy + r * math.sin(ang)
        if r > 2.0: c.dot(px, py, 2.0 + (1.5 if au > 5 else 0), col, a_orb)
    c.blob(cx, cy, 16, (255, 220, 150), 0.9); c.dot(cx, cy, 3.5, (255, 240, 200), 1.0)
    img = c.out(); sa = fin(u, 0.5, 0.8)
    img = screen(img, layer(cx + _SX * 150 * (0.4 + 0.6 * sm(A(u, 0.45, 1.0))) * 0.6 * s2 ** 0.35, cy + _SY * 230 * (0.4 + 0.6 * sm(A(u, 0.45, 1.0))) * 0.6 * s2 ** 0.35, np.ones((7000, 3), np.float32) * np.array([0.75, 0.85, 1.0], np.float32) * 0.5, 1.0, 2.0) * sa)
    its += [I(CX, H * 0.64, "NEPTUNE · 30 TIMES EARTH'S DISTANCE FROM THE SUN", 15, GREY, fin(u, 0.3, 0.45) * (1 - fin(u, 0.5, 0.6)) * a_orb, 'Medium'),
            I(CX, H * 0.66, "ONE STAR AMONG HUNDREDS OF BILLIONS", 22, WHITE, fin(u, 0.6, 0.85), 'Medium')]
    return frame(img, its)

# ---------- z04: the Milky Way ----------
_RM = np.random.default_rng(14); NMW = 9000
_r = 0.04 + 0.96 * _RM.random(NMW) ** 0.75; _arm = _RM.integers(0, 4, NMW); _th = np.log(_r / 0.04) * 3.0 + _arm * (math.pi / 2) + _RM.normal(0, 0.22, NMW) * (0.4 + _r)
