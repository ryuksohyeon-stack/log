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
    try:
        d = {a: val(b) for a, b in json.load(urllib.request.urlopen(url, timeout=20)).get('fields', {}).items()}
    except Exception as e:
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
NIGHT = {'n1', 'n2'}          # these also get a polar-night map, <name>a.svg
HOST = 'vasilic'    # the luvlog home this widget sits on
# banner pins: map file -> (mark, x, y in the 1280x1000 map, luvlog handle, caption)
# The pin is an invisible tap area over an 'APT' marker drawn into the map (widget.MARKERS,
# bake.py); tapping it rings the marker and opens the banner beside it, on that floor only.
# The pin links to luvlog.me/<handle>. When the widget is built, luvlog's public record for
# that home gives its banner image, and whether its banner list carries HOST back (맞배너).
# Re-run the build to pick up changed banners.
PINS = {'n1': [('APT', 130, 705, 'milan', '404호')]}    # the panel block at Norilsk's south-west corner

# The root class is .srm because luvlog's own page CSS styles .hm (display:flex).
# CSS is written for luvlog's widget renderer: it rewrites every selector as
# ".<widget> <selector>" (splitting lists at commas), and puts a widget into a sandboxed
# frame where links can't open when its CSS has overflow:hidden, html/body rules,
# vh heights or position:fixed. So: overflow:clip, no commas inside :has()/:is(), and
# each keyframe starts with a throwaway `:root{};` that soaks up the prefix.
CSS = '''
.srm{container-type:inline-size;word-break:keep-all}.srm *{margin:0;box-sizing:border-box}.srm input{display:none}
.hw{counter-reset:pt px;position:relative;overflow:clip;font-size:clamp(9px,1.2cqi,14px);--F:#dcc7c8;--V:#bccad8;--v:77cqi;--vh:66.67cqi;--w0:77cqi;background:#efe5e5;color:#2a1416}
{NAMES}
.hv{position:relative;aspect-ratio:3/2}
.mb{position:absolute;left:0;top:0;width:77%;height:100%;overflow:clip}
.mi{position:relative;width:var(--w0);top:calc(var(--vh)/2 - var(--w0)/2.56);aspect-ratio:1.28}
.mb,.mi{background:var(--F)}
.srm:has(#q1:checked):has(#n1:checked) .mb,.srm:has(#q2:checked):has(#n1:checked) .mb{background:linear-gradient(var(--F) 50%,var(--V) 0)}.srm:has(#q6:checked) .mb{background:var(--V)}
.mi>div,.fs p{position:absolute;inset:0;visibility:hidden}
{SHOW}{visibility:visible;--c:pt;--e:pt px}
.z{position:absolute;inset:0;--o:0;pointer-events:none}
{ACTIVE}{--o:1;--pe:auto;pointer-events:auto;--a:var(--c);--b:var(--e)}
.z>img{position:absolute;z-index:var(--o);width:100%;height:100%;opacity:max(.13,var(--o));transition:opacity .4s}
.p{counter-increment:var(--a)}.p.x{counter-increment:var(--b)}
.p{position:absolute;left:calc(var(--x)*1%);top:calc(var(--y)*1%);width:3.6%;aspect-ratio:3/4;translate:-50% -55%;z-index:3;border-radius:.3em;pointer-events:var(--pe,none);cursor:pointer}:checked+.p{box-shadow:0 0 0 .15em #7fe3f0,0 0 .5em #7fe3f0}
.bn{display:none;position:absolute;left:calc(var(--x)*1% + 2.6%);top:calc(var(--y)*1%);translate:0 -50%;z-index:6;padding:.2em;border-radius:.3em;background:#fff;box-shadow:0 .2em .6em #0006;opacity:var(--o);pointer-events:var(--pe,none)}
:checked+.p+.bn{display:block}.bn img{display:block;max-width:13em}.bn b{display:block;padding:.1em .3em .25em;font-size:.75em;color:#555}
.hd:after{content:var(--nm)}.tr b:after{content:counter(px) " / " counter(pt)}
.hl{position:absolute;top:4%;right:1.5%;width:20%;z-index:5}
.hl>b{display:block;margin-bottom:.9em;padding:.5em .9em;white-space:nowrap;overflow:clip;text-overflow:ellipsis;border-radius:2em;background:#3a3a3a;color:#eee;font-weight:500}
.hl p{padding:.3em .8em;background:#c4c4c4;color:#555;font-size:.85em}
.hl label{display:block;padding:.75em 1em;border-bottom:1px solid #ddd;background:#f4f4f4;color:#333}
.hl label:before{content:"✦ ";font-size:.7em}
.hl :checked+label{background:#1d1d1d;color:#fff}
.hl :checked+label:after{content:"▼";float:right;color:#36d2e6;font-size:.75em}
.fs{position:absolute;left:2.5%;bottom:5%;z-index:4;width:3.8em;height:14em}
.fs p{top:auto;display:flex;flex-direction:column;gap:.1em;padding:.25em;border-radius:2em;background:#3a3a3ab8}
.fs label{position:relative;padding:.75em 0 .45em;border-radius:2em;color:#f2f2f2;font-size:.85em;line-height:1.15;text-align:center}
.fs label:before{content:"Этаж";display:block;font-size:.8em}
.fs :checked+label{background:#fff;color:#333}
.fs :checked+label:after{content:"▼";position:absolute;inset:-.1em 0 auto;color:#36c6e0;font-size:.6em}
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
.pn:after{content:"";position:absolute;left:100%;top:100%;width:1px;height:1px;scroll-snap-align:center}
.mi{top:0;pointer-events:none;animation:zw linear both,tx linear both,ty linear both;animation-timeline:--zt,--tx,--ty}
.z{pointer-events:none!important}
.zc{display:flex;flex-direction:column;justify-content:space-between;align-items:center;position:absolute;right:1.5%;bottom:4%;z-index:4;width:2.2em;height:9em;border:1px solid #8c1724;background:linear-gradient(#d9b3b7 0 0) 50%/1px 60% no-repeat #fff;color:#8c1724;font-weight:700}
.zc:before{content:"+"}.zc:after{content:"−"}
.zg{touch-action:pan-y;scroll-timeline:--zt y}
.zg i{display:block;height:400%}
.zc u{position:absolute;left:50%;top:calc(100% - 2.1em);width:.6em;height:.6em;margin:-.3em;rotate:45deg;background:#8c1724;pointer-events:none;animation:zk linear both;animation-timeline:--zt}
}
@keyframes k1{from,to{:root{};scroll-snap-type:both mandatory}}
@keyframes zw{to{:root{};width:calc(var(--w0)*3)}}
@keyframes tx{from{:root{};translate:max(0px,calc(var(--v)/2 - 50%))}to{:root{};translate:min(calc(var(--v) - 100%),calc(var(--v)/2 - 50%))}}
@keyframes ty{from{:root{};transform:translateY(max(0px,calc(var(--vh)/2 - 50%)))}to{:root{};transform:translateY(min(calc(var(--vh) - 100%),calc(var(--vh)/2 - 50%)))}}
@keyframes zk{to{:root{};top:2.1em}}
.srm:not(:has(#q1:checked)) .pd,.srm:has(#q1:checked) .z>img:not(.pd){display:none}
.srm:has(#q1:checked) .hd,.srm:has(#q1:checked) .zc{filter:invert(1) hue-rotate(180deg)}
@container (max-width:560px){.hv{aspect-ratio:auto;height:calc(100cqi/1.28)}.mb{width:100%}.hl{position:static;width:auto;padding:.6em}.hw{--v:100cqi;--vh:78.13cqi;--w0:100cqi}.zc{right:3%;width:34px;height:130px}}
'''
# extra colours per list entry: polar night is dark, the abandoned town ash grey
EXTRA = {'q1': ';--F:#161c2e;--V:#0c1222;background:#0f1424', 'q7': ';--F:#d6d2ce;--V:#b7c0c6'}

