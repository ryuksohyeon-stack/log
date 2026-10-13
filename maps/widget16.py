"""Builds ../star-rail-map.html, widget 16 (kremlin colours, Star Rail UI).

python3 widget16.py <7-char commit sha holding k/>   -> writes ../star-rail-map.html
python3 widget16.py --local <out.html>                -> preview using ../k/ on disk

Maps come from k/ (maps/kremlin with the shop markers drawn in by bake.py).
Edit REGIONS, FLOORS and PINS below; everything else follows."""
import os, sys, json, urllib.request

def luvlog(h):
    """(banner image, links back to HOST?) for @h, from its public pages/<h> record, the same
    record luvlog's own "러브로그 홈 걸기" reads. Image: the home's banner, else its card image."""
    url = 'https://firestore.googleapis.com/v1/projects/lovelog-cc579/databases/(default)/documents/pages/' + h
    def val(v):
        k, x = next(iter(v.items()))
        if k == 'mapValue': return {a: val(b) for a, b in x.get('fields', {}).items()}
        if k == 'arrayValue': return [val(b) for b in x.get('values', [])]
        return x
    get = lambda u: {a: val(b) for a, b in json.load(urllib.request.urlopen(u, timeout=20)).get('fields', {}).items()}
    try:
        d = get(url)
    except Exception as e:     # a locked home: only its card (banner, image) is public, not its lists
        try:
            c = get(url.replace('/pages/', '/cards/')); print('@%s is locked: banner from its card, 맞배너 unknown' % h)
            return c.get('banner') or c.get('img'), False
        except Exception:
            print('luvlog lookup failed for', h, e); return None, False
    m = d.get('modes') or {}
    pick = lambda k: d.get(k) or ((m.get('a') or {}).get('snap') or {}).get(k) or ((m.get('b') or {}).get('snap') or {}).get(k) or ''
    hero = next((o for o in d.get('heroImgs') or [] if isinstance(o, dict) and o.get('img')), {})
    img = next((v for v in (pick('bannerImg'), pick('cardImg'), hero.get('img'), d.get('heroImg')) if isinstance(v, str) and v.startswith('https://')), None)
    links = set()     # the handles in its banner and neighbour lists, as luvlog's linkedSetOf
    for w in d.get('side') or []:
        if isinstance(w, dict) and w.get('t') in ('banner', 'nb'):
            for b in w.get('items') or []:
                x = b.get('h') if isinstance(b, dict) else b
                if isinstance(x, str) and x.strip(): links.add(x.strip().lower().lstrip('@'))
    return img, HOST in links

# list entries: (radio id, list label, title shown top left, map box)
GROUPS = [
    ('러시아', [('q1', '노릴스크의 극야', '노릴스크 · 극야', 'mn'),
               ('q2', '노릴스크의 백야', '노릴스크 · 백야', 'mn'),
               ('q3', '모스크바의 거리', '모스크바의 거리', 'mm')]),
    ('보금자리', [('q4', '센가물', '보금자리 · 센가물', 's1'),
               ('q5', '현대물', '보금자리 · 현대물', 's2'),
               ('q6', '바다', '보금자리 · 바다', 's3'),
               ('q7', '폐도시', '보금자리 · 폐도시', 'mr')]),
]
# map boxes: floors as (map file, floor label); one floor means no floor buttons
FLOORS = {'mn': [('n1', '1'), ('n2', 'B1')], 'mm': [('m1', '1'), ('m2', 'B1')],
          's1': [('s1', '')], 's2': [('s2', '')], 's3': [('s3', '')], 'mr': [('r1', '1'), ('r2', 'B1')]}
# n1 and n2 hold the white-night map on the left and the polar-night map on the right
# (bake.py); polar night shows the right half
HOST = 'vasilic'    # the luvlog home this widget sits on
# banner pins: map file -> (mark, x, y in the 1280x1000 map, luvlog handle, caption)
# The pin is an invisible tap area over a marker drawn into the map (widget.MARKERS, bake.py):
# 'APT' the apartment block, '1' to '9' the white numerals (numbers start at 1 on each map).
# Keep x, y on whole percents (x a multiple of 12.8, y of 10) and the same as the marker's, so
# the red-orange copy from on.svg lands on the drawn marker. Tapping a pin turns its marker
# red-orange and opens the banner beside it, on that floor
# only: to the left for a pin on the left half of the map, else to the right; the map pans so
# the whole banner is in view. The banner links to luvlog.me/<handle>. When the widget is
# built, luvlog's public record for that home gives its banner image, and whether its banner
# list carries HOST back (맞배너). Re-run the build to pick up changed banners.
PINS = {'n1': [('APT', 128, 700, 'milan', '404호')],     # the panel block at Norilsk's south-west corner
        's3': [('1', 1139, 500, 'legion', '')],          # the ship's bow
        'r1': [('1', 384, 400, 'pixelatedkisses', '')],  # the round plaza
        's2': [('1', 128, 760, 'aiden', '')]}            # the L-shaped block

