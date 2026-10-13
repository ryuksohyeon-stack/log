"""Builds widget 16 (kremlin colours, Star Rail UI) as two pieces for luvlog:

  ../star-rail-map.css   the design: paste once into the home's 꾸미기 CSS (in every mode)
  ../star-rail-map.html  the widget: maps, list, floors and banner pins, under 10,000 chars

python3 widget16.py <7-char commit sha holding k/>   -> writes both, maps from jsDelivr
python3 widget16.py --local <out.html>                -> one preview page using ../k/ on disk

The CSS lives in 꾸미기 CSS so the widget's 10,000 characters go to banners (each pin is
about 300 characters with its image link). The CSS only changes when the design or the maps
change; adding a banner changes only the widget. Maps come from k/ (maps/kremlin with the
markers drawn in by bake.py). Edit GROUPS, FLOORS and PINS below; everything else follows."""
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
    ('보금자리', [('q4', '센가물', '보금자리 · 센가물', 'ma'),
               ('q5', '현대물', '보금자리 · 현대물', 'mo'),
               ('q6', '바다', '보금자리 · 바다', 'mq'),
               ('q7', '폐도시', '보금자리 · 폐도시', 'mr')]),
]
# map boxes: floors as (map file, floor label), top floor first as the floor buttons stack;
# the floor labelled '1' is shown first. One floor means no floor buttons. Box names must
# differ from file names: each floor's layer carries its file name as a class.
FLOORS = {'mn': [('n1', '1'), ('n2', 'B1')], 'mm': [('m1', '1'), ('m2', 'B1')], 'ma': [('s1', '')],
          'mo': [('o2', '2'), ('s2', '1')], 'mq': [('s3', '')], 'mr': [('r1', '1'), ('r2', 'B1')]}
PAIRS = {'n1', 'n2'}  # hold the white-night map on the left and the polar-night map on the right
HOST = 'vasilic'    # the luvlog home this widget sits on
# banner pins: map file -> (mark, x, y in the 1280x1000 map, luvlog handle, caption)
# The pin is an invisible tap area over a marker drawn into the map (widget.MARKERS, bake.py):
# 'APT' the apartment block, '1' to '9' the white numerals (numbers start at 1 on each map).
# Keep x, y on whole percents (x a multiple of 12.8, y of 10) and the same as the marker's, so
# the red-orange copy from on.svg lands on the drawn marker. Tapping a pin turns its marker
# red-orange and opens the banner beside it, on that floor only: to the left for a pin on the
# left half of the map, else to the right; the map pans so the whole banner is in view. The
# banner links to luvlog.me/<handle>. When the widget is built, luvlog's public record for
# that home gives its banner image, and whether its banner list carries HOST back (맞배너).
# Re-run the build to pick up changed banners.
PINS = {'n1': [('APT', 128, 700, 'milan', '404호')],      # the panel block at Norilsk's south-west corner
        's1': [('1', 243.2, 360, 'karma', ''),            # the west hall
               ('2', 729.6, 200, 'meltaway', '')],        # beside the north gate
        's2': [('1', 128, 760, 'aiden', ''),              # the L-shaped block
               ('2', 742.4, 960, '915', ''),             # in front of the sandwich shop
               ('3', 384, 130, 'chajaehyeon', ''),        # the concert hall's stage
               ('4', 422.4, 260, 'koyubin', '')],         # the concert hall's seats
        'o2': [('1', 1164.8, 190, '574839', '')],         # the seat between the head and the 대리
        's3': [('1', 1139, 500, 'legion', ''),            # the ship's bow
               ('2', 281.6, 370, 'stray', ''),            # the deck by the lifeboats
               ('3', 192, 590, 'johann', '')],            # by the helipad
        'r1': [('1', 384, 400, 'pixelatedkisses', ''),    # the round plaza
               ('2', 665.6, 100, 'raymond', '')],         # the crane yard
        'r2': [('1', 486.4, 400, 'woojaegyeong', '')]}    # the platform
