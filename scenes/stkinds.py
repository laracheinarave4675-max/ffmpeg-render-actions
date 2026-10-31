import numpy as np, cv2, math
from stlib import *
rng0 = np.random.default_rng(11)
def seeded(k, n, w=W, h=H):
    r = np.random.default_rng(k); return r.random(n) * w, r.random(n) * h
# ---------- backgrounds for cards ----------
def bg_none(cv, t, u): pass
def bg_string(cv, t, u):
    for i, (y, m, c) in enumerate([(150, 2, CYAN), (570, 3, VIOLET), (360, 5, GOLD)]):
        string_open(cv, 90, 1190, y, m, t + i, 26, c, 2, a=0.35)
def bg_loop(cv, t, u):
    string_loop(cv, 640, 360, 260, 3, t, 0.12, CYAN, 2, a=0.35, tilt=0.55)
    string_loop(cv, 640, 360, 190, 5, t + 1, 0.10, VIOLET, 2, a=0.3, tilt=0.55)
def bg_grid(cv, t, u): grid_well(cv, 640, 330, 70 + 25 * math.sin(t * 0.8), t, a=0.35)
def bg_cy(cv, t, u): draw_cy(cv, t, 5, 340, 640, 360, a=0.3)
def bg_dots(cv, t, u):
    xs, ys = seeded(5, 70)
    for x, y in zip(xs, ys): cv.dot(x + 12 * math.sin(t + x), y + 10 * math.cos(t * 0.8 + y), 2, CYAN, 0.35, 0.4)
BGS = {'none': bg_none, 'string': bg_string, 'loop': bg_loop, 'grid': bg_grid, 'cy': bg_cy, 'dots': bg_dots}
def draw_cy(cv, t, n, sc, cx, cy, a=0.8, c=(120, 200, 255)):
    L = cy_lines(n)
    ax = 0.5 + 0.2 * math.sin(t * 0.3); ay = t * 0.35
    for ln in L:
        pts, z = project(ln, ax, ay, f=sc * 2.2, d=3.2, cx=cx, cy=cy)
        shade = float(np.clip(0.55 - z.mean() * 0.3, 0.2, 1.0))
        cc = (int(c[0] * shade), int(c[1] * shade), int(c[2] * (0.6 + 0.4 * shade)))
        cv.line(pts, cc, 1, a * 0.8, 0.5)
# ---------- zoom ----------
def zoom_layer(cv, i, alpha, sc, t):
    if alpha <= 0.01: return []
    its = []
    r = np.random.default_rng(i + 3)
    if i == 0:   # object surface: dense lattice of tiny points
        for gx in range(-14, 15):
            for gy in range(-8, 9):
                x = 640 + gx * 46 * sc; y = 360 + gy * 46 * sc
                if 0 <= x < W and 0 <= y < H: cv.dot(x, y, 2 + 1.2 * sc, (170, 190, 230), alpha * 0.5, 0.4)
        its.append(I(640, 640, 'AN ORDINARY OBJECT', 32, WHITE, alpha))
    elif i == 1:  # molecules
        for gx in range(-4, 5):
            for gy in range(-2, 3):
                bx = 640 + gx * 150 * sc + 20 * math.sin(t + gx); by = 360 + gy * 130 * sc + 14 * math.cos(t * 1.1 + gy)
                for k in range(3):
                    a_ = k * 2.1 + 0.4 * math.sin(t * 0.7 + gx * gy)
                    px = bx + math.cos(a_) * 34 * sc; py = by + math.sin(a_) * 34 * sc
                    cv.line([(bx, by), (px, py)], (160, 190, 255), 2, alpha * 0.6, 0.3)
                    cv.dot(px, py, 10 * sc, (255, 150, 140) if k else (130, 190, 255), alpha, 0.6)
                cv.dot(bx, by, 14 * sc, (120, 200, 255), alpha, 0.6)
        its.append(I(640, 640, 'MOLECULES', 32, WHITE, alpha))
    elif i == 2:  # atom
        cv.blob(640, 360, 22 * sc, (255, 190, 120), 0.9 * alpha)
        cv.dot(640, 360, 7 * sc, (255, 220, 160), alpha, 1.0)
        for k in range(160):
            rr = (0.4 + 0.6 * r.random()) * 300 * sc; th = r.random() * 6.283 + t * 0.4 * (1.5 - rr / 400)
            cv.dot(640 + rr * math.cos(th), 360 + rr * math.sin(th) * 0.9, 2, (110, 190, 255), alpha * 0.55, 0.8)
        its.append(I(640, 650, 'A HAZE OF ELECTRONS AROUND A TINY NUCLEUS', 28, WHITE, alpha))
    elif i == 3:  # nucleus
        for k in range(14):
            th = r.random() * 6.283; rr = 95 * math.sqrt(r.random()) * sc
            x = 640 + rr * math.cos(th + 0.2 * math.sin(t + k)); y = 360 + rr * math.sin(th + 0.2 * math.sin(t + k))
            cc = (255, 120, 110) if k % 2 else (140, 170, 255)
            cv.blob(x, y, 22 * sc, cc, 0.55 * alpha); cv.dot(x, y, 24 * sc, cc, alpha * 0.9, 0.6)
        its.append(I(640, 650, 'PROTONS AND NEUTRONS', 28, WHITE, alpha))
    elif i == 4:  # quarks
        cols = [(255, 90, 90), (90, 255, 140), (110, 150, 255)]
        pts = []
        for k in range(3):
            th = k * 2.094 + t * 0.9
            x = 640 + 70 * sc * math.cos(th) + 6 * math.sin(t * 7 + k); y = 360 + 70 * sc * math.sin(th) + 6 * math.cos(t * 6 + k)
            pts.append((x, y))
        for a_ in range(3):
            for b_ in range(a_ + 1, 3):
                cv.line([pts[a_], pts[b_]], (255, 235, 170), 2, alpha * 0.6, 0.7)
        for k, (x, y) in enumerate(pts):
            cv.blob(x, y, 24 * sc, cols[k], 0.8 * alpha); cv.dot(x, y, 15 * sc, cols[k], alpha, 0.9)
        its.append(I(640, 650, 'QUARKS, BOUND BY GLUONS', 28, WHITE, alpha))
    elif i == 5:
        cv.blob(640, 360, 20 * sc, (255, 255, 255), 1.0 * alpha); cv.dot(640, 360, 6, (255, 255, 255), alpha, 1.0)
    return its
def k_zoom(cv, t, T, u, P):
    s0, s1 = P.get('s0', 0), P.get('s1', 1)
    st = lerp(s0, s1, sm(u))
    its = []; dom = int(round(st))
    for i in range(6):
        d = st - i
        alpha = float(np.clip(1.0 - abs(d) * 1.35, 0, 1))
        sc = math.exp(d * 1.5) if d > 0 else math.exp(d * 0.9)
        sc = float(np.clip(sc, 0.5, 4.5))
        li = zoom_layer(cv, i, alpha, sc, t)
        its += [x for x in li if x.get('k') != 'text' or i == dom]
    return its
# ---------- point / dot ----------
def k_point(cv, t, T, u, P):
    its = []
    a = fin(u, 0.0, 0.2)
    cv.blob(640, 360, 26, (255, 255, 255), 0.9 * a); cv.dot(640, 360, 6, (255, 255, 255), a, 1.0)
    for k in range(3):
        ph = (t * 0.5 + k / 3) % 1; cv.ring(640, 360, 20 + ph * 280, CYAN, 1, (1 - ph) * 0.4 * a)
    its.append(I(640, 150, P.get('title', 'A POINT'), 52, WHITE, fin(u, 0.2, 0.4)))
    for i, ln in enumerate(P.get('lines', ['NO SIZE', 'NO PARTS'])):
        its.append(I(640, 540 + i * 50, ln, 36, GOLD, fin(u, 0.35 + i * 0.12, 0.55 + i * 0.12)))
    return its
def k_dotloop(cv, t, T, u, P):
    its = []
    g = sm(A(u, 0.15, 0.6))
    r = lerp(2, 130, g)
    cv.blob(640, 360, 24, (255, 255, 255), 0.6 * (1 - g))
    if g < 0.05: cv.dot(640, 360, 6, WHITE, 1, 1)
    else: string_loop(cv, 640, 360, r, 4, t, 0.12 * g, CYAN, 3, a=min(1, g * 2))
    its.append(I(640, 140, P.get('title', 'WHAT IF THE DOT IS NOT A DOT?'), 46, WHITE, fin(u, 0.05, 0.25)))
    its.append(I(640, 600, P.get('sub', 'A TINY LOOP INSTEAD OF A POINT?'), 30, GOLD, fin(u, 0.6, 0.8)))
    return its