BANNERS = {}
PIN_IDS = {}

def build(base):
    items = [it for _, its in GROUPS for it in its]
    boxes = list(dict.fromkeys(it[3] for it in items))
    qs = lambda box: [it[0] for it in items if it[3] == box]
    names = ''.join('.srm:has(#%s:checked) .hw{--nm:"%s"%s}' % (q, t, EXTRA.get(q, '')) for q, _, t, _ in items)
    show, active = [], []
    for b in boxes:
        fl = FLOORS[b]
        if len(fl) > 1:
            show += ['.srm:has(#%s:checked) .%s' % (q, b) for q in qs(b)]
            active += ['.hw:has(#%s:checked) .%s>:nth-child(%d)' % (f, b, k + 1) for k, (f, _) in enumerate(fl)]
        else:
            show += ['.srm:has(#%s:checked) .%s' % (q, b) for q in qs(b)]; active.append('.%s>*' % b)
    css = CSS.replace('{NAMES}', names).replace('{SHOW}', ','.join(show)).replace('{ACTIVE}', ','.join(active)).replace('\n', '')

    def pins(f):
        o = ''
        for mark, x, y, h, cap in PINS.get(f, []):
            n = PIN_IDS.setdefault((f, mark, x, y), len(PIN_IDS) + 1)
            pos = 'style=--x:%d;--y:%d' % (round(x / 12.8), round(y / 10))
            if h not in BANNERS: BANNERS[h] = luvlog(h); print('@%s: banner %s, 맞배너 %s' % (h, 'found' if BANNERS[h][0] else 'missing', BANNERS[h][1]))
            img, ex = BANNERS[h]; img = img or base + 'b1.svg'
            cls = ' '.join(['p'] + ['x'] * ex)
            o += ('<input type=checkbox id=b%d><label for=b%d class=%s %s></label><a class=bn href=https://luvlog.me/%s target=_blank %s>%s<img src=%s></a>'
                  % (n, n, '"%s"' % cls if ' ' in cls else cls, pos, h, pos, '<b>%s</b>' % cap if cap else '', img.replace('&', '&amp;')))
        return o
    maps = ''.join('<div class=%s>%s</div>' % (b, ''.join(
        '<div class=z><img src=%s%s.svg>%s%s</div>' % (base, f, '<img class=pd src=%s%sa.svg>' % (base, f) if f in NIGHT else '', pins(f))
        for f, _ in FLOORS[b])) for b in boxes)
    floors = ''.join('<p class=%s>%s</p>' % (b, ''.join('<input type=radio name=%s id=%s%s><label for=%s>%s</label>' % (b, f, ' checked' if k == 0 else '', f, lab)
                     for k, (f, lab) in enumerate(FLOORS[b]))) for b in boxes if len(FLOORS[b]) > 1)
    lst = ''.join('<p>◈ %s</p>%s' % (g, ''.join('<input type=radio name=q id=%s%s><label for=%s>%s</label>' % (q, ' checked' if q == 'q1' else '', q, lab)
                  for q, lab, _, _ in its)) for g, its in GROUPS)
    html = ('<div class=hw><div class=hv><div class=zc><b class=zg><i></i></b><u></u></div><div class=mb><b class=pn></b><div class=mi>' + maps +
            '</div></div><h4 class=hd></h4><div class=tr><i></i><b></b></div><div class=fs>' + floors + '</div></div>'
            '<div class=hl><b>✦ Карта звёздного пути ›</b>' + lst + '</div></div>')
    return '<div class=srm><style>' + css + '</style>' + html + '</div>'

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