# extra colours per list entry: polar night is dark, the abandoned town ash grey
EXTRA = {'q1': ';--F:#161c2e;--V:#0c1222;background:#0f1424', 'q7': ';--F:#d6d2ce;--V:#b7c0c6'}

# The design, for 꾸미기 CSS. It is page-wide there, so every rule starts at .srm (the root
# class is .srm because luvlog's page CSS styles .hm) and keyframes are named srm-*.
# Panning: .pn is an invisible scroller over the map; its scroll progress moves the map (.mi)
# from 25% past one edge to 25% past the other, so the map's apron (bake.py, kit.EX/EY) can
# be dragged into view. On phones the scroller is as long as the map's travel, so the map
# follows the finger. Zoom (desktop) is the registered --z, 0..1, from the zoom bar.
# An open banner moves the view to itself once: from the map's focus --fx, --fy, --fs (see
# SNAPS) .pn works out --sx, --sy, the scroll that centres the pin and its banner, and puts
# its snap lines there (:before across, :after down: one per axis, each running the scroller's
# whole length, so Chrome always counts it as in view); ticking the pin starts a short
# animation that switches snapping on, so the scroller jumps there, and then lets go, so the
# map can still be dragged. Without scroll-driven animations (older Safari, Firefox) the
# map does not pan; the focus then shifts it statically (--f, --g) so the banner is in view.
CSS = '''
@property --z{syntax:"<number>";inherits:true;initial-value:0}
.srm{container-type:inline-size;word-break:keep-all}.srm *{margin:0;box-sizing:border-box}.srm input{display:none}
.srm .hw{counter-reset:pt px;position:relative;overflow:clip;font-size:clamp(9px,1.2cqi,14px);--F:#dcc7c8;--V:#bccad8;--v:77cqi;--vh:66.67cqi;--r:.8658;--k:1;--bw:13em;background:#efe5e5;color:#2a1416}
{NAMES}
.srm .hv{position:relative;aspect-ratio:3/2}
.srm .mb{position:absolute;inset:0 23% 0 0;overflow:clip;--kz:calc(var(--k)*(1 + 2*var(--z,0)));--fx:{FX};--fy:{FY};--fs:{FS}}
.srm .mi{position:relative;width:calc(var(--v)*var(--k)*(1 + 2*var(--z,0)));aspect-ratio:1.28;translate:var(--f);transform:translateY(var(--g,max(0px,var(--vh)/2 - 50%)));--f:clamp(2.6% + var(--bw) + 2em - var(--fx)*100% - (1 + var(--fs))*1e4px,clamp(var(--v) - 125%,var(--v)/2 - var(--fx)*100%,25%),var(--v) - 2.6% - var(--bw) - 2em - var(--fx)*100% + (1 - var(--fs))*1e4px);--g:clamp(3.6em - var(--fy)*100%,clamp(var(--vh) - 125%,var(--vh)/2 - var(--fy)*100%,25%),var(--vh) - 3.6em - var(--fy)*100%)}
.srm .mb,.srm .mi{background:var(--F)}
.srm:has(.A:checked):has(#n1:checked) .mb{background:linear-gradient(var(--F) 50%,var(--V) 0)}.srm:has(#q6:checked) .mb{background:var(--V)}
.srm .mi>div,.srm .fs p{position:absolute;inset:0;display:none}
{SHOW}{display:grid}
.srm .z{position:absolute;inset:0;--o:0;z-index:var(--o);opacity:max(.13,var(--o));transition:opacity .4s;pointer-events:none}
.srm .z:before{content:"";position:absolute;inset:-25%;background:var(--m) 0 0/100% 100% no-repeat}
{ACTIVE}{--o:1;--d:block}
{MAPS}
{PAIRS}{background-size:200% 100%}.srm:has(#q1:checked) .z:before{background-position:100% 0}
.srm .p{position:absolute;left:var(--x);top:var(--y);width:4%;aspect-ratio:1;translate:-50% -50%;z-index:3;display:var(--d,none);pointer-events:auto;cursor:pointer;counter-increment:pt}.srm .p.x{counter-increment:pt px}
.srm .p:before{content:"";position:absolute;inset:-.5em}
.srm .p:has(:checked){background:url({BASE}on.svg) 0/1000%}
{PICKED}
.srm .p a{display:none;position:absolute;left:calc(50% + var(--s)*(50% + .6em));top:50%;translate:calc(var(--s)*50% - 50%) -50%;padding:.2em;border-radius:.3em;background:#fff;box-shadow:0 .2em .6em #0006}
.srm .p :checked+a{display:block}.srm .p img{display:block;max-width:var(--bw)}.srm .p b{display:block;padding:.1em .3em .25em;font-size:.75em;color:#555}
.srm .hd:after{content:var(--nm)}.srm .tr b:after{content:counter(px) " / " counter(pt)}
.srm .hl{position:absolute;top:4%;right:1.5%;width:20%;z-index:5}
.srm .hl>b{display:block;margin-bottom:.9em;padding:.5em .9em;white-space:nowrap;overflow:clip;text-overflow:ellipsis;border-radius:2em;background:#3a3a3a;color:#eee;font-weight:500}
.srm .hl p{padding:.3em .8em;background:#c4c4c4;color:#555;font-size:.85em}
.srm .hl label{display:block;padding:.75em 1em;border-bottom:1px solid #ddd;background:#f4f4f4;color:#333}
.srm .hl label:before{content:"✦ ";font-size:.7em}
.srm .hl :has(>:checked){background:#1d1d1d;color:#fff}
.srm .hl :has(>:checked):after{content:"▼";float:right;color:#36d2e6;font-size:.75em}
.srm .fs{position:absolute;left:2.5%;bottom:5%;z-index:4;width:3.8em;height:14em}
.srm .fs p{top:auto;gap:.1em;padding:.25em;border-radius:2em;background:#3a3a3ab8}
.srm .fs label{position:relative;padding:.75em 0 .45em;border-radius:2em;color:#f2f2f2;font-size:.85em;line-height:1.15;text-align:center}
.srm .fs label:before{content:"Этаж";display:block;font-size:.8em}
.srm .fs :has(>:checked){background:#fff;color:#333}
.srm .fs :has(>:checked):after{content:"▼";position:absolute;inset:-.1em 0 auto;color:#36c6e0;font-size:.6em}
.srm .hd{position:absolute;left:2.5%;top:3.5%;z-index:4;padding-left:1.5em;background:radial-gradient(circle at .5em .6em,#0000 .13em,#222 .15em .4em,#0000 .42em),conic-gradient(from -30deg at 50% 100%,#222 60deg,#0000 0) .1em .8em/.8em .6em no-repeat;color:#555;font-size:1.15em;font-weight:500}
.srm .hd:before{content:"Навигация";display:block;color:#222;font-size:.62em;font-weight:700}
.srm .tr{position:absolute;left:2.5%;top:calc(3.5% + 3.3em);z-index:4;display:flex;align-items:center;gap:.6em;padding:.35em .8em .35em 1em;border-radius:2em;background:#2b2b2bd9;color:#eee}
.srm .tr i{width:1.4em;height:1.1em;border-radius:.4em .4em .1em .1em;background:linear-gradient(90deg,#0000 40%,#fbe3a0 0 60%,#0000 0) 0 40%/100% 30% no-repeat,linear-gradient(#0000 42%,#6b3f14 0 54%,#0000 0),#e3b04f}
.srm .tr:after{content:"▾";margin-left:1.6em}
.srm .hd,.srm .tr,.srm .fs{pointer-events:none}.srm .fs label{pointer-events:auto}
.srm .pn,.srm .zc{display:none}
@supports (timeline-scope:none){
.srm .hw{timeline-scope:--tx,--ty,--zt;animation:srm-z linear both;animation-timeline:--zt}
.srm .pn,.srm .zg{position:absolute;inset:0;overflow:scroll;scrollbar-width:none;overscroll-behavior:contain}
.srm .pn{display:block;touch-action:pan-x pan-y;scroll-timeline:--tx x,--ty y;animation:{SLOTS};--cw:calc(2*var(--v));--ch:calc(2*var(--vh));--sx:clamp(0px,(var(--v)*(var(--kz)*(.25 + var(--fx) + .02*var(--fs)) - .5) + (var(--bw)/2 + .8em)*var(--fs))/(var(--kz)*1.5 - 1),var(--v));--sy:clamp(0px,var(--r)*var(--v)*(var(--kz)*(.25 + var(--fy))/1.28 - var(--r)/2)/(var(--kz)*1.5/1.28 - var(--r)),var(--vh))}
.srm .pn:before,.srm .pn:after{content:"";position:absolute;left:0;top:0;width:1px;height:1px}
.srm .pn:before{left:calc(var(--sx) + var(--v)/2);height:var(--ch);scroll-snap-align:none center}
.srm .pn:after{top:calc(var(--sy) + var(--vh)/2);width:var(--cw);scroll-snap-align:center none}
.srm .mi{pointer-events:none;animation:srm-tx linear both,srm-ty linear both;animation-timeline:--tx,--ty}
.srm .zc{display:grid;align-content:space-between;justify-items:center;position:absolute;right:1.5%;bottom:4%;z-index:4;width:2.2em;height:9em;border:1px solid #8c1724;background:linear-gradient(#d9b3b7 0 0) 50%/1px 60% no-repeat #fff;color:#8c1724;font-weight:700}
.srm .zc:before{content:"+"}.srm .zc:after{content:"−"}
.srm .zg{touch-action:pan-y;scroll-timeline:--zt y;animation:srm-k1 .6s}
.srm .zg i{display:block;height:400%}
.srm .zc u{position:absolute;left:50%;top:calc(100% - 2.1em);padding:.3em;margin:-.3em;rotate:45deg;background:#8c1724;pointer-events:none;animation:srm-zk linear both;animation-timeline:--zt}
}
{SNAPS}
@keyframes srm-k1{from,to{scroll-snap-type:both mandatory}}
@keyframes srm-z{to{--z:1}}
@keyframes srm-tx{from{translate:25%}to{translate:calc(var(--v) - 125%)}}
@keyframes srm-ty{from{transform:translateY(25%)}to{transform:translateY(calc(var(--vh) - 125%))}}
@keyframes srm-zk{to{top:2.1em}}
.srm:has(#q1:checked) .hd,.srm:has(#q1:checked) .zc{filter:invert(1) hue-rotate(180deg)}
@container (max-width:560px){
.srm .hw{--v:100cqi;--vh:calc(100cqi/1.28);--bw:11em}
.srm .hv{aspect-ratio:1.28}.srm .mb{inset:0}.srm .zc{display:none}
.srm .hv .tr{top:calc(3.5% + 1em);left:auto;right:2.5%}
.srm .hl{position:static;width:auto;padding:.6em 0}}
@supports (timeline-scope:none){@container (max-width:560px){
.srm .hw{--k:1.28;--vh:100cqi}.srm .hv{aspect-ratio:1}
.srm .pn{--cw:calc(1.5*var(--k)*var(--v));--ch:calc(1.5*var(--k)*var(--v)/1.28);--sx:clamp(0px,var(--v)*(var(--k)*(.25 + var(--fx) + .02*var(--fs)) - .5) + (var(--bw)/2 + .8em)*var(--fs),var(--v)*(1.5*var(--k) - 1));--sy:clamp(0px,var(--v)*var(--k)*(.25 + var(--fy))/1.28 - var(--vh)/2,var(--v)*var(--k)*1.5/1.28 - var(--vh))}}}
'''
# Pins b1..b40. The widget sets --xN, --yN, --sN (the pin's place and banner side) on .mb while
# pin N is open and its floor shown. The map's focus --fx, --fy, --fs is the highest-numbered
# such pin, else the view's default (DEFAULT_FOCUS, else the middle); the static fallback uses it.
# Each pin also has its own animation slot on .pn: ticking it starts that slot, which switches
# snapping on for .6s with the focus set to that pin, so the newest open banner wins.
NPIN = 40
def chain(v, last):
    for n in range(1, NPIN + 1): last = 'var(--%s%d,%s)' % (v, n, last)
    return last
