"""Drawing kit for the Star Rail style maps (1280 x 1000 canvas).

Layers, bottom to top: far city, water, buildings (+ inner wall line),
roof detail, walkable area (one path, holes cut counter-clockwise) with
floor tiles and an inner curb line, floor detail, lanes, stairs, dots.
Anything placed inside a walkable area (monuments, medians, hatches) is
drawn in the building layers and cut out of the walkable path."""
import math, random
from pl import P, rect, rr, cham, ngon, circ, poly, line, ring, reverse, fillet

# Palettes. "hsr" is the grey game-map look; the others are the draft
# themes (white-night travel journal, transit board, polar explorer HUD).
PALETTES = {
    'hsr': dict(f='#c9c9c9', fs='#d3d3d3', fr='#c1c1c1', v='#dedede', vw='#cfcfcf', b='#d8d8d8', b2='#c6c6c6', rim='#e6e6e6',
                r='#b9b9b9', rk='#c3c3c3', rks='#b8b8b8', w='#3c3c3c', w2='#6e6e6e', curb='#474747', t='#4a4a4a',
                s='#8e8e8e', d='#9a9a9a', o='#cfcfcf', os='#e2e2e2', blur=.9, shadow=None),
    'journal': dict(f='#e4e1ec', fs='#ebe8f1', fr='#d9d5e4', v='#cfe0ee', vw='#bdd3e7', b='#fdfcff', b2='#f2f0f8', rim='#ffffff',
                r='#dcd7e8', rk='#ebe8f3', rks='#d8d3e5', w='#8a8db8', w2='#b9bbd8', curb='#999cc4', t='#9da0c8',
                s='#e3e4f3', d='#e08aa0', o='#fdfcff', os='#d3cfe2', blur=.6, shadow='#6f62a040'),
    'transit': dict(f='#e6e8ec', fs='#eceef1', fr='#dde0e6', v='#cfe3f3', vw='#bdd6ec', b='#ffffff', b2='#f2f3f6', rim='#ffffff',
                r='#e0e3e9', rk='#eceef2', rks='#dcdfe5', w='#2f333c', w2='#8a909c', curb='#3b4049', t='#40454f',
                s='#b8bdc6', d='#d63a3a', o='#ffffff', os='#c5c9d1', blur=0, shadow=None),
    'hud': dict(f='#d2dce5', fs='#dae3eb', fr='#c8d3dd', v='#b8d1e5', vw='#a7c4dc', b='#f5f9fc', b2='#e5ecf2', rim='#ffffff',
                r='#cdd9e3', rk='#dbe4ec', rks='#c9d5df', w='#45576c', w2='#8397ac', curb='#596c82', t='#5b6e83',
                s='#a8bbcc', d='#2fb4d8', o='#f5f9fc', os='#b3c4d3', blur=.5, shadow='#3a5a7a30'),
    # clean drafts: light map-app, white-night glass, dark minimal, line art
    'clean': dict(f='#e2e6eb', fs='#e8ebef', fr='#d9dee4', v='#c6ddf0', vw='#b5d1e8', b='#d8dde4', b2='#ced4dc', rim='#e4e8ed',
                r='#c8cfd8', rk='#d2d8df', rks='#c2c9d2', w='#ffffff', ws='#c3cad3', wsw=3, w2='#eef1f5', curb='#ffffff', t='#e7ebf0',
                s='#cfd5dd', d='#ef6f6c', o='#d8dde4', os='#c2c9d2', blur=.6, shadow='#4a5b7030'),
    'dusk': dict(f='#d8d3e7', fs='#dfdbeb', fr='#cec9df', v='#bccde8', vw='#aabfe0', b='#ccc7df', b2='#c1bbd7', rim='#d8d4e8',
                r='#bcb6d2', rk='#c6c0db', rks='#b7b1ce', w='#f8f6fc', ws='#bdb6d4', wsw=3, w2='#e6e2f1', curb='#f8f6fc', t='#e7e3f1',
                s='#cdc7e0', d='#e98aa0', o='#ccc7df', os='#b9b3cf', blur=.6, shadow='#5a4a8a33'),
    'nord': dict(f='#262b32', fs='#2b3139', fr='#22272d', v='#1d3247', vw='#233c55', b='#323a44', b2='#2c333c', rim='#3a434e',
                r='#2a3139', rk='#38414b', rks='#2a3038', w='#5c6775', ws='#6c7785', wsw=2, w2='#46505c', curb='#5c6775', t='#66717f',
                s='#7c8796', d='#f4a3b4', o='#3a434e', os='#545f6b', blur=.5, shadow=None),
    'line': dict(f='#f1f3f6', fs='#e7eaef', fr='#e5e8ed', v='#dbe8f3', vw='#c7d9ea', b='#ffffff', b2='#f6f7f9', rim='#ffffff', bs='#9aa5b6', bsw=1.6,
                r='#dde1e7', rk='#f0f2f5', rks='#d4d9e0', w='#e9eef4', ws='#1d2433', wsw=2.2, w2='#d9e0e9', curb='#e9eef4', t='#c9d1db',
                s='#1d2433', d='#d94141', o='#ffffff', os='#1d2433', blur=0, shadow=None),
    # second batch: blueprint, constructivist poster, white-night duotone, aurora
    'blueprint': dict(f='#1b3157', fs='#213962', fr='#25406b', v='#12284a', vw='#1a3358', b='#21396a', b2='#1d3562', rim='#365689', bs='#5b7fbd', bsw=1.4,
                r='#33538a', rk='#29467a', rks='#3c5d96', w='#dce8f8', ws='#ffffff', wsw=1.5, w2='#a9c1e3', curb='#c9daf1', t='#bccfeb',
                s='#7f9cc9', d='#ffb38a', o='#21396a', os='#9fb8de', blur=0, shadow=None),
    'poster': dict(f='#ececec', fs='#e4e4e4', fr='#e1e1e1', v='#d8e2ea', vw='#c7d4df', b='#f7f7f7', b2='#eeeeee', rim='#ffffff', bs='#1c1c1c', bsw=1.4,
                r='#dadada', rk='#ececec', rks='#cdcdcd', w='#ffffff', ws='#1c1c1c', wsw=2.4, w2='#e2e2e2', curb='#ffffff', t='#e3e3e3',
                s='#1c1c1c', d='#d7261e', o='#f7f7f7', os='#1c1c1c', blur=0, shadow=None),
    'duotone': dict(f='#e3ebf5', fs='#eaf0f7', fr='#dae3ee', v='#c2d8ee', vw='#b0cce7', b='#dce7f3', b2='#d2dfee', rim='#eaf1f8',
                r='#cad8e9', rk='#d5e1ef', rks='#c5d3e5', w='#f6d3da', ws='#ebbbc5', wsw=2, w2='#f9e4e8', curb='#f9dde3', t='#efc6cf',
                s='#e6b1bd', d='#e2768c', o='#dce7f3', os='#c5d3e5', blur=.5, shadow='#7a8cb030'),
    'aurora': dict(f='#13262f', fs='#172f38', fr='#11222a', v='#0e2939', vw='#143549', b='#1a3540', b2='#16303a', rim='#21414d',
                r='#1d3a45', rk='#22434f', rks='#183540', w='#2f5a63', ws='#3e6f79', wsw=2, w2='#244a52', curb='#36676f', t='#3b6b75',
                s='#4f8590', d='#7de3b8', o='#21414d', os='#3e6f79', blur=.4, shadow=None),
    # fourth batch: metro signage, soft UI, white-night sunset, sage
    'metro': dict(f='#e6eaf0', fs='#edf0f4', fr='#dde2e9', v='#c9dcf0', vw='#b6cfe9', b='#f8f9fb', b2='#eef1f5', rim='#ffffff', bs='#b8c3d3', bsw=1.4,
                r='#dde2ea', rk='#eceff3', rks='#d0d6df', w='#d6e3f5', ws='#0b2f6b', wsw=2, w2='#bccde6', curb='#d6e3f5', t='#bdcde4',
                s='#0b2f6b', d='#e4312b', o='#f8f9fb', os='#0b2f6b', blur=0, shadow=None),
    'soft': dict(f='#dde1e8', fs='#e3e6ec', fr='#d6dbe3', v='#cbd9ea', vw='#bccee3', b='#e9ecf1', b2='#e2e6ec', rim='#f4f6f9',
                r='#d6dbe3', rk='#e4e8ee', rks='#d0d5dd', w='#f7f8fa', ws='#d3d8e0', wsw=3, w2='#eceff3', curb='#f7f8fa', t='#e8ebf0',
                s='#d3d8e0', d='#9a8cd8', o='#e9ecf1', os='#cfd4dc', blur=.6, shadow='#8a94a840'),
    'sunset': dict(f='#2a1d38', fs='#31223f', fr='#271a33', v='#23304f', vw='#2c3b5e', b='#382848', b2='#32233f', rim='#443254',
                r='#33243f', rk='#3f2e4f', rks='#2f2139', w='#f3b7a7', ws='#ffd0c2', wsw=1.5, w2='#c98fa6', curb='#f8c7b9', t='#e8a796',
                s='#ffd6ca', d='#a77bf3', o='#382848', os='#c98fa6', blur=.4, shadow=None),
    'sage': dict(f='#e1e7e3', fs='#e8ede9', fr='#d8dfda', v='#cfe1e6', vw='#bdd4db', b='#eef2ef', b2='#e5ebe7', rim='#f7f9f8', bs='#c4d0c8', bsw=1.2,
                r='#d6ded9', rk='#e5ebe7', rks='#ccd6cf', w='#ffffff', ws='#a9bfb3', wsw=2.4, w2='#e8eeea', curb='#ffffff', t='#e4eae6',
                s='#b9cbc0', d='#5f9a86', o='#eef2ef', os='#a9bfb3', blur=.5, shadow='#56706330'),
    # fifth batch: Kremlin red, taiga, neon night, candy
    'kremlin': dict(f='#ece4e4', fs='#f1eaea', fr='#e4dada', v='#d6e1ea', vw='#c5d3df', b='#e8d6d7', b2='#dfcacb', rim='#f2e6e7',
                r='#d9c3c5', rk='#e4d2d3', rks='#d1babc', w='#ffffff', ws='#a8202b', wsw=1.6, w2='#f3e9ea', curb='#ffffff', t='#efe1e2',
                s='#c79a9f', d='#a8202b', o='#e8d6d7', os='#c9a9ac', blur=.4, shadow='#7a2a3025'),
    'taiga': dict(f='#182b21', fs='#1c3127', fr='#15261d', v='#16313a', vw='#1c3d48', b='#21392c', b2='#1c3226', rim='#2a4537',
                r='#203629', rk='#29433a', rks='#1d3428', w='#cfe3d4', ws='#e9f4ec', wsw=1.2, w2='#9dbba6', curb='#c2d9c8', t='#b9d1bf',
                s='#7fa58b', d='#a8d5b5', o='#21392c', os='#9dbba6', blur=.4, shadow=None),
    'neon': dict(f='#14141f', fs='#191926', fr='#11111b', v='#121a2e', vw='#18223b', b='#1c1c2b', b2='#181826', rim='#24243a',
                r='#1f1f30', rk='#26263a', rks='#1c1c2c', w='#232338', ws='#ff4fd8', wsw=2, w2='#1d1d30', curb='#2b2b45', t='#2f2f4a',
                s='#59e0ff', d='#59e0ff', o='#24243a', os='#ff4fd8', blur=0, shadow=None),
    'candy': dict(f='#fbe9f1', fs='#fdf0f6', fr='#f6dfe9', v='#d9d6f6', vw='#c9c5f0', b='#ffd6e7', b2='#ffcbe0', rim='#ffe6f0', bs='#f2a7c6', bsw=2,
                r='#f8c4d9', rk='#ffdbe9', rks='#f2b5cd', w='#c4f1e2', ws='#7fd8bc', wsw=3, w2='#ddf7ee', curb='#d4f6ea', t='#aee6d3',
                s='#ffffff', d='#b48cf0', o='#ffe6f0', os='#f2a7c6', blur=0, shadow='#e48fb233'),
}