# ---------- ladder (log scale) ----------
def k_ladder(cv, t, T, u, P):
    mode = P['mode']; its = []
    if mode == 'size':
        marks = [(-10, 'ATOM', '≈ 10^-10 m', CYAN), (-15, 'PROTON · NUCLEUS', '≈ 10^-15 m', (255, 140, 130)), (-19, 'SMALLEST SCALES PROBED AT THE LHC', '≈ 10^-19 m', GREEN), (-35, 'PLANCK LENGTH', '≈ 10^-35 m', GOLD)]
        lo, hi = -37, -8
    else:
        marks = [(4.13, 'LARGE HADRON COLLIDER', '≈ 10^4 GeV (13.6 TeV)', GREEN), (19.1, 'PLANCK ENERGY', '≈ 10^19 GeV', GOLD)]
        lo, hi = 2, 21
    x0, x1 = 160, 1120; y = 380
    cv.line([(x0, y), (x1, y)], GREY, 2, 0.8, 0.3)
    def px(v):
        f = (v - lo) / (hi - lo)
        return x0 + (x1 - x0) * (f if mode == 'energy' else 1 - f)
    reveal = P.get('reveal', len(marks))
    for i, (v, name, val, c) in enumerate(marks):
        a = fin(u, 0.05 + i * (0.8 / len(marks)) * 0.7, 0.18 + i * (0.8 / len(marks)) * 0.7)
        if i >= reveal: a = 0
        x = px(v); up = (i % 2 == 0)
        cv.line([(x, y - 14), (x, y + 14)], c, 3, a); cv.dot(x, y, 9, c, a)
        yy = y - 120 if up else y + 120
        cv.line([(x, y + (-14 if up else 14)), (x, yy + (30 if up else -30))], c, 1, a * 0.5, 0.2)
        its.append(I(x, yy, name, 24, c, a)); its.append(I(x, yy + (36 if up else 36), val, 22, WHITE, a * 0.9, 'Medium'))
    if mode == 'energy':
        g = fin(u, 0.7, 0.9); xa, xb = px(4.13), px(19.1)
        cv.line([(xa, y + 230), (xb, y + 230)], RED, 3, g)
        its.append(I((xa + xb) / 2, y + 270, 'A GAP OF ROUGHLY A QUADRILLION', 34, RED, g))
    if mode == 'size':
        g = fin(u, 0.75, 0.95)
        its.append(I(640, 640, P.get('foot', ''), 28, GOLD, g))
    its.insert(0, I(640, 110, P.get('title', ''), 40, WHITE, fin(u, 0.0, 0.15)))
    return its
# ---------- card ----------
def k_cards(cv, t, T, u, P):
    BGS[P.get('bg', 'none')](cv, t, u)
    n = len(P['lines'])
    return title_items(P['lines'], u, P.get('y', 360), P.get('sizes'), P.get('cols'), P.get('gap', 72))
def k_gap(cv, t, T, u, P):
    its = []
    a1 = fin(u, 0.05, 0.25); a2 = fin(u, 0.2, 0.4)
    cv.poly([(110, 240), (470, 240), (470, 520), (110, 520)], (60, 110, 200), 0.35 * a1)
    cv.poly([(810, 240), (1170, 240), (1170, 520), (810, 520)], (200, 140, 60), 0.35 * a2)
    its += [I(290, 300, 'MATHEMATICS', 36, CYAN, a1), I(290, 370, 'what the theory suggests', 24, WHITE, a1, 'Medium'),
            I(990, 300, 'EXPERIMENT', 36, GOLD, a2), I(990, 370, 'what we are able to test', 24, WHITE, a2, 'Medium')]
    g = fin(u, 0.45, 0.7)
    cv.line([(480, 380), (800, 380)], RED, 3, g * 0.8)
    for k in range(5):
        x = 500 + k * 60 + 10 * math.sin(t * 2 + k); cv.dot(x, 380, 3, RED, g * 0.8)
    its.append(I(640, 330, 'THE GAP', 40, RED, g)); its.append(I(640, 450, P.get('sub', 'THE DOCUMENTARY LIVES HERE'), 24, WHITE, fin(u, 0.7, 0.9)))
    return its
def k_pillars(cv, t, T, u, P):
    its = []
    a1 = fin(u, 0.05, 0.25); a2 = fin(u, 0.3, 0.5)
    # left: quantum cloud, right: curved grid
    r = np.random.default_rng(2)
    for k in range(120):
        rr = r.random() ** 0.6 * 150; th = r.random() * 6.283 + t * 0.5
        cv.dot(330 + rr * math.cos(th), 330 + rr * math.sin(th), 2, CYAN, a1 * 0.7, 0.6)
    its.append(I(330, 560, 'QUANTUM MECHANICS', 32, CYAN, a1)); its.append(I(330, 605, 'the very small', 24, WHITE, a1, 'Medium'))
    if a2 > 0:
        gw = grid_well(cv, 950, 300, 80, t, span=230, n=11, a=0.8 * a2, sig=70)
    its.append(I(950, 560, 'GENERAL RELATIVITY', 32, GOLD, a2)); its.append(I(950, 605, 'gravity and spacetime', 24, WHITE, a2, 'Medium'))
    return its
def k_qm(cv, t, T, u, P):
    r = np.random.default_rng(4); its = []
    cv.blob(640, 360, 20, (255, 200, 140), 0.8); cv.dot(640, 360, 6, (255, 230, 180), 1, 1)
    for k in range(260):
        rr = (0.25 + 0.75 * r.random()) * 270; th = r.random() * 6.283 + t * 0.45 * (1.6 - rr / 300)
        flick = 0.4 + 0.6 * abs(math.sin(t * 3 + k))
        cv.dot(640 + rr * math.cos(th), 360 + rr * math.sin(th) * 0.85, 2, (120, 200, 255), flick * 0.6, 0.7)
    its.append(I(640, 110, 'QUANTUM FIELD THEORY', 44, WHITE, fin(u, 0, 0.2)))
    its.append(I(640, 640, 'GOVERNS THE VERY SMALL', 30, GOLD, fin(u, 0.3, 0.5)))
    return its
def wavy(cv, p0, p1, amp, freq, t, c, w=2, a=1.0, coil=False):
    n = 120; s = np.linspace(0, 1, n)
    x = lerp(p0[0], p1[0], s); y = lerp(p0[1], p1[1], s)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) + 1e-6; nx, ny = -dy / L, dx / L
    off = amp * np.sin(freq * s * 6.283 - t * 8) * np.sin(np.pi * s)
    if coil:
        x = x + amp * np.cos(freq * s * 6.283 - t * 8) * dx / L * 0.8
    cv.line(np.stack([x + nx * off, y + ny * off], 1), c, w, a)
def k_forces(cv, t, T, u, P):
    its = []
    items = [('PHOTONS', 'LIGHT · ELECTROMAGNETISM', GOLD, 0.0, False), ('GLUONS', 'THE STRONG FORCE', RED, 0.2, True), ('W AND Z BOSONS', 'THE WEAK FORCE', VIOLET, 0.4, False)]
    sel = P.get('show', [0, 1, 2])
    for j, (nm, sub, c, st, coil) in enumerate(items):
        if j not in sel: continue
        a = fin(u, st + 0.05, st + 0.3)
        y = 200 + j * 150
        cv.dot(260, y, 14, WHITE, a, 0.8); cv.dot(1020, y, 14, WHITE, a, 0.8)
        wavy(cv, (270, y), (1010, y), 22, 9, t, c, 3, a, coil)
        its.append(I(640, y - 50, nm, 28, c, a)); its.append(I(640, y + 54, sub, 20, WHITE, a * 0.85, 'Medium'))
    its.insert(0, I(640, 80, P.get('title', 'FORCES ARE CARRIED BY PARTICLES'), 38, WHITE, fin(u, 0, 0.15)))
    return its
def k_gr(cv, t, T, u, P):
    its = []; depth = lerp(10, 110, sm(A(u, 0.0, 0.5)))
    f = grid_well(cv, 640, 330, depth, t, a=0.8)
    # orbiting ball
    ang = t * 0.9; X = 260 * math.cos(ang); Z = 260 * math.sin(ang) * 1.0
    x, y = f(X, Z); cv.dot(x, y - 6, 8, GOLD, 1, 1)
    cv.dot(*f(0, 0), 12, (255, 220, 130), 0.9, 1)
    its.append(I(640, 90, P.get('title', 'GRAVITY IS THE SHAPE OF SPACETIME'), 40, WHITE, fin(u, 0.05, 0.25)))
    if P.get('sub'): its.append(I(640, 650, P['sub'], 28, GOLD, fin(u, 0.35, 0.6)))
    return its
def k_waves(cv, t, T, u, P):
    its = []
    # two black holes spiral, ripple rings
    ph = u * 14 + t * 0.5; rr = max(18, 110 * (1 - u) ** 0.6)
    for sgn in (1, -1):
        x = 640 + sgn * rr * math.cos(ph); y = 360 + sgn * rr * math.sin(ph) * 0.6
        cv.dot(x, y, 16, (30, 30, 40), 1, 0); cv.ring(x, y, 17, GOLD, 2, 0.9)
    for k in range(7):
        pp = (t * 0.45 + k / 7) % 1
        cv.ring(640, 360, 40 + pp * 520, CYAN, 2, (1 - pp) * 0.5 * min(1, u * 3 + 0.3))
    its.append(I(640, 100, 'RIPPLES IN SPACETIME', 42, WHITE, fin(u, 0.05, 0.25)))
    its.append(I(640, 650, 'TWO COLLIDING BLACK HOLES · 2015', 28, GOLD, fin(u, 0.3, 0.5)))
    return its
def k_ratio(cv, t, T, u, P):
    its = []
    a1 = fin(u, 0.05, 0.3); a2 = fin(u, 0.35, 0.65)
    cv.poly([(380, 520), (520, 520), (520, 520 - 330 * a1), (380, 520 - 330 * a1)], GOLD, 0.8)
    its += [I(450, 560, 'ELECTRIC FORCE', 24, GOLD, a1), I(450, 150, '1', 40, GOLD, a1)]
    cv.poly([(760, 520), (900, 520), (900, 519 - 1.5 * a2), (760, 519 - 1.5 * a2)], CYAN, 1.0)
    cv.blob(830, 516, 12, CYAN, 0.9 * a2)
    its += [I(830, 560, 'GRAVITY', 24, CYAN, a2), I(830, 450, '≈ 10^-36', 40, CYAN, a2)]
    its.append(I(640, 640, 'BETWEEN TWO PROTONS · A TRILLION TRILLION TRILLION TIMES WEAKER', 24, WHITE, fin(u, 0.6, 0.85), 'Medium'))
    return its
