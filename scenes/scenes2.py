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
