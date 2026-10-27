import sys
import numpy as np
from scenes2 import *   # engine + scenes + helpers (glowdot, quasar, orbit_scene, A, sm, ...)

SEQ3 = [
 ('u01_return', "Now return to the Milky Way, and look at what TON six-eighteen would actually be facing.", 1),
 ('u02_empty', "The Milky Way is not a solid object. It is mostly empty space, with stars scattered through it at astonishing distances.", 0),
 ('u03_golf', "If our Sun were a golf ball in New York, the nearest star would be another golf ball roughly as far away as Chicago.", 0),
 ('u04_crowd', "And that is the crowded neighborhood of a galactic disk. Billions of stars, and almost none of them anywhere near each other.", 1),
 ('u05_halo', "Around all of that sits something we cannot see. By most estimates, the total mass of the Milky Way, including its halo of dark matter, is somewhere above one trillion Suns.", 0),
 ('u06_share', "Only a few percent of that is visible stars. So TON six-eighteen would not be a giant meeting a dwarf. It would be a compact object holding a few percent of the galaxy's total mass, confronting a vast, loosely bound structure held together by its own collective gravity.", 1),
 ('u07_three', "Now we have to be precise about what we mean by an encounter, because there are three very different stories hiding inside that word.", 1),
 ('u08_flyby', "In the first, the black hole passes by at a great distance. Say, a few hundred thousand light-years away. Its pull on any single star would be tiny. But gravity is not equal across a galaxy. The near side feels slightly more than the far side. That difference, the tidal force, would stretch the galaxy, and could pull out long ribbons of stars, like the ones we see in colliding galaxies. The galaxy would be scarred. It would not be eaten.", 1),
 ('u09_plunge', "In the second, the black hole plunges straight through the disk. Now the story changes. Stars along its path are flung in new directions. The disk is shaken, warped, and heated. Some stars would be thrown out of the galaxy altogether. A few would be sent close enough to be swallowed. But the vast majority would be rearranged, not removed.", 1),
 ('u10_sink', "In the third, the black hole stays. As it moves through the stars and the dark matter, it gives up energy through countless tiny gravitational tugs, a process called dynamical friction. Over hundreds of millions of years, it would sink toward the center. And there, it would meet Sagittarius A star.", 1),
 ('u11_heart', "What happens next is the heart of the question.", 1),
 ('u12_capture', "Here is the central fact. Having enormous mass is not the same as being able to capture enormous amounts of matter.", 1),
 ('u13_horizon', "Start with the size of the trap. The boundary of a black hole, its event horizon, is the surface inside which escape is impossible.", 0),
 ('u14_au', "For sixty-six billion Suns, that boundary has a radius of about thirteen hundred astronomical units. More than forty times the distance from the Sun to Neptune. It is colossal. A sphere roughly four hundredths of a light-year across.", 0),
 ('u15_coin', "But the Milky Way is a hundred thousand light-years wide. The galaxy is about two and a half million times wider than the horizon of TON six-eighteen. Imagine a coin lying in the middle of a city fifty kilometers across. That is the horizon, compared with the galaxy.", 1),
 ('u16_cone', "And a star is smaller still. For a star to fall in, its orbit must aim almost straight at the black hole. Astronomers call the set of such orbits the loss cone, and it is narrow. Stars on ordinary orbits keep missing, again and again, for billions of years.", 0),
 ('u17_rate', "In a typical galaxy, a star is swallowed or torn apart only about once every ten thousand to a hundred thousand years.", 1),
 ('u18_tides', "Here is a surprise. You might expect a star approaching a black hole to be shredded by tides long before it arrives. Around a black hole like Sagittarius A star, that happens. But the bigger the black hole, the larger its horizon, and the gentler the tides at that boundary.", 0),
 ('u19_whole', "Above roughly a hundred million solar masses, a Sun-like star can cross the horizon in one piece. For TON six-eighteen, a star would not be torn apart. It would simply be gone, whole, without a flash.", 1),
 ('u20_gas', "Stars are not the only matter in a galaxy, though. There is also gas, and gas behaves differently. Stars pass through each other's space almost without touching. Gas clouds collide, shock, and lose energy as heat and light.", 0),
 ('u21_feed', "Gas can lose its angular momentum and spiral inward. That is the matter that feeds quasars. TON six-eighteen shines as it does because it is swallowing gas right now.", 0),
 ('u22_budget', "A rough back-of-the-envelope estimate suggests tens of Suns of gas every year. The Milky Way holds something on the order of ten billion Suns of gas. At that appetite, a reservoir like that could be drained in about a hundred million years. A blink, for a galaxy. But the hundred billion stars would still be there.", 1),
 ('u23_cata', "So the true aftermath would not be a swallowing. It would be an orbital catastrophe.", 0),
 ('u24_binary', "The black hole would settle near the center and pair up with Sagittarius A star, two black holes circling one another, hurling away the stars that wander too close, until they finally merge in a burst of gravitational waves.", 0),
 ('u25_scour', "The center of the galaxy would be scoured of stars, as we see in the cores of giant elliptical galaxies. For a while, the gas could ignite as a quasar. And the thin, graceful spiral might not survive in its present form. It could be thickened, heated, reshaped.", 1),
 ('u26_nosingle', "But how much of that would happen depends on the details. The speed. The angle. How close the black hole comes. There is no single outcome. Anyone who gives you one, without telling you the starting conditions, is selling a story, not science.", 1),
 ('u27_return2', "Return, now, to the image where we began. A galaxy, and a black hole of tens of billions of Suns.", 1),
 ('u28_terrify', "By now you can see why the comparison is both terrifying and misleading. It is terrifying because the mass is real. TON six-eighteen could rearrange our galaxy. It could scatter its stars, scar its disk, rewrite its center, and light the whole thing up as a quasar.", 0),
 ('u29_mislead', "And it is misleading because swallowing a galaxy is not what black holes do. Gravity pulls, but it does not funnel. Stars orbit. They carry angular momentum. Space is almost empty. The horizon is tiny. And the overwhelming majority of stars would survive the encounter, not as they were, but on new paths.", 1),
 ('u30_no', "So the honest answer to the question on the thumbnail is no. Not like that. Not in any way that anyone could truly call swallowing. A black hole of this size would take a sliver of a galaxy's stars, perhaps most of its gas, and change almost everything else.", 1),
 ('u31_thought', "And one thing deserves to be said plainly. This was a thought experiment. TON six-eighteen is not heading toward us. Its light left more than ten billion years ago, and the universe has been expanding between us ever since. We will never meet it.", 1),
 ('u32_reverse', "But here is the part I find hardest to put down. We asked whether TON six-eighteen could swallow a galaxy. The deeper question runs the other way. How did something like this come to exist at all?", 0),
 ('u33_young', "When its light left, the universe was about three billion years old. And already, a black hole of tens of billions of Suns had formed and grown.", 0),
 ('u34_alma', "Observations with the Atacama Large Millimeter Array revealed an enormous cloud of gas surrounding the quasar and its host galaxy, one of the largest of its kind ever found.", 0),
 ('u35_grows', "A black hole like this does not grow by eating a galaxy. It grows inside one, fed by the gas around it, in a partnership we are still trying to understand.", 1),
 ('u36_geometry', "Gravity, in the end, is not a hunger. It is geometry. It shapes the path of everything, and asks only that the paths be followed.", 0),
 ('u37_paths', "A galaxy is a hundred billion stars, each tracing its own path. And a black hole, even one as vast as TON six-eighteen, is simply one more traveler bound by the same rules.", 1),
 ('u38_end', "The same laws that keep the Earth circling the Sun govern the black hole at the edge of the visible universe. And they tell us something quietly reassuring. Even the largest monster cannot take what does not fall.", 1),
]
BASE3 = 0.0
DUR3 = {k: S1.est(t, p) for k, t, p in SEQ3}
START3 = {}; _a = BASE3
for k, t, p in SEQ3:
    START3[k] = _a; _a += DUR3[k]