def k_sing(cv, t, T, u, P):
    its = []
    bh = np.zeros((H, W, 3), np.float32)
    img = (BG * 0.8).copy()
    img = lens(img, 340, 360, 110 + 6 * math.sin(t))
    # big bang: expanding point
    pp = (t * 0.25) % 1
    cv.blob(940, 360, 10 + 90 * pp ** 0.6, (255, 220, 160), 1.0 * (1 - pp * 0.6)); cv.dot(940, 360, 5, WHITE, 1, 1)
    cv.im = np.clip(cv.im + img * 0.9, 0, 1)
    its += [I(340, 560, 'CENTER OF A BLACK HOLE', 28, WHITE, fin(u, 0.1, 0.3)), I(340, 600, 'INFINITE DENSITY IN THE EQUATIONS', 20, RED, fin(u, 0.2, 0.4), 'Medium'),
            I(940, 560, 'THE FIRST INSTANT OF THE BIG BANG', 28, WHITE, fin(u, 0.4, 0.6))]
    return its
def k_exchange(cv, t, T, u, P):
    its = []
    cv.dot(300, 360, 34, (120, 170, 255), 1, 0.8); cv.dot(980, 360, 34, (120, 170, 255), 1, 0.8)
    a = fin(u, 0.2, 0.5)
    wavy(cv, (336, 360), (944, 360), 26, 8, t, VIOLET, 3, a)
    for k in range(3):
        ph = (t * 0.4 + k / 3) % 1; cv.dot(lerp(336, 944, ph), 360, 7, WHITE, a, 1)
    its += [I(640, 270, 'GRAVITON · HYPOTHETICAL', 30, VIOLET, a), I(640, 110, P.get('title', 'TREAT GRAVITY LIKE THE OTHER FORCES'), 40, WHITE, fin(u, 0, 0.15)),
            I(640, 600, P.get('sub', 'A PARTICLE THAT CARRIES GRAVITY'), 28, GOLD, fin(u, 0.5, 0.75))]
    return its
def k_blowup(cv, t, T, u, P):
    its = []
    n = 300; x = np.linspace(0.02, 0.985, n); x = x[x <= 0.02 + 0.965 * sm(A(u, 0.1, 0.85))]
    if len(x) > 2:
        y = 1 / (1.02 - x) * 0.06
        pts = np.stack([180 + x * 920, 600 - np.clip(y * 440, 0, 480)], 1)
        cv.line(pts, RED, 4, 1)
        cv.dot(pts[-1][0], pts[-1][1], 8, WHITE, 1, 1)
    cv.line([(180, 600), (1100, 600)], GREY, 1, 0.6, 0); cv.line([(180, 600), (180, 110)], GREY, 1, 0.6, 0)
    its += [I(640, 70, P.get('title', 'PUSH THE CALCULATION FURTHER...'), 36, WHITE, fin(u, 0, 0.15)), I(1060, 150, '∞', 90, RED, fin(u, 0.7, 0.9)),
            I(640, 660, 'HIGHER PRECISION · HIGHER ENERGY', 24, GREY, fin(u, 0.1, 0.3), 'Medium')]
    return its
def k_renorm(cv, t, T, u, P):
    its = []; n = 200
    x = np.linspace(0, 1, n); g = sm(A(u, 0.1, 0.7))
    m = int(n * g) + 2
    # left: other forces converge
    yl = 1 - np.exp(-x * 4)
    cv.line(np.stack([140 + x[:m] * 420, 560 - yl[:m] * 300], 1), GREEN, 4, 1)
    its += [I(350, 140, 'OTHER FORCES', 30, GREEN, fin(u, 0.05, 0.2)), I(350, 600, 'INFINITIES ABSORBED INTO A FEW MEASURED NUMBERS', 20, WHITE, fin(u, 0.4, 0.6), 'Medium')]
    # right: gravity diverges
    xr = x[:m] * 0.97; yr = np.clip(0.06 / (1.02 - xr) * 5.5, 0, 6) * 55
    cv.line(np.stack([720 + xr * 420, 560 - np.clip(yr, 0, 440)], 1), RED, 4, 1)
    its += [I(930, 140, 'GRAVITY', 30, RED, fin(u, 0.1, 0.25)), I(930, 600, 'THE INFINITIES KEEP MULTIPLYING', 20, WHITE, fin(u, 0.5, 0.7), 'Medium')]
    cv.line([(640, 130), (640, 640)], GREY, 1, 0.4, 0)
    if P.get('end'): its.append(I(640, 380, 'NO PREDICTIONS', 44, RED, fin(u, 0.8, 0.95)))
    return its
def k_vertex(cv, t, T, u, P):
    its = []; a = fin(u, 0.1, 0.4)
    for sgn in (-1, 1):
        for yy in (-1, 1):
            cv.line([(640 + sgn * 330, 360 + yy * 220), (640, 360)], CYAN if sgn < 0 else GOLD, 3, a)
    cv.blob(640, 360, 18 + 8 * math.sin(t * 4), (255, 255, 255), a); cv.dot(640, 360, 9, WHITE, a, 1)
    its += [I(640, 100, 'POINT PARTICLES · ONE POINT OF INTERACTION', 36, WHITE, fin(u, 0.0, 0.2)), I(640, 560, 'THAT IS WHERE THE INFINITIES ARISE', 30, RED, fin(u, 0.55, 0.8))]
    return its
def k_well(cv, t, T, u, P):
    its = []; g = sm(A(u, 0.1, 0.9))
    r = lerp(240, 18, g)
    grid_well(cv, 640, 330, lerp(20, 190, g), t, a=0.7, sig=lerp(160, 60, g))
    cv.ring(640, 330, r, GOLD, 3, 0.9); cv.blob(640, 330, max(r * 0.5, 8), (255, 220, 140), 0.8)
    its += [I(640, 80, 'PACK ENERGY INTO A SMALLER REGION', 36, WHITE, fin(u, 0, 0.15)), I(640, 650, 'AND GRAVITY ITSELF GROWS STRONGER', 30, GOLD, fin(u, 0.55, 0.8))]
    return its
def k_others(cv, t, T, u, P):
    its = []
    cv.ring(640, 360, 90, WHITE, 2, 0.6 * fin(u, 0, 0.2))
    its.append(I(640, 360, 'QUANTUM\nGRAVITY', 26, WHITE, fin(u, 0, 0.2)))
    nodes = [(250, 220, 'LOOP QUANTUM GRAVITY', CYAN), (1030, 220, 'ASYMPTOTIC SAFETY', GREEN), (640, 590, 'STRING THEORY', GOLD)]
    for i, (x, y, n_, c) in enumerate(nodes):
        a = fin(u, 0.2 + i * 0.2, 0.4 + i * 0.2)
        cv.line([(640, 360), (x, y)], c, 2, a * 0.6, 0.6); cv.blob(x, y, 28, c, 0.6 * a); cv.dot(x, y, 12, c, a, 1)
        its.append(I(x, y + 46, n_, 26, c, a))
    its.append(I(640, 660, 'NONE COMPLETED AND CONFIRMED', 24, WHITE, fin(u, 0.8, 0.95), 'Medium'))
    return its
def k_timeline(cv, t, T, u, P):
    its = []; BGS[P.get('bg', 'none')](cv, t, u)
    its.append(I(640, 230, P['year'], 120, GOLD, fin(u, 0.0, 0.2)))
    for i, ln in enumerate(P['lines']):
        its.append(I(640, 360 + i * 56, ln, P.get('s', 36), (WHITE if i == 0 else CYAN) if not P.get('cols') else P['cols'][i], fin(u, 0.2 + i * 0.15, 0.4 + i * 0.15)))
    return its
def k_amp(cv, t, T, u, P):
    its = []; n = 400; x = np.linspace(0.02, 1, n)
    y = np.abs(np.sin(x * 22) / (x * 22)) * 1.1 + 0.4 * np.exp(-((x - 0.5) / 0.1) ** 2)
    m = int(n * sm(A(u, 0.05, 0.6))) + 2
    cv.line(np.stack([140 + x[:m] * 1000, 560 - y[:m] * 330], 1), CYAN, 3, 1)
    cv.line([(140, 560), (1140, 560)], GREY, 1, 0.5, 0)
    its += [I(640, 100, 'NINETEEN SIXTY-EIGHT · A FORMULA FOR THE STRONG FORCE', 32, WHITE, fin(u, 0, 0.2)), I(640, 640, 'IT WORKED REMARKABLY WELL. NOBODY KNEW WHY.', 26, GOLD, fin(u, 0.55, 0.8))]
    return its
def k_morph(cv, t, T, u, P):
    its = []; g = sm(A(u, 0.15, 0.7))
    for i, (y, m_, c) in enumerate([(220, 2, CYAN), (360, 3, GOLD), (500, 5, VIOLET)]):
        string_open(cv, 160, 1120, y, m_, t + i, 34 * g, c, 3, a=g)
    its += [I(640, 100, 'NOT POINTS', 44, WHITE, fin(u, 0.3, 0.5)), I(640, 640, 'TINY, VIBRATING STRINGS', 40, GOLD, fin(u, 0.6, 0.85))]
    return its
def k_quad(cv, t, T, u, P):
    its = []; ph = math.cos(t * 2.4)
    rx = 120 * (1 + 0.45 * ph); ry = 120 * (1 - 0.45 * ph)
    th = np.linspace(0, 6.283, 120)
    cv.line(np.stack([640 + rx * np.cos(th), 340 + ry * np.sin(th)], 1), VIOLET, 3, 1)
    for k in range(6):
        a_ = k / 6 * 6.283 + t * 0.3; cv.dot(640 + (rx + 40) * math.cos(a_), 340 + (ry + 40) * math.sin(a_), 4, WHITE, 0.4, 0.5)
    its += [I(640, 110, P.get('title', 'MASSLESS · SPIN TWO'), 44, WHITE, fin(u, 0, 0.2)), I(640, 580, P.get('sub', 'THE PROPERTIES EXPECTED OF THE GRAVITON'), 28, GOLD, fin(u, 0.4, 0.65))]
    return its