# The root class is .srm because luvlog's own page CSS styles .hm (display:flex).
# CSS is written for luvlog's widget renderer: it rewrites every selector as
# ".<widget> <selector>" (splitting lists at commas), and puts a widget into a sandboxed
# frame where links can't open when its CSS has overflow:hidden, html/body rules,
# vh heights or position:fixed. So: overflow:clip, no commas inside :has()/:is(), and
# each keyframe starts with a throwaway `:root{};` that soaks up the prefix. Since every
# selector gets that prefix, a bare :has(#q1:checked) means "the widget has q1 checked".
# An open banner (focus rules below) stops the scroll-driven pan (--t:n) and puts the map at
# .mi's --f / translateY: its pin centred, clamped to the map's edges, then moved just enough
# that the banner (up to 15em out, on side --s) is inside the view.
CSS = '''
.srm{container-type:inline-size;word-break:keep-all}.srm *{margin:0;box-sizing:border-box}.srm input{display:none}
.hw{counter-reset:pt px;position:relative;overflow:clip;font-size:clamp(9px,1.2cqi,14px);--F:#dcc7c8;--V:#bccad8;--v:77cqi;--vh:66.67cqi;--w0:77cqi;background:#efe5e5;color:#2a1416}
{NAMES}
.hv{position:relative;aspect-ratio:3/2}
.mb{position:absolute;inset:0 23% 0 0;overflow:clip}
.mi{position:relative;width:var(--w0);top:calc(var(--vh)/2 - var(--w0)/2.56);aspect-ratio:1.28;translate:var(--f);--f:clamp(2.6% + 15em - var(--x) - (1 + var(--s))*1e4px,clamp(var(--v) - 100%,var(--v)/2 - var(--x),0px),var(--v) - 2.6% - 15em - var(--x) + (1 - var(--s))*1e4px)}
.mb,.mi{background:var(--F)}
:has(.A:checked):has(#n1:checked) .mb{background:linear-gradient(var(--F) 50%,var(--V) 0)}:has(#q6:checked) .mb{background:var(--V)}
.mi>div,.fs p{position:absolute;inset:0;display:none}
{SHOW}{display:grid}
.z{position:absolute;inset:0;--o:0;pointer-events:none}
{ACTIVE}{--o:1;--d:block}
.z>img{position:absolute;z-index:var(--o);width:100%;height:100%;object-fit:cover;object-position:0;opacity:max(.13,var(--o));transition:opacity .4s}
:has(#q1:checked) .z>img{object-position:100%}
.p{position:absolute;left:var(--x);top:var(--y);width:4%;aspect-ratio:1;translate:-50% -50%;z-index:3;display:var(--d,none);pointer-events:auto;cursor:pointer;counter-increment:pt}.p.x{counter-increment:pt px}.p:before{content:"";position:absolute;inset:-.5em}.p:has(:checked){background:url({ON}) 0/1000%}
.p a{display:none;position:absolute;left:calc(50% + var(--s)*(50% + .6em));top:50%;translate:calc(var(--s)*50% - 50%) -50%;padding:.2em;border-radius:.3em;background:#fff;box-shadow:0 .2em .6em #0006}
:checked+a{display:block}.p img{display:block;max-width:13em}.p b{display:block;padding:.1em .3em .25em;font-size:.75em;color:#555}
.hd:after{content:var(--nm)}.tr b:after{content:counter(px) " / " counter(pt)}
.hl{position:absolute;top:4%;right:1.5%;width:20%;z-index:5}
.hl>b{display:block;margin-bottom:.9em;padding:.5em .9em;white-space:nowrap;overflow:clip;text-overflow:ellipsis;border-radius:2em;background:#3a3a3a;color:#eee;font-weight:500}
.hl p{padding:.3em .8em;background:#c4c4c4;color:#555;font-size:.85em}
.hl label{display:block;padding:.75em 1em;border-bottom:1px solid #ddd;background:#f4f4f4;color:#333}
.hl label:before{content:"✦ ";font-size:.7em}
.hl :has(>:checked){background:#1d1d1d;color:#fff}
.hl :has(>:checked):after{content:"▼";float:right;color:#36d2e6;font-size:.75em}
.fs{position:absolute;left:2.5%;bottom:5%;z-index:4;width:3.8em;height:14em}
.fs p{top:auto;gap:.1em;padding:.25em;border-radius:2em;background:#3a3a3ab8}
.fs label{position:relative;padding:.75em 0 .45em;border-radius:2em;color:#f2f2f2;font-size:.85em;line-height:1.15;text-align:center}
.fs label:before{content:"Этаж";display:block;font-size:.8em}
.fs :has(>:checked){background:#fff;color:#333}
.fs :has(>:checked):after{content:"▼";position:absolute;inset:-.1em 0 auto;color:#36c6e0;font-size:.6em}
.hd{position:absolute;left:2.5%;top:3.5%;z-index:4;padding-left:1.5em;background:radial-gradient(circle at .5em .6em,#0000 .13em,#222 .15em .4em,#0000 .42em),conic-gradient(from -30deg at 50% 100%,#222 60deg,#0000 0) .1em .8em/.8em .6em no-repeat;color:#555;font-size:1.15em;font-weight:500}
.hd:before{content:"Навигация";display:block;color:#222;font-size:.62em;font-weight:700}
.tr{position:absolute;left:2.5%;top:calc(3.5% + 3.3em);z-index:4;display:flex;align-items:center;gap:.6em;padding:.35em .8em .35em 1em;border-radius:2em;background:#2b2b2bd9;color:#eee}
.tr i{width:1.4em;height:1.1em;border-radius:.4em .4em .1em .1em;background:linear-gradient(90deg,#0000 40%,#fbe3a0 0 60%,#0000 0) 0 40%/100% 30% no-repeat,linear-gradient(#0000 42%,#6b3f14 0 54%,#0000 0),#e3b04f}
.tr:after{content:"▾";margin-left:1.6em}
.pn,.zc{display:none}
@supports (timeline-scope:none){
.hw{timeline-scope:--tx,--ty,--zt}
.pn,.zg{position:absolute;inset:0;overflow:scroll;scrollbar-width:none;overscroll-behavior:contain;animation:k1 .6s}
.pn{display:block;touch-action:pan-x pan-y;scroll-timeline:--tx x,--ty y}
.pn:before{content:"";display:block;width:200%;height:200%}
.pn:after{content:"";position:absolute;left:100%;top:100%;padding:.5px;scroll-snap-align:center}
.mi{top:0;pointer-events:none;animation:zw linear both,var(--t,tx) linear both,var(--t,ty) linear both;animation-timeline:--zt,--tx,--ty;transform:translateY(clamp(min(var(--vh) - 100%,var(--vh)/2 - 50%),var(--vh)/2 - var(--y),max(0px,var(--vh)/2 - 50%)))}
.zc{display:grid;align-content:space-between;justify-items:center;position:absolute;right:1.5%;bottom:4%;z-index:4;width:2.2em;height:9em;border:1px solid #8c1724;background:linear-gradient(#d9b3b7 0 0) 50%/1px 60% no-repeat #fff;color:#8c1724;font-weight:700}
.zc:before{content:"+"}.zc:after{content:"−"}
.zg{touch-action:pan-y;scroll-timeline:--zt y}
.zg i{display:block;height:400%}
.zc u{position:absolute;left:50%;top:calc(100% - 2.1em);padding:.3em;margin:-.3em;rotate:45deg;background:#8c1724;pointer-events:none;animation:zk linear both;animation-timeline:--zt}
}
@keyframes k1{from,to{:root{};scroll-snap-type:both mandatory}}
@keyframes zw{to{:root{};width:calc(var(--w0)*3)}}
@keyframes tx{to{:root{};translate:calc(var(--v) - 100%)}}
@keyframes ty{from{:root{};transform:translateY(max(0px,var(--vh)/2 - 50%))}to{:root{};transform:translateY(min(var(--vh) - 100%,var(--vh)/2 - 50%))}}
@keyframes zk{to{:root{};top:2.1em}}
:has(#q1:checked) .hd,:has(#q1:checked) .zc{filter:invert(1) hue-rotate(180deg)}
@container (max-width:560px){.hv{aspect-ratio:auto;height:calc(100cqi/1.28)}.mb{right:0}.hl{position:static;width:auto;padding:.6em}.hw{--v:100cqi;--vh:78.13cqi;--w0:100cqi}.zc{right:3%;width:34px;height:130px}}
'''
# extra colours per list entry: polar night is dark, the abandoned town ash grey
EXTRA = {'q1': ';--F:#161c2e;--V:#0c1222;background:#0f1424', 'q7': ';--F:#d6d2ce;--V:#b7c0c6'}