TOTAL3 = _a

def I(x, y, t, s=36, c=WH, a=1.0, an='mm', w='Bold'):
    return {'k': 'text', 'x': x, 'y': y, 't': t, 's': s, 'c': c, 'a': a, 'an': an, 'w': w}
def fadein(u, a, b=None): return sm(A(u, a, (a + 0.15) if b is None else b))

def comp_gb(tg, bhx=1040, th=85, gcx=420, gs=330, expo=1.0):
    return enc(tg, gcx, 370, gs, 60, bhx, 350, th, expo=expo)

# ---------- restricted N-body: disk of test particles, a massive perturber, galaxy potential ----------
class DiskSim:
    def __init__(s, scen, n=20000, seed=3):
        rng = np.random.default_rng(seed)
        r = 0.12 + 0.95 * rng.random(n) ** 0.75; ph = rng.random(n) * 2 * np.pi
        s.r0 = r.astype(np.float32)
        s.P = np.stack([r * np.cos(ph), r * np.sin(ph), rng.normal(0, 0.012, n)], 1).astype(np.float32)
        v = r / np.sqrt(r * r + 0.0025)
        s.V = np.stack([-v * np.sin(ph), v * np.cos(ph), np.zeros(n)], 1).astype(np.float32)
        s.G = np.zeros(3); s.GV = np.zeros(3)
        warm = np.clip(1 - r / 0.45, 0, 1) ** 1.2
        col = np.stack([0.6 + 0.4 * warm, 0.7 + 0.15 * warm, 1.0 - 0.5 * warm], 1)
        s.col = (col * (0.25 + 0.4 * np.exp(-r * 2.5))[:, None]).astype(np.float32)
        cfg = {'flyby': dict(B=(-7.0, -2.5, 0.3), BV=(1.6, 0.0, 0.0), mb=0.45, T=18.0, drag=0.0),
               'plunge': dict(B=(0.35, 0.1, -5.0), BV=(0.0, 0.0, 1.9), mb=0.20, T=14.0, drag=0.0),
               'sink': dict(B=(2.2, 0.0, 0.3), BV=(0.0, 0.5, 0.0), mb=0.25, T=26.0, drag=0.7)}[scen]
        s.B = np.array(cfg['B'], float); s.BV = np.array(cfg['BV'], float); s.mb = cfg['mb']; s.T = cfg['T']; s.drag = cfg['drag']
        s.sb = 0.12; s.dt = 0.02; s.steps = int(s.T / s.dt); s.i = 0; s.trail = []
    def step(s):
        dt = s.dt
        def accP(P):
            d = P - s.G; r2 = (d * d).sum(1) + 0.0025
            a = -d / r2[:, None]
            db = s.B - P; q = (db * db).sum(1) + s.sb ** 2
            return a + s.mb * db / (q ** 1.5)[:, None]
        a0 = accP(s.P)
        s.V += 0.5 * dt * a0; s.P += dt * s.V
        # galaxy centre and perturber
        dB = s.B - s.G; q = (dB @ dB) + s.sb ** 2
        aG = 0.6 * s.mb * dB / q ** 1.5
        dd = s.B - s.G; r2 = dd @ dd + 0.0025
        aB = -dd / r2
        if s.drag: aB += -s.drag * (s.BV - s.GV) / (1 + (dd @ dd) / 4.0)
        s.GV += dt * aG; s.G += dt * s.GV
        s.BV += dt * aB; s.B += dt * s.BV
        a1 = accP(s.P)
        s.V += 0.5 * dt * a1
        s.i += 1
        if s.i % 3 == 0: s.trail.append(s.B - s.G)
    def advance(s, upto):
        while s.i < min(upto, s.steps): s.step()