SLOTS = 'srm-k1 .6s,var(--sv,srm-x) .6s,' + ','.join('var(--a%d,srm-x) .6s' % n for n in range(1, NPIN + 1))
SNAPS = ('\n'.join('.srm:has(#b%d:checked) .pn{--a%d:srm-s%d}' % (n, n, n) for n in range(1, NPIN + 1)) + '\n' +
         '\n'.join('@keyframes srm-s%d{from,to{scroll-snap-type:both mandatory;--fx:var(--x%d);--fy:var(--y%d);--fs:var(--s%d)}}' % (n, n, n, n) for n in range(1, NPIN + 1)))
# where a view opens when no banner is open (map fractions of the 1280x1000 core); others: the middle
DEFAULT_FOCUS = {'o2': (.75, .23)}    # the company floor: its office block in the north-east

BANNERS = {}
PIN_IDS = {}

def build(base):
    """(css for 꾸미기 CSS, widget html)"""
    items = [it for _, its in GROUPS for it in its]
    boxes = list(dict.fromkeys(it[3] for it in items))
    files = [f for b in boxes for f, _ in FLOORS[b]]
    assert not set(boxes) & set(files), 'box and file names must differ'
    qs = lambda box: [it[0] for it in items if it[3] == box]
    names = ''.join('.srm:has(#%s:checked) .hw{--nm:"%s"%s}' % (q, t, EXTRA.get(q, '')) for q, _, t, _ in items)
    # a box shown for several list entries (Norilsk: polar night, white night) gets a class on
    # those radios, so one :has(.A:checked) stands for all of them
    grp = {b: 'ABCDEFG'[k] for k, b in enumerate(b for b in boxes if len(qs(b)) > 1)}
    reg = lambda b: ':has(%s:checked)' % ('.' + grp[b] if b in grp else '#' + qs(b)[0])
    show = ['.srm%s .%s' % (reg(b), b) for b in boxes]
    active = ['.srm:has(#%s:checked) .%s' % (f, f) if len(FLOORS[b]) > 1 else '.srm .' + f for b in boxes for f, _ in FLOORS[b]]
    maps = ''.join('.srm .%s{--m:url(%s%s.svg)}' % (f, base, f) for f in files)
    # switching to another map or floor restarts its own snap slot: the view goes to the open
    # banner there, else to the view's default
    view = lambda b, f: '.srm%s%s' % (reg(b), ':has(#%s:checked)' % f if len(FLOORS[b]) > 1 else '')
    views = ('\n' + ''.join('%s .pn{--sv:srm-v%s}' % (view(b, f), f) for b in boxes for f, _ in FLOORS[b]) +
             ''.join('%s .mb{--dx:%g;--dy:%g}' % (view(b, f), *DEFAULT_FOCUS[f]) for b in boxes for f, _ in FLOORS[b] if f in DEFAULT_FOCUS) +
             '\n' +
             '\n'.join('@keyframes srm-v%s{from,to{scroll-snap-type:both mandatory}}' % f for f in files))
    picked = ''.join('.srm .c%d:has(:checked){background-position:%.4g%%}' % (k, k / .09) for k in range(1, 10))
    css = (CSS.replace('{NAMES}', names).replace('{SHOW}', ','.join(show)).replace('{ACTIVE}', ','.join(active))
           .replace('{MAPS}', maps).replace('{PAIRS}', ','.join('.srm .%s:before' % f for f in sorted(PAIRS))).replace('{PICKED}', picked)
           .replace('{SNAPS}', SNAPS + views).replace('{SLOTS}', SLOTS).replace('{FX}', chain('x', 'var(--dx,.5)'))
           .replace('{FY}', chain('y', 'var(--dy,.5)')).replace('{FS}', chain('s', '0')).replace('{BASE}', base).strip())   # one rule group per line: easier to find in 꾸미기 CSS

    focus = ''     # per open banner, only while its floor is shown: its --xN, --yN, --sN (see SNAPS)
    def pins(b, f):
        nonlocal focus
        o = ''
        for mark, x, y, h, cap in PINS.get(f, []):
            n = PIN_IDS.setdefault((f, mark, x, y), len(PIN_IDS) + 1)
            assert n <= NPIN, 'more than %d pins: raise NPIN' % NPIN
            px, py, side = round(x / 12.8), round(y / 10), 1 if x >= 640 else -1
            if h not in BANNERS: BANNERS[h] = luvlog(h); print('@%s: banner %s, 맞배너 %s' % (h, 'found' if BANNERS[h][0] else 'missing', BANNERS[h][1]))
            img, ex = BANNERS[h]; img = (img or base + 'b1.svg').replace('https://', '//')
            cls = ' '.join(['p'] + ['c' + mark] * (mark != 'APT') + ['x'] * ex)
            o += ('<label class=%s style=--x:%d%%;--y:%d%%;--s:%d><input type=checkbox id=b%d><a href=//luvlog.me/%s>%s<img src=%s></a></label>'
                  % ('"%s"' % cls if ' ' in cls else cls, px, py, side, n, h, '<b>%s</b>' % cap if cap else '', img))
            g = lambda v: ('%g' % v).replace('0.', '.', 1) if 0 < v < 1 else '%g' % v
            focus += '%s%s:has(#b%d:checked) .mb{--x%d:%s;--y%d:%s;--s%d:%d}' % (reg(b), ':has(#%s:checked)' % f if len(FLOORS[b]) > 1 else '', n, n, g(px / 100), n, g(py / 100), n, side)
        return o
    layers = ''.join('<div class=%s>%s</div>' % (b, ''.join('<div class="z %s">%s</div>' % (f, pins(b, f)) for f, _ in FLOORS[b])) for b in boxes)
    first = lambda b: next((f for f, lab in FLOORS[b] if lab == '1'), FLOORS[b][0][0])
    floors = ''.join('<p class=%s>%s</p>' % (b, ''.join('<label><input type=radio name=%s id=%s%s>%s</label>' % (b, f, ' checked' if f == first(b) else '', lab)
                     for f, lab in FLOORS[b])) for b in boxes if len(FLOORS[b]) > 1)
    lst = ''.join('<p>◈ %s</p>%s' % (g, ''.join('<label><input type=radio name=q id=%s%s%s>%s</label>' % (
                  q, ' class=' + grp[b] if b in grp else '', ' checked' if q == 'q1' else '', lab) for q, lab, _, b in its)) for g, its in GROUPS)
    html = ('<div class=hw><div class=hv><div class=zc><b class=zg><i></i></b><u></u></div><div class=mb><b class=pn></b><div class=mi>' + layers +
            '</div></div><b class=hd></b><div class=tr><i></i><b></b></div><div class=fs>' + floors + '</div></div>'
            '<div class=hl><b>✦ Карта звёздного пути ›</b>' + lst + '</div></div>')
    widget = '<div class=srm>' + ('<style>' + focus + '</style>' if focus else '') + html + '</div>'
    return css, widget

CSS_HEAD = '/* ▼ star rail map (스타레일 지도 위젯) ▼ */\n'
CSS_TAIL = '\n/* ▲ star rail map ▲ */'

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    if sys.argv[1] == '--local':
        css, out = build(os.path.join(here, '..', 'k') + '/')
        open(sys.argv[2], 'w', encoding='utf-8').write('<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width">'
            '<style>' + css + '</style><body style="margin:0;padding:24px;background:#f4f4f6"><div style="max-width:1000px;margin:auto">' + out + '</div>')
    else:
        css, out = build('//cdn.jsdelivr.net/gh/ryuksohyeon-stack/log@%s/k/' % sys.argv[1])
        open(os.path.join(here, '..', 'star-rail-map.html'), 'w', encoding='utf-8').write(out)
        open(os.path.join(here, '..', 'star-rail-map.css'), 'w', encoding='utf-8').write(CSS_HEAD + css + CSS_TAIL)
        print('css', len(CSS_HEAD + css + CSS_TAIL))
    print('chars', len(out))
