"""Draw the shop markers into the map SVGs, so the widget does not have
to carry them as HTML (about 1,300 characters).

python3 bake.py <src dir> <out dir> [size]
  Writes <out>/<key>.svg for every map in widget.MARKERS. n1 and n2 get the
  white-night state (polar-night-only shops closed); n1a and n2a, the
  polar-night maps, get the polar-night state (white-night-only shops closed).

The look copies the HTML markers: the emoji as a gold silhouette with a dark
rim and a soft drop shadow; closed shops grey."""
import os, sys
from widget import MARKERS

FILTER = ('<filter id="m%s" x="-40%%" y="-40%%" width="180%%" height="180%%" color-interpolation-filters="sRGB">'
          '<feMorphology in="SourceAlpha" operator="dilate" radius="1.6" result="d"/>'
          '<feGaussianBlur in="d" stdDeviation="2"/><feOffset dy="3" result="s"/>'
          '<feFlood flood-color="#000" flood-opacity=".5"/><feComposite in2="s" operator="in" result="h"/>'
          '<feFlood flood-color="%s"/><feComposite in2="d" operator="in" result="o"/>'
          '<feFlood flood-color="%s"/><feComposite in2="SourceAlpha" operator="in" result="g"/>'
          '<feMerge><feMergeNode in="h"/><feMergeNode in="o"/><feMergeNode in="g"/></feMerge></filter>')

def bake(svg, marks, closed, size):
    out = [FILTER % ('o', '#1a1a1a', '#f1cd84'), FILTER % ('c', '#131313', '#9b9b9b'),
           '<g font-family="sans-serif" font-size="%g" text-anchor="middle" dominant-baseline="central">' % size]
    for m in marks:
        shut = len(m) > 3 and m[3] == closed
        out.append('<text x="%d" y="%d" filter="url(#m%s)">%s</text>' % (m[1], m[2], 'c' if shut else 'o', m[0]))
    return svg.replace('</svg>', ''.join(out) + '</g></svg>')

if __name__ == '__main__':
    src, dst = sys.argv[1:3]; size = float(sys.argv[3]) if len(sys.argv) > 3 else 34
    os.makedirs(dst, exist_ok=True)
    for key, marks in MARKERS.items():
        for f, closed in ((key, 'n'), (key + 'a', 'w')) if key in ('n1', 'n2') else ((key, None),):
            p = os.path.join(src, f + '.svg')
            if os.path.exists(p):
                open(os.path.join(dst, f + '.svg'), 'w').write(bake(open(p).read(), marks, closed, size))
                print(f, 'closed:', closed)