def k_vib(cv, t, T, u, P):
    its = []; modes = P.get('modes', [1, 2, 3, 4])
    n = len(modes); labs = P.get('labels', [''] * n)
    for i, m_ in enumerate(modes):
        y = 190 + i * (430 / max(n, 1)); a = fin(u, 0.05 + i * 0.12, 0.25 + i * 0.12)
        c = [CYAN, GOLD, VIOLET, GREEN, RED][i % 5]
        string_open(cv, 220, 1060, y, m_, t, 28, c, 3, a=a)
        if labs[i]: its.append(I(1140, y, labs[i], 22, c, a, an='lm' if False else 'mm'))
    its.insert(0, I(640, 80, P.get('title', 'DIFFERENT VIBRATIONS · DIFFERENT NOTES'), 38, WHITE, fin(u, 0, 0.15)))
    if P.get('sub'): its.append(I(640, 660, P['sub'], 28, GOLD, fin(u, 0.6, 0.85)))
    return its
def k_two(cv, t, T, u, P):
    its = []
    for i, (y, m_, c, lab) in enumerate([(260, 2, CYAN, P.get('a', 'ELECTRON')), (470, 5, GOLD, P.get('b', 'QUARK'))]):
        a = fin(u, 0.1 + i * 0.2, 0.3 + i * 0.2)
        string_open(cv, 200, 1080, y, m_, t, 32, c, 3, a=a); its.append(I(640, y - 70, lab, 32, c, a))
    its.append(I(640, 100, P.get('title', 'SAME STRING · DIFFERENT NOTES'), 40, WHITE, fin(u, 0.0, 0.15)))
    its.append(I(640, 650, P.get('sub', ''), 28, GOLD, fin(u, 0.7, 0.9)))
    return its
def k_dotstring(cv, t, T, u, P):
    its = []; g = sm(A(u, 0.15, 0.55))
    # point expands into filament then closes: show both loop and open string side by side
    r = lerp(3, 110, g)
    cv.blob(640, 360, 26 * (1 - g) + 3, WHITE, 0.8 * (1 - g))
    string_loop(cv, 400, 360, r, 3, t, 0.15, CYAN, 3, a=g); string_open(cv, 760, 760 + 2 * r, 360, 2, t, 24 * g, GOLD, 3, a=g)
    its += [I(640, 110, P.get('title', 'A POINT BECOMES A STRING'), 44, WHITE, fin(u, 0, 0.2)), I(400, 560, 'CLOSED STRING · A LOOP', 26, CYAN, fin(u, 0.55, 0.75)), I(880, 560, 'OPEN STRING · TWO ENDS', 26, GOLD, fin(u, 0.65, 0.85))]
    return its
def k_ladder_string(cv, t, T, u, P):
    its = []
    # proton vs string size comparison
    cv.ring(640, 360, 200, (255, 130, 120), 3, 0.9); its.append(I(640, 360, 'PROTON', 34, (255, 150, 140), 0.9))
    g = fin(u, 0.4, 0.7)
    cv.dot(640, 440, 2, GOLD, g, 1); cv.blob(640, 440, 8, GOLD, g)
    cv.line([(660, 440), (760, 520)], GOLD, 1, g * 0.6, 0)
    its += [I(840, 540, 'A STRING · NEAR THE PLANCK LENGTH', 24, GOLD, g), I(640, 120, 'ABOUT A HUNDRED BILLION BILLION TIMES SMALLER', 34, WHITE, fin(u, 0.1, 0.3)),
            I(640, 650, 'IT WOULD LOOK LIKE A POINT TO ANY MACHINE WE HAVE BUILT', 26, WHITE, fin(u, 0.7, 0.9), 'Medium')]
    return its
def k_guitar(cv, t, T, u, P):
    its = []; a1 = fin(u, 0.05, 0.25); a2 = fin(u, 0.4, 0.6)
    string_open(cv, 140, 1140, 220, 2, t, 30, CYAN, 3, a=a1)
    for k in range(40):
        x = 140 + k * 25; cv.dot(x, 220 + 30 * math.sin(2 * math.pi * (x - 140) / 1000) * math.cos(1.3 * t), 4, (255, 170, 120), a1 * 0.9, 0.5)
    its.append(I(640, 150, 'A GUITAR STRING · MADE OF MATTER', 28, (255, 190, 150), a1))
    string_open(cv, 140, 1140, 480, 2, t, 30, GOLD, 4, a=a2)
    its.append(I(640, 410, 'A FUNDAMENTAL STRING · NOT MADE OF ANYTHING MORE BASIC', 28, GOLD, a2))
    its.append(I(640, 640, 'IT IS THE BASIC THING', 34, WHITE, fin(u, 0.7, 0.9)))
    return its
def k_tension(cv, t, T, u, P):
    its = []
    string_open(cv, 160, 1120, 360, 1, t, 22, GOLD, 5, a=1, speed=3)
    cv.blob(640, 360, 120, (255, 200, 100), 0.35)
    its += [I(640, 130, 'ITS VIBRATION IS A PATTERN IN HOW IT MOVES THROUGH SPACETIME', 28, WHITE, fin(u, 0.05, 0.25)), I(640, 600, 'TENSION · ALMOST UNIMAGINABLY HIGH', 36, GOLD, fin(u, 0.5, 0.75))]
    return its
def k_spectrum(cv, t, T, u, P):
    its = []; heavy = P.get('heavy', False)
    lv = [0, 1, 2, 3, 4, 5]
    for i, l in enumerate(lv):
        y = 560 - i * (70 if not heavy else 80)
        a = fin(u, 0.05 + i * 0.1, 0.2 + i * 0.1)
        c = GREEN if i == 0 else (GOLD if heavy else GREY)
        string_open(cv, 180, 560, y, max(i, 1), t, 12 if i else 4, c, 2, a=a)
        its.append(I(600, y, ['LIGHT OR MASSLESS · THE PARTICLES WE KNOW', 'NEAR THE PLANCK MASS', 'HEAVIER', 'HEAVIER', 'HEAVIER', 'HEAVIER'][i] if i < 2 else '', 20, c, a, an='lm'))
    its.append(I(640, 80, P.get('title', 'THE VIBRATIONAL PATTERNS'), 38, WHITE, fin(u, 0, 0.15)))
    if heavy: its.append(I(640, 650, 'FAR BEYOND ANYTHING A COLLIDER COULD CREATE', 28, RED, fin(u, 0.6, 0.85)))
    else: its.append(I(640, 650, 'THE QUIETEST NOTES ON A VAST SCALE', 28, GOLD, fin(u, 0.6, 0.85)))
    return its
def k_brane(cv, t, T, u, P):
    its = []
    cv.poly([(180, 470), (1100, 470), (1180, 560), (100, 560)], (90, 140, 230), 0.35)
    cv.line([(100, 560), (1180, 560), (1100, 470), (180, 470), (100, 560)], (140, 180, 255), 1, 0.7, 0.3)
    for k in range(5):
        x0 = 260 + k * 170; y0 = 515; ph = t * 1.8 + k
        pts = []
        for s in np.linspace(0, 1, 50): pts.append((x0 + 90 * s + 10 * math.sin(ph), y0 - 210 * math.sin(math.pi * s) * (0.7 + 0.3 * math.sin(ph + s * 3))))
        cv.line(pts, CYAN, 3, fin(u, 0.1 + k * 0.08, 0.3 + k * 0.08)); cv.dot(x0 + 10 * math.sin(ph), y0, 6, CYAN, 1, 1); cv.dot(x0 + 90 + 10 * math.sin(ph), y0, 6, CYAN, 1, 1)
    its += [I(640, 100, 'OPEN STRINGS · ENDS ATTACHED TO BRANES', 38, WHITE, fin(u, 0, 0.2)), I(640, 640, 'THEY CAN PRODUCE FORCE CARRIERS LIKE THE PHOTON', 28, GOLD, fin(u, 0.6, 0.85))]
    return its
def k_eq(cv, t, T, u, P):
    its = []; string_loop(cv, 340, 360, 130, 2, t, 0.2, VIOLET, 3, tilt=0.8)
    its += [I(340, 580, 'CLOSED STRING', 26, VIOLET, fin(u, 0.1, 0.3)), I(820, 330, 'CURVATURE = ENERGY', 54, GOLD, fin(u, 0.35, 0.6)), I(820, 430, "EINSTEIN'S GRAVITY AT LARGE DISTANCES", 26, WHITE, fin(u, 0.55, 0.8), 'Medium'),
            I(640, 100, P.get('title', 'ANY CONSISTENT MASSLESS SPIN-TWO PARTICLE'), 36, WHITE, fin(u, 0, 0.2))]
    return its
def tube(cv, cx, y0, y1, r, t, c, a=1.0, rings=7, ax=0.35):
    for k in range(rings):
        y = lerp(y0, y1, k / (rings - 1)); th = np.linspace(0, 6.283, 60)
        cv.line(np.stack([cx + r * np.cos(th), y + r * np.sin(th) * 0.28], 1), c, 1, a * 0.7, 0.3)
    for k in range(10):
        a_ = k / 10 * 6.283; cv.line([(cx + r * math.cos(a_), y0 + r * math.sin(a_) * 0.28), (cx + r * math.cos(a_), y1 + r * math.sin(a_) * 0.28)], c, 1, a * 0.35, 0.2)