_SIMS = {}
def sim_frame(scen, u, cx, cy, scale, tilt, cap, label, sublabel=None, extra=None):
    s = _SIMS.get(scen)
    if s is None: s = _SIMS[scen] = DiskSim(scen)
    s.advance(int(u * s.steps))
    P = s.P - s.G.astype(np.float32); B = s.B - s.G
    tl = np.radians(tilt); ct, st = np.cos(tl), np.sin(tl)
    sx = (cx + P[:, 0] * scale).astype(np.int32); sy = (cy + (P[:, 1] * ct - P[:, 2] * st) * scale).astype(np.int32)
    ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H); idx = sy[ok] * W + sx[ok]
    lay = np.empty((H, W, 3), np.float32)
    for ch in range(3): lay[:, :, ch] = np.bincount(idx, weights=s.col[ok, ch], minlength=W * H).reshape(H, W)
    lay *= float(np.clip((330 / scale) ** 1.2, 0.6, 3))
    gl = cv2.GaussianBlur(lay, (0, 0), 4) * 1.5 + cv2.GaussianBlur(lay, (0, 0), 1.2) * 0.8 + lay * 0.6
    img = screen(BG * 0.7, 1 - np.exp(-gl * 1.1))
    # perturber trail + body
    for k in range(1, len(s.trail)):
        p0 = s.trail[k - 1]; p1 = s.trail[k]
        a = k / len(s.trail)
        x0 = cx + p0[0] * scale; y0 = cy + (p0[1] * ct - p0[2] * st) * scale
        x1 = cx + p1[0] * scale; y1 = cy + (p1[1] * ct - p1[2] * st) * scale
        cv2.line(img, (int(x0), int(y0)), (int(x1), int(y1)), (1.0 * a, 0.6 * a, 0.25 * a), 2, cv2.LINE_AA)
    bx = cx + B[0] * scale; by = cy + (B[1] * ct - B[2] * st) * scale
    circ(img, bx, by, 13, (0, 0, 0)); circ(img, bx, by, 17, (1.0, 0.6, 0.25), 3)
    img = glowdot(img, bx, by, 18, (1.0, 0.55, 0.2), 1.3)
    items = [I(640, 60, label, 34, GOLD, fadein(u, 0.0, 0.1))]
    if sublabel: items.append(I(640, 100, sublabel, 22, GR, fadein(u, 0.05, 0.15), w='Medium'))
    if extra: items += extra(u)
    return overlay(vignette(img), items, caption=cap, tag='CONCEPTUAL ILLUSTRATION · NOT A PREDICTION')

