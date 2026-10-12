"""Drawing kit for the Star Rail style maps (1280 x 1000 canvas).

Layers, bottom to top: far city, water, buildings, roof detail, walkable
area (one path, holes cut counter-clockwise), floor detail, stairs, dots.
Anything placed inside a walkable area (monuments, medians, hatches) is
drawn in the building layers and cut out of the walkable path."""
import math
from pl import P, rect, cham, ngon, circ, poly, line, ring

STYLE = (
    '.f{fill:#cbcbcb;stroke:#c3c3c3;stroke-width:2}'
    '.v{fill:#bcc0c4}.vw{fill:none;stroke:#c8cbce;stroke-width:2}'
    '.b{fill:#e3e3e3;stroke:#a7a7a7;stroke-width:2}'
    '.r{fill:none;stroke:#c1c1c1;stroke-width:1.6}'
    '.w{fill:#444;stroke:#7b7b7b;stroke-width:6;paint-order:stroke;stroke-linejoin:round}'
    '.t{fill:none;stroke:#565656;stroke-width:2}'
    '.s{fill:none;stroke:#636363;stroke-dasharray:5 5}'
    '.d{fill:none;stroke:#6b6b6b;stroke-width:4;stroke-linecap:round;stroke-dasharray:0 14}'
    '.l{fill:none;stroke:#686868;stroke-width:3;stroke-dasharray:22 18}'
)

class Map:
    def __init__(s):
        s.L = {k: [] for k in ('f', 'v', 'vw', 'b', 'r', 'w', 't', 'l', 's', 'd')}
        s.stairs = []
    # raw layer access
    def add(s, layer, *shapes):
        for sh in shapes: s.L[layer].append(sh)
    # ---- motifs -------------------------------------------------------
    def hip(s, x, y, w, h, i=10):
        """Building with a hipped roof seen from above."""
        s.add('b', rect(x, y, w, h))
        a, b2 = x + i, y + i; c, d = x + w - i, y + h - i
        s.add('r', rect(a, b2, c - a, d - b2))
        if w >= h:
            m = y + h / 2; e = min(h / 2 - i, (w - 2 * i) / 2)
            s.add('r', line((a + e, m), (c - e, m)), line((a, b2), (a + e, m), (a, d)), line((c, b2), (c - e, m), (c, d)))
        else:
            m = x + w / 2; e = min(w / 2 - i, (h - 2 * i) / 2)
            s.add('r', line((m, b2 + e), (m, d - e)), line((a, b2), (m, b2 + e), (c, b2)), line((a, d), (m, d - e), (c, d)))
    def flat(s, x, y, w, h, i=10, nx=0, ny=0, sk=0):
        """Flat roof with parapet line and optional skylight grid."""
        s.add('b', rect(x, y, w, h)); s.add('r', rect(x + i, y + i, w - 2 * i, h - 2 * i))
        if nx and ny:
            gw = (w - 2 * i) / nx; gh = (h - 2 * i) / ny; k = sk or min(gw, gh) * .3
            for a in range(nx):
                for b2 in range(ny):
                    cx = x + i + gw * (a + .5); cy = y + i + gh * (b2 + .5)
                    s.add('r', rect(cx - k, cy - k / 2, 2 * k, k))
    def court(s, x, y, w, h, cx, cy, cw, ch, i=10):
        """Perimeter block around a courtyard (courtyard itself added by caller)."""
        s.add('b', rect(x, y, w, h))
        s.add('r', rect(x + i, y + i, w - 2 * i, h - 2 * i), rect(cx - i, cy - i, cw + 2 * i, ch + 2 * i),
              line((x + i, y + i), (cx - i, cy - i)), line((x + w - i, y + i), (cx + cw + i, cy - i)),
              line((x + i, y + h - i), (cx - i, cy + ch + i)), line((x + w - i, y + h - i), (cx + cw + i, cy + ch + i)))
    def dome(s, cx, cy, r, spokes=8):
        s.add('b', circ(cx, cy, r)); s.add('r', ring(cx, cy, r * .72), ring(cx, cy, r * .38))
        for k in range(spokes):
            a = 2 * math.pi * k / spokes
            s.add('r', line((round(cx + r * .38 * math.cos(a), 1), round(cy + r * .38 * math.sin(a), 1)),
                            (round(cx + r * .72 * math.cos(a), 1), round(cy + r * .72 * math.sin(a), 1))))
    def plaza(s, cx, cy, r, inner, rings=(), spokes=0, hole=True):
        """Round walkable plaza with a monument/fountain cut out of it."""
        s.add('w', circ(cx, cy, r))
        if hole: s.add('w', circ(cx, cy, inner, True)); s.dome(cx, cy, inner, 8)
        for q in rings: s.add('t', ring(cx, cy, q))
        for k in range(spokes):
            a = 2 * math.pi * k / spokes + math.pi / spokes
            s.add('t', line((round(cx + (inner + 8) * math.cos(a), 1), round(cy + (inner + 8) * math.sin(a), 1)),
                            (round(cx + (r - 10) * math.cos(a), 1), round(cy + (r - 10) * math.sin(a), 1))))
    def isl(s, x, y, w, h, trees=0):
        """Island inside a walkable area (median, planter)."""
        s.add('w', rect(x, y, w, h, True)); s.add('b', rect(x, y, w, h))
        for k in range(trees):
            s.add('r', ring(x + w * (k + .5) / trees, y + h / 2, min(h, w / trees) * .32))
    def steps(s, x1, y1, x2, y2, width, dash=None):
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        s.stairs.append(('<path class="s" stroke-width="%g"%s d="%s"/>' % (width, da, P(line((x1, y1), (x2, y2))))))
    def holes(s, *shapes):
        """Cut shapes out of the walkable area and draw them as solid objects."""
        for sh in shapes:
            pts = [c[1] for c in sh if c[0] in 'ML']
            s.add('b', sh)
            if any(c[0] == 'A' for c in sh):   # circle: flip the sweep direction
                s.add('w', [(c[0], c[1], c[2], 1 - c[3], c[4]) if c[0] == 'A' else c for c in sh])
            else:
                s.add('w', poly(pts, True))
    # ---- output -------------------------------------------------------
    def svg(s):
        o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 1000" preserveAspectRatio="none"><style>%s</style>' % STYLE]
        for k in ('f', 'v', 'vw', 'b', 'r', 'w', 't', 'l'):
            if s.L[k]: o.append('<path class="%s" d="%s"/>' % (k, P(*s.L[k])))
        o += s.stairs
        if s.L['d']: o.append('<path class="d" d="%s"/>' % P(*s.L['d']))
        return ''.join(o) + '</svg>'
