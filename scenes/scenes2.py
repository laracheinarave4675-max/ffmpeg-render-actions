import sys
import scenes as S1
from scenes import *

SEQ2 = [
 ('t17_stranger', "The real answer is stranger. And, I think, far more beautiful.", 1),
 ('t18_three', "Because to answer it honestly, we need three things.", 0),
 ('t19_what', "We need to know what TON six-eighteen really is, and how much of it we have truly measured.", 0),
 ('t20_gravity', "We need to understand what gravity actually does, which is not what most movies taught us.", 0),
 ('t21_fall', "And we need to ask the question that decides everything: what does it take, physically, to make a single star fall into a black hole?", 0),
 ('t22_keep', "Keep that last question in mind. We will come back to it.", 1),
 ('t23_meet', "But first, let us meet the monster.", 1),
 ('t24_catalog', "Long before anyone suspected what it was, TON six-eighteen was just a number in a catalog.", 0),
 ('t25_plate', "Astronomers at the Tonantzintla Observatory in Mexico had photographed the sky on glass plates, and on one of them a faint point looked strangely violet.", 0),
 ('t26_entry', "They gave it entry number six hundred and eighteen. A star, most likely. Nothing more.", 1),
 ('t27_notstar', "It was not a star.", 1),
 ('t28_radio', "In nineteen seventy, radio telescopes detected emission from that point.", 0),
 ('t29_spectra', "Then spectra revealed lines of glowing gas shifted far toward the red.", 0),
 ('t30_shift', "A shift that large meant the light had been traveling for an immense time.", 0),
 ('t31_z', "The redshift is about two point two, which corresponds to a light travel time of roughly ten point eight billion years.", 0),
 ('t32_age', "The light we collect tonight left TON six-eighteen when the universe was only about three billion years old.", 1),
 ('t33_quasar', "At that distance, nothing ordinary could possibly be seen. TON six-eighteen is visible only because it is one of the brightest objects known. It is a quasar.", 0),
 ('t34_confuse', "And this is where people often confuse two different things. The black hole itself is dark. A quasar is what happens when a black hole is being fed.", 0),
 ('t35_disk', "Gas spirals inward, forms a rotating disk, and rubs against itself as it falls, heating to millions of degrees. That disk is what shines.", 0),
 ('t36_lum', "TON six-eighteen emits about as much light as one hundred and forty trillion Suns. Thousands of times more than the entire Milky Way.", 1),
 ('t37_weigh', "So how do you weigh something you cannot see? You watch what orbits it.", 0),
 ('t38_fast', "Gas near a black hole moves fast, and the faster it moves, the more mass is needed to hold it.", 0),
 ('t39a_smear', "Astronomers measure how widely that gas smears the colors of its light, estimate its distance from the brightness of the quasar,", 0),
 ('t39b_earth', "and apply the same logic we use to weigh the Sun from the orbit of the Earth.", 1),
 ('t40_est', "One study, using the light of hydrogen, arrived at roughly sixty-six billion solar masses. A later analysis, using a different spectral line, found closer to forty.", 0),
 ('t41_honest', "Neither number is a direct weighing. Both are estimates built on assumptions. The honest summary is this: tens of billions of Suns, among the heaviest black holes ever inferred.", 1),
 ('t42_look', "And what does it look like? Nobody knows.", 0),
 ('t43_eht', "We have photographed the shadows of two black holes, one in the galaxy M eighty-seven, and the one at the center of our own.", 0),
 ('t44_unseen', "TON six-eighteen is far too distant for that. Every picture of it you have seen is an artist's imagination, or a simulation. The real thing, up close, has never been seen by any human eye or instrument.", 1),
 ('t45_suck', "Here is the first thing that has to be corrected. Black holes do not suck.", 1),
 ('t46_curve', "Gravity does not care what an object is made of, or how dense it has become. At a distance, it cares about only two things: how much mass there is, and how far away you are. That is all.", 0),
 ('t47_replace', "Replace the Sun, tonight, with a black hole of exactly the same mass, and the Earth would keep orbiting along exactly the same path. It would be dark, and cold, and miserable. But it would not fall in.", 1),
 ('t48_ordinary', "A black hole is not a stronger kind of gravity. It is ordinary gravity, concentrated into a place so small that you can get dangerously close to the center. Far away, it is just mass.", 1),
 ('t49_missing', "So why does anything fall in at all? Think about the Earth. Right now, our planet is falling toward the Sun. It has been falling for four and a half billion years. And it keeps missing.", 0),
 ('t50_sideways', "Because it is also moving sideways, at about thirty kilometers every second. Gravity bends that path into a curve, and the sideways motion carries the planet past the Sun again and again.", 0),
 ('t51_orbit', "An orbit is not the opposite of falling. An orbit is falling, with enough sideways speed to keep missing.", 1),
 ('t52_ang', "Physicists call that sideways quantity angular momentum, and it is the hero of this story. To fall into a massive object, something must give up its angular momentum. It has to be slowed, or nudged, or robbed of that sideways motion. Without that, it circles. Forever.", 1),
 ('t53_sstars', "Add more mass, and the orbit does not collapse. It simply gets faster. In our own galaxy, stars race around the black hole Sagittarius A star at thousands of kilometers per second. One of them completes a full circuit in only about sixteen years. They do not fall in. They orbit.", 1),
 ('t54_principle', "This is the principle we will carry forward. Gravity pulls. But only the loss of orbital motion lets anything arrive.", 1),
]
BASE = S1.TOTAL
DUR2 = {k: S1.est(t, p) for k, t, p in SEQ2}
START2 = {}; acc = BASE
for k, t, p in SEQ2:
    START2[k] = acc; acc += DUR2[k]
TOTAL2 = acc - BASE

GOLD = (255, 215, 120); CY = (120, 220, 255); WH = (240, 245, 255); GR = (160, 170, 190)

def dark(m=0.5): return BG * m
def circ(img, x, y, r, col, th=-1):
    cv2.circle(img, (int(x), int(y)), int(max(r, 1)), col, th, cv2.LINE_AA)