def k_worldsheet(cv, t, T, u, P):
    its = []
    g = fin(u, 0.1, 0.8)
    # pair of pants: two tubes merge to one (side view wireframe)
    n = 24
    for side, cc in ((-1, CYAN), (1, GOLD)):
        for k in range(12):
            a_ = k / 12 * 6.283
            pts = []
            for s in np.linspace(0, 1, 60):
                if s > g: break
                x = 640 + side * 170 * (1 - sm(A(s, 0.0, 0.62))) ; rr = lerp(70, 110, sm(A(s, 0.45, 0.8)))
                y = 140 + s * 420
                pts.append((x + rr * math.cos(a_) * (1 if s < 0.5 else 1) * 0.55 * (side * 0 + 1), y + rr * math.sin(a_) * 0.28))
            if len(pts) > 1: cv.line(pts, cc, 1, 0.55, 0.3)
    for s in np.linspace(0.03, 0.97, 9):
        if s > g: continue
        for side, cc in ((-1, CYAN), (1, GOLD)):
            x = 640 + side * 170 * (1 - sm(A(s, 0.0, 0.62))); rr = lerp(70, 110, sm(A(s, 0.45, 0.8))); y = 140 + s * 420
            th = np.linspace(0, 6.283, 50); cv.line(np.stack([x + rr * 0.55 * np.cos(th), y + rr * np.sin(th) * 0.28 * 0.55], 1), cc, 2, 0.8, 0.5)
    its += [I(640, 70, P.get('title', 'WHEN STRINGS INTERACT'), 38, WHITE, fin(u, 0, 0.15)), I(640, 650, 'THE HISTORY OF THE PROCESS IS A SMOOTH SURFACE · NO SHARP POINT', 26, GOLD, fin(u, 0.6, 0.85))]
    return its
def k_web(cv, t, T, u, P):
    its = []; nodes = P['nodes']; n = len(nodes)
    cv.blob(640, 390, 40, GOLD, 0.8 * fin(u, 0.4, 0.7)); cv.dot(640, 390, 14, GOLD, fin(u, 0.4, 0.7), 1)
    for i, (nm, c) in enumerate(nodes):
        a = fin(u, 0.05 + i * 0.1, 0.25 + i * 0.1); ang = i / n * 6.283 - 1.57
        g = sm(A(u, 0.45, 0.85))
        x = 640 + lerp(1.0, 0.0 if P.get('merge') else 1.0, g) * 340 * math.cos(ang); y = 390 + lerp(1.0, 0.0 if P.get('merge') else 1.0, g) * 175 * math.sin(ang)
        cv.dot(x, y, 12, c, a, 1); cv.line([(x, y), (640, 390)], c, 2, a * 0.5, 0.4)
        its.append(I(640 + 340 * math.cos(ang), 390 + 175 * math.sin(ang) + (30 if math.sin(ang) > 0.3 else -30), nm, 22, c, a))
    its.append(I(640, 90 if not P.get('top') else 60, P.get('title', ''), 36, WHITE, fin(u, 0, 0.15)))
    its.append(I(640, 470, P.get('center', ''), 28, WHITE, fin(u, 0.7, 0.9)))
    return its
def k_dims(cv, t, T, u, P):
    its = []
    a1, a2, a3 = fin(u, 0.05, 0.25), fin(u, 0.3, 0.5), fin(u, 0.55, 0.75)
    cv.line([(110, 360), (110 + 330 * a1, 360)], CYAN, 4, 1); cv.dot(110 + 330 * a1, 360, 8, CYAN, a1)
    its += [I(275, 480, '1 NUMBER', 30, CYAN, a1), I(275, 440, 'A LINE', 22, WHITE, a1, 'Medium')]
    cv.line([(520, 460), (520 + 250 * a2, 460)], GOLD, 3, a2); cv.line([(520, 460), (520, 460 - 200 * a2)], GOLD, 3, a2)
    its += [I(645, 560, '2 NUMBERS', 30, GOLD, a2), I(645, 520, 'A PLANE', 22, WHITE, a2, 'Medium')]
    cv.line([(860, 480), (860 + 250 * a3, 480)], VIOLET, 3, a3); cv.line([(860, 480), (860, 480 - 200 * a3)], VIOLET, 3, a3); cv.line([(860, 480), (860 + 110 * a3, 480 - 90 * a3)], VIOLET, 3, a3)
    its += [I(985, 580, '3 NUMBERS', 30, VIOLET, a3), I(985, 540, 'SPACE', 22, WHITE, a3, 'Medium')]
    its.append(I(640, 110, P.get('title', 'A DIMENSION IS AN INDEPENDENT DIRECTION'), 38, WHITE, fin(u, 0, 0.15)))
    return its
def k_cable(cv, t, T, u, P):
    its = []; z = sm(A(u, 0.15, 0.85)) if P.get('zoom') else 0.0
    ry = lerp(2, 120, z)
    # cable from left to right, thickness grows as we zoom
    for k in range(12):
        a_ = k / 12 * 6.283; yy = 360 + ry * math.sin(a_)
        cv.line([(60, yy), (1220, yy)], (150, 170, 210), 1, 0.3 + 0.4 * z, 0.3)
    for s in np.linspace(0, 1, 9):
        x = 80 + s * 1120; th = np.linspace(0, 6.283, 40); cv.line(np.stack([x + 0.3 * ry * np.cos(th) * 0.5, 360 + ry * np.sin(th)], 1), (170, 190, 230), 1, 0.35 * z, 0.2)
    cv.line([(60, 360), (1220, 360)], WHITE, max(1, int(3 * (1 - z))), 0.9 * (1 - z) + 0.2)
    if z > 0.6 and P.get('ant'):
        ph = t * 0.4; x = 200 + (ph % 1) * 700; cv.dot(x, 360 - ry - 8, 10, GOLD, 1, 1)
    its.append(I(640, 110, P.get('title', 'A THIN CABLE ACROSS A CANYON'), 40, WHITE, fin(u, 0.0, 0.2)))
    its.append(I(640, 640, P.get('sub', 'FROM FAR AWAY: A LINE · ONE NUMBER'), 28, GOLD, fin(u, 0.4, 0.7)))
    return its
def k_ant(cv, t, T, u, P):
    its = []
    R = 130; cx = 640
    for k in range(9):
        x = 180 + k * 115; th = np.linspace(0, 6.283, 60)
        cv.line(np.stack([x + 16 * np.cos(th), 360 + R * np.sin(th)], 1), (150, 190, 255), 1, 0.45, 0.2)
    cv.line([(150, 360 - R), (1130, 360 - R)], (150, 190, 255), 2, 0.7, 0.2); cv.line([(150, 360 + R), (1130, 360 + R)], (150, 190, 255), 2, 0.7, 0.2)
    ph = t * 0.5; mode = fin(u, 0.35, 0.5)
    x = 260 + 700 * ((ph) % 1); yy = 360 - R
    around = fin(u, 0.4, 0.55)
    ang = t * 2.2
    ay = 360 - R * math.cos(ang) * around if around > 0 else 360 - R
    ax_ = 640 + 0 * mode
    xx = 200 + 800 * (0.5 + 0.5 * math.sin(t * 0.4))
    cv.dot(xx, 360 - R * math.cos(ang * around) , 10, GOLD, 1, 1)
    its += [I(640, 100, 'FOR THE ANT THERE ARE TWO DIRECTIONS', 40, WHITE, fin(u, 0, 0.15)), I(300, 600, 'ALONG THE CABLE', 28, CYAN, fin(u, 0.2, 0.4)), I(980, 600, 'AROUND IT · A TINY CIRCLE', 28, GOLD, fin(u, 0.55, 0.75))]
    return its
def k_compact(cv, t, T, u, P):
    its = []; g = fin(u, 0.1, 0.5)
    for gx in range(-6, 7):
        for gy in range(-3, 4):
            x = 640 + gx * 90; y = 330 + gy * 80
            cv.dot(x, y, 2, WHITE, 0.5, 0.2)
            cv.ring(x, y, 11 * g, VIOLET, 1, 0.9 * g, 0.5)
    its += [I(640, 90, 'COMPACTIFICATION', 42, WHITE, fin(u, 0, 0.15)), I(640, 640, 'A HIDDEN SPACE ATTACHED TO EVERY LOCATION', 30, GOLD, fin(u, 0.5, 0.75))]
    return its
def k_cy(cv, t, T, u, P):
    its = []; draw_cy(cv, t, P.get('n', 5), 360, 640, 360, a=1.0)
    its.append(I(640, 80, P.get('title', 'A SIX-DIMENSIONAL SHAPE · CALABI-YAU'), 38, WHITE, fin(u, 0, 0.2)))
    its.append(I(640, 660, P.get('sub', 'A TWO-DIMENSIONAL SLICE · ARTIST-STYLE PROJECTION'), 22, GREY, fin(u, 0.3, 0.5), 'Medium'))
    return its
def k_trumpet(cv, t, T, u, P):
    its = []
    top = [(150, 330), (500, 330), (780, 300), (1000, 240), (1130, 150)]
    bot = [(150, 390), (500, 390), (780, 420), (1000, 480), (1130, 570)]
    cv.line(top, (210, 170, 90), 4, 1); cv.line(bot, (210, 170, 90), 4, 1)
    for i in range(4):
        ph = (t * 0.6 + i * 0.25) % 1; x = 160 + ph * 950
        h = 24 + 80 * ((x - 400) / 700 if x > 400 else 0); cv.ring(x, 360, h, GOLD, 1, (1 - ph) * 0.6)
    its += [I(640, 90, 'THE SHAPE OF A TRUMPET DECIDES WHICH NOTES IT CAN PLAY', 32, WHITE, fin(u, 0.0, 0.2)), I(640, 640, 'THE SHAPE OF THE HIDDEN DIMENSIONS WOULD DECIDE WHICH VIBRATIONS ARE ALLOWED', 24, GOLD, fin(u, 0.5, 0.8))]
    return its
def k_family(cv, t, T, u, P):
    its = []; draw_cy(cv, t, 5, 230, 360, 360, a=0.9)
    rows = ['WHICH PARTICLES EXIST', 'HOW MANY FAMILIES', 'HOW STRONG THE FORCES ACT']
    for i, r_ in enumerate(rows): its.append(I(900, 250 + i * 90, r_, 28, [CYAN, GOLD, VIOLET][i], fin(u, 0.15 + i * 0.2, 0.35 + i * 0.2)))
    its.append(I(640, 660, 'THE GEOMETRY OF THE INVISIBLE WRITES THE RULES OF THE VISIBLE', 28, WHITE, fin(u, 0.7, 0.9)))
    return its