def f_u01(t, T, tg, cap):
    u = t / T
    img = comp_gb(tg, bhx=lerp(1200, 1040, sm(u)), th=lerp(60, 85, sm(u)))
    items = [I(420, 590, 'THE MILKY WAY', 30, WH, fadein(u, 0.25)), I(1040, 520, 'TON 618', 30, GOLD, fadein(u, 0.4))]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def f_u02(t, T, tg, cap):
    u = sm(t / T)
    sc = lerp(450, 2600, u ** 1.3)
    img = gal(640 - (sc - 450) * 0.20, 350 + (sc - 450) * 0.05, sc, lerp(62, 40, u), tg, expo=lerp(1.1, 2.4, u))
    return overlay(vignette(img), [I(640, 620, 'MOSTLY EMPTY SPACE', 50, WH, fadein(t / T, 0.45, 0.65))], caption=cap)
def f_u03(t, T, tg, cap):
    u = t / T
    img = BG * 0.45
    a1 = fadein(u, 0.05); a2 = fadein(u, 0.4); p = sm(A(u, 0.25, 0.6))
    img = glowdot(img.copy(), 200, 360, 9, (1.0, 0.9, 0.5), 2.0) if a1 > 0.01 else img
    img = glowdot(img, 1080, 360, 9, (0.8, 0.9, 1.0), 2.0) if a2 > 0.01 else img
    items = [I(200, 300, 'OUR SUN', 24, WH, a1), I(200, 420, 'A GOLF BALL · NEW YORK', 22, GR, a1, w='Medium'),
             {'k': 'line', 'x1': 215, 'y1': 360, 'x2': 215 + 850 * p, 'y2': 360, 'wd': 2, 'c': GOLD, 'a': 0.9},
             I(1080, 300, 'NEAREST STAR', 24, WH, a2), I(1080, 420, 'ANOTHER GOLF BALL · CHICAGO', 22, GR, a2, w='Medium'),
             I(640, 330, '≈ 1,150 KM', 40, GOLD, fadein(u, 0.5, 0.7))]
    return overlay(vignette(img), items, caption=cap, tag='SCALE ANALOGY')
def f_u04(t, T, tg, cap):
    u = t / T
    rng = np.random.default_rng(9)
    img = BG * 0.35
    xs = rng.integers(40, W - 40, 70); ys = rng.integers(40, H - 80, 70)
    for i, (x, y) in enumerate(zip(xs, ys)):
        a = fadein(u, 0.02 + i * 0.006, 0.12 + i * 0.006)
        if a > 0.02: img = glowdot(img, x, y, 4, (0.8, 0.9, 1.0), 1.6 * a)
    items = [I(640, 90, 'BILLIONS OF STARS', 46, WH, fadein(u, 0.2)), I(640, 640, 'ALMOST NONE NEAR EACH OTHER', 36, GOLD, fadein(u, 0.55))]
    return overlay(vignette(img), items, caption=cap)
def f_u05(t, T, tg, cap):
    u = t / T
    img = gal(640, 370, 210, 58, tg, expo=1.0)
    yy, xx = gy_, gx_
    d = np.sqrt((xx - 640) ** 2 + (yy - 370) ** 2)
    R = 120 + 420 * sm(A(u, 0.1, 0.7))
    halo = np.exp(-(d / R) ** 2) * 0.28 * sm(A(u, 0.05, 0.4))
    img = screen(img, np.stack([halo * 0.55, halo * 0.35, halo * 1.0], 2))
    items = [{'k': 'ring', 'x': 640, 'y': 370, 'r': R * 1.25, 'c': (150, 120, 255), 'wd': 2, 'a': 0.55 * fadein(u, 0.3, 0.5)},
             I(640, 90, 'DARK MATTER HALO', 40, (190, 170, 255), fadein(u, 0.25)),
             I(640, 630, '> 1 TRILLION SUNS  (ESTIMATE)', 40, WH, fadein(u, 0.6, 0.8))]
    return overlay(vignette(img), items, caption=cap, tag='ILLUSTRATION')
def f_u06(t, T, tg, cap):
    u = t / T
    img = BG * 0.4
    x0 = 150; X = lambda v: x0 + v / 1000.0 * 980
    p1 = sm(A(u, 0.05, 0.4)); p2 = sm(A(u, 0.35, 0.65)); p3 = sm(A(u, 0.6, 0.9))
    items = [I(640, 60, 'ON ONE LINEAR SCALE', 28, GR, 1, w='Medium'),
             I(x0, 190, 'TOTAL MASS, WITH DARK MATTER  >  1,000 BILLION SUNS', 26, WH, p1, 'lm'),
             {'k': 'rect', 'x1': x0, 'y1': 220, 'x2': x0 + 980 * p1, 'y2': 270, 'c': (150, 130, 255), 'a': 0.85},
             I(x0, 360, 'VISIBLE STARS  ≈ 60 BILLION', 26, WH, p2, 'lm'),
             {'k': 'rect', 'x1': x0, 'y1': 390, 'x2': x0 + (X(60) - x0) * p2, 'y2': 440, 'c': (170, 195, 255), 'a': 0.9},
             I(x0, 520, 'TON 618  ≈ 40–66 BILLION', 26, GOLD, p3, 'lm'),
             {'k': 'rect', 'x1': x0, 'y1': 550, 'x2': x0 + (X(66) - x0) * p3, 'y2': 600, 'c': GOLD, 'a': 0.9},
             I(640, 660, 'A COMPACT OBJECT WITH A FEW PERCENT OF THE GALAXY\'S MASS', 24, GR, fadein(u, 0.8, 0.95), w='Medium')]
    return overlay(vignette(img), items, caption=cap)
