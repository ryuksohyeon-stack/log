"""Draw the shop markers into the map SVGs, so the widget does not have
to carry them as HTML (about 1,300 characters).

python3 bake.py <src dir> <out dir> [size]
  Writes <out>/<key>.svg for every map in widget.MARKERS. n1 and n2 hold two
  maps side by side: on the left the white night (polar-night-only shops
  closed), on the right the polar-night map n1a/n2a (white-night-only shops
  closed). Widget 16 shows one half with object-position, which saves it an
  <img> per floor.

The look copies the HTML markers: the emoji as a gold silhouette with a dark
rim and a soft drop shadow; closed shops grey."""
import os, re, sys
from widget import MARKERS
from digits import D

FILTER = ('<filter id="m%s" x="-40%%" y="-40%%" width="180%%" height="180%%" color-interpolation-filters="sRGB">'
          '<feMorphology in="SourceAlpha" operator="dilate" radius="1.6" result="d"/>'
          '<feGaussianBlur in="d" stdDeviation="2"/><feOffset dy="3" result="s"/>'
          '<feFlood flood-color="#000" flood-opacity=".5"/><feComposite in2="s" operator="in" result="h"/>'
          '<feFlood flood-color="%s"/><feComposite in2="d" operator="in" result="o"/>'
          '<feFlood flood-color="%s"/><feComposite in2="SourceAlpha" operator="in" result="g"/>'
          '<feMerge><feMergeNode in="h"/><feMergeNode in="o"/><feMergeNode in="g"/></feMerge></filter>')

def apartment(x, y):
    """A panel block drawn as a marker: roof box, body with three rows of three windows and
    a door, the openings cut out so the marker filter's dark rim shows through them."""
    d = 'M%g %gh30v40h-11.5v-11h-7v11h-11.5zM%g %gh20v5h-20z' % (x - 15, y - 20, x - 10, y - 25)
    for r in range(3):
        for c in range(3):
            d += 'M%g %gh5v5h-5z' % (x - 10.5 + 8 * c, y - 16 + 8 * r)
    return d

def number(n, x, y, shut):
    """A numbered banner spot: a gold disc in the marker filter with the number on it in
    Pretendard Bold, the same size on every map."""
    k, gap = 19 / 1468, 90                # numeral height 19, 1468 font units tall
    w = [D[c][0] for c in n]; at = -(sum(w) + gap * (len(n) - 1)) / 2
    o = '<circle cx="%g" cy="%g" r="17" filter="url(#m%s)"/>' % (x, y, 'c' if shut else 'o')
    for c, cw in zip(n, w):
        o += '<path fill="#1a1a1a" transform="translate(%g %g) scale(%g)" d="%s"/>' % (x + (at + cw / 2) * k, y, k, D[c][1])
        at += cw + gap
    return o

def bake(svg, marks, closed, size):
    out = [FILTER % ('o', '#1a1a1a', '#f1cd84'), FILTER % ('c', '#131313', '#9b9b9b'),
           '<g font-family="sans-serif" font-size="%g" text-anchor="middle" dominant-baseline="central">' % size]
    for m in marks:
        shut = len(m) > 3 and m[3] == closed
        if m[0][0] == '#':    # numbered banner spot, '#1'
            out.append(number(m[0][1:], m[1], m[2], shut))
        elif m[0] == 'APT':     # drawn, not an emoji: banner pins sit on these
            out.append('<path fill="#000" fill-rule="evenodd" filter="url(#m%s)" d="%s"/>' % ('c' if shut else 'o', apartment(m[1], m[2])))
        else:
            out.append('<text x="%d" y="%d" filter="url(#m%s)">%s</text>' % (m[1], m[2], 'c' if shut else 'o', m[0]))
    return svg.replace('</svg>', ''.join(out) + '</g></svg>')

def pair(day, night):
    """Both Norilsk palettes in one 2560x1000 file, the polar night on the right. The polar
    half's ids are renamed and its style rules scoped to #P so the palettes don't collide."""
    inner = lambda s: s[s.index('>') + 1:s.rindex('</svg>')]
    n = re.sub(r'(id="|url\(#|href="#)(\w+)', r'\1p\2', inner(night))
    n = re.sub(r'<style>(.*?)</style>', lambda m: '<style>' + re.sub(r'([^{}]+)\{', lambda r: ','.join(
        '#P ' + x for x in r.group(1).split(',')) + '{', m.group(1)) + '</style>', n, flags=re.S)
    half = '<svg %swidth="1280" height="1000" viewBox="0 0 1280 1000" preserveAspectRatio="none">%s</svg>'
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1000" viewBox="0 0 2560 1000">'
            + half % ('', inner(day)) + half % ('id="P" x="1280" ', n) + '</svg>')

if __name__ == '__main__':
    src, dst = sys.argv[1:3]; size = float(sys.argv[3]) if len(sys.argv) > 3 else 34
    os.makedirs(dst, exist_ok=True)
    read = lambda f: open(os.path.join(src, f + '.svg')).read()
    for key, marks in MARKERS.items():
        if not os.path.exists(os.path.join(src, key + '.svg')): continue
        if key in ('n1', 'n2'):
            out = pair(bake(read(key), marks, 'n', size), bake(read(key + 'a'), marks, 'w', size))
        else:
            out = bake(read(key), marks, None, size)
        open(os.path.join(dst, key + '.svg'), 'w').write(out); print(key)