def k_forcedev(cv, t, T, u, P):
    its = []; n = 200; x = np.linspace(0.12, 1, n); y = 1 / x ** 2 * 0.06
    cv.line(np.stack([150 + x * 950, 600 - np.clip(y, 0, 1) * 430 * 2.2], 1), CYAN, 3, 1)
    g = fin(u, 0.35, 0.7)
    if P.get('dev', True):
        yy = y * (1 + 2.5 * np.exp(-((x - 0.14) / 0.1) ** 2))
        cv.line(np.stack([150 + x[:60] * 950, 600 - np.clip(yy[:60], 0, 1) * 430 * 2.2], 1), RED, 3, g * 0.8)
        its.append(I(300, 200, 'WHAT LARGE EXTRA DIMENSIONS WOULD DO', 22, RED, g))
    cv.line([(150, 600), (1120, 600)], GREY, 1, 0.5, 0)
    its += [I(640, 90, 'IF EXTRA DIMENSIONS WERE LARGE, GRAVITY WOULD CHANGE AT SHORT DISTANCES', 28, WHITE, fin(u, 0, 0.2)), I(640, 650, 'DISTANCE', 20, GREY, 0.8, 'Medium')]
    return its
def k_lab(cv, t, T, u, P):
    its = []; n = 200; x = np.linspace(0.12, 1, n); y = 1 / x ** 2 * 0.06
    cv.line(np.stack([150 + x * 950, 600 - np.clip(y, 0, 1) * 430 * 2.2], 1), CYAN, 3, 1)
    g = fin(u, 0.2, 0.55)
    cv.poly([(150, 130), (150 + 950 * 0.45 * g, 130), (150 + 950 * 0.45 * g, 600), (150, 600)], GREEN, 0.15)
    its += [I(640, 90, 'GRAVITY MEASURED DOWN TO A FEW HUNDREDTHS OF A MILLIMETER', 30, WHITE, fin(u, 0, 0.2)), I(380, 380, 'TESTED · NO DEVIATION FROM NEWTON', 26, GREEN, g), I(640, 650, 'DISTANCE', 20, GREY, 0.8, 'Medium')]
    return its
def k_lhcring(cv, t, T, u, P):
    its = []; cv.ring(640, 360, 230, (140, 180, 255), 3, 0.8)
    for k in range(2):
        a_ = t * (2.5 if k else -2.5); cv.dot(640 + 230 * math.cos(a_), 360 + 230 * math.sin(a_), 6, [GOLD, CYAN][k], 1, 1)
    if int(t * 3) % 3 == 0: cv.blob(640 + 230, 360, 20, WHITE, 0.8)
    its += [I(640, 360, 'LARGE HADRON COLLIDER', 30, WHITE, fin(u, 0.1, 0.3)), I(640, 90, 'SEARCHES FOR EXTRA DIMENSIONS', 38, WHITE, fin(u, 0, 0.2)), I(640, 640, 'NO SIGNS FOUND', 36, RED, fin(u, 0.5, 0.75))]
    return its
def k_search(cv, t, T, u, P):
    """left: tested range, right: untouched; for 'ruleout'"""
    its = []; a1 = fin(u, 0.05, 0.3); a2 = fin(u, 0.35, 0.6); a3 = fin(u, 0.65, 0.9)
    cv.poly([(120, 300), (560, 300), (560, 460), (120, 460)], GREEN, 0.25 * a1); its.append(I(340, 380, 'SOME SCENARIOS RULED OUT', 26, GREEN, a1))
    cv.poly([(700, 300), (1160, 300), (1160, 460), (700, 460)], GOLD, 0.2 * a2); its.append(I(930, 380, 'TINY DIMENSIONS NEAR THE STRING SCALE', 24, GOLD, a2)); its.append(I(930, 420, 'FAR BEYOND REACH', 22, WHITE, a2, 'Medium'))
    its.append(I(640, 150, 'WHAT THE RESULTS SAY', 40, WHITE, fin(u, 0, 0.2)))
    its.append(I(640, 600, 'A REQUIREMENT OF THE MATHEMATICS · NOT A DISCOVERY OF NATURE', 30, RED if False else WHITE, a3))
    return its
def k_sparticles(cv, t, T, u, P):
    its = []; names = ['ELECTRON', 'QUARK', 'PHOTON']; pn = ['SELECTRON', 'SQUARK', 'PHOTINO']
    for i, (a_, b_) in enumerate(zip(names, pn)):
        y = 220 + i * 120; a = fin(u, 0.05 + i * 0.1, 0.25 + i * 0.1)
        its.append(I(300, y, a_, 28, CYAN, a)); cv.dot(430, y, 10, CYAN, a, 1); cv.line([(445, y), (700, y)], GREY, 1, a * 0.6, 0)
        g = fin(u, 0.4 + i * 0.1, 0.6 + i * 0.1)
        its.append(I(860, y, b_ + '  ?', 28, GOLD, g)); cv.dot(780, y, 10, GOLD, g * (0.4 + 0.4 * math.sin(t * 3 + i)), 1)
    its += [I(640, 90, 'SUPERSYMMETRY · EVERY KNOWN PARTICLE GETS A HEAVIER PARTNER', 30, WHITE, fin(u, 0, 0.2)), I(640, 620, 'NO SUCH PARTNERS FOUND SO FAR', 36, RED, fin(u, 0.7, 0.9))]
    return its
def k_sky(cv, t, T, u, P):
    its = []; r = np.random.default_rng(8)
    xs = r.random(90) * 1100 + 90; ys = r.random(90) * 440 + 130
    for x, y in zip(xs, ys): cv.dot(x, y, 2, WHITE, 0.6, 0.4)
    scan = A(u, 0.1, 0.8); sx = 90 + 1100 * scan
    cv.line([(sx, 120), (sx, 600)], CYAN, 2, 0.6, 0.6)
    if P.get('cmb'):
        for k in range(40): cv.blob(r.random() * 1100 + 90, r.random() * 440 + 130, 30 + r.random() * 30, (255, 150, 90) if k % 2 else (90, 130, 255), 0.18)
        txt = 'FAINT PATTERNS IN THE COSMIC MICROWAVE BACKGROUND · AND GRAVITATIONAL WAVES'
        end = 'NO EVIDENCE FOR STRING THEORY'
    else:
        txt = 'SEARCHING THE SKY FOR COSMIC STRINGS'; end = 'NONE FOUND'
    its += [I(640, 80, txt, 28, WHITE, fin(u, 0, 0.2)), I(640, 650, end, 38, RED, fin(u, 0.75, 0.95))]
    return its
