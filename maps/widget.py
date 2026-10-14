"""Builds ../star-rail-map.html, the luvlog widget that shows the maps.
Run: python3 widget.py <commit-sha-holding-the-svgs>   (or --local for a preview)

Markers are placed in map coordinates (1280 x 1000), the same canvas as
the SVGs. Class w = open only during the white nights, n = only during
the polar night; both apply to the Norilsk maps."""
import os, sys

CSS = '''
.hm{container-type:inline-size;font-family:Pretendard,sans-serif;word-break:keep-all}
.hm *{margin:0}
.hm input{display:none}
.hw{counter-reset:st sn sm ss;--k:sn;position:relative;overflow:hidden;font-size:clamp(9px,1.2cqi,14px);background:#d2d2d2;color:#333}
.hm:has(#q1:checked) .hw{--t:" · 극야"}.hm:has(#q2:checked) .hw{--t:" · 백야"}.hm:has(#q3:checked) .hw{--k:sm}.hm:has(#q4:checked) .hw{--k:ss}
.hv{position:relative;aspect-ratio:16/9}
.mb{position:absolute;inset:0 28% 0 0}
.mb:after{content:"";position:absolute;inset:0;z-index:3;pointer-events:none;box-shadow:inset 0 0 3em 2em #d2d2d2}
.mb>*{position:absolute;inset:0;visibility:hidden}
.hm:has(#q1:checked,#q2:checked) .mn,.hm:has(#q3:checked) .mm,.hm:has(#q4:checked) .ms{visibility:visible}
.z{position:absolute;inset:0;--o:0;pointer-events:none}
:checked+.z{--o:1;pointer-events:auto}
.z img{position:absolute;z-index:var(--o);width:100%;height:100%;opacity:max(.13,var(--o));transition:opacity .4s}
.z i{position:absolute;z-index:2;left:calc(var(--x)*1%);top:calc(var(--y)*1%);translate:-50% -50%;font:normal 1.55em/1 sans-serif;color:#0000;text-shadow:0 0 0 #f1cd84;opacity:var(--o);--g:drop-shadow(0 0 .06em #1a1a1a) drop-shadow(0 0 .06em #1a1a1a) drop-shadow(0 .08em .1em #0008);filter:var(--g)}
.hm:has(#q1:checked) .w,.hm:has(#q2:checked) .n{filter:grayscale(1) brightness(.75) var(--g)}
.mb h4{position:absolute;left:2.5%;top:3%;z-index:4;padding-left:1.3em;font-size:1.3em;background:radial-gradient(circle at .42em .75em,#333 .1em,#0000 .12em .22em,#333 .24em .36em,#0000 .38em) no-repeat}
.mb h4:before{content:"Навигация";display:block;font-size:.55em;font-weight:400;opacity:.6}
.mb h4:after{content:var(--t)}
.tr{position:absolute;left:2.5%;top:calc(3% + 3.4em);z-index:4;display:flex;gap:.5em;padding:.2em .8em;border-radius:2em;background:#222c;color:#eee}
.tr i{width:1.5em;border-radius:.4em .4em .1em .1em;background:linear-gradient(#0000 40%,#6b3f14 0 52%,#0000 0),#dca444}
.tr b:after{content:counter(var(--k)) " / " counter(st)}.tr:after{content:"▾";opacity:.6}
.mn{--n:sn}.mm{--n:sm}.ms{--n:ss}.p{counter-increment:st var(--n)}
.z label{position:absolute;left:2.5%;bottom:calc(6% + var(--f,0)*2.8em);z-index:4;min-width:3.4em;padding:.3em;border-radius:1.4em;background:#fff6;color:#444;font-size:.9em;line-height:1.2;text-align:center;pointer-events:auto;cursor:pointer}
.z label:before{content:"Этаж";display:block;font-size:.7em}
:checked+.z label{background:#fafafa;color:#222;box-shadow:0 .1em .4em #0002}
:checked+.z label:after{content:"";position:absolute;left:50%;top:-.5em;margin-left:-.3em;border:.3em solid #0000;border-top:.4em solid #3cc8e0;border-bottom:0}
.zs{position:absolute;left:36%;bottom:3%;z-index:4;translate:-50%;display:flex;justify-content:space-between;align-items:center;width:23%;padding:.15em .3em;border-radius:1em;background:radial-gradient(circle,#fff .25em,#f39a33 .3em .42em,#0000 .46em) 34% 50%/1em 1em no-repeat,linear-gradient(90deg,#f39a33 34%,#888 0) 50%/calc(100% - 3.4em) .18em no-repeat,#2b2b2bdd;color:#fff;font-size:.9em}
.zs:before,.zs:after{content:"−";display:grid;place-items:center;width:1.2em;height:1.2em;border:.1em solid #fff;border-radius:50%;line-height:1}.zs:after{content:"+"}
.hl{position:absolute;top:4%;right:1.5%;width:25.5%;z-index:5}
.hl>b{display:block;margin-bottom:.9em;padding:.5em 1.1em;border-radius:2em;background:#3a3a3a;color:#eee;font-weight:500}
.hl p{padding:.3em .8em;background:#c4c4c4;color:#555;font-size:.85em}
.hl label{display:block;padding:.75em 1em;border-bottom:1px solid #ddd;background:#f4f4f4;color:#333;cursor:pointer}
.hl label:before{content:"✦ ";font-size:.7em}
.hl :checked+label{background:#1d1d1d;color:#fff}
.hl :checked+label:after{content:"▼";float:right;color:#36d2e6;font-size:.75em}
@container (max-width:560px){.hv{aspect-ratio:1.28}.mb{right:0}.zs{left:50%}.hl{position:static;width:auto;padding:.6em}}
'''