BANNERS = {}
PIN_IDS = {}

def build(base):
    items = [it for _, its in GROUPS for it in its]
    boxes = list(dict.fromkeys(it[3] for it in items))
    qs = lambda box: [it[0] for it in items if it[3] == box]
    names = ''.join(':has(#%s:checked) .hw{--nm:"%s"%s}' % (q, t, EXTRA.get(q, '')) for q, _, t, _ in items)
    # a box shown for several list entries (Norilsk: polar night, white night) gets a class on
    # those radios, so one :has(.A:checked) stands for all of them
    grp = {b: 'ABCDEFG'[k] for k, b in enumerate(b for b in boxes if len(qs(b)) > 1)}
    reg = lambda b: ':has(%s:checked)' % ('.' + grp[b] if b in grp else '#' + qs(b)[0])
    show = [reg(b) + ' .' + b for b in boxes]
    active = [':has(#%s:checked) .%s' % (f, f) if len(FLOORS[b]) > 1 else '.%s>*' % b for b in boxes for f, _ in FLOORS[b]]
    picked = set()  # numbers on the map: each picks its red-orange cell of on.svg (bake.py)
    focus = ''     # per open banner: the map pans to it (see .mi --f), only while its floor is shown
    css = CSS.replace('{ON}', base + 'on.svg').replace('{NAMES}', names).replace('{SHOW}', ','.join(show)).replace('{ACTIVE}', ','.join(active)).replace('\n', '')

    def pins(b, f):
        nonlocal focus
        o = ''
        for mark, x, y, h, cap in PINS.get(f, []):
            n = PIN_IDS.setdefault((f, mark, x, y), len(PIN_IDS) + 1)
            px, py, side = round(x / 12.8), round(y / 10), 1 if x >= 640 else -1
            if h not in BANNERS: BANNERS[h] = luvlog(h); print('@%s: banner %s, 맞배너 %s' % (h, 'found' if BANNERS[h][0] else 'missing', BANNERS[h][1]))
            img, ex = BANNERS[h]; img = (img or base + 'b1.svg').replace('https://', '//')
            cls = ' '.join(['p'] + ['c' + mark] * (mark != 'APT') + ['x'] * ex)
            if mark != 'APT': picked.add(int(mark))
            o += ('<label class=%s style=--x:%d%%;--y:%d%%;--s:%d><input type=checkbox id=b%d><a href=//luvlog.me/%s>%s<img src=%s></a></label>'
                  % ('"%s"' % cls if ' ' in cls else cls, px, py, side, n, h, '<b>%s</b>' % cap if cap else '', img))
            focus += '%s%s:has(#b%d:checked) .mi{--x:%d%%;--y:%d%%;--s:%d;--t:n}' % (reg(b), ':has(#%s:checked)' % f if len(FLOORS[b]) > 1 else '', n, px, py, side)
        return o
    maps = ''.join('<div class=%s>%s</div>' % (b, ''.join(
        '<div class=%s><img src=%s%s.svg>%s</div>' % ('"z %s"' % f if len(FLOORS[b]) > 1 else 'z', base, f, pins(b, f))
        for f, _ in FLOORS[b])) for b in boxes)
    floors = ''.join('<p class=%s>%s</p>' % (b, ''.join('<label><input type=radio name=%s id=%s%s>%s</label>' % (b, f, ' checked' if k == 0 else '', lab)
                     for k, (f, lab) in enumerate(FLOORS[b]))) for b in boxes if len(FLOORS[b]) > 1)
    lst = ''.join('<p>◈ %s</p>%s' % (g, ''.join('<label><input type=radio name=q id=%s%s%s>%s</label>' % (
                  q, ' class=' + grp[b] if b in grp else '', ' checked' if q == 'q1' else '', lab) for q, lab, _, b in its)) for g, its in GROUPS)
    html = ('<div class=hw><div class=hv><div class=zc><b class=zg><i></i></b><u></u></div><div class=mb><b class=pn></b><div class=mi>' + maps +
            '</div></div><b class=hd></b><div class=tr><i></i><b></b></div><div class=fs>' + floors + '</div></div>'
            '<div class=hl><b>✦ Карта звёздного пути ›</b>' + lst + '</div></div>')
    focus += ''.join('.c%d:has(:checked){background-position:%.3g%%}' % (k, k / .09) for k in sorted(picked))
    return '<div class=srm><style>' + css + focus + '</style>' + html + '</div>'

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    if sys.argv[1] == '--local':
        out = build(os.path.join(here, '..', 'k') + '/')
        open(sys.argv[2], 'w', encoding='utf-8').write('<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width">'
            '<body style="margin:0;padding:24px;background:#f4f4f6"><div style="max-width:1000px;margin:auto">' + out + '</div>')
    else:
        out = build('//cdn.jsdelivr.net/gh/ryuksohyeon-stack/log@%s/k/' % sys.argv[1])
        open(os.path.join(here, '..', 'star-rail-map.html'), 'w', encoding='utf-8').write(out)
    print('chars', len(out))