def k_shapes(cv, t, T, u, P):
    its = []
    for i in range(8):
        cx = 220 + (i % 4) * 280; cy = 230 + (i // 4) * 260; a = fin(u, 0.05 + i * 0.07, 0.2 + i * 0.07)
        draw_cy(cv, t + i, [3, 4, 5, 6][i % 4], 105, cx, cy, a=0.9 * a, c=[(120, 200, 255), (255, 200, 120), (190, 150, 255), (140, 235, 170)][i % 4])
    its.append(I(640, 60, 'DIFFERENT SHAPES · DIFFERENT WAYS OF THREADING FIELDS THROUGH THEM', 26, WHITE, fin(u, 0, 0.2)))
    its.append(I(640, 660, 'DIFFERENT PARTICLES · FORCES · CONSTANTS OF NATURE', 28, GOLD, fin(u, 0.7, 0.9)))
    return its
def land_height(x, y, t=0):
    return (np.sin(x * 3.1) * np.cos(y * 2.7) + 0.6 * np.sin(x * 7.3 + y * 5.1) + 0.4 * np.cos(y * 9.1 - x * 4.2)) * 0.5
def k_land(cv, t, T, u, P):
    its = []; n = 46
    xs = np.linspace(-1.4, 1.4, n)
    rot = 0.25 * math.sin(t * 0.15)
    def P3(x, y):
        h = land_height(x, y) * 0.45
        return np.array([x, h + 0.25, y])
    for j in range(n):
        pts = np.array([P3(x, xs[j]) for x in xs]); pp, z = project(pts, 0.85 + rot, 0.0, f=680, d=3.6, cx=640, cy=330)
        cv.line(pp, (90, 150, 255), 1, 0.65, 0.3)
    for j in range(0, n, 2):
        pts = np.array([P3(xs[j], y) for y in xs]); pp, z = project(pts, 0.85 + rot, 0.0, f=680, d=3.6, cx=640, cy=330)
        cv.line(pp, (90, 150, 255), 1, 0.4, 0.2)
    r = np.random.default_rng(9)
    lit = int(fin(u, 0.2, 0.9) * 50)
    for k in range(lit):
        x = r.uniform(-1.3, 1.3); y = r.uniform(-1.3, 1.3); p, z = project(P3(x, y)[None], 0.85 + rot, 0.0, f=680, d=3.6, cx=640, cy=330)
        cv.dot(p[0][0], p[0][1], 3, GOLD, 0.9, 1)
    its += [I(640, 70, P.get('title', 'THE STRING LANDSCAPE'), 44, WHITE, fin(u, 0, 0.15))]
    if P.get('num'): its += [I(640, 600, '≈ 10^500', 80, GOLD, fin(u, 0.4, 0.65)), I(640, 665, 'A ROUGH ESTIMATE · NOT A PRECISE COUNT', 24, WHITE, fin(u, 0.6, 0.85), 'Medium')]
    if P.get('sub'): its.append(I(640, 640, P['sub'], 30, GOLD, fin(u, 0.4, 0.7)))
    return its
def k_cols2(cv, t, T, u, P):
    its = []; a1 = fin(u, 0.05, 0.3); a2 = fin(u, 0.4, 0.65)
    cv.line([(640, 130), (640, 600)], GREY, 1, 0.5, 0)
    its += [I(340, 170, 'CRITICS', 38, RED, a1), I(340, 300, 'HARD TO FALSIFY', 30, WHITE, a1), I(340, 360, 'NO SHARP PREDICTIONS', 30, WHITE, a1), I(340, 420, 'DRIFTING AWAY FROM SCIENCE?', 26, GREY, a1, 'Medium'),
            I(940, 170, 'SUPPORTERS', 38, GREEN, a2), I(940, 300, 'THE LANDSCAPE IS A RESULT', 28, WHITE, a2), I(940, 360, 'THE SWAMPLAND PROGRAM', 28, WHITE, a2), I(940, 420, 'RULES THAT COULD BE TESTED', 26, GREY, a2, 'Medium')]
    its.append(I(640, 640, 'SERIOUS PHYSICISTS STAND ON BOTH SIDES', 30, GOLD, fin(u, 0.75, 0.95)))
    return its
def k_checks(cv, t, T, u, P):
    its = []; which = P.get('which', [0, 1, 2])
    rows = [('1', 'IS THE MATHEMATICS INTERNALLY CONSISTENT?', 'LARGELY YES · THE FULL THEORY IS UNFINISHED', GREEN, 'YES'), ('2', 'IS THE FRAMEWORK USEFUL?', 'YES · REAL INSIGHT INTO GRAVITY AND MATHEMATICS', GREEN, 'YES'), ('3', 'DOES NATURE ACTUALLY BEHAVE THIS WAY?', 'COMPLETELY OPEN', GOLD, '?')]
    for j, i in enumerate(which):
        n_, q, ans, c, ck = rows[i]; y = 230 + i * 150 if len(which) > 1 else 330
        a = fin(u, 0.05 + j * 0.2, 0.25 + j * 0.2); b = fin(u, 0.3 + j * 0.2, 0.5 + j * 0.2)
        its += [I(180, y, n_, 70, c, a), I(250, y - 22, q, 28, WHITE, a, an='lm'), I(250, y + 28, ans, 24, c, b, 'Medium', 'lm'), I(1150, y, ck, 70, c, b)]
    return its
def k_balance(cv, t, T, u, P):
    its = []; a = fin(u, 0.1, 0.4); tilt = 0.18 * sm(A(u, 0.4, 0.8))
    cv.line([(340, 400 - 50 * tilt / 0.18), (940, 400 + 50 * tilt / 0.18)], WHITE, 3, 1)
    cv.dot(640, 400, 10, WHITE, 1, 1)
    its += [I(340, 330 - 50 * tilt / 0.18, 'MATHEMATICAL BEAUTY', 30, GOLD, a), I(940, 330 + 50 * tilt / 0.18, 'EMPIRICAL EVIDENCE', 30, CYAN, a),
            I(640, 150, 'NOT INTERCHANGEABLE', 44, WHITE, fin(u, 0.0, 0.2)), I(640, 600, 'A REASON TO EXPLORE · NEVER BY ITSELF EVIDENCE', 28, WHITE, fin(u, 0.55, 0.8))]
    return its
def horizon(cv, cx, cy, R, t, cells=0, flick=False, a=1.0):
    th = np.linspace(0, 6.283, 120)
    cv.ring(cx, cy, R, (255, 190, 110), 3, a)
    cv.blob(cx, cy, R * 0.9, (20, 20, 30), 0.0)
    cv.poly([(cx + R * math.cos(x), cy + R * math.sin(x)) for x in th], (5, 5, 10), 0.95)
    r = np.random.default_rng(12)
    for k in range(cells):
        ph = r.random() * 6.283; ps = r.random() * 3.1416; x = cx + R * math.sin(ps) * math.cos(ph + t * 0.2); y = cy - R * math.cos(ps)
        on = (math.sin(t * 4 + k) > 0) if flick else True
        cv.dot(x, y, 3, GOLD if on else (80, 80, 100), a * 0.9, 0.6)
def k_bh(cv, t, T, u, P):
    its = []
    img = lens((BG * 0.8).copy(), 640, 360, 130 + 4 * math.sin(t)); cv.im = np.clip(cv.im + img, 0, 1)
    its += [I(640, 100, P.get('title', 'BLACK HOLES'), 46, WHITE, fin(u, 0, 0.2)), I(640, 640, P.get('sub', ''), 30, GOLD, fin(u, 0.4, 0.7))]
    return its
def k_entropy(cv, t, T, u, P):
    its = []; g = fin(u, 0.1, 0.5)
    horizon(cv, 640, 360, 170, t, cells=int(260 * g))
    its += [I(640, 90, 'BLACK HOLE ENTROPY', 46, WHITE, fin(u, 0, 0.2)), I(640, 600, 'PROPORTIONAL TO THE AREA OF THE HORIZON · NOT THE VOLUME', 28, GOLD, fin(u, 0.5, 0.8)), I(1000, 360, 'S ~ A', 70, CYAN, fin(u, 0.4, 0.7))]
    return its
def k_micro(cv, t, T, u, P):
    its = []
    horizon(cv, 640, 360, 190, t, cells=360, flick=True)
    its += [I(640, 90, 'HIDDEN MICROSCOPIC ARRANGEMENTS', 40, WHITE, fin(u, 0, 0.2)), I(640, 620, 'AN ASTRONOMICAL NUMBER OF INTERNAL QUANTUM STATES', 28, GOLD, fin(u, 0.45, 0.75)), I(1040, 360, 'WHAT ARE THEY?', 34, RED, fin(u, 0.7, 0.9))]
    return its
def k_count(cv, t, T, u, P):
    its = []
    horizon(cv, 340, 360, 130, t, cells=int(150 * fin(u, 0.1, 0.4)), flick=True)
    for i in range(4): string_loop(cv, 880, 250 + i * 70, 40, 2 + i, t, 0.2, [CYAN, GOLD, VIOLET, GREEN][i], 2, a=fin(u, 0.2 + i * 0.08, 0.4 + i * 0.08))
    g = fin(u, 0.65, 0.9)
    its += [I(340, 560, 'BEKENSTEIN-HAWKING', 26, GOLD, fin(u, 0.1, 0.3)), I(880, 560, 'COUNT THE STRING STATES', 26, CYAN, fin(u, 0.3, 0.5)), I(640, 360, '=', 80, WHITE, g), I(640, 100, 'STROMINGER AND VAFA · NINETEEN NINETY-SIX', 34, WHITE, fin(u, 0, 0.2)), I(640, 650, 'AN EXACT MATCH · FOR A SPECIAL CLASS OF IDEALIZED BLACK HOLES', 26, GOLD, g)]
    return its
def k_region(cv, t, T, u, P):
    its = []; g = fin(u, 0.15, 0.6)
    s = 150 + 70 * math.sin(t * 0.6)
    cv.line([(640 - s, 360 - s), (640 + s, 360 - s), (640 + s, 360 + s), (640 - s, 360 + s), (640 - s, 360 - s)], CYAN, 3, 1)
    for k in range(int(80 * g)):
        r = np.random.default_rng(k);
        x = 640 + (r.random() * 2 - 1) * s * 0.9; y = 360 + (r.random() * 2 - 1) * s * 0.9; cv.dot(x, y, 2, WHITE, 0.4, 0.2)
    for k in range(int(48 * g)):
        a_ = k / 48 * 4; side = int(a_) % 4; f = a_ - int(a_)
        pts = [(640 - s + 2 * s * f, 360 - s), (640 + s, 360 - s + 2 * s * f), (640 + s - 2 * s * f, 360 + s), (640 - s, 360 + s - 2 * s * f)][side]
        cv.dot(pts[0], pts[1], 4, GOLD, 1, 1)
    its += [I(640, 90, 'THE MAXIMUM INFORMATION A REGION CAN HOLD', 36, WHITE, fin(u, 0, 0.2)), I(640, 620, 'SCALES WITH THE AREA OF ITS BOUNDARY · NOT ITS VOLUME', 28, GOLD, fin(u, 0.55, 0.8))]
    return its
def k_ads(cv, t, T, u, P):
    its = []; R = 250; cx, cy = 640, 360
    cv.ring(cx, cy, R, WHITE, 2, 0.9)
    r = np.random.default_rng(21)
    angs = np.sort(r.random(14) * 6.283)
    g = fin(u, 0.15, 0.6)
    for i in range(len(angs)):
        a, b = angs[i], angs[(i + 3) % len(angs)]
        pts = poincare_geodesic(a, b, R, cx, cy); m = max(2, int(len(pts) * g)); cv.line(pts[:m], (110, 170, 255), 1, 0.7, 0.4)
    for k, a in enumerate(angs):
        bx = cx + R * math.cos(a); by = cy + R * math.sin(a); f = 0.5 + 0.5 * math.sin(t * 2 + k)
        cv.dot(bx, by, 4 + 3 * f, GOLD, 1, 1)
    cv.blob(cx, cy, 14 + 4 * math.sin(t * 2), (140, 200, 255), 0.7)
    its += [I(640, 70, 'A UNIVERSE WITH GRAVITY · ANTI-DE SITTER SPACE', 30, CYAN, fin(u, 0.1, 0.3)), I(640, 660, 'A QUANTUM THEORY WITHOUT GRAVITY · LIVING ON THE BOUNDARY', 26, GOLD, fin(u, 0.45, 0.7))]
    return its
def k_dict(cv, t, T, u, P):
    its = []; a1 = fin(u, 0.05, 0.25); a2 = fin(u, 0.2, 0.4); a3 = fin(u, 0.5, 0.75)
    R = 140
    cv.ring(340, 330, R, WHITE, 2, a1)
    for i, ang in enumerate(np.linspace(0, 6.283, 9)[:-1]): cv.line([poincare_geodesic(ang, ang + 2.2, R, 340, 330)[k] for k in range(60)], (110, 170, 255), 1, a1 * 0.6, 0.3)
    its += [I(340, 530, 'GRAVITY', 36, CYAN, a1), I(340, 580, 'STRING THEORY IN ANTI-DE SITTER SPACE', 20, WHITE, a1, 'Medium')]
    cv.ring(940, 330, R, GOLD, 3, a2)
    for k in range(40): a_ = k / 40 * 6.283; cv.dot(940 + R * math.cos(a_), 330 + R * math.sin(a_), 3 + 2 * math.sin(t * 3 + k), GOLD, a2, 1)
    its += [I(940, 530, 'NO GRAVITY', 36, GOLD, a2), I(940, 580, 'QUANTUM FIELD THEORY · ONE FEWER DIMENSION', 20, WHITE, a2, 'Medium')]
    cv.line([(500, 330), (780, 330)], WHITE, 3, a3); its.append(I(640, 290, 'TWO DESCRIPTIONS', 26, WHITE, a3)); its.append(I(640, 370, 'OF THE SAME PHYSICS', 26, WHITE, a3))
    its.append(I(640, 80, 'THE A D S / C F T CORRESPONDENCE', 40, WHITE, fin(u, 0, 0.15)))
    return its
def k_holo(cv, t, T, u, P):
    its = []; a1 = fin(u, 0.05, 0.3); a2 = fin(u, 0.5, 0.75)
    # flat film left with 3D image
    cv.poly([(130, 420), (520, 420), (560, 500), (90, 500)], (120, 160, 255), 0.4 * a1)
    for k in range(50): cv.dot(230 + (k % 10) * 24, 440 + (k // 10) * 12, 2, CYAN, a1 * 0.7, 0.6)
    cv.blob(325, 300, 50, GOLD, 0.8 * a1); its += [I(325, 560, 'A HOLOGRAM · A 3D IMAGE ON A FLAT SURFACE', 22, CYAN, a1)]
    its.append(I(640, 100, 'USEFUL ANALOGY · RISKY ANALOGY', 40, WHITE, fin(u, 0, 0.2)))
    its += [I(940, 360, 'BUT THE INTERIOR\nIS NOT AN ILLUSION', 34, GOLD, a2), I(940, 450, 'BOTH DESCRIPTIONS ARE EQUALLY REAL', 22, WHITE, a2, 'Medium')]
    return its
def k_dsads(cv, t, T, u, P):
    its = []; a1 = fin(u, 0.05, 0.3); a2 = fin(u, 0.3, 0.55); a3 = fin(u, 0.6, 0.85)
    cv.ring(330, 340, 140, CYAN, 2, a1)
    its += [I(330, 540, 'ANTI-DE SITTER SPACE', 28, CYAN, a1), I(330, 580, 'NEGATIVELY CURVED · THE SETTING OF THE CORRESPONDENCE', 18, WHITE, a1, 'Medium')]
    g = (t * 0.2) % 1
    for k in range(6): cv.ring(950, 340, 30 + 130 * ((g + k / 6) % 1), GOLD, 1, (1 - ((g + k / 6) % 1)) * 0.6 * a2)
    its += [I(950, 540, 'OUR UNIVERSE', 28, GOLD, a2), I(950, 580, 'EXPANDING · AND THE EXPANSION IS ACCELERATING', 18, WHITE, a2, 'Medium')]
    its.append(I(640, 90, 'THE UNIVERSE WE LIVE IN IS NOT ANTI-DE SITTER SPACE', 34, WHITE, fin(u, 0, 0.2)))
    its.append(I(640, 650, 'NO PROOF THAT WE LIVE IN A HOLOGRAM', 30, RED, a3))
    return its
def k_emerge(cv, t, T, u, P):
    its = []; g = fin(u, 0.2, 0.8)
    R = 220; cx, cy = 640, 360
    cv.ring(cx, cy, R, GOLD, 3, 1)
    for k in range(60): a_ = k / 60 * 6.283; cv.dot(cx + R * math.cos(a_), cy + R * math.sin(a_), 3 + 2 * math.sin(t * 2 + k * 0.7), GOLD, 1, 1)
    r = np.random.default_rng(31); angs = np.sort(r.random(16) * 6.283)
    for i in range(16):
        pts = poincare_geodesic(angs[i], angs[(i + 5) % 16], R, cx, cy); m = max(2, int(len(pts) * g)); cv.line(pts[:m], (110, 170, 255), 1, 0.8 * g, 0.4)
    its += [I(640, 70, 'GRAVITY AND SPACETIME EMERGING FROM A QUANTUM THEORY', 32, WHITE, fin(u, 0, 0.2)), I(640, 640, 'THAT CONTAINS NEITHER', 34, GOLD, fin(u, 0.6, 0.85))]
    return its
def k_tiers(cv, t, T, u, P):
    its = []; tiers = [('ESTABLISHED RESULTS', 'THE MATHEMATICAL ONES', GREEN), ('THEORETICAL IMPLICATIONS', 'IF NATURE CHOSE STRINGS', GOLD), ('SPECULATION', 'THE HORIZON', VIOLET)]
    for i, (a_, b_, c) in enumerate(tiers):
        y = 220 + i * 140; a = fin(u, 0.1 + i * 0.22, 0.3 + i * 0.22)
        cv.poly([(220, y - 48), (1060, y - 48), (1060, y + 48), (220, y + 48)], c, 0.18 * a)
        its += [I(640, y - 10, a_, 32, c, a), I(640, y + 30, b_, 22, WHITE, a, 'Medium')]
    return its
def k_return(cv, t, T, u, P):
    return k_zoom(cv, t, T, u, {'s0': 5, 's1': 0})
def k_split(cv, t, T, u, P):
    its = []; a1 = fin(u, 0.05, 0.3); a2 = fin(u, 0.4, 0.65)
    cv.blob(330, 360, 24, WHITE, 0.9 * a1); cv.dot(330, 360, 6, WHITE, a1, 1)
    string_loop(cv, 950, 360, 90, 4, t, 0.18, CYAN, 3, a=a2)
    its += [I(330, 520, 'THE DOTS ARE REALLY DOTS', 30, WHITE, a1), I(330, 565, 'AND GRAVITY NEEDS ANOTHER SOLUTION', 22, GREY, a1, 'Medium'),
            I(950, 520, 'TINY VIBRATING STRINGS', 30, CYAN, a2), I(950, 565, 'A HUNDRED BILLION BILLION TIMES SMALLER THAN A PROTON', 18, GREY, a2, 'Medium'), I(640, 360, 'OR', 36, GOLD, fin(u, 0.3, 0.5))]
    return its
def k_windows(cv, t, T, u, P):
    its = []; names = ['A PREDICTION SHARP ENOUGH TO FAIL', 'A NEW WINDOW ONTO THE PLANCK SCALE', 'A SURPRISE NOBODY HAS IMAGINED']
    sub = ['', 'THE EARLIEST LIGHT · THE RIPPLES OF COLLIDING BLACK HOLES', '']
    for i, n_ in enumerate(names):
        y = 220 + i * 140; a = fin(u, 0.1 + i * 0.22, 0.3 + i * 0.22)
        cv.ring(190, y, 22, [GOLD, CYAN, VIOLET][i], 3, a); its.append(I(250, y, n_, 30, WHITE, a, an='lm'))
        if sub[i]: its.append(I(250, y + 40, sub[i], 20, GREY, a, 'Medium', 'lm'))
    its.append(I(640, 90, 'WHAT WOULD IT TAKE?', 44, GOLD, fin(u, 0, 0.2)))
    return its
def k_final(cv, t, T, u, P):
    its = []; a1 = fin(u, 0.0, 0.2); a2 = fin(u, 0.25, 0.5); fade = 1 - fin(u, 0.82, 1.0)
    cv.blob(330, 360, 24, WHITE, 0.9 * a1 * fade); cv.dot(330, 360, 6, WHITE, a1 * fade, 1)
    string_open(cv, 700, 1150, 360, 3, t, 34, CYAN, 3, a=a2 * fade)
    its += [I(330, 480, 'A DOT', 40, WHITE, a1 * fade), I(925, 480, 'A NOTE', 40, CYAN, a2 * fade)]
    its.append(I(640, 140, 'THE UNIVERSE HAS ALREADY DECIDED', 36, GOLD, fin(u, 0.55, 0.75) * fade))
    its.append(I(640, 620, 'WHAT WE LACK IS A WAY TO ASK', 42, WHITE, fin(u, 0.7, 0.9) * fade))
    return its
def k_matters(cv, t, T, u, P):
    its = []; lines = ['GRAVITY AND QUANTUM MECHANICS CAN COEXIST', 'IN ONE CONSISTENT MATHEMATICAL FRAMEWORK', 'SPACETIME MAY BE BUILT FROM SOMETHING DEEPER']
    BGS['string'](cv, t, u)
    for i, ln in enumerate(lines): its.append(I(640, 250 + i * 90, ln, 34, [WHITE, WHITE, GOLD][i], fin(u, 0.1 + i * 0.22, 0.3 + i * 0.22)))
    its.append(I(640, 100, 'STRING THEORY MATTERS EVEN IF IT IS NOT TRUE', 38, CYAN, fin(u, 0, 0.15)))
    return its
def k_nowhat(cv, t, T, u, P):
    its = []
    its.append(I(340, 330, 'MATHEMATICS', 44, CYAN, fin(u, 0.05, 0.25))); its.append(I(340, 400, 'WHAT COULD BE', 30, WHITE, fin(u, 0.1, 0.3)))
    its.append(I(940, 330, 'NATURE', 44, GOLD, fin(u, 0.4, 0.6))); its.append(I(940, 400, 'WHAT IS', 30, WHITE, fin(u, 0.45, 0.65)))
    string_loop(cv, 340, 540, 60, 3, t, 0.15, CYAN, 2, a=fin(u, 0.1, 0.3));
    cv.dot(940, 540, 6, GOLD, fin(u, 0.4, 0.6), 1)
    return its
KINDS = {k[2:]: v for k, v in globals().items() if k.startswith('k_')}