def style(p):
    p = dict(dict(ws='none', wsw=0, bs='none', bsw=0), **p)
    return (
        '.f{fill:%(f)s;stroke:%(fs)s;stroke-width:2}.fr{fill:none;stroke:%(fr)s;stroke-width:1.5}'
        '.v{fill:%(v)s}.vw{fill:none;stroke:%(vw)s;stroke-width:2;stroke-linecap:round}'
        '.b,.b2{stroke:%(bs)s;stroke-width:%(bsw)s}.b{fill:%(b)s}.b2{fill:%(b2)s}'
        '.r,.or{fill:none;stroke:%(r)s;stroke-width:1.6}.rk{fill:%(rk)s;stroke:%(rks)s;stroke-width:1}'
        '.w{fill:%(w)s;stroke:%(ws)s;stroke-width:%(wsw)s;paint-order:stroke;stroke-linejoin:round}.w2{fill:%(w2)s;stroke:%(ws)s;stroke-width:%(wsw)s;paint-order:stroke}'
        '.t{fill:none;stroke:%(t)s;stroke-width:2}.tk{fill:%(w)s;stroke:%(t)s;stroke-width:1.2}'
        '.s{fill:none;stroke:%(s)s;stroke-dasharray:4 4}'
        '.d{fill:none;stroke:%(d)s;stroke-width:3.5;stroke-linecap:round;stroke-dasharray:0 11}'
        '.l{fill:none;stroke:%(t)s;stroke-width:3;stroke-dasharray:22 18}'
        '.o{fill:%(o)s;stroke:%(os)s;stroke-width:1.5}' % p)

