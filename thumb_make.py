import os, io, json, base64, math, urllib.request, urllib.error
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

PROMPT = os.environ['PROMPT']
TAG = os.environ.get('TAG', '').strip()
LINES = [os.environ.get(k, '').strip() for k in ('L1', 'L2', 'L3')]
LINES = [l for l in LINES if l]
CORE_X = float(os.environ.get('CORE_X') or 0.75)
CORE_Y = float(os.environ.get('CORE_Y') or 0.45)
OUT = os.environ.get('OUT', 'out.jpg')
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
W, H, S = 1280, 720, 2
if not LINES:
    raise SystemExit('need at least line1')

url = ('https://api.cloudflare.com/client/v4/accounts/%s/ai/run/'
       '@cf/black-forest-labs/flux-1-schnell' % os.environ['CF_ACCOUNT_ID'])
req = urllib.request.Request(
    url, data=json.dumps({'prompt': PROMPT, 'steps': 8}).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['CF_API_TOKEN'],
             'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.load(r)
except urllib.error.HTTPError as e:
    raise SystemExit('Cloudflare error %s: %s' % (e.code, e.read()[:400]))
b64 = (data.get('result') or data).get('image')
if not b64:
    raise SystemExit('no image: ' + str(data)[:400])
src = Image.open(io.BytesIO(base64.b64decode(b64))).convert('RGB')
src.save('raw.jpg', quality=95)

w0, h0 = src.size
cw, ch = w0, round(w0 * 9 / 16)
if ch > h0:
    ch, cw = h0, round(h0 * 16 / 9)
x0, y0 = (w0 - cw) // 2, (h0 - ch) // 2
base = src.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)
base = ImageEnhance.Contrast(base).enhance(1.12)
base = ImageEnhance.Color(base).enhance(1.15)
base = base.filter(ImageFilter.UnsharpMask(radius=2.2, percent=140, threshold=2))
arr = np.asarray(base).astype(np.float32) / 255.0

lum = arr.mean(axis=2)
bright = np.clip((lum - 0.72) / 0.28, 0, 1)
glow = Image.fromarray((bright * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(38))
g = np.asarray(glow).astype(np.float32) / 255.0
gold = np.array([1.0, 0.78, 0.42], dtype=np.float32)
arr = 1 - (1 - arr) * (1 - g[..., None] * gold * 0.55)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
d = np.sqrt(((xx - W * 0.57) / (W * 0.75)) ** 2 + ((yy - H * 0.5) / (H * 0.85)) ** 2)
vig = np.clip(1 - 0.45 * np.clip(d - 0.35, 0, 1) ** 1.5, 0, 1)
arr *= vig[..., None]
lg = np.clip(1 - (xx / (W * 0.58)), 0, 1) ** 1.25 * 0.80
arr *= (1 - lg)[..., None]
rng = np.random.default_rng(7)
arr += rng.normal(0, 0.008, arr.shape).astype(np.float32)
arr = np.clip(arr, 0, 1)
canvas = Image.fromarray((arr * 255).astype(np.uint8)).convert('RGBA')

ov = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))

def font(size):
    return ImageFont.truetype(FONT, size, index=0)

def draw_line(overlay, txt, size, fill, squeeze, stroke, x, baseline):
    f = font(size)
    pad = stroke + 10
    tw = int(f.getlength(txt))
    Wc, Hc = tw + 2 * pad, int(size * 1.5)
    base_y = int(size * 1.15)
    lay = Image.new('RGBA', (Wc, Hc), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((pad, base_y), txt, font=f, fill=fill, anchor='ls',
                             stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    lay = lay.resize((max(1, int(Wc * squeeze)), Hc), Image.LANCZOS)
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 0))
    sh.putalpha(lay.split()[3].point(lambda v: int(v * 0.85)))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    px, py = x - int(pad * squeeze), baseline - base_y
    overlay.alpha_composite(sh, (px + 6, py + 16))
    overlay.alpha_composite(lay, (px, py))
    return int(tw * squeeze)

