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