def f_u07(t, T, tg, cap):
    u = t / T
    img = BG * 0.45
    items = [I(640, 90, 'THREE VERY DIFFERENT STORIES', 44, WH, 1)]
    cards = [(240, '1', 'FLYBY'), (640, '2', 'PLUNGE'), (1040, '3', 'IT STAYS')]
    for i, (x, n, nm) in enumerate(cards):
        a = fadein(u, 0.2 + i * 0.22)
        items += [{'k': 'ring', 'x': x, 'y': 330, 'r': 110, 'c': GOLD, 'wd': 3, 'a': 0.85 * a}, I(x, 330, n, 90, GOLD, a), I(x, 500, nm, 40, WH, a)]
    return overlay(vignette(img), items, caption=cap)
def f_u08(t, T, tg, cap):
    return sim_frame('flyby', t / T, 640, 360, 190, 55, cap, 'SCENARIO 1 · A DISTANT FLYBY', 'THE GALAXY IS SCARRED, NOT EATEN',
                     lambda u: [I(640, 650, 'TIDAL FORCES STRETCH THE DISK', 30, WH, fadein(u, 0.55))])
def f_u09(t, T, tg, cap):
    return sim_frame('plunge', t / T, 640, 380, 300, 62, cap, 'SCENARIO 2 · A PLUNGE THROUGH THE DISK', 'MOST STARS: REARRANGED, NOT REMOVED',
                     lambda u: [I(640, 660, 'SHAKEN · WARPED · HEATED', 30, WH, fadein(u, 0.5))])
def f_u10(t, T, tg, cap):
    return sim_frame('sink', t / T, 640, 380, 270, 60, cap, 'SCENARIO 3 · IT STAYS', 'DYNAMICAL FRICTION: IT SINKS TOWARD THE CENTER',
                     lambda u: [I(640, 660, 'SAGITTARIUS A*', 34, (255, 225, 160), fadein(u, 0.8, 0.95))])
def f_u11(t, T, tg, cap):
    u = t / T
    img = gal(640, 370, 380, 60, tg, expo=0.6)
    img = center_obj(img, 'bh', 640, 370, 8)
    items = [I(640, 620, 'WHAT HAPPENS NEXT?', 56, WH, fadein(u, 0.2))]
    return overlay(vignette(img), items, caption=cap if False else cap, tag=TAG)
def f_u12(t, T, tg, cap):
    u = t / T
    img = lens(BG * 0.5, 960, 360, 110)
    items = [I(330, 300, 'MASS', 110, GOLD, fadein(u, 0.1)), I(330, 420, '≠', 110, WH, fadein(u, 0.3)), I(330, 540, 'CAPTURE', 110, WH, fadein(u, 0.5))]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def f_u13(t, T, tg, cap):
    u = t / T
    img = BG * 0.45
    cx, cy = 780, 360; R = 70
    img = lens(img, cx, cy, 130, shadow=True, ring=True)
    items = []
    for k in range(7):
        y0 = 120 + k * 80
        pts = []
        for xx in range(60, 700, 8):
            dx = xx - cx; dy = y0 - cy
            b = dy; rr = np.hypot(dx, dy) + 1
            bend = -dy / (abs(dy) + 30) * 200 * np.exp(-((dx) / 260) ** 2)
            pts.append((xx, y0 + bend * sm(A(u, 0.05, 0.5))))
        pr = sm(A(u, 0.0, 0.5))
        items += [{'k': 'line', 'x1': pts[i][0], 'y1': pts[i][1], 'x2': pts[i + 1][0], 'y2': pts[i + 1][1], 'wd': 2, 'c': (255, 235, 170), 'a': 0.5 * pr} for i in range(len(pts) - 1)]
    items += [{'k': 'ring', 'x': cx, 'y': cy, 'r': 72, 'c': GOLD, 'wd': 3, 'a': fadein(u, 0.4, 0.6)},
              I(cx, 560, 'EVENT HORIZON', 36, GOLD, fadein(u, 0.45)), I(cx, 604, 'INSIDE IT, NOTHING ESCAPES — NOT EVEN LIGHT', 22, WH, fadein(u, 0.6, 0.8), w='Medium')]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def f_u14(t, T, tg, cap):
    u = t / T
    img = BG * 0.4
    cx, cy = 640, 370; R = 280
    zi = sm(A(u, 0.0, 0.2))
    yy, xx = gy_, gx_
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    img = img * np.clip((d - R * zi) / 3, 0, 1)[:, :, None]
    items = [{'k': 'ring', 'x': cx, 'y': cy, 'r': R * zi + 1, 'c': GOLD, 'wd': 4},
             {'k': 'ring', 'x': cx, 'y': cy, 'r': 30 / 1300 * R + 1, 'c': (130, 200, 255), 'wd': 2, 'a': fadein(u, 0.4, 0.55)},
             {'k': 'dot', 'x': cx, 'y': cy, 'r': 3, 'c': (255, 230, 150), 'a': fadein(u, 0.4, 0.55)},
             I(cx, 90, 'EVENT HORIZON  ·  RADIUS ≈ 1,300 AU', 36, GOLD, fadein(u, 0.15)),
             I(cx, 660, "≈ 0.04 LIGHT-YEARS ACROSS", 34, WH, fadein(u, 0.75)),
             I(cx + 150, cy - 40, "NEPTUNE'S ORBIT", 22, (150, 210, 255), fadein(u, 0.45), 'lm'),
             I(cx + 150, cy - 10, "30 AU  ·  THE SOLAR SYSTEM FITS 40+ TIMES", 20, GR, fadein(u, 0.5), 'lm', 'Medium')]
    return overlay(vignette(img), items, caption=cap, tag='TO SCALE')
