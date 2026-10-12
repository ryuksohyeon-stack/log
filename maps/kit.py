"""Drawing kit for the Star Rail style maps (1280 x 1000 canvas).

Layers, bottom to top: far city, water, buildings (+ inner wall line),
roof detail, walkable area (one path, holes cut counter-clockwise) with
floor tiles and an inner curb line, floor detail, lanes, stairs, dots.
Anything placed inside a walkable area (monuments, medians, hatches) is
drawn in the building layers and cut out of the walkable path."""
import math, random
from pl import P, rect, cham, ngon, circ, poly, line, ring

STYLE = (
    '.f{fill:#cbcbcb;stroke:#c4c4c4;stroke-width:2}.fr{fill:none;stroke:#c5c5c5;stroke-width:1.4}'
    '.v{fill:#bcc0c4}.vw{fill:none;stroke:#c9ccd0;stroke-width:2;stroke-linecap:round}'
    '.b{fill:#e3e3e3;stroke:#a5a5a5;stroke-width:2}'
    '.o{fill:#e3e3e3;stroke:#9c9c9c;stroke-width:1.6}.r,.or{fill:none;stroke:#c3c3c3;stroke-width:1.5}.rk{fill:#d6d6d6;stroke:#bdbdbd;stroke-width:1.2}'
    '.w{fill:#444;stroke:#7d7d7d;stroke-width:6;paint-order:stroke;stroke-linejoin:round}'
    '.t{fill:none;stroke:#585858;stroke-width:2}.tk{fill:#4f4f4f;stroke:#5d5d5d;stroke-width:1.2}'
    '.s{fill:none;stroke:#646464;stroke-dasharray:5 5}'
    '.d{fill:none;stroke:#6e6e6e;stroke-width:4;stroke-linecap:round;stroke-dasharray:0 14}'
    '.l{fill:none;stroke:#6a6a6a;stroke-width:3;stroke-dasharray:22 18}'
)

DEFS = (
    '<defs>'
    # inner curb line that follows the outline of the whole walkable area
    '<filter id="e"><feMorphology in="SourceAlpha" operator="erode" radius="9" result="a"/>'
    '<feMorphology in="SourceAlpha" operator="erode" radius="11" result="b"/>'
    '<feComposite in="a" in2="b" operator="out" result="c"/><feFlood flood-color="#5d5d5d"/><feComposite in2="c" operator="in"/></filter>'
    # inner wall line on building footprints
    '<filter id="eb"><feMorphology in="SourceAlpha" operator="erode" radius="4" result="a"/>'
    '<feMorphology in="SourceAlpha" operator="erode" radius="5.5" result="b"/>'
    '<feComposite in="a" in2="b" operator="out" result="c"/><feFlood flood-color="#cdcdcd"/><feComposite in2="c" operator="in"/></filter>'
    # paving joints over every walkable surface
    '<pattern id="p" width="44" height="44" patternUnits="userSpaceOnUse">'
    '<path d="M0 .6H44M.6 0V44" fill="none" stroke="#4b4b4b" stroke-width="1.2"/></pattern>'
    '</defs>'
)

class Map:
    def __init__(s, seed=1):
        s.L = {k: [] for k in ('f', 'fr', 'v', 'vw', 'b', 'r', 'rk', 'w', 't', 'tk', 'l', 'o', 'or', 'd')}
        s.stairs = []
        s.rng = random.Random(seed)
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
    def hip(s, x, y, w, h, i=10):
        """Building with a hipped roof seen from above, gutter line and chimneys."""
        s.add('b', rect(x, y, w, h))
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
        s.add('b', rect(x, y, w, h)); s.add('r', rect(x + i, y + i, w - 2 * i, h - 2 * i))
        if w > 50 and h > 50: s.rhythm(x, y, w, h, 3, 22, 7, 3)
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
        s.add('b', rect(x, y, w, h))
        s.add('r', rect(x + i, y + i, w - 2 * i, h - 2 * i), rect(cx - i, cy - i, cw + 2 * i, ch + 2 * i),
              line((x + i, y + i), (cx - i, cy - i)), line((x + w - i, y + i), (cx + cw + i, cy - i)),
              line((x + i, y + h - i), (cx - i, cy + ch + i)), line((x + w - i, y + h - i), (cx + cw + i, cy + ch + i)))
        # roof sections across the ring
        for px in range(int(cx + seg / 2), int(cx + cw), seg):
            s.add('r', line((px, y + i), (px, cy - i)), line((px, cy + ch + i), (px, y + h - i)))
        for py in range(int(cy + seg / 2), int(cy + ch), seg):
            s.add('r', line((x + i, py), (cx - i, py)), line((cx + cw + i, py), (x + w - i, py)))
        s.rhythm(x, y, w, h, 3, 22, 7, 3)
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
            s.add('b', sh)
            if any(c[0] == 'A' for c in sh):   # circle: flip the sweep direction
                s.add('w', [(c[0], c[1], c[2], 1 - c[3], c[4]) if c[0] == 'A' else c for c in sh])
            else:
                s.add('w', poly(pts, True))
    # ---- output -------------------------------------------------------
    def svg(s, tiles=True):
        o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 1000" preserveAspectRatio="none"><style>%s</style>%s' % (STYLE, DEFS)]
        for k in ('f', 'fr', 'v', 'vw'):
            if s.L[k]: o.append('<path class="%s" d="%s"/>' % (k, P(*s.L[k])))
        o.append('<g class="b"><path id="B" d="%s"/></g><use href="#B" filter="url(#eb)"/>' % P(*s.L['b']))
        for k in ('r', 'rk'):
            if s.L[k]: o.append('<path class="%s" d="%s"/>' % (k, P(*s.L[k])))
        o.append('<g class="w"><path id="W" d="%s"/></g>' % P(*s.L['w']))
        if tiles: o.append('<use href="#W" fill="url(#p)"/>')
        o.append('<use href="#W" filter="url(#e)"/>')
        for k in ('t', 'tk', 'l'):
            if s.L[k]: o.append('<path class="%s" d="%s"/>' % (k, P(*s.L[k])))
        if s.L['o']: o.append('<path class="o" d="%s"/>' % P(*s.L['o']))
        if s.L['or']: o.append('<path class="or" d="%s"/>' % P(*s.L['or']))
        o += s.stairs
        if s.L['d']: o.append('<path class="d" d="%s"/>' % P(*s.L['d']))
        return ''.join(o) + '</svg>'
