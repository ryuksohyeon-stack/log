"""Drawing kit for the Star Rail style maps (1280 x 1000 canvas).

Layers, bottom to top: far city, water, buildings (+ inner wall line),
roof detail, walkable area (one path, holes cut counter-clockwise) with
floor tiles and an inner curb line, floor detail, lanes, stairs, dots.
Anything placed inside a walkable area (monuments, medians, hatches) is
drawn in the building layers and cut out of the walkable path."""
import math, random
from pl import P, rect, rr, cham, ngon, circ, poly, line, ring, reverse, fillet

# Palette sampled from the in-game maps: background #d0d0d0, walkable #3c3c3c,
# soft low-contrast blocks for everything you cannot walk on.
STYLE = (
    '.f{fill:#c9c9c9;stroke:#d3d3d3;stroke-width:2}.fr{fill:none;stroke:#c1c1c1;stroke-width:1.5}'
    '.v{fill:#dedede}.vw{fill:none;stroke:#cfcfcf;stroke-width:2;stroke-linecap:round}'
    '.b{fill:#d8d8d8}.b2{fill:#c6c6c6}'
    '.r,.or{fill:none;stroke:#b9b9b9;stroke-width:1.6}.rk{fill:#c3c3c3;stroke:#b8b8b8;stroke-width:1}'
    '.w{fill:#3c3c3c}.w2{fill:#6e6e6e}'
    '.t{fill:none;stroke:#4a4a4a;stroke-width:2}.tk{fill:#444;stroke:#4c4c4c;stroke-width:1.2}'
    '.s{fill:none;stroke:#8e8e8e;stroke-dasharray:4 4}'
    '.d{fill:none;stroke:#9a9a9a;stroke-width:3.5;stroke-linecap:round;stroke-dasharray:0 11}'
    '.l{fill:none;stroke:#555;stroke-width:3;stroke-dasharray:22 18}'
    '.o{fill:#cfcfcf;stroke:#e2e2e2;stroke-width:1.5}'
)

DEFS = (
    '<defs>'
    # faint inner line along the edge of the walkable area
    '<filter id="e"><feMorphology in="SourceAlpha" operator="erode" radius="8" result="a"/>'
    '<feMorphology in="SourceAlpha" operator="erode" radius="10" result="b"/>'
    '<feComposite in="a" in2="b" operator="out" result="c"/><feFlood flood-color="#474747"/><feComposite in2="c" operator="in"/></filter>'
    # light rim just inside every block
    '<filter id="eb"><feMorphology in="SourceAlpha" operator="erode" radius="2" result="a"/>'
    '<feMorphology in="SourceAlpha" operator="erode" radius="4.5" result="b"/>'
    '<feComposite in="a" in2="b" operator="out" result="c"/><feFlood flood-color="#e6e6e6"/><feComposite in2="c" operator="in"/></filter>'
    # roof texture is softened like the rendered top-down view in game
    '<filter id="sb"><feGaussianBlur stdDeviation="0.9"/></filter>'
    '</defs>'
)

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
    def svg(s):
        o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 1000" preserveAspectRatio="none"><style>%s</style>%s' % (STYLE, DEFS)]
        if s.L['f']: o.append('<path class="f" d="%s"/>' % P(*s.L['f']))
        if s.L['fr']: o.append('<path class="fr" filter="url(#sb)" d="%s"/>' % P(*s.L['fr']))
        for k in ('v', 'vw'):
            if s.L[k]: o.append('<path class="%s" d="%s"/>' % (k, P(*s.L[k])))
        o.append('<g id="B">' + ''.join('<path class="%s" d="%s"/>' % (k, P(*s.L[k])) for k in ('b', 'b2') if s.L[k]) + '</g>')
        o.append('<use href="#B" filter="url(#eb)"/>')
        o.append('<g filter="url(#sb)">' + ''.join('<path class="%s" d="%s"/>' % (k, P(*s.L[k])) for k in ('r', 'rk') if s.L[k]) + '</g>')
        if s.L['w2']: o.append('<path class="w2" d="%s"/>' % P(*s.L['w2']))
        o.append('<path id="W" class="w" d="%s"/><use href="#W" filter="url(#e)"/>' % P(*s.L['w']))
        for k in ('t', 'tk', 'l', 'o', 'or'):
            if s.L[k]: o.append('<path class="%s" d="%s"/>' % (k, P(*s.L[k])))
        o += s.stairs
        if s.L['d']: o.append('<path class="d" d="%s"/>' % P(*s.L['d']))
        return ''.join(o) + '</svg>'