def f_u15(t, T, tg, cap):
    u = t / T
    img = BG * 0.4
    items = []
    p = sm(A(u, 0.1, 0.45))
    cx, cy = 640, 360
    items += [{'k': 'ring', 'x': cx, 'y': cy, 'r': 290 * p + 1, 'c': (150, 180, 255), 'wd': 3},
              I(cx, 60, 'THE GALAXY  =  A CITY 50 KM ACROSS', 34, (190, 205, 255), fadein(u, 0.2)),
              {'k': 'dot', 'x': cx, 'y': cy, 'r': 3, 'c': (255, 225, 140), 'a': fadein(u, 0.5, 0.65)},
              {'k': 'ring', 'x': cx, 'y': cy, 'r': 10 + 5 * np.sin(t * 6), 'c': GOLD, 'wd': 2, 'a': fadein(u, 0.55, 0.7)},
              I(cx, 660, 'THE HORIZON  =  A COIN IN THE MIDDLE', 36, GOLD, fadein(u, 0.62)),
              I(cx, 560, '≈ 2,500,000 × SMALLER', 30, WH, fadein(u, 0.78))]
    return overlay(vignette(img), items, caption=cap, tag='SCALE ANALOGY')
def f_u16(t, T, tg, cap):
    pans = [dict(cx=640, cy=370, sc=250, kind='bh', key='u16a', cr=14, vy=v, x0=1.0, y0=0.0, turns=tr, col=(0.6, 0.8, 1.0), trail=100)
            for v, tr in [(0.5, 1.3), (0.62, 1.5), (0.78, 1.7), (0.95, 1.9)]]
    pans = [dict(p, key=f'u16_{i}') for i, p in enumerate(pans)]
    pans.append(dict(cx=640, cy=370, sc=250, kind='bh', key='u16_plunge', cr=14, vy=0.02, x0=1.0, y0=0.0, turns=0.5, col=(1.0, 0.45, 0.35), trail=100))
    return orbit_scene(t, T, tg, cap, pans, lambda u: [I(640, 80, 'THE LOSS CONE', 46, WH, fadein(u, 0.1)),
                                                      I(640, 640, 'ONLY NEAR-HEAD-ON ORBITS FALL IN. THE REST KEEP MISSING.', 28, GOLD, fadein(u, 0.5), w='Bold')])
def f_u17(t, T, tg, cap):
    u = t / T
    img = BG * 0.4
    items = [I(640, 100, 'ONE STAR SWALLOWED OR TORN APART', 38, WH, fadein(u, 0.05)),
             I(640, 150, 'EVERY ≈ 10,000 TO 100,000 YEARS', 40, GOLD, fadein(u, 0.15)),
             {'k': 'line', 'x1': 120, 'y1': 400, 'x2': 1160, 'y2': 400, 'wd': 3, 'c': (110, 130, 170)}]
    for k in range(11):
        x = 120 + k * 104
        items.append({'k': 'line', 'x1': x, 'y1': 388, 'x2': x, 'y2': 412, 'wd': 2, 'c': (110, 130, 170)})
    for k, fr in enumerate([0.25, 0.62]):
        x = 120 + 1040 * fr
        a = fadein(u, fr * 0.9, fr * 0.9 + 0.1)
        if a > 0.02: img = glowdot(img.copy(), x, 400, 14, (1.0, 0.8, 0.4), 2.5 * a)
    items += [I(120, 450, '0', 20, GR, 1, 'mm', 'Medium'), I(1160, 450, '100,000 YEARS', 20, GR, 1, 'rm', 'Medium'),
              I(640, 600, 'MOST STARS NEVER COME NEAR', 34, WH, fadein(u, 0.7))]
    return overlay(vignette(img), items, caption=cap)