sq = 0.84
f300 = font(300)
maxw = max(f300.getlength(t) for t in LINES) * sq
size = min(int(300 * (545 * S) / maxw), 330)
tag_size = 74
tag_cap = -font(tag_size).getbbox('H', anchor='ls')[1]
n = len(LINES)
while True:
    cap = -font(size).getbbox('H', anchor='ls')[1]
    gap = int(cap * 0.26)
    block_h = (tag_cap + 60 if TAG else 0) + n * cap + (n - 1) * gap
    if block_h <= 640 * S or size <= 60:
        break
    size -= 10
top = (H * S - block_h) // 2 + 10
x_left = 58 * S
WHITE = (255, 255, 255, 255)
GOLD = (255, 197, 61, 255)
y = top
if TAG:
    y += tag_cap
    draw_line(ov, TAG, tag_size, GOLD, 0.9, 5, x_left, y)
    y += 60
w_last, y_last = 0, 0
for i, t in enumerate(LINES):
    y += cap
    last = (i == n - 1)
    w_last = draw_line(ov, t, size, GOLD if last else WHITE, sq, 12, x_left, y)
    y_last = y
    y += gap

core = (CORE_X * W * S, CORE_Y * H * S)
start = (x_left + w_last + 70, y_last - cap * 0.5)
vx, vy = core[0] - start[0], core[1] - start[1]
dist = math.hypot(vx, vy) or 1.0
ux, uy = vx / dist, vy / dist
tip = (core[0] - ux * 300, core[1] - uy * 300)
mid = ((start[0] + tip[0]) / 2, (start[1] + tip[1]) / 2)
ctrl = (mid[0] + uy * 120, mid[1] - ux * 120)
tx, ty = tip[0] - ctrl[0], tip[1] - ctrl[1]
tl = math.hypot(tx, ty) or 1.0
tx, ty = tx / tl, ty / tl
head_len, head_w = 150, 78
bp = (tip[0] - tx * head_len, tip[1] - ty * head_len)
left = (bp[0] - ty * head_w, bp[1] + tx * head_w)
right = (bp[0] + ty * head_w, bp[1] - tx * head_w)

arrow = Image.new('RGBA', ov.size, (0, 0, 0, 0))
ad = ImageDraw.Draw(arrow)
dense = []
for i in range(401):
    t = i / 400
    px = (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * ctrl[0] + t ** 2 * tip[0]
    py = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * ctrl[1] + t ** 2 * tip[1]
    dense.append((px, py))
dense = [p for p in dense if math.hypot(p[0] - tip[0], p[1] - tip[1]) > head_len * 0.85]

def stamp(draw, pts, radius, fill):
    for (px, py) in pts:
        draw.ellipse([px - radius, py - radius, px + radius, py + radius], fill=fill)

stamp(ad, dense, 32, (0, 0, 0, 255))
ad.polygon([tip, left, right], fill=(0, 0, 0, 255), outline=(0, 0, 0, 255), width=22)
stamp(ad, dense, 19, GOLD)
ad.polygon([tip, left, right], fill=GOLD)
ash = arrow.filter(ImageFilter.GaussianBlur(16))
ash.putalpha(ash.split()[3].point(lambda v: int(v * 0.7)))
ov.alpha_composite(ash, (6, 16))
ov.alpha_composite(arrow)

ov = ov.resize((W, H), Image.LANCZOS)
canvas.alpha_composite(ov)
final = canvas.convert('RGB')
q = 93
while True:
    final.save(OUT, 'JPEG', quality=q, subsampling=0, optimize=True)
    kb = os.path.getsize(OUT) / 1024
    if kb < 1900 or q <= 70:
        break
    q -= 3
print('saved', OUT, final.size, '%.0f KB' % kb)