# (emoji, x, y[, class]) in map coordinates
MARKERS = {
    'n1': [('🍺', 668, 640), ('🔧', 130, 310), ('💊', 870, 600), ('🛒', 1120, 700),
           ('☕', 630, 345, 'w'), ('🌷', 870, 345, 'w'), ('📚', 620, 140, 'w'), ('🥐', 1125, 140, 'w'),
           ('🎬', 410, 345, 'w'), ('🔭', 900, 935, 'n'), ('APT', 128, 700)],
    'n2': [('🍲', 250, 340), ('🧖', 1050, 640)],
    'm1': [('🛍', 742, 290), ('🍦', 742, 510), ('🎭', 765, 105), ('☕', 940, 310), ('🍺', 985, 510),
           ('🥐', 1135, 510), ('🌷', 470, 185)],
    'm2': [('📰', 80, 420), ('🌭', 1200, 700)],
    's1': [('🏛', 640, 190), ('⚡', 185, 425), ('🏚', 1060, 420), ('#1', 243.2, 360), ('#2', 729.6, 200), ('#3', 768, 450)],
    's2': [('🏢', 950, 210), ('🏫', 165, 700), ('🏪', 720, 595), ('PNO', 295, 112), ('SDW', 735, 905), ('CIN', 1115, 852), ('GTE', 595, 470),
           ('#1', 128, 760), ('#2', 742.4, 960), ('#3', 384, 130), ('#4', 422.4, 260), ('#5', 435.2, 580),
           ('#6', 1075.2, 920), ('#7', 652.8, 460), ('#8', 601.6, 390)],
    'o2': [('🏢', 955, 200), ('#1', 1164.8, 190)],
    's3': [('🧭', 555, 495), ('🍳', 340, 495), ('🛏', 470, 575), ('#1', 1139, 500), ('#2', 281.6, 370), ('#3', 192, 590), ('#4', 985.6, 410)],
    'r1': [('📻', 570, 110), ('🔥', 715, 720), ('🏚', 880, 310), ('🚂', 620, 912), ('⚠️', 1095, 520), ('#1', 384, 400), ('#2', 665.6, 100)],
    'r2': [('🚆', 640, 470), ('🕯', 210, 240), ('🥫', 210, 860), ('🔦', 880, 790), ('#1', 780.8, 690), ('#12', 627.2, 690), ('#13', 947.2, 690)],
}

def floors(name, base, layers):
    """layers: (id, map key, floor label, stack position from the bottom)"""
    o = ''
    for k, (fid, key, lab, f) in enumerate(layers):
        mk = ''.join('<i%s style=--x:%d;--y:%d>%s</i>' % (' class=' + m[3] if len(m) > 3 else '', round(m[1] / 12.8), round(m[2] / 10), m[0])
                     for m in MARKERS[key])
        o += '<input type=radio name=%s id=%s%s><div class=z><img src=%s%s.svg>%s<label for=%s%s>%s</label></div>' % (
            name, fid, ' checked' if k == 0 else '', base, key, mk, fid, ' style=--f:%d' % f if f else '', lab)
    return o

def build(base):
    html = ('<div class=hw><div class=hv><div class=mb>'
        '<div class=mn>' + floors('n', base, [('n1', 'n1', '1', 1), ('n2', 'n2', 'B1', 0)]) + '<h4>노릴스크</h4></div>'
        '<div class=mm>' + floors('m', base, [('m1', 'm1', '1', 1), ('m2', 'm2', 'B1', 0)]) + '<h4>모스크바</h4></div>'
        '<div class=ms>' + floors('s', base, [('s1', 's1', '센가물', 2), ('s2', 's2', '현대물', 1), ('s3', 's3', '바다', 0)]) + '<h4>보금자리</h4></div>'
        '</div><div class=tr><i></i><b></b></div><div class=zs></div></div>'
        '<div class=hl><b>✦ Карта звёздного пути ›</b><p>◈ 러시아</p>'
        '<input type=radio name=q id=q1 checked><label for=q1>노릴스크의 극야</label>'
        '<input type=radio name=q id=q2><label for=q2>노릴스크의 백야</label>'
        '<input type=radio name=q id=q3><label for=q3>모스크바의 거리</label><p>◈ 보금자리</p>'
        '<input type=radio name=q id=q4><label for=q4>소중한 이들과 만남</label></div></div>')
    return '<div class=hm><style>' + CSS.replace('\n', '') + '</style>' + html + '</div>'

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    if sys.argv[1] == '--local':
        out = build('file://' + here + '/')
        open(sys.argv[2], 'w', encoding='utf-8').write(
            '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width">'
            '<body style="margin:0;padding:24px;background:#eee"><div style="max-width:1000px;margin:auto">' + out + '</div>')
    else:
        out = build('https://cdn.jsdelivr.net/gh/ryuksohyeon-stack/log@%s/maps/' % sys.argv[1])
        open(os.path.join(here, '..', 'star-rail-map.html'), 'w', encoding='utf-8').write(out + '\n')
    print('chars', len(out))