def f_u18(t, T, tg, cap):
    u = t / T
    img = BG * 0.4; items = []
    for cx, kind, big in [(330, 'small', False), (950, 'big', True)]:
        r = 14 if not big else 46
        img = center_obj(img, 'bh', cx, 380, r)
        p = sm(A(u, 0.15, 0.8))
        sx = cx - 240 + (240 - r * 2.6) * p
        sy = 380 - 90 * (1 - p)
        near = sm(A(p, 0.55, 1.0))
        stretch = 1 + (7 * near if not big else 0.0)
        w = 9 * (1.0 if big else (1 - 0.6 * near))
        lay = np.zeros_like(img)
        cv2.ellipse(lay, (int(sx), int(sy)), (int(w * stretch) + 1, int(max(2, w * 0.7))), 20 if not big else 0, 0, 360, (1.0, 0.9, 0.5), -1, cv2.LINE_AA)
        img = screen(img, np.clip(cv2.GaussianBlur(lay, (0, 0), 3) * 1.4 + lay, 0, 1))
    items += [I(330, 190, 'SAGITTARIUS A*', 30, WH, fadein(u, 0.05)), I(330, 230, 'THE STAR IS TORN APART', 22, (255, 150, 120), fadein(u, 0.6), w='Medium'),
              I(950, 190, 'TON 618', 30, GOLD, fadein(u, 0.4)), I(950, 230, 'GENTLER TIDES AT THE HORIZON', 22, (150, 230, 170), fadein(u, 0.7), w='Medium')]
    return overlay(vignette(img), items, caption=cap, tag='SIMPLIFIED ILLUSTRATION')
def f_u19(t, T, tg, cap):
    u = t / T
    img = lens(BG * 0.6, 780, 360, 150)
    p = sm(A(u, 0.1, 0.7))
    sx = lerp(180, 780, p); sy = lerp(260, 360, p)
    rr = np.hypot(sx - 780, sy - 360)
    vis = float(np.clip((rr - 82) / 20, 0, 1))
    if vis > 0.02: img = glowdot(img.copy(), sx, sy, 8, (1.0, 0.92, 0.6), 2.0 * vis)
    items = [I(380, 120, '≈ 100 MILLION SUNS', 36, WH, fadein(u, 0.05)), I(380, 165, 'THE LIMIT FOR SUN-LIKE STARS TO CROSS WHOLE', 20, GR, fadein(u, 0.1), w='Medium'),
             I(780, 630, 'TON 618: WHOLE · NO FLASH', 44, GOLD, fadein(u, 0.7))]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def f_u20(t, T, tg, cap):
    u = t / T
    img = BG * 0.4; rng = np.random.default_rng(4)
    items = [{'k': 'line', 'x1': 640, 'y1': 140, 'x2': 640, 'y2': 600, 'wd': 1, 'c': (90, 105, 140), 'a': 0.6}]
    p = sm(A(u, 0.1, 0.9))
    for i in range(30):
        y = 200 + rng.random() * 360
        xa = 40 + rng.random() * 40 + 560 * p; xb = 590 - rng.random() * 40 - 560 * p
        img = glowdot(img.copy(), xa, y, 3, (0.6, 0.8, 1.0), 1.4)
        img = glowdot(img, xb, y + 20, 3, (1.0, 0.85, 0.6), 1.4)
    c = sm(A(u, 0.1, 0.55)); hot = sm(A(u, 0.5, 0.85))
    for k, (dy) in enumerate([-60, 0, 60]):
        xl = 700 + 160 * c; xr = 1200 - 160 * c
        col = (0.5 + 0.5 * hot, 0.55 + 0.1 * hot, 0.8 - 0.5 * hot)
        lay = np.zeros_like(img); cv2.circle(lay, (int(xl), 370 + dy), 44, col, -1, cv2.LINE_AA); cv2.circle(lay, (int(xr), 370 - dy), 44, col, -1, cv2.LINE_AA)
        img = screen(img, np.clip(cv2.GaussianBlur(lay, (0, 0), 14) * 0.7, 0, 1))
    if hot > 0.05: img = glowdot(img, 940, 370, 40, (1.0, 0.8, 0.4), 2.5 * hot)
    items += [I(320, 100, 'STARS: PASS THROUGH EACH OTHER', 26, (150, 200, 255), fadein(u, 0.05)), I(960, 100, 'GAS: COLLIDES, HEATS, SHINES', 26, (255, 200, 140), fadein(u, 0.35))]
    return overlay(vignette(img), items, caption=cap, tag='SIMPLIFIED ILLUSTRATION')