def glowdot(img, x, y, r, col, g=3.0):
    r = max(r, 1.5)
    R = int(r * g * 3 + r + 4)
    x = int(x); y = int(y)
    x0, x1, y0, y1 = max(0, x - R), min(W, x + R), max(0, y - R), min(H, y + R)
    if x1 <= x0 or y1 <= y0: return img
    q = 4 if r * g > 12 else 1
    h, w = y1 - y0, x1 - x0
    lay = np.zeros((max(1, h // q), max(1, w // q), 3), np.float32)
    cv2.circle(lay, ((x - x0) // q, (y - y0) // q), max(1, int(r / q)), col, -1, cv2.LINE_AA)
    bl = cv2.GaussianBlur(lay, (0, 0), max(0.6, r * g / q)) * 2.2 + lay
    add = cv2.resize(bl, (w, h), interpolation=cv2.INTER_LINEAR)
    if q == 1:
        full = np.zeros((h, w, 3), np.float32); cv2.circle(full, (x - x0, y - y0), int(r), col, -1, cv2.LINE_AA); add = add * 0 + cv2.GaussianBlur(full, (0, 0), r * g) * 2.2 + full
    add = np.clip(add, 0, 1)
    img[y0:y1, x0:x1] = 1 - (1 - img[y0:y1, x0:x1]) * (1 - add)
    return img
def poly(img, pts, col, th=2):
    cv2.polylines(img, [np.array(pts, np.int32).reshape(-1, 1, 2)], False, col, th, cv2.LINE_AA)

# ---- orbit tools ----
_tc = {}
def traj(key, x0, y0, vx, vy, GM, dt, steps, drag=0.0):
    if key in _tc: return _tc[key]
    p = np.zeros((steps, 2)); x = np.array([x0, y0], float); v = np.array([vx, vy], float)
    for i in range(steps):
        p[i] = x
        r = np.linalg.norm(x) + 1e-9
        v += (-GM * x / r ** 3 - drag * v) * dt; x += v * dt
        if r < 0.04: p[i:] = x; break
    _tc[key] = p; return p
def trail(img, pts, i, cx, cy, sc, col, n=70, step=2):
    lo = max(0, i - n * step)
    seg = pts[lo:i + 1:step]
    for k in range(1, len(seg)):
        a = k / len(seg)
        cv2.line(img, (int(cx + seg[k - 1][0] * sc), int(cy + seg[k - 1][1] * sc)), (int(cx + seg[k][0] * sc), int(cy + seg[k][1] * sc)),
                 tuple(c * a for c in col), 2, cv2.LINE_AA)
def center_obj(img, kind, cx, cy, r):
    if kind == 'sun':
        return glowdot(img, cx, cy, r, (1.0, 0.85, 0.4), 2.0)
    if r < 2: return img
    circ(img, cx, cy, r * 1.35, (1.0, 0.6, 0.25), 3); circ(img, cx, cy, r, (0, 0, 0))
    return glowdot(img, cx, cy, r * 1.4, (1.0, 0.55, 0.2), 1.2)
def planet_xy(pts, i, cx, cy, sc): return cx + pts[i][0] * sc, cy + pts[i][1] * sc

# ---- accretion disk ----
class Disk:
    def __init__(s, n=70000, seed=11):
        rng = np.random.default_rng(seed)
        s.r0 = 1.0 + rng.random(n) ** 1.6 * 5.0
        s.ph = rng.random(n) * 2 * np.pi
        s.f = rng.random(n)
        s.j = rng.normal(0, 0.012, n)
D = Disk()
def disk_layer(tg, cx, cy, sc, tilt=74, inflow=0.0, expo=1.0, rot=0.9):
    r = D.r0.copy()
    if inflow > 0:
        f = (D.f + tg * 0.08 * inflow) % 1.0
        r = 1.0 + (D.r0 - 1.0) * (1 - f) ** 1.5 + 0.0
        r = np.maximum(r, 1.0)
    ph = D.ph + tg * rot * r ** -1.5 * 3.0
    x = r * np.cos(ph); y = r * np.sin(ph) * np.cos(np.radians(tilt)); z = r * np.sin(ph) * np.sin(np.radians(tilt))
    sx = (cx + x * sc).astype(np.int32); sy = (cy + y * sc + D.j * sc * 4).astype(np.int32)
    ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
    heat = np.clip(1.0 - (r - 1.0) / 4.0, 0, 1)
    col = np.stack([1.0 * np.ones_like(heat), 0.45 + 0.5 * heat, 0.15 + 0.8 * heat ** 2], 1)
    br = r ** -1.1 * (1 + 0.55 * np.sin(ph)) * 0.55
    w = col * br[:, None]
    lay = np.zeros((H, W, 3), np.float32); idx = sy[ok] * W + sx[ok]
    for ch in range(3): lay[:, :, ch] = np.bincount(idx, weights=w[ok, ch], minlength=W * H).reshape(H, W)
    gl = cv2.GaussianBlur(lay, (0, 0), 3) * 1.4 + lay * 0.8
    return 1 - np.exp(-gl * expo * 1.3)
def quasar(tg, cx, cy, sc, expo=1.0, inflow=0.0, bgdim=0.7, thmul=1.15):
    base = screen(BG * bgdim, disk_layer(tg, cx, cy, sc, inflow=inflow, expo=expo))
    return lens(base, cx, cy, sc * thmul, shadow=True, ring=True)

# ---------------- scenes ----------------
def three_card(t, T, tg, cap, stage):
    u = t / T
    img = lens(BG * 0.55, 1060, 380, 120)
    items = [{'k': 'text', 'x': 560, 'y': 100, 't': 'THREE THINGS', 's': 54, 'c': WH}]
    rows = [(250, '1', 'WHAT IS TON 618?', 'AND WHAT HAVE WE TRULY MEASURED?'),
            (390, '2', 'WHAT DOES GRAVITY ACTUALLY DO?', ''),
            (530, '3', 'WHAT MAKES A STAR FALL IN?', '')]
    for i, (y, n, a, b) in enumerate(rows):
        show = 1.0 if (stage > i) else (sm(A(u, 0.1, 0.35)) if stage == i else 0.0)
        hl = 1.0 if (stage == 4 and i == 2) else (0.35 if stage == 4 else 1.0)
        items += [{'k': 'ring', 'x': 110, 'y': y, 'r': 36, 'c': GOLD, 'wd': 3, 'a': 0.9 * show * hl},
                  {'k': 'text', 'x': 110, 'y': y, 't': n, 's': 40, 'c': GOLD, 'a': show * hl},
                  {'k': 'text', 'x': 180, 'y': y - (14 if b else 0), 't': a, 's': 36, 'c': WH, 'an': 'lm', 'a': show * hl},
                  {'k': 'text', 'x': 180, 'y': y + 28, 't': b, 's': 22, 'w': 'Medium', 'c': GR, 'an': 'lm', 'a': show * hl}]
    if stage == 3:
        p = sm(A(u, 0.2, 0.95))
        sx = lerp(760, 1010, p); sy = lerp(150, 380, p ** 1.6)
        items.append({'k': 'dot', 'x': sx, 'y': sy, 'r': 7, 'c': (255, 245, 210)})
    return overlay(vignette(img), items, caption=cap)
def f_t17(t, T, tg, cap):
    u = t / T
    img = enc(tg, 320, 380, 210, 58, 950, 350, lerp(100, 125, u), expo=0.8)
    return overlay(vignette(img), caption=cap, tag=TAG)
def f_t18(t, T, tg, cap): return three_card(t, T, tg, cap, 0)
def f_t19(t, T, tg, cap): return three_card(t, T, tg, cap, 1)
def f_t20(t, T, tg, cap): return three_card(t, T, tg, cap, 2)
def f_t21(t, T, tg, cap): return three_card(t, T, tg, cap, 3)
def f_t22(t, T, tg, cap): return three_card(t, T, tg, cap, 4)
def f_t23(t, T, tg, cap):
    u = sm(t / T)
    img = quasar(tg, 640, 360, lerp(40, 190, u), expo=1.0)
    return overlay(vignette(img), caption=cap, tag=TAG)

def catalog(t, T, tg, cap):
    u = t / T
    img = dark(0.35).copy(); items = []
    items.append({'k': 'rect', 'x1': 330, 'y1': 70, 'x2': 950, 'y2': 650, 'c': (22, 24, 34), 'a': 0.95})
    items.append({'k': 'text', 'x': 640, 'y': 108, 't': 'CATALOG OF BLUE OBJECTS', 's': 24, 'w': 'Medium', 'c': GR, 'a': 0.9})
    for i in range(9):
        y = 170 + i * 52
        items.append({'k': 'rect', 'x1': 370, 'y1': y - 14, 'x2': 370 + 120, 'y2': y + 14, 'c': (60, 66, 84), 'a': 0.6})
        items.append({'k': 'rect', 'x1': 520, 'y1': y - 14, 'x2': 520 + 200 + (i * 37) % 120, 'y2': y + 14, 'c': (46, 52, 68), 'a': 0.6})
    hl = sm(A(u, 0.35, 0.6)); y = 170 + 4 * 52
    items.append({'k': 'rect', 'x1': 360, 'y1': y - 24, 'x2': 920, 'y2': y + 24, 'c': (255, 215, 120), 'a': 0.22 * hl})
    items.append({'k': 'text', 'x': 380, 'y': y, 't': 'TON 618', 's': 34, 'c': GOLD, 'an': 'lm', 'a': hl})
    return overlay(vignette(img), items, caption=cap, tag='ILLUSTRATION')
def plate_img(seed=5):
    rng = np.random.default_rng(seed)
    p = np.zeros((H, W, 3), np.float32) + 0.06
    p += rng.normal(0, 0.025, (H, W, 1)).astype(np.float32)
    n = 900; xs = rng.integers(60, W - 60, n); ys = rng.integers(40, H - 40, n); b = rng.random(n) ** 3
    for x, y, bb in zip(xs, ys, b): circ(p, x, y, 1 + bb * 3, (0.8 * bb + 0.15,) * 3)
    return np.clip(cv2.GaussianBlur(p, (0, 0), 0.8), 0, 1)
PLATE = plate_img()
VIOLET = (860, 300)
def plate(t, T, tg, cap, label, strike=False, zoom=True):
    u = t / T
    z = lerp(1.0, 1.35, sm(u)) if zoom else 1.0
    M = cv2.getRotationMatrix2D(VIOLET, 0, z)
    img = cv2.warpAffine(PLATE, M, (W, H)) * 0.95
    vx = VIOLET[0]; vy = VIOLET[1]
    img = glowdot(img, vx, vy, 5, (0.75, 0.45, 1.0), 3.0)
    items = [{'k': 'ring', 'x': vx, 'y': vy, 'r': 34 * sm(A(u, 0.1, 0.5)) + 1, 'c': (200, 150, 255), 'wd': 2, 'a': 0.95}]
    items += label(u)
    return overlay(vignette(img), items, caption=cap, tag='ILLUSTRATION')
def f_t24(t, T, tg, cap): return catalog(t, T, tg, cap)
def f_t25(t, T, tg, cap):
    return plate(t, T, tg, cap, lambda u: [
        {'k': 'text', 'x': 330, 'y': 560, 't': 'TONANTZINTLA OBSERVATORY · MEXICO', 's': 30, 'c': WH, 'a': sm(A(u, 0.15, 0.4))},
        {'k': 'text', 'x': 330, 'y': 604, 't': 'PHOTOGRAPHIC GLASS PLATE', 's': 22, 'w': 'Medium', 'c': GR, 'a': sm(A(u, 0.25, 0.5))},
        {'k': 'text', 'x': 860, 'y': 230, 't': 'A FAINT VIOLET POINT', 's': 22, 'c': (215, 180, 255), 'a': sm(A(u, 0.5, 0.75))}])
def f_t26(t, T, tg, cap):
    return plate(t, T, tg, cap, lambda u: [
        {'k': 'text', 'x': 860, 'y': 400, 't': 'ENTRY 618', 's': 44, 'c': WH, 'a': sm(A(u, 0.1, 0.35))},
        {'k': 'text', 'x': 860, 'y': 450, 't': 'A STAR, MOST LIKELY', 's': 26, 'w': 'Medium', 'c': GR, 'a': sm(A(u, 0.5, 0.75))}], zoom=False)
def f_t27(t, T, tg, cap):
    return plate(t, T, tg, cap, lambda u: [
        {'k': 'text', 'x': 860, 'y': 450, 't': 'A STAR, MOST LIKELY', 's': 26, 'w': 'Medium', 'c': GR, 'a': 0.6},
        {'k': 'line', 'x1': 700, 'y1': 450, 'x2': 700 + 320 * sm(A(u, 0.1, 0.4)), 'y2': 450, 'wd': 5, 'c': (255, 120, 100)},
        {'k': 'text', 'x': 640, 'y': 600, 't': 'IT WAS NOT A STAR.', 's': 64, 'c': WH, 'a': sm(A(u, 0.35, 0.7))}], zoom=False)
def f_t28(t, T, tg, cap):
    u = t / T
    img = dark(0.7).copy(); items = []
    img = glowdot(img, 640, 380, 6, (0.9, 0.8, 1.0), 3.0)
    for k in range(5):
        ph = (u * 1.2 + k / 5.0) % 1.0
        items.append({'k': 'ring', 'x': 640, 'y': 380, 'r': 20 + 380 * ph, 'c': CY, 'wd': 2, 'a': 0.7 * (1 - ph)})
    items += [{'k': 'text', 'x': 640, 'y': 110, 't': '1970', 's': 96, 'c': WH, 'a': sm(A(u, 0.05, 0.3))},
              {'k': 'text', 'x': 640, 'y': 620, 't': 'RADIO EMISSION DETECTED', 's': 34, 'c': CY, 'a': sm(A(u, 0.35, 0.6))}]
    return overlay(vignette(img), items, caption=cap)

LINES = [(300, 'Hγ'), (560, 'Hβ'), (880, 'Hα')]
def spectrum(t, T, tg, cap, shift_p, texts):
    img = dark(0.4).copy(); items = []
    x0, x1, y0, y1 = 140, 1140, 250, 380
    for x in range(x0, x1):
        u = (x - x0) / (x1 - x0)
        hue = int(120 - 120 * u)  # blue(120) -> red(0) in OpenCV half-scale
        c = cv2.cvtColor(np.uint8([[[hue, 255, 70]]]), cv2.COLOR_HSV2RGB)[0, 0] / 255.0
        img[y0:y1, x, :] = c
    for xr, nm in LINES:
        xs = xr + shift_p * 190
        items.append({'k': 'line', 'x1': xr, 'y1': y0 - 24, 'x2': xr, 'y2': y1 + 24, 'wd': 2, 'c': (150, 160, 180), 'a': 0.8})
        items.append({'k': 'line', 'x1': xs, 'y1': y0, 'x2': xs, 'y2': y1, 'wd': 6, 'c': GOLD})
        if shift_p > 0.05:
            items.append({'k': 'line', 'x1': xr, 'y1': y1 + 50, 'x2': xs, 'y2': y1 + 50, 'wd': 3, 'c': (255, 180, 120), 'a': 0.9})
    items += [{'k': 'text', 'x': 140, 'y': 205, 't': 'BLUER', 's': 22, 'w': 'Medium', 'c': (130, 160, 255), 'an': 'lm'},
              {'k': 'text', 'x': 1140, 'y': 205, 't': 'REDDER', 's': 22, 'w': 'Medium', 'c': (255, 140, 120), 'an': 'rm'}]
    items += texts(t / T)
    return overlay(vignette(img), items, caption=cap)
def f_t29(t, T, tg, cap):
    u = t / T
    return spectrum(t, T, tg, cap, sm(A(u, 0.25, 0.85)), lambda u: [
        {'k': 'text', 'x': 640, 'y': 110, 't': 'LIGHT FROM GLOWING GAS', 's': 40, 'c': WH},
        {'k': 'text', 'x': 640, 'y': 560, 't': 'SPECTRAL LINES SHIFTED TOWARD THE RED', 's': 32, 'c': GOLD, 'a': sm(A(u, 0.5, 0.8))}])
def f_t30(t, T, tg, cap):
    return spectrum(t, T, tg, cap, 1.0, lambda u: [
        {'k': 'text', 'x': 640, 'y': 110, 't': 'BIGGER SHIFT = LONGER JOURNEY', 's': 44, 'c': WH, 'a': sm(A(u, 0.1, 0.4))},
        {'k': 'text', 'x': 640, 'y': 560, 't': 'THE EXPANDING UNIVERSE STRETCHES THE LIGHT', 's': 28, 'w': 'Medium', 'c': GR, 'a': sm(A(u, 0.5, 0.8))}])
def f_t31(t, T, tg, cap):
    u = t / T
    img = quasar(tg, 1000, 360, 70, expo=0.9)
    items = [{'k': 'text', 'x': 330, 'y': 250, 't': 'REDSHIFT', 's': 28, 'w': 'Medium', 'c': GR, 'a': sm(A(u, 0.05, 0.25))},
             {'k': 'text', 'x': 330, 'y': 320, 't': 'z ≈ 2.2', 's': 96, 'c': GOLD, 'a': sm(A(u, 0.05, 0.3))},
             {'k': 'text', 'x': 330, 'y': 440, 't': 'LIGHT TRAVEL TIME', 's': 28, 'w': 'Medium', 'c': GR, 'a': sm(A(u, 0.5, 0.7))},
             {'k': 'text', 'x': 330, 'y': 505, 't': '≈ 10.8 BILLION YEARS', 's': 50, 'c': WH, 'a': sm(A(u, 0.5, 0.75))}]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def f_t32(t, T, tg, cap):
    u = t / T
    img = dark(0.4).copy()
    X0, X1, Y = 140, 1140, 330
    xl = X0 + (X1 - X0) * 3.0 / 13.8
    items = [{'k': 'line', 'x1': X0, 'y1': Y, 'x2': X1, 'y2': Y, 'wd': 6, 'c': (90, 105, 140)},
             {'k': 'text', 'x': X0, 'y': Y + 50, 't': 'BIG BANG', 's': 24, 'w': 'Medium', 'c': GR},
             {'k': 'text', 'x': X1, 'y': Y + 50, 't': 'TODAY · 13.8 BILLION YEARS', 's': 24, 'w': 'Medium', 'c': GR, 'an': 'rm'}]
    a1 = sm(A(u, 0.1, 0.3))
    items += [{'k': 'dot', 'x': xl, 'y': Y, 'r': 14, 'c': GOLD, 'a': a1},
              {'k': 'text', 'x': xl, 'y': Y - 70, 't': 'LIGHT LEAVES', 's': 30, 'c': GOLD, 'a': a1},
              {'k': 'text', 'x': xl, 'y': Y - 36, 't': 'UNIVERSE ≈ 3 BILLION YEARS OLD', 's': 22, 'w': 'Medium', 'c': WH, 'a': a1}]
    p = sm(A(u, 0.35, 0.85)); xe = lerp(xl, X1, p)
    items += [{'k': 'line', 'x1': xl, 'y1': Y, 'x2': xe, 'y2': Y, 'wd': 8, 'c': (255, 235, 170), 'a': a1},
              {'k': 'dot', 'x': xe, 'y': Y, 'r': 10, 'c': (255, 250, 230), 'a': a1},
              {'k': 'text', 'x': (xl + X1) / 2, 'y': Y + 130, 't': '≈ 10.8 BILLION YEARS OF TRAVEL', 's': 34, 'c': (255, 235, 170), 'a': sm(A(u, 0.5, 0.75))}]
    return overlay(vignette(img), items)

def f_t33(t, T, tg, cap):
    u = sm(t / T)
    img = quasar(tg, 640, 360, lerp(8, 120, u ** 1.4), expo=lerp(1.4, 1.0, u))
    items = [{'k': 'text', 'x': 640, 'y': 620, 't': 'QUASAR', 's': 70, 'c': WH, 'a': sm(A(t / T, 0.6, 0.9))}]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def f_t34(t, T, tg, cap):
    u = t / T
    img = quasar(tg, 520, 380, 150)
    a1 = sm(A(u, 0.35, 0.55)); a2 = sm(A(u, 0.65, 0.85))
    items = [{'k': 'line', 'x1': 520, 'y1': 380, 'x2': 900, 'y2': 170, 'wd': 2, 'c': WH, 'a': a1},
             {'k': 'text', 'x': 910, 'y': 150, 't': 'THE BLACK HOLE: DARK', 's': 30, 'c': WH, 'an': 'lm', 'a': a1},
             {'k': 'line', 'x1': 680, 'y1': 420, 'x2': 900, 'y2': 560, 'wd': 2, 'c': GOLD, 'a': a2},
             {'k': 'text', 'x': 910, 'y': 580, 't': 'THE DISK OF GAS: SHINES', 's': 30, 'c': GOLD, 'an': 'lm', 'a': a2}]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def f_t35(t, T, tg, cap):
    u = t / T
    img = quasar(tg, 520, 380, 150, inflow=1.0)
    items = [{'k': 'text', 'x': 900, 'y': 190, 't': 'GAS SPIRALS INWARD', 's': 32, 'c': WH, 'an': 'lm', 'a': sm(A(u, 0.1, 0.3))},
             {'k': 'text', 'x': 900, 'y': 250, 't': 'FRICTION HEATS IT', 's': 32, 'c': (255, 190, 130), 'an': 'lm', 'a': sm(A(u, 0.4, 0.6))},
             {'k': 'text', 'x': 900, 'y': 290, 't': 'TO MILLIONS OF DEGREES', 's': 24, 'w': 'Medium', 'c': (255, 190, 130), 'an': 'lm', 'a': sm(A(u, 0.4, 0.6))},
             {'k': 'text', 'x': 900, 'y': 380, 't': 'THE DISK IS WHAT SHINES', 's': 32, 'c': GOLD, 'an': 'lm', 'a': sm(A(u, 0.7, 0.9))}]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def f_t36(t, T, tg, cap):
    u = t / T
    img = quasar(tg, 360, 380, 120, expo=lerp(0.8, 1.6, u))
    n = int(140 * sm(A(u, 0.05, 0.55)))
    items = [{'k': 'text', 'x': 900, 'y': 230, 't': f'{n} TRILLION SUNS', 's': 52, 'c': GOLD, 'a': sm(A(u, 0.05, 0.2))},
             {'k': 'text', 'x': 900, 'y': 290, 't': 'OF LIGHT', 's': 30, 'w': 'Medium', 'c': WH, 'a': sm(A(u, 0.05, 0.2))},
             {'k': 'text', 'x': 900, 'y': 430, 't': 'THOUSANDS OF TIMES', 's': 38, 'c': WH, 'a': sm(A(u, 0.6, 0.8))},
             {'k': 'text', 'x': 900, 'y': 478, 't': 'THE ENTIRE MILKY WAY', 's': 38, 'c': (170, 195, 255), 'a': sm(A(u, 0.6, 0.8))}]
    return overlay(vignette(img), items, caption=cap, tag=TAG)

def orbit_scene(t, T, tg, cap, panels, items_extra=None, bgm=0.5):
    """panels: list of dict(cx,cy,sc,kind,key,x0,y0,vx,vy,GM,drag,turns,label,sub)"""
    u = t / T
    img = dark(bgm).copy(); items = []
    for pn in panels:
        steps = 6000
        pts = traj(pn['key'], pn.get('x0', 1.0), pn.get('y0', 0.0), pn.get('vx', 0.0), pn.get('vy', 1.0), pn.get('GM', 1.0), 0.006, steps, pn.get('drag', 0.0))
        i = int(min(steps - 1, u * pn.get('frac', 0.95) * steps * pn.get('turns', 1.0)))
        trail(img, pts, i, pn['cx'], pn['cy'], pn['sc'], pn.get('col', (1.0, 0.9, 0.5)), n=pn.get('trail', 90), step=3)
        img = center_obj(img, pn['kind'], pn['cx'], pn['cy'], pn.get('cr', 16))
        px, py = planet_xy(pts, i, pn['cx'], pn['cy'], pn['sc'])
        img = glowdot(img, px, py, pn.get('pr', 6), (0.5, 0.8, 1.0), 2.0)
        if pn.get('label'):
            items.append({'k': 'text', 'x': pn['cx'], 'y': pn.get('ly', 100), 't': pn['label'], 's': pn.get('ls', 28), 'c': WH, 'a': sm(A(u, 0.05, 0.25))})
        if pn.get('sub'):
            items.append({'k': 'text', 'x': pn['cx'], 'y': pn.get('ly', 100) + 36, 't': pn['sub'], 's': 20, 'w': 'Medium', 'c': GR, 'a': sm(A(u, 0.15, 0.35))})
        if pn.get('vec'):
            vx = pts[min(i + 1, steps - 1)] - pts[i]; vn = np.linalg.norm(vx) + 1e-9; vx = vx / vn
            items.append({'k': 'line', 'x1': px, 'y1': py, 'x2': px + vx[0] * 90, 'y2': py + vx[1] * 90, 'wd': 4, 'c': CY})
            gx, gy = (-pts[i][0], -pts[i][1]); gn = np.hypot(gx, gy) + 1e-9
            items.append({'k': 'line', 'x1': px, 'y1': py, 'x2': px + gx / gn * 70, 'y2': py + gy / gn * 70, 'wd': 4, 'c': (255, 150, 120)})
    if items_extra: items += items_extra(u)
    return overlay(vignette(img), items, caption=cap)

def f_t37(t, T, tg, cap):
    return orbit_scene(t, T, tg, cap, [dict(cx=640, cy=370, sc=230, kind='bh', key='t37', cr=18, turns=1.6, col=(1.0, 0.7, 0.3))],
                       lambda u: [{'k': 'text', 'x': 640, 'y': 640, 't': 'YOU WATCH WHAT ORBITS IT', 's': 44, 'c': GOLD, 'a': sm(A(u, 0.4, 0.7))}])
def f_t38(t, T, tg, cap):
    return orbit_scene(t, T, tg, cap, [
        dict(cx=340, cy=380, sc=190, kind='bh', key='t38a', cr=10, GM=0.5, vy=0.707, turns=1.0, label='LESS MASS', sub='SLOWER ORBIT', ly=110),
        dict(cx=940, cy=380, sc=190, kind='bh', key='t38b', cr=22, GM=2.0, vy=1.414, turns=2.8, label='MORE MASS', sub='FASTER ORBIT', ly=110)])
def broad(t, T, tg, cap, sig, texts):
    img = dark(0.35).copy(); items = []
    xs = np.arange(140, 1141)
    base_y = 520
    for s, col, hh in sig:
        ys = base_y - hh * np.exp(-0.5 * ((xs - 640) / s) ** 2)
        pts = np.stack([xs, ys], 1)
        fill = np.concatenate([pts, [[1140, base_y], [140, base_y]]]).astype(np.int32)
        lay = np.zeros_like(img); cv2.fillPoly(lay, [fill.reshape(-1, 1, 2)], col); img = img + lay * 0.28
        poly(img, pts, col, 3)
    items.append({'k': 'line', 'x1': 140, 'y1': base_y, 'x2': 1140, 'y2': base_y, 'wd': 2, 'c': GR})
    items.append({'k': 'text', 'x': 640, 'y': base_y + 36, 't': 'WAVELENGTH OF ONE SPECTRAL LINE', 's': 20, 'w': 'Medium', 'c': GR})
    items += texts(t / T)
    return overlay(vignette(img), items, caption=cap)
def f_t39a(t, T, tg, cap):
    u = t / T
    s2 = lerp(14, 20, 0) + 70 * sm(A(u, 0.25, 0.7))
    return broad(t, T, tg, cap, [(14, (0.5, 0.8, 1.0), 300), (max(s2, 14), (1.0, 0.8, 0.4), 300 * 14 / max(s2, 14) * 1.1)], lambda u: [
        {'k': 'text', 'x': 640, 'y': 100, 't': 'FASTER GAS SMEARS THE LINE WIDER', 's': 40, 'c': WH, 'a': sm(A(u, 0.1, 0.35))},
        {'k': 'text', 'x': 400, 'y': 250, 't': 'SLOW GAS: NARROW', 's': 24, 'c': (130, 200, 255), 'a': sm(A(u, 0.2, 0.4))},
        {'k': 'text', 'x': 900, 'y': 380, 't': 'FAST GAS NEAR THE BLACK HOLE: WIDE', 's': 24, 'c': GOLD, 'a': sm(A(u, 0.6, 0.85))}])
def f_t39b(t, T, tg, cap):
    return orbit_scene(t, T, tg, cap, [dict(cx=640, cy=380, sc=210, kind='sun', key='t39', cr=22, turns=1.3, ly=100,
                                           label='SAME LOGIC', sub="WEIGH THE SUN FROM THE EARTH'S ORBIT", ls=40)])

def f_t40(t, T, tg, cap):
    u = t / T
    img = dark(0.4).copy(); items = []
    x0 = 330; X = lambda v: x0 + (v - 20) / (80 - 20) * 760
    items += [{'k': 'line', 'x1': X(20), 'y1': 560, 'x2': X(80), 'y2': 560, 'wd': 2, 'c': GR}]
    for v in (20, 40, 60, 80):
        items += [{'k': 'text', 'x': X(v), 'y': 590, 't': str(v), 's': 18, 'w': 'Medium', 'c': GR}]
    items += [{'k': 'text', 'x': 640, 'y': 640, 't': 'BILLIONS OF SOLAR MASSES', 's': 20, 'w': 'Medium', 'c': GR}]
    a1 = sm(A(u, 0.05, 0.4)); a2 = sm(A(u, 0.5, 0.85))
    items += [{'k': 'text', 'x': 330, 'y': 160, 't': 'USING THE LIGHT OF HYDROGEN', 's': 28, 'c': GOLD, 'an': 'lm', 'a': a1},
              {'k': 'rect', 'x1': X(20), 'y1': 200, 'x2': X(20) + (X(66) - X(20)) * a1, 'y2': 250, 'c': GOLD, 'a': 0.9},
              {'k': 'text', 'x': X(66) + 18, 'y': 225, 't': '≈ 66 BILLION', 's': 34, 'c': WH, 'an': 'lm', 'a': a1},
              {'k': 'text', 'x': 330, 'y': 340, 't': 'USING A DIFFERENT SPECTRAL LINE', 's': 28, 'c': CY, 'an': 'lm', 'a': a2},
              {'k': 'rect', 'x1': X(20), 'y1': 380, 'x2': X(20) + (X(40) - X(20)) * a2, 'y2': 430, 'c': CY, 'a': 0.9},
              {'k': 'text', 'x': X(40) + 18, 'y': 405, 't': '≈ 40 BILLION', 's': 34, 'c': WH, 'an': 'lm', 'a': a2}]
    return overlay(vignette(img), items, caption=cap)
def f_t41(t, T, tg, cap):
    u = t / T
    img = dark(0.4).copy(); items = []
    x0 = 160; X = lambda v: x0 + (v - 20) / (80 - 20) * 960
    a = sm(A(u, 0.1, 0.45))
    items += [{'k': 'rect', 'x1': X(40), 'y1': 300, 'x2': X(40) + (X(66) - X(40)) * a, 'y2': 380, 'c': GOLD, 'a': 0.85},
              {'k': 'line', 'x1': X(20), 'y1': 420, 'x2': X(80), 'y2': 420, 'wd': 2, 'c': GR},
              {'k': 'text', 'x': 640, 'y': 150, 't': 'ESTIMATES, NOT DIRECT WEIGHINGS', 's': 44, 'c': WH, 'a': sm(A(u, 0.05, 0.3))},
              {'k': 'text', 'x': 640, 'y': 220, 't': 'BUILT ON ASSUMPTIONS', 's': 28, 'w': 'Medium', 'c': GR, 'a': sm(A(u, 0.3, 0.55))},
              {'k': 'text', 'x': 640, 'y': 520, 't': '≈ 40–66 BILLION SOLAR MASSES', 's': 52, 'c': GOLD, 'a': sm(A(u, 0.6, 0.85))}]
    for v in (20, 40, 60, 80): items.append({'k': 'text', 'x': X(v), 'y': 450, 't': str(v), 's': 18, 'w': 'Medium', 'c': GR})
    return overlay(vignette(img), items, caption=cap)
def f_t42(t, T, tg, cap):
    u = t / T
    img = lens(BG * 0.8, 640, 360, 130 * (0.9 + 0.1 * u), shadow=True, ring=True)
    items = [{'k': 'text', 'x': 640, 'y': 360, 't': '?', 's': 150, 'c': WH, 'a': 0.0}]
    items += [{'k': 'text', 'x': 640, 'y': 620, 't': 'WHAT DOES IT LOOK LIKE?', 's': 44, 'c': WH, 'a': sm(A(u, 0.3, 0.6))}]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def eht_icon(img, cx, cy, r, ph):
    yy, xx = gy_, gx_
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2); phi = np.arctan2(yy - cy, xx - cx)
    ring = np.exp(-((d - r) / (0.22 * r)) ** 2) * (0.5 + 0.5 * np.cos(phi - ph)) ** 1.2
    col = np.stack([ring * 1.0, ring * 0.55, ring * 0.2], 2)
    return screen(img, np.clip(col, 0, 1))
def f_t43(t, T, tg, cap):
    u = t / T
    img = dark(0.5).copy()
    img = eht_icon(img, 340, 360, 120, 0.6) if u > 0.1 else img
    img = eht_icon(img, 940, 360, 120, 2.3) if u > 0.5 else img
    a1 = sm(A(u, 0.1, 0.3)); a2 = sm(A(u, 0.5, 0.7))
    items = [{'k': 'text', 'x': 340, 'y': 540, 't': 'M87*', 's': 40, 'c': WH, 'a': a1},
             {'k': 'text', 'x': 340, 'y': 586, 't': 'GALAXY M87', 's': 20, 'w': 'Medium', 'c': GR, 'a': a1},
             {'k': 'text', 'x': 940, 'y': 540, 't': 'SAGITTARIUS A*', 's': 40, 'c': WH, 'a': a2},
             {'k': 'text', 'x': 940, 'y': 586, 't': 'CENTER OF THE MILKY WAY', 's': 20, 'w': 'Medium', 'c': GR, 'a': a2},
             {'k': 'text', 'x': 640, 'y': 90, 't': 'SHADOWS OF TWO BLACK HOLES, PHOTOGRAPHED', 's': 32, 'c': GOLD, 'a': a1}]
    return overlay(vignette(img), items, caption=cap, tag='SCHEMATIC · NOT THE REAL IMAGES')
def f_t44(t, T, tg, cap):
    u = t / T
    img = lens(BG * 0.8, 640, 340, 125, shadow=True, ring=True)
    items = [{'k': 'text', 'x': 640, 'y': 570, 't': 'NO IMAGE OF TON 618 EXISTS', 's': 46, 'c': WH, 'a': sm(A(u, 0.1, 0.35))},
             {'k': 'text', 'x': 640, 'y': 626, 't': "WHAT YOU SEE: AN ARTIST'S CONCEPT", 's': 26, 'w': 'Medium', 'c': GOLD, 'a': sm(A(u, 0.5, 0.75))}]
    return overlay(vignette(img), items, caption=cap, tag=TAG)

def f_t45(t, T, tg, cap):
    u = t / T
    return orbit_scene(t, T, tg, cap, [dict(cx=640, cy=330, sc=170, kind='bh', key='t45a', cr=16, turns=1.2, col=(1.0, 0.7, 0.3), trail=120),
                                       dict(cx=640, cy=330, sc=250, kind='bh', key='t45b', cr=0, GM=1.0, x0=1.0, y0=0.0, vy=0.72, turns=1.0, trail=120)],
                       lambda u: [{'k': 'text', 'x': 640, 'y': 640, 't': 'BLACK HOLES DO NOT SUCK.', 's': 62, 'c': WH, 'a': sm(A(u, 0.15, 0.45))}])
def gcurve(t, T, tg, cap, stage):
    u = t / T
    img = dark(0.35).copy(); items = []
    ox, oy, w, h = 200, 560, 880, 400
    LX = lambda d: ox + (np.log10(d) + 2) / 4.0 * w
    LY = lambda g: oy - (np.log10(g) + 4) / 8.0 * h
    items += [{'k': 'line', 'x1': ox, 'y1': oy, 'x2': ox + w, 'y2': oy, 'wd': 2, 'c': GR}, {'k': 'line', 'x1': ox, 'y1': oy, 'x2': ox, 'y2': oy - h, 'wd': 2, 'c': GR},
              {'k': 'text', 'x': ox + w / 2, 'y': oy + 38, 't': 'DISTANCE FROM THE CENTER', 's': 22, 'w': 'Medium', 'c': GR},
              {'k': 'text', 'x': ox + 8, 'y': oy - h - 22, 't': 'GRAVITY', 's': 22, 'w': 'Medium', 'c': GR, 'an': 'lm'}]
    ds = np.logspace(-1.5, 1.8, 200); gs = 1.0 / ds ** 2
    pts_all = [(LX(d), LY(g)) for d, g in zip(ds, gs) if oy - h <= LY(g) <= oy]
    ds_sun = ds[ds >= 1.0]; pts_sun = [(LX(d), LY(1.0 / d ** 2)) for d in ds_sun]
    p = sm(A(u, 0.05, 0.6))
    n = max(2, int(len(pts_sun) * p)); poly(img, pts_sun[:n], (0.5, 0.8, 1.0), 4)
    sx = LX(1.0)
    items += [{'k': 'line', 'x1': sx, 'y1': oy - h, 'x2': sx, 'y2': oy, 'wd': 1, 'c': (140, 160, 200), 'a': 0.6},
              {'k': 'text', 'x': sx + 8, 'y': oy - h + 18, 't': 'SURFACE OF THE SUN', 's': 18, 'w': 'Medium', 'c': (130, 200, 255), 'an': 'lm'}]
    if stage >= 1:
        n2 = max(2, int(len(pts_all) * sm(A(u, 0.05, 0.7)))); 
        poly(img, pts_all[:n2], (1.0, 0.8, 0.4), 2)
    items += [{'k': 'text', 'x': 640, 'y': 70, 't': 'GRAVITY DEPENDS ON ONLY TWO THINGS', 's': 38, 'c': WH, 'a': sm(A(u, 0.1, 0.3)) if stage == 0 else 1},
              {'k': 'text', 'x': 640, 'y': 118, 't': 'MASS  AND  DISTANCE', 's': 34, 'c': GOLD, 'a': sm(A(u, 0.3, 0.55)) if stage == 0 else 1}]
    if stage >= 1:
        items += [{'k': 'text', 'x': 840, 'y': 300, 't': 'SAME MASS = SAME GRAVITY', 's': 28, 'c': GOLD, 'a': sm(A(u, 0.4, 0.65))},
                  {'k': 'text', 'x': 840, 'y': 338, 't': 'FAR AWAY', 's': 28, 'c': GOLD, 'a': sm(A(u, 0.4, 0.65))}]
    if stage == 2:
        items += [{'k': 'text', 'x': 330, 'y': 215, 't': 'ONLY A BLACK HOLE LETS YOU GET THIS CLOSE', 's': 22, 'c': (255, 190, 120), 'an': 'lm', 'a': sm(A(u, 0.55, 0.85))}]
    return overlay(vignette(img), items, caption=cap)
def f_t46(t, T, tg, cap): return gcurve(t, T, tg, cap, 0)
def f_t47(t, T, tg, cap):
    return orbit_scene(t, T, tg, cap, [
        dict(cx=340, cy=390, sc=200, kind='sun', key='t47a', cr=24, turns=1.3, label='THE SUN', sub='TODAY', ly=110),
        dict(cx=940, cy=390, sc=200, kind='bh', key='t47a', cr=14, turns=1.3, label='A BLACK HOLE · SAME MASS', sub='SAME ORBIT · IT DOES NOT FALL IN', ly=110, ls=26)])
def f_t48(t, T, tg, cap): return gcurve(t, T, tg, cap, 2)
def f_t49(t, T, tg, cap):
    return orbit_scene(t, T, tg, cap, [dict(cx=640, cy=360, sc=210, kind='sun', key='t49', cr=24, turns=1.2, vec=False)],
                       lambda u: [{'k': 'text', 'x': 640, 'y': 90, 't': 'THE EARTH IS FALLING TOWARD THE SUN', 's': 38, 'c': WH, 'a': sm(A(u, 0.1, 0.35))},
                                  {'k': 'text', 'x': 640, 'y': 640, 't': 'FALLING FOR 4.5 BILLION YEARS. AND MISSING.', 's': 36, 'c': GOLD, 'a': sm(A(u, 0.45, 0.75))}])
def f_t50(t, T, tg, cap):
    return orbit_scene(t, T, tg, cap, [dict(cx=640, cy=370, sc=215, kind='sun', key='t49', cr=24, turns=1.2, vec=True)],
                       lambda u: [{'k': 'text', 'x': 1000, 'y': 150, 't': '~30 KM/S SIDEWAYS', 's': 30, 'c': CY, 'a': sm(A(u, 0.1, 0.35))},
                                  {'k': 'text', 'x': 1000, 'y': 196, 't': 'GRAVITY PULLS INWARD', 's': 30, 'c': (255, 150, 120), 'a': sm(A(u, 0.3, 0.55))}])
def f_t51(t, T, tg, cap):
    return orbit_scene(t, T, tg, cap, [
        dict(cx=230, cy=400, sc=130, kind='sun', key='t51a', cr=14, vy=0.0, turns=0.6, label='NO SIDEWAYS SPEED', sub='FALLS STRAIGHT IN', ly=130, ls=22, col=(1.0, 0.5, 0.4)),
        dict(cx=640, cy=400, sc=130, kind='sun', key='t51b', cr=14, vy=0.6, turns=1.4, label='A LITTLE SPEED', sub='FALLS, BUT MISSES · ELLIPSE', ly=130, ls=22),
        dict(cx=1050, cy=400, sc=130, kind='sun', key='t51c', cr=14, vy=1.0, turns=1.3, label='ENOUGH SPEED', sub='KEEPS MISSING · CIRCLE', ly=130, ls=22, col=(0.5, 1.0, 0.7))],
        lambda u: [{'k': 'text', 'x': 640, 'y': 640, 't': 'AN ORBIT IS FALLING, AND MISSING', 's': 40, 'c': GOLD, 'a': sm(A(u, 0.5, 0.8))}])
def f_t52(t, T, tg, cap):
    return orbit_scene(t, T, tg, cap, [
        dict(cx=340, cy=400, sc=170, kind='bh', key='t52a', cr=12, vy=1.0, turns=2.0, label='KEEPS ANGULAR MOMENTUM', sub='CIRCLES. FOREVER.', ly=110, ls=24, col=(0.5, 1.0, 0.7)),
        dict(cx=940, cy=400, sc=170, kind='bh', key='t52b', cr=12, vy=1.0, drag=0.06, turns=2.0, label='GIVES IT UP', sub='SPIRALS IN', ly=110, ls=24, col=(1.0, 0.5, 0.4))],
        lambda u: [{'k': 'text', 'x': 640, 'y': 640, 't': 'ANGULAR MOMENTUM: THE SIDEWAYS MOTION', 's': 34, 'c': GOLD, 'a': sm(A(u, 0.1, 0.35))}])
def f_t53(t, T, tg, cap):
    u = t / T
    img = dark(0.45).copy(); items = []
    cx, cy = 640, 370
    img = center_obj(img, 'bh', cx, cy, 10)
    specs = [(1.0, 0.88, 0.0, 16.0, (0.5, 0.8, 1.0), 'S2 · ≈ 16 YEARS'), (1.9, 0.5, 2.0, 55.0, (1.0, 0.8, 0.4), ''), (2.6, 0.3, 4.0, 110.0, (0.6, 1.0, 0.7), '')]
    for a, e, w, per, col, nm in specs:
        pts = []
        for k in range(360):
            th = k / 360 * 2 * np.pi; r = a * (1 - e * e) / (1 + e * np.cos(th))
            pts.append((cx + 118 * r * np.cos(th + w) * 1.0, cy + 118 * r * np.sin(th + w) * 0.78))
        poly(img, pts, tuple(c * 0.5 for c in col), 1)
        M = (t / T) * (T / per) * 12 * 2 * np.pi
        E = M
        for _ in range(8): E = M + e * np.sin(E)
        th = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))
        r = a * (1 - e * e) / (1 + e * np.cos(th))
        px = cx + 118 * r * np.cos(th + w); py = cy + 118 * r * np.sin(th + w) * 0.78
        img = glowdot(img, px, py, 5, col, 2.0)
        if nm: items.append({'k': 'text', 'x': px + 14, 'y': py - 18, 't': nm, 's': 20, 'c': (170, 215, 255), 'an': 'lm'})
    items += [{'k': 'text', 'x': 640, 'y': 70, 't': 'STARS AT THE CENTER OF THE MILKY WAY', 's': 32, 'c': WH, 'a': sm(A(u, 0.05, 0.3))},
              {'k': 'text', 'x': 640, 'y': 640, 't': 'THOUSANDS OF KM/S  ·  THEY DO NOT FALL IN', 's': 34, 'c': GOLD, 'a': sm(A(u, 0.5, 0.8))}]
    return overlay(vignette(img), items, caption=cap, tag='SIMPLIFIED ILLUSTRATION')
def f_t54(t, T, tg, cap):
    u = t / T
    img = lens(BG * 0.7, 960, 360, 120)
    items = [{'k': 'text', 'x': 120, 'y': 250, 't': 'GRAVITY PULLS.', 's': 66, 'c': WH, 'an': 'lm', 'a': sm(A(u, 0.1, 0.35))},
             {'k': 'text', 'x': 120, 'y': 380, 't': 'ONLY LOSING ORBITAL MOTION', 's': 50, 'c': GOLD, 'an': 'lm', 'a': sm(A(u, 0.45, 0.7))},
             {'k': 'text', 'x': 120, 'y': 450, 't': 'LETS ANYTHING ARRIVE.', 's': 50, 'c': GOLD, 'an': 'lm', 'a': sm(A(u, 0.55, 0.8))}]
    return overlay(vignette(img), items, caption=cap, tag=TAG)

FUNCS2 = {k: globals()['f_' + k.split('_')[0]] for k, *_ in SEQ2}

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'plan':
        for k, t, p in SEQ2: print(f'{k:14s} start {START2[k]:6.1f}  dur {DUR2[k]:5.1f}')
        print('TOTAL2', round(TOTAL2, 1), 'END', round(BASE + TOTAL2, 1))
    elif mode == 'frames':
        only = sys.argv[2:] or [k for k, *_ in SEQ2]
        for k, t, p in SEQ2:
            if k not in only: continue
            T = DUR2[k]; fr = FUNCS2[k](T * 0.7, T, START2[k] + T * 0.7, None)
            Image.fromarray(fr).resize((640, 360)).save(f'{OUT}/f_{k}.png')
        print('ok')
    elif mode == 'render':
        only = sys.argv[2:] or [k for k, *_ in SEQ2]
        for i, (k, t, p) in enumerate(SEQ2):
            if k not in only: continue
            T = DUR2[k] + (0.5 if i < len(SEQ2) - 1 else 0)
            render_scene(k, T, FUNCS2[k], START2[k], caption=t)
        print('RENDER_DONE', flush=True)
    elif mode == 'assemble':
        S1.assemble([k for k, *_ in SEQ2], DUR2, os.path.join(OUT,'preview_part1b.mp4')); print('ASSEMBLED')
