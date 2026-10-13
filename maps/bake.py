"""Draw the shop markers into the map SVGs, so the widget does not have
to carry them as HTML (about 1,300 characters).

python3 bake.py <src dir> <out dir> [size]
  Writes <out>/<key>.svg for every map in widget.MARKERS. n1 and n2 hold two
  maps side by side: on the left the white night (polar-night-only shops
  closed), on the right the polar-night map n1a/n2a (white-night-only shops
  closed). Widget 16 shows one half with object-position, which saves it an
  <img> per floor. Also writes on.svg, the banner spots in red-orange as they
  look when picked.

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

def piano(x, y):
    """A grand piano seen from above, keyboard at the bottom: the straight bass side on the
    left, the bentside curving in to the rounded tail, black keys cut out of the keyboard."""
    d = ('M%g %gL%g %gC%g %g %g %g %g %gC%g %g %g %g %g %gC%g %g %g %g %g %gL%g %gZ'
         % (x - 15, y + 12, x - 15, y - 13, x - 15, y - 20, x - 9, y - 22, x - 4, y - 22,
            x + 3, y - 22, x + 5, y - 13, x + 9, y - 7, x + 13, y - 1, x + 15, y + 2, x + 15, y + 7, x + 15, y + 12))
    d += 'M%g %gh34v8h-34z' % (x - 17, y + 12)
    for k in (-12.5, -9, -3.5, 0, 3.5, 9, 12.5):
        d += 'M%g %gh2.4v4.4h-2.4z' % (x + k - 1.2, y + 12.6)
    return d

def sandwich(x, y):
    """A filled roll seen from the side: domed top bun with seeds, a wavy lettuce edge, the
    filling and the bottom bun, the gaps cut out so the dark rim shows through."""
    d = 'M%g %gC%g %g %g %g %g %gL%g %gZ' % (x - 20, y - 1, x - 20, y - 14, x + 20, y - 14, x + 20, y - 1, x - 20, y - 1)
    for k in (-9, 0, 9): d += 'M%g %gl2 -1.4l2 1.4l-2 1.4z' % (x + k - 2, y - 7)
    d += 'M%g %g' % (x - 21, y + 1) + 'q1.75 3 3.5 0' * 12 + 'v4h-42z'
    d += 'M%g %gh42v4h-42z' % (x - 21, y + 6.5)
    d += 'M%g %gh40c0 4 -3 6 -6 6h-28c-3 0 -6 -2 -6 -6z' % (x - 20, y + 12.5)
    return d

ON = '#ff4b1f'      # red-orange: a selected banner spot (on.svg)

def number(n, x, y, shut, fill='#fff'):
    """A numbered banner spot in the Star Rail map-guide style: a bold white numeral
    (Pretendard Bold) with a thin dark outline, straight on the map, the same size on every
    map. A closed spot is grey."""
    k, gap = 28 / 1468, 70                # numeral height 28, 1468 font units tall
    w = [D[c][0] for c in n]; at = -(sum(w) + gap * (len(n) - 1)) / 2
    o = '<g fill="%s" stroke="#1f1f1f" stroke-width="%g" stroke-linejoin="round" paint-order="stroke">' % ('#9b9b9b' if shut else fill, 4.4 / k)
    for c, cw in zip(n, w):
        o += '<path transform="translate(%g %g) scale(%g)" d="%s"/>' % (x + (at + cw / 2) * k, y, k, D[c][1])
        at += cw + gap
    return o + '</g>'

def bake(svg, marks, closed, size):
    out = [FILTER % ('o', '#1a1a1a', '#f1cd84'), FILTER % ('c', '#131313', '#9b9b9b'),
           '<g font-family="sans-serif" font-size="%g" text-anchor="middle" dominant-baseline="central">' % size]
    for m in marks:
        shut = len(m) > 3 and m[3] == closed
        if m[0][0] == '#':    # numbered banner spot or room number, '#1', '#12'
            out.append(number(m[0][1:], m[1], m[2], shut))
        elif m[0] in ('PNO', 'SDW'):   # drawn: the concert hall's grand piano, the sandwich shop
            out.append('<path fill="#000" fill-rule="evenodd" filter="url(#m%s)" d="%s"/>' % ('c' if shut else 'o', (piano if m[0] == 'PNO' else sandwich)(m[1], m[2])))
        elif m[0] == 'APT':     # drawn, not an emoji: banner pins sit on these
            out.append('<path fill="#000" fill-rule="evenodd" filter="url(#m%s)" d="%s"/>' % ('c' if shut else 'o', apartment(m[1], m[2])))
        else:
            out.append('<text x="%d" y="%d" filter="url(#m%s)">%s</text>' % (m[1], m[2], 'c' if shut else 'o', m[0]))
    return svg.replace('</svg>', ''.join(out) + '</g></svg>')

def selected():
    """on.svg, the banner spots as they look when picked, red-orange: cell 0 the apartment,
    cells 1-9 the numerals. Each cell is a pin's 4%-wide tap square (51.2 map units) centred
    on the marker, so widget 16 lays a cell over the drawn marker as the pin's background."""
    c = 51.2
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%g" viewBox="0 0 %g %g">' % (10 * c, c, 10 * c, c),
         FILTER % ('r', '#1a1a1a', ON),
         '<path fill="#000" fill-rule="evenodd" filter="url(#mr)" d="%s"/>' % apartment(c / 2, c / 2)]
    o += [number(str(k), c * k + c / 2, c / 2, False, ON) for k in range(1, 10)]
    return ''.join(o) + '</svg>'

def pair(day, night):
    """Both Norilsk palettes in one file, the polar night on the right. The polar half's ids
    are renamed and its style rules scoped to #P so the palettes don't collide."""
    x0, y0, w, h = map(float, re.search(r'viewBox="([^"]+)"', day).group(1).split())
    inner = lambda s: s[s.index('>') + 1:s.rindex('</svg>')]
    n = re.sub(r'(id="|url\(#|href="#)(\w+)', r'\1p\2', inner(night))
    n = re.sub(r'<style>(.*?)</style>', lambda m: '<style>' + re.sub(r'([^{}]+)\{', lambda r: ','.join(
        '#P ' + x for x in r.group(1).split(',')) + '{', m.group(1)) + '</style>', n, flags=re.S)
    half = '<svg %%sx="%%g" y="%%g" width="%g" height="%g" viewBox="%g %g %g %g" preserveAspectRatio="none">%%s</svg>' % (w, h, x0, y0, w, h)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%g" viewBox="%g %g %g %g">' % (2 * w, h, x0, y0, 2 * w, h)
            + half % ('', x0, y0, inner(day)) + half % ('id="P" ', x0 + w, y0, n) + '</svg>')

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
    open(os.path.join(dst, 'on.svg'), 'w').write(selected()); print('on')