def defs(p):
    return (
        '<defs>'
        # faint inner line along the edge of the walkable area
        '<filter id="e"><feMorphology in="SourceAlpha" operator="erode" radius="8" result="a"/>'
        '<feMorphology in="SourceAlpha" operator="erode" radius="10" result="b"/>'
        '<feComposite in="a" in2="b" operator="out" result="c"/><feFlood flood-color="%(curb)s"/><feComposite in2="c" operator="in"/></filter>'
        # light rim just inside every block
        '<filter id="eb"><feMorphology in="SourceAlpha" operator="erode" radius="2" result="a"/>'
        '<feMorphology in="SourceAlpha" operator="erode" radius="4.5" result="b"/>'
        '<feComposite in="a" in2="b" operator="out" result="c"/><feFlood flood-color="%(rim)s"/><feComposite in2="c" operator="in"/></filter>'
        # roof texture is softened like a rendered top-down view
        '<filter id="sb"><feGaussianBlur stdDeviation="%(blur)s"/></filter>'
        + ('<filter id="sh"><feDropShadow dx="0" dy="5" stdDeviation="4" flood-color="%(shadow)s"/></filter>' if p['shadow'] else '')
        + '</defs>') % p

class Map:
    def __init__(s, seed=1):
        s.L = {k: [] for k in ('f', 'fr', 'v', 'vw', 'b', 'b2', 'r', 'rk', 'w2', 'w', 't', 'tk', 'l', 'o', 'or', 'd')}
        s.stairs = []; s.rects = []
        s.rng = random.Random(seed)
    def wr(s, x, y, w, h, layer='w'):
        """Walkable corridor/street rectangle; remembered for automatic fillets."""
        s.add(layer, rect(x, y, w, h)); s.rects.append((x, y, w, h))
    def auto_fillets(s, q=12):
        """Curve the inside corners where one corridor runs into another, as the
        in-game maps do, wherever the curve would not cut into another corridor."""
        R = s.rects
        def free(px, py, sx, sy):
            fx0, fx1 = sorted((px, px + sx * q)); fy0, fy1 = sorted((py, py + sy * q))
            for (x, y, w, h) in R:
                if x < fx1 - .5 and x + w > fx0 + .5 and y < fy1 - .5 and y + h > fy0 + .5: return False
            return True
        for (ax, ay, aw, ah) in R:
            for (bx, by, bw, bh) in R:
                if (ax, ay, aw, ah) == (bx, by, bw, bh): continue
                # b is a vertical corridor touching a's top or bottom edge
                if bx > ax + q and bx + bw < ax + aw - q:
                    if by < ay and ay <= by + bh <= ay + ah:          # b comes from above
                        for px, cn, sx in ((bx, 'tl', -1), (bx + bw, 'tr', 1)):
                            if free(px, ay, sx, -1): s.add('w', fillet(px, ay, q, cn))
                    if by + bh > ay + ah and ay <= by <= ay + ah:      # b leaves below
                        for px, cn, sx in ((bx, 'bl', -1), (bx + bw, 'br', 1)):
                            if free(px, ay + ah, sx, 1): s.add('w', fillet(px, ay + ah, q, cn))
                # b is a horizontal corridor touching a's left or right edge
                if by > ay + q and by + bh < ay + ah - q:
                    if bx < ax and ax <= bx + bw <= ax + aw:
                        for py, cn, sy in ((by, 'tl', -1), (by + bh, 'bl', 1)):
                            if free(ax, py, -1, sy): s.add('w', fillet(ax, py, q, cn))
                    if bx + bw > ax + aw and ax <= bx <= ax + aw:
                        for py, cn, sy in ((by, 'tr', -1), (by + bh, 'br', 1)):
                            if free(ax + aw, py, 1, sy): s.add('w', fillet(ax + aw, py, q, cn))
    def apse(s, cx, cy, r, layer='w'):
        """Round bay bulging out of a walkable edge."""
        s.add(layer, circ(cx, cy, r))
    def add(s, layer, *shapes):
        for sh in shapes: s.L[layer].append(sh)
    # ---- background ---------------------------------------------------
    def far_city(s, cell=(104, 84), gap=14):
        """Faint surrounding city filling the whole canvas behind the map."""
        cw, ch = cell; R = s.rng
        for gy in range(-1, int(1000 / ch) + 1):
            for gx in range(-1, int(1280 / cw) + 1):
                if R.random() < .12: continue
                x = gx * cw + R.uniform(0, 6) + (gy % 2) * cw * .35; y = gy * ch + R.uniform(0, 6)
                w = cw - gap - R.uniform(0, 26); h = ch - gap - R.uniform(0, 20)
                if R.random() < .35:     # split block
                    w2 = w * R.uniform(.35, .6)
                    for bx, bw in ((x, w2 - 6), (x + w2 + 6, w - w2 - 6)):
                        s.add('f', rect(bx, y, bw, h)); s.add('fr', rect(bx + 6, y + 6, bw - 12, h - 12))
                else:
                    s.add('f', rect(x, y, w, h)); s.add('fr', rect(x + 7, y + 7, w - 14, h - 14))
                    if R.random() < .4: s.add('fr', line((x + 7, y + h / 2), (x + w - 7, y + h / 2)))
    def far_rock(s, n=60):
        """Faint rock masses for underground floors."""
        R = s.rng
        for _ in range(n):
            cx, cy = R.uniform(0, 1280), R.uniform(0, 1000); r = R.uniform(40, 110)
            k = R.randint(5, 7); a0 = R.uniform(0, 6.3)
            pts = [(round(cx + r * R.uniform(.6, 1) * math.cos(a0 + 2 * math.pi * j / k), 1),
                    round(cy + r * R.uniform(.6, 1) * math.sin(a0 + 2 * math.pi * j / k), 1)) for j in range(k)]
            s.add('f', poly(pts))
            s.add('fr', line(pts[0], ((pts[2][0] + pts[3][0]) / 2, (pts[2][1] + pts[3][1]) / 2)))
    # ---- building detail ----------------------------------------------
    def rhythm(s, x, y, w, h, inset=6, step=24, a=7, b=4):
        """Window / balcony rhythm along the four sides of a roof."""
        n = max(1, int((w - 2 * inset) // step)); off = (w - n * step) / 2
        for k in range(n):
            px = x + off + k * step + (step - a) / 2
            s.add('r', rect(px, y + inset, a, b), rect(px, y + h - inset - b, a, b))
        n = max(1, int((h - 2 * inset) // step)); off = (h - n * step) / 2
        for k in range(n):
            py = y + off + k * step + (step - a) / 2
            s.add('r', rect(x + inset, py, b, a), rect(x + w - inset - b, py, b, a))
    def furniture(s, x, y, w, h, n=None):
        """Roof equipment: AC units, vents and a stair housing."""
        R = s.rng
        if w < 60 or h < 50: return
        n = n if n is not None else R.randint(2, 4)
        for _ in range(n):
            a, b = R.choice(((12, 9), (16, 10), (9, 9), (20, 12)))
            px = R.uniform(x + 14, x + w - 14 - a); py = R.uniform(y + 14, y + h - 14 - b)
            s.add('rk', rect(round(px, 1), round(py, 1), a, b))
        if R.random() < .6:
            px = round(R.uniform(x + 16, x + w - 46), 1); py = round(R.uniform(y + 16, y + h - 36), 1)
            s.add('rk', rect(px, py, 30, 20)); s.add('r', line((px, py), (px + 30, py + 20)))
    def block(s, sh):
        s.add('b2' if s.rng.random() < .35 else 'b', sh)
    def hip(s, x, y, w, h, i=10):
        """Building with a hipped roof seen from above, gutter line and chimneys."""
        s.block(rect(x, y, w, h))
        a, b2 = x + i, y + i; c, d = x + w - i, y + h - i
        s.add('r', rect(a, b2, c - a, d - b2), rect(x + 4, y + 4, w - 8, h - 8))
        if w >= h:
            m = y + h / 2; e = min(h / 2 - i, (w - 2 * i) / 2)
            s.add('r', line((a + e, m), (c - e, m)), line((a, b2), (a + e, m), (a, d)), line((c, b2), (c - e, m), (c, d)))
            for k in range(1, 4):   # tile courses
                t = k / 4
                s.add('r', line((a + e * t, b2 + (m - b2) * t), (c - e * t, b2 + (m - b2) * t)), line((a + e * t, d - (d - m) * t), (c - e * t, d - (d - m) * t)))
        else:
            m = x + w / 2; e = min(w / 2 - i, (h - 2 * i) / 2)
            s.add('r', line((m, b2 + e), (m, d - e)), line((a, b2), (m, b2 + e), (c, b2)), line((a, d), (m, d - e), (c, d)))
            for k in range(1, 4):
                t = k / 4
                s.add('r', line((a + (m - a) * t, b2 + e * t), (a + (m - a) * t, d - e * t)), line((c - (c - m) * t, b2 + e * t), (c - (c - m) * t, d - e * t)))
        R = s.rng
        for _ in range(2 if w * h > 9000 else 1):
            px = R.uniform(a + 8, c - 18); py = R.uniform(b2 + 8, d - 16)
            s.add('rk', rect(round(px, 1), round(py, 1), 10, 8))
    def flat(s, x, y, w, h, i=10, nx=0, ny=0, sk=0, furn=True):
        """Flat roof: parapet, window rhythm, skylights and equipment."""
        s.block(rect(x, y, w, h)); s.add('r', rect(x + i, y + i, w - 2 * i, h - 2 * i))
        if nx and ny:
            gw = (w - 2 * i) / nx; gh = (h - 2 * i) / ny; k = sk or min(gw, gh) * .3
            for a in range(nx):
                for b2 in range(ny):
                    cx = x + i + gw * (a + .5); cy = y + i + gh * (b2 + .5)
                    s.add('r', rect(cx - k, cy - k / 2, 2 * k, k), line((cx - k, cy), (cx + k, cy)))
        elif furn:
            s.furniture(x + i, y + i, w - 2 * i, h - 2 * i)
    def court(s, x, y, w, h, cx, cy, cw, ch, i=10, seg=34):
        """Perimeter block around a courtyard (courtyard itself added by caller)."""
        s.block(rect(x, y, w, h))
        s.add('r', rect(x + i, y + i, w - 2 * i, h - 2 * i), rect(cx - i, cy - i, cw + 2 * i, ch + 2 * i),
              line((x + i, y + i), (cx - i, cy - i)), line((x + w - i, y + i), (cx + cw + i, cy - i)),
              line((x + i, y + h - i), (cx - i, cy + ch + i)), line((x + w - i, y + h - i), (cx + cw + i, cy + ch + i)))
        # roof sections across the ring
        for px in range(int(cx + seg / 2), int(cx + cw), seg):
            s.add('r', line((px, y + i), (px, cy - i)), line((px, cy + ch + i), (px, y + h - i)))
        for py in range(int(cy + seg / 2), int(cy + ch), seg):
            s.add('r', line((x + i, py), (cx - i, py)), line((cx + cw + i, py), (x + w - i, py)))
    def dome(s, cx, cy, r, spokes=8):
        s.add('b', circ(cx, cy, r)); s.add('r', ring(cx, cy, r * .72), ring(cx, cy, r * .38), ring(cx, cy, r * .88))
        for k in range(spokes):
            a = 2 * math.pi * k / spokes
            s.add('r', line((round(cx + r * .38 * math.cos(a), 1), round(cy + r * .38 * math.sin(a), 1)),
                            (round(cx + r * .88 * math.cos(a), 1), round(cy + r * .88 * math.sin(a), 1))))
    def isl(s, x, y, w, h, trees=0):
        """Island inside a walkable area (median, planter)."""
        s.add('w', rect(x, y, w, h, True)); s.add('b', rect(x, y, w, h))
        for k in range(trees):
            q = min(h, w / trees) * .32
            s.add('r', ring(x + w * (k + .5) / trees, y + h / 2, q))
    def lamps(s, x1, y1, x2, y2, step=60):
        """Lamp posts: small light bases cut into the walkway."""
        n = max(1, int(math.hypot(x2 - x1, y2 - y1) // step))
        for k in range(n + 1):
            t = k / n
            s.holes(circ(round(x1 + (x2 - x1) * t, 1), round(y1 + (y2 - y1) * t, 1), 3.5))
    def planters(s, x1, y1, x2, y2, step=70, size=14):
        n = max(1, int(math.hypot(x2 - x1, y2 - y1) // step))
        for k in range(n + 1):
            t = k / n; px = x1 + (x2 - x1) * t; py = y1 + (y2 - y1) * t
            s.holes(rect(round(px - size / 2, 1), round(py - size / 2, 1), size, size))
            s.add('or', ring(round(px, 1), round(py, 1), size * .3))
    def steps(s, x1, y1, x2, y2, width, dash=None):
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        s.stairs.append(('<path class="s" stroke-width="%g"%s d="%s"/>' % (width, da, P(line((x1, y1), (x2, y2))))))
    def obj(s, *shapes):
        """Small prop standing on the walkway (lamp, bench, kiosk): drawn on top, not cut out."""
        for sh in shapes: s.add('o', sh)
    def holes(s, *shapes):
        """Cut shapes out of the walkable area and draw them as solid objects.
        Small shapes become props on top instead, so the curb line skips them."""
        for sh in shapes:
            pts = [c[1] for c in sh if c[0] in 'ML']
            if any(c[0] == 'A' for c in sh):
                big = math.pi * sh[1][1] * sh[1][2] >= 500
            else:
                xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
                big = (max(xs) - min(xs)) * (max(ys) - min(ys)) >= 500
            if not big:
                s.obj(sh); continue
            s.add('b', sh); s.add('w', reverse(sh))
    # ---- output -------------------------------------------------------
    def svg(s, theme='hsr'):
        p = PALETTES[theme]
        o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 1000" preserveAspectRatio="none"><style>%s</style>%s' % (style(p), defs(p))]
        if s.L['f']: o.append('<path class="f" d="%s"/>' % P(*s.L['f']))
        if s.L['fr']: o.append('<path class="fr" filter="url(#sb)" d="%s"/>' % P(*s.L['fr']))
        for k in ('v', 'vw'):
            if s.L[k]: o.append('<path class="%s" d="%s"/>' % (k, P(*s.L[k])))
        o.append('<g id="B"%s>' % (' filter="url(#sh)"' if p['shadow'] else '') + ''.join('<path class="%s" d="%s"/>' % (k, P(*s.L[k])) for k in ('b', 'b2') if s.L[k]) + '</g>')
        o.append('<use href="#B" filter="url(#eb)"/>')
        o.append('<g filter="url(#sb)">' + ''.join('<path class="%s" d="%s"/>' % (k, P(*s.L[k])) for k in ('r', 'rk') if s.L[k]) + '</g>')
        if s.L['w2']: o.append('<path class="w2" d="%s"/>' % P(*s.L['w2']))
        o.append('<path id="W" class="w" d="%s"/><use href="#W" filter="url(#e)"/>' % P(*s.L['w']))
        for k in ('t', 'tk', 'l', 'o', 'or'):
            if s.L[k]: o.append('<path class="%s" d="%s"/>' % (k, P(*s.L[k])))
        o += s.stairs
        if s.L['d']: o.append('<path class="d" d="%s"/>' % P(*s.L['d']))
        return ''.join(o) + '</svg>'