def f_u21(t, T, tg, cap):
    u = t / T
    img = quasar(tg, 360, 380, 135, inflow=1.0)
    items = [I(760, 200, 'GAS LOSES ITS ANGULAR MOMENTUM', 24, WH, fadein(u, 0.1), 'lm'), I(760, 245, 'AND SPIRALS INWARD', 24, WH, fadein(u, 0.2), 'lm'),
             I(760, 360, 'THIS FEEDS THE QUASAR', 30, GOLD, fadein(u, 0.5), 'lm'), I(760, 405, 'TON 618 IS SWALLOWING GAS RIGHT NOW', 20, (255, 220, 160), fadein(u, 0.7), 'lm', 'Medium')]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def f_u22(t, T, tg, cap):
    u = t / T
    img = BG * 0.4; items = []
    x0, x1, y0, y1 = 140, 640, 180, 560
    drain = sm(A(u, 0.25, 0.8))
    level = 1 - drain
    items += [{'k': 'rect', 'x1': x0, 'y1': y0, 'x2': x1, 'y2': y1, 'c': (30, 34, 50), 'a': 0.9},
              {'k': 'rect', 'x1': x0, 'y1': y1 - (y1 - y0) * level, 'x2': x1, 'y2': y1, 'c': (255, 170, 90), 'a': 0.85},
              I((x0 + x1) // 2, 130, 'GAS IN THE MILKY WAY', 28, WH, fadein(u, 0.05)), I((x0 + x1) // 2, 160, '≈ 10 BILLION SUNS', 24, (255, 200, 140), fadein(u, 0.1), w='Medium'),
              I((x0 + x1) // 2, 610, 'TENS OF SUNS OF GAS PER YEAR  (ROUGH ESTIMATE)', 22, GR, fadein(u, 0.15), w='Medium'),
              I(900, 150, 'TIME', 26, GR, fadein(u, 0.2), w='Medium'), I(900, 210, f'{int(100 * drain)} MILLION YEARS', 44, GOLD, fadein(u, 0.2)),
              I(900, 300, 'A BLINK, FOR A GALAXY', 30, WH, fadein(u, 0.75))]
    rng = np.random.default_rng(6)
    for i in range(120):
        x = 740 + rng.random() * 400; y = 360 + rng.random() * 200
        img = glowdot(img.copy(), x, y, 2.5, (0.8, 0.9, 1.0), 1.2) if i < 100 else img
    items += [I(940, 610, 'THE 100 BILLION STARS ARE STILL THERE', 24, (170, 200, 255), fadein(u, 0.82), w='Medium')]
    return overlay(vignette(img), items, caption=cap, tag='ROUGH ESTIMATE')
def f_u23(t, T, tg, cap):
    u = t / T
    img = lens(BG * 0.5, 1000, 360, 100)
    items = [I(500, 250, 'NOT A SWALLOWING.', 60, WH, fadein(u, 0.1), 'mm'), I(500, 380, 'AN ORBITAL CATASTROPHE.', 56, GOLD, fadein(u, 0.5), 'mm')]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def f_u24(t, T, tg, cap):
    u = t / T
    img = BG * 0.35; items = []
    cx, cy = 640, 370
    r = 150 * (1 - 0.93 * sm(A(u, 0.05, 0.85))) + 6
    om = 2.0 * (150 / r) ** 1.5 * 0.35
    ph = np.cumsum([0])[0] + 0
    # integrate phase deterministically from u
    uu = np.linspace(0, u, 80); rr = 150 * (1 - 0.93 * sm((uu - 0.05) / 0.8)) + 6
    phase = float(np.sum(0.35 * 2.0 * (150 / rr) ** 1.5) * (u / 80) * T * 0.35)
    x1 = cx + r * np.cos(phase); y1 = cy + r * 0.7 * np.sin(phase); x2 = cx - r * np.cos(phase); y2 = cy - r * 0.7 * np.sin(phase)
    rng = np.random.default_rng(12)
    for i in range(60):
        a0 = rng.random() * 2 * np.pi; rad0 = 40 + rng.random() * 140; t_ej = 0.15 + rng.random() * 0.6
        if u < t_ej:
            ang = a0 + u * 3 * (150 / rad0) ** 1.0; rr_ = rad0
        else:
            k = (u - t_ej); ang = a0 + t_ej * 3 * (150 / rad0); rr_ = rad0 + 900 * k ** 1.3
        img = glowdot(img.copy(), cx + rr_ * np.cos(ang), cy + rr_ * 0.75 * np.sin(ang), 2.5, (0.8, 0.9, 1.0), 1.2)
    merged = u > 0.88
    if not merged:
        for (x, y, rad) in [(x1, y1, 12), (x2, y2, 10)]:
            circ(img, x, y, rad, (0, 0, 0)); circ(img, x, y, rad * 1.3, (1.0, 0.6, 0.25), 2)
