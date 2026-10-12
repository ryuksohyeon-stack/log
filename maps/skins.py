"""Draft widgets: one markup (regions, floors, real zoom, treasure counter,
markers) dressed in three different skins for the white-night / travel /
Russia concept.

python3 skins.py <skin> <image-base> <out.html>
  skin: journal | transit | hud
  image-base: URL prefix the maps are loaded from (ends with '/')
"""
import os, sys
from widget import MARKERS

# ---------------------------------------------------------------- shared --
BASE = '''
.hm{container-type:inline-size;word-break:keep-all}
.hm *{margin:0;box-sizing:border-box}
.hm input{display:none}
.hw{counter-reset:st sn sm ss;--k:sn;--zm:1;--zi:0;position:relative;overflow:hidden;font-size:clamp(9px,1.2cqi,14px)}
.hm:has(#q1:checked) .hw{--nm:"노릴스크 · 극야";--co:"69°20′N 88°12′E"}
.hm:has(#q2:checked) .hw{--nm:"노릴스크 · 백야";--co:"69°20′N 88°12′E"}
.hm:has(#q3:checked) .hw{--nm:"모스크바의 거리";--co:"55°45′N 37°37′E";--k:sm}
.hm:has(#q4:checked) .hw{--nm:"소중한 이들과 만남";--co:"ДОМ · 보금자리";--k:ss}
.hw:has(#z2:checked){--zm:1.5;--zi:1}.hw:has(#z3:checked){--zm:2;--zi:2}.hw:has(#z4:checked){--zm:3;--zi:3}
.hv{position:relative;aspect-ratio:16/9}
.mb{position:absolute;left:0;top:0;width:72%;aspect-ratio:1.28;overflow:auto;scrollbar-width:none;scroll-snap-type:both proximity}
.mb::-webkit-scrollbar{display:none}
.mi{position:relative;width:calc(var(--zm)*100%);aspect-ratio:1.28;transition:width .35s}
.mi:after{content:"";position:absolute;left:50%;top:50%;width:1px;height:1px;scroll-snap-align:center}
.mi>div,.fs p{position:absolute;inset:0;visibility:hidden}
.hm:has(#q1:checked,#q2:checked) :is(.mn,.fn),.hm:has(#q3:checked) :is(.mm,.fm),.hm:has(#q4:checked) :is(.ms,.fx){visibility:visible}
.z{position:absolute;inset:0;--o:0;pointer-events:none}
.hw:has(#n1:checked) .mn>:nth-child(1),.hw:has(#n2:checked) .mn>:nth-child(2),.hw:has(#m1:checked) .mm>:nth-child(1),.hw:has(#m2:checked) .mm>:nth-child(2),.hw:has(#s1:checked) .ms>:nth-child(1),.hw:has(#s2:checked) .ms>:nth-child(2),.hw:has(#s3:checked) .ms>:nth-child(3){--o:1;pointer-events:auto}
.z img{position:absolute;z-index:var(--o);width:100%;height:100%;opacity:max(.13,var(--o));transition:opacity .4s}
.z i{position:absolute;z-index:2;left:calc(var(--x)*1%);top:calc(var(--y)*1%);translate:-50% -50%;font:normal 1.55em/1 sans-serif;color:#0000;text-shadow:0 0 0 #f1cd84;opacity:var(--o);--g:drop-shadow(0 0 .06em #1a1a1a) drop-shadow(0 0 .06em #1a1a1a) drop-shadow(0 .08em .1em #0008);filter:var(--g)}
.hm:has(#q1:checked) .w,.hm:has(#q2:checked) .n{filter:grayscale(1) brightness(.75) var(--g)}
.mn{--n:sn}.mm{--n:sm}.ms{--n:ss}.p{counter-increment:st var(--n)}
.hd:after{content:var(--nm)}
.tr b:after{content:counter(var(--k)) " / " counter(st)}
.fs label,.zc label,.hl label{cursor:pointer}
.zm label,.zp label{display:none}
.hw:has(#z2:checked) .zm [for=z1],.hw:has(#z3:checked) .zm [for=z2],.hw:has(#z4:checked) .zm [for=z3],.hw:has(#z1:checked) .zp [for=z2],.hw:has(#z2:checked) .zp [for=z3],.hw:has(#z3:checked) .zp [for=z4]{display:grid}
.zc b{position:relative;display:flex;justify-content:space-between}
.zc b:after{content:"";position:absolute;pointer-events:none;transition:.35s}
.hl{position:absolute;top:4%;right:1.5%;width:25.5%;z-index:5}
.hl>b{display:block;margin-bottom:.9em;padding:.5em 1.1em;border-radius:2em;background:#3a3a3a;color:#eee;font-weight:500}
.hl p{padding:.3em .8em;background:#c4c4c4;color:#555;font-size:.85em}
.hl label{display:block;padding:.75em 1em;border-bottom:1px solid #ddd;background:#f4f4f4;color:#333}
.hl label:before{content:"✦ ";font-size:.7em}
.hl :checked+label{background:#1d1d1d;color:#fff}
.hl :checked+label:after{content:"▼";float:right;color:#36d2e6;font-size:.75em}
'''
NARROW = '@container (max-width:560px){.hv{aspect-ratio:auto;height:calc(100cqi/1.28)}.mb{left:0;top:0;width:100%;translate:none}.hl{position:static;width:auto;padding:.6em}{SK}}'

# ---------------------------------------------------------------- skins --
SKINS = {}

# 1. Travel journal on a white night: pastel sky, photo-corner map, stamps,
#    luggage-tag floors, sticker markers (cosy life-sim UI x scrapbook).
SKINS['journal'] = dict(
    head='Дневник путешествий',
    css='''
.hw{background:linear-gradient(160deg,#dbe6f6,#ece4f3 50%,#f9e2e7);color:#2f3157;font-family:Pretendard,sans-serif}
.mb{left:2.5%;top:50%;width:66%;translate:0 -50%;border-radius:1em;background:#e8e5ef;box-shadow:0 0 0 .45em #fff,0 .8em 2em #6f62a040}
.hv:before,.hv:after{content:"";position:absolute;z-index:4;width:7em;height:1.6em;background:repeating-linear-gradient(90deg,#f3b9c8cc 0 .5em,#f7cdd8cc 0 1em);pointer-events:none}
.hv:before{left:.6%;top:3%;rotate:-32deg}.hv:after{left:63%;top:88%;rotate:-32deg;background:repeating-linear-gradient(90deg,#b9c3f0cc 0 .5em,#cdd4f6cc 0 1em)}
.hd{position:absolute;left:5%;top:7%;z-index:4;padding:.35em .8em;border:.14em solid #e07f98;border-radius:.4em;background:#fffd;color:#e07f98;font:700 1.15em Georgia,serif;rotate:-3deg}
.hd:before{content:var(--co);display:block;font:600 .55em Pretendard,sans-serif;letter-spacing:.12em}
.tr{position:absolute;left:5%;top:calc(7% + 4.6em);z-index:4;display:flex;align-items:center;gap:.4em;padding:.35em .8em .35em .4em;border:.12em dashed #c6bedc;border-radius:.3em;background:#fff;font-weight:700;rotate:2deg}
.tr i{display:grid;place-items:center;width:1.6em;height:1.6em;border:.12em solid #8a8db8;border-radius:50%;color:#8a8db8;font:normal .8em/1 Georgia}.tr i:before{content:"✦"}
.tr:after{content:"STAMPS";font-size:.6em;letter-spacing:.15em;color:#9a9cc0}
.fs{position:absolute;left:4.5%;bottom:8%;z-index:4;width:4em;height:7em}
.fs p{display:flex;flex-direction:column;justify-content:flex-end;gap:.35em}
.fs label{position:relative;padding:.3em .3em .3em 1em;border-radius:.3em .9em .9em .3em;background:#fff;box-shadow:0 .15em .4em #6f62a033;font-weight:700;text-align:center}
.fs label:before{content:"";position:absolute;left:.35em;top:50%;width:.35em;height:.35em;margin-top:-.175em;border-radius:50%;background:#d9d4e8}
.fs :checked+label{background:#e07f98;color:#fff;rotate:-4deg}
.zc{position:absolute;left:69.5%;top:50%;translate:-50% -50%;z-index:4;display:flex;flex-direction:column-reverse;align-items:center;gap:.4em;padding:.4em .3em;border-radius:2em;background:#fff;box-shadow:0 .2em .6em #6f62a033}
.zm,.zp{display:grid;place-items:center;width:1.8em;height:1.8em;border-radius:50%;background:#f1eff8;color:#c9c4dc;font-weight:700}
.zm:before{content:"−"}.zp:before{content:"+"}.zm:before,.zp:before{grid-area:1/1}
.zm label,.zp label{grid-area:1/1;place-items:center;width:1.8em;height:1.8em;border-radius:50%;background:#8a8db8;color:#fff}
.zc b{flex-direction:column-reverse;height:5.5em;align-items:center}
.zc b label{width:.5em;height:.5em;border-radius:50%;background:#d9d4e8}
.zc b:after{left:50%;bottom:calc(var(--zi)/3*(100% - .9em));width:.9em;height:.9em;margin-left:-.45em;border-radius:50%;background:#e07f98;box-shadow:0 0 0 .2em #f9d5df}
''',
    narrow='.mb{left:4%;top:4%;width:92%}.zc{left:auto;right:6%}.hv:after{display:none}')

# 2. Trans-Siberian departure board: transit-map crispness, split-flap board,
#    platform signs, a rail-track zoom (minimal metro sim x station signage).
SKINS['transit'] = dict(
    head='ОТПРАВЛЕНИЕ · 출발',
    css='''
.hw{background:#eef0f3;color:#22252b;font-family:Pretendard,sans-serif;border-top:.35em solid #d63a3a}
.mb{background:#e7e9ed}
.hv:after{content:"";position:absolute;left:72%;top:0;bottom:0;width:.15em;background:#d63a3a;z-index:4}
.hd{position:absolute;left:2.5%;top:3%;z-index:4;padding:.45em .9em .45em .8em;border-left:.35em solid #d63a3a;background:#fff;box-shadow:0 .15em .5em #0002;font-size:1.15em}
.hd:before{content:"МАРШРУТ · " var(--co);display:block;font-size:.55em;font-weight:500;letter-spacing:.1em;color:#8a909c}
.tr{position:absolute;left:2.5%;top:calc(3% + 4.4em);z-index:4;display:flex;align-items:center;gap:.5em;padding:.3em .9em .3em .5em;background:#fff;border:1px solid #d5d9df;font:700 .95em ui-monospace,Menlo,monospace;box-shadow:0 .15em .4em #0001}
.tr i{width:1.5em;height:1em;background:repeating-linear-gradient(90deg,#d63a3a 0 .18em,#fff 0 .3em)}
.tr:before{content:"БИЛЕТ";font-size:.65em;color:#8a909c;letter-spacing:.1em}
.fs{position:absolute;left:2.5%;bottom:6%;z-index:4;width:4.2em;height:8em}
.fs p{display:flex;flex-direction:column;justify-content:flex-end;gap:.3em}
.fs label{display:flex;align-items:center;gap:.3em;padding:.25em .4em;border-radius:.3em;background:#1f3c88;color:#fff;font-size:.85em;font-weight:700}
.fs label:before{content:"ПУТЬ";font-size:.6em;font-weight:500;opacity:.75}
.fs :checked+label{background:#ffd23f;color:#1f3c88}
.zc{position:absolute;left:36%;bottom:4%;translate:-50%;z-index:4;display:flex;align-items:center;gap:.5em;padding:.3em .5em;border-radius:.3em;background:#22252b;color:#fff}
.zm,.zp{display:grid;place-items:center;width:1.5em;height:1.5em;border:1px solid #555b66;border-radius:.2em;color:#555b66}
.zm:before{content:"−"}.zp:before{content:"+"}.zm:before,.zp:before{grid-area:1/1}
.zm label,.zp label{grid-area:1/1;place-items:center;width:1.5em;height:1.5em;border-radius:.2em;background:#d63a3a;color:#fff}
.zc b{width:9em;height:1em;align-items:center;background:linear-gradient(#9aa1ad 0 0) 0 30%/100% .12em no-repeat,linear-gradient(#9aa1ad 0 0) 0 70%/100% .12em no-repeat,repeating-linear-gradient(90deg,#555b66 0 .15em,#0000 0 .6em)}
.zc b label{width:.7em;height:.7em;border-radius:50%;border:.12em solid #9aa1ad;background:#22252b}
.zc b:after{top:50%;left:calc(var(--zi)/3*(100% - 1em));width:1em;height:1em;margin-top:-.5em;border-radius:50%;background:#d63a3a;box-shadow:0 0 0 .18em #fff}
''',
    narrow='.hv:after{display:none}.zc{left:50%}')

# 3. Polar expedition HUD: snowy map under dark glass panels, compass tape,
#    midnight-sun gauge, altitude-ladder floors (open-world slate x flight HUD).
SKINS['hud'] = dict(
    head='МАРШРУТЫ · 경로',
    css='''
.hw{background:#0d1520;color:#dff4ff;font-family:Pretendard,sans-serif}
.mb{background:#dbe4ec}
.hv:before{content:"СЗ        С        СВ        В        ЮВ";white-space:pre;position:absolute;left:14%;width:44%;top:2.5%;z-index:4;padding-bottom:.5em;text-align:center;font-size:.75em;letter-spacing:.1em;color:#0d1520;background:repeating-linear-gradient(90deg,#0d1520aa 0 1px,#0000 0 1.1em) bottom/100% .45em no-repeat;-webkit-mask:linear-gradient(90deg,#0000,#000 25%,#000 75%,#0000);mask:linear-gradient(90deg,#0000,#000 25%,#000 75%,#0000)}
.hv:after{content:"";position:absolute;left:0;top:0;width:72%;aspect-ratio:1.28;z-index:3;pointer-events:none;background:linear-gradient(#2fb4d8 0 0) 1em 1em/2em .15em,linear-gradient(#2fb4d8 0 0) 1em 1em/.15em 2em,linear-gradient(#2fb4d8 0 0) calc(100% - 1em) calc(100% - 1em)/2em .15em,linear-gradient(#2fb4d8 0 0) calc(100% - 1em) calc(100% - 1em)/.15em 2em;background-repeat:no-repeat;box-shadow:inset 0 0 4em #0d152066}
.hw:before{content:"☀ БЕЛАЯ НОЧЬ  23:47\\A ВЫСОТА СОЛНЦА +3°";white-space:pre;position:absolute;left:52%;top:4%;z-index:4;padding:.5em .8em;border:1px solid #2fb4d855;border-radius:.3em;background:#0d1520d9;font-size:.72em;letter-spacing:.08em;line-height:1.6;color:#9fe6ff}
.hd{position:absolute;left:2.5%;top:3%;z-index:4;padding:.5em .9em;border:1px solid #2fb4d855;border-radius:.3em;background:#0d1520d9;font-size:1.1em;letter-spacing:.04em}
.hd:before{content:"ЭКСПЕДИЦИЯ · " var(--co);display:block;font-size:.55em;letter-spacing:.14em;color:#2fb4d8}
.tr{position:absolute;left:2.5%;top:calc(3% + 4.4em);z-index:4;display:flex;align-items:center;gap:.5em;padding:.25em .8em .25em .5em;border:1px solid #2fb4d855;border-radius:.3em;background:#0d1520d9;font-weight:700}
.tr i{width:.8em;height:.8em;rotate:45deg;border:.14em solid #2fb4d8;box-shadow:0 0 .5em #2fb4d8}
.tr:before{content:"СИГНАЛ";order:1;font-size:.6em;letter-spacing:.14em;color:#2fb4d8}
.fs{position:absolute;left:2.5%;bottom:6%;z-index:4;width:3.6em;height:8em;padding:.3em;border:1px solid #2fb4d855;border-radius:.3em;background:#0d1520d9}
.fs p{display:flex;flex-direction:column;justify-content:flex-end;gap:.2em;padding:.3em;background:repeating-linear-gradient(#2fb4d833 0 1px,#0000 0 .6em) right/.4em 100% no-repeat}
.fs label{padding:.2em .3em;font-size:.85em;font-weight:700;color:#9fb4c6}
.fs :checked+label{color:#0d1520;background:#2fb4d8;border-radius:.2em;box-shadow:0 0 .6em #2fb4d8}
.zc{position:absolute;left:69.3%;top:50%;translate:-50% -50%;z-index:4;display:flex;flex-direction:column-reverse;align-items:center;gap:.4em;padding:.4em .3em;border:1px solid #2fb4d855;border-radius:.3em;background:#0d1520d9}
.zm,.zp{display:grid;place-items:center;width:1.5em;height:1.5em;color:#3b5368;font-weight:700}
.zm:before{content:"−"}.zp:before{content:"+"}.zm:before,.zp:before{grid-area:1/1}
.zm label,.zp label{grid-area:1/1;place-items:center;width:1.5em;height:1.5em;border:1px solid #2fb4d8;border-radius:.2em;color:#2fb4d8}
.zc b{flex-direction:column-reverse;height:5.5em;width:1.4em;align-items:center;background:repeating-linear-gradient(#2fb4d855 0 1px,#0000 0 .5em)}
.zc b label{width:1.4em;height:.3em}
.zc b:after{left:50%;bottom:calc(var(--zi)/3*(100% - .8em));width:.8em;height:.8em;margin-left:-.4em;rotate:45deg;background:#2fb4d8;box-shadow:0 0 .6em #2fb4d8}
''',
    narrow='.hv:after{width:100%}.hw:before{left:auto;right:3%}.zc{left:auto;right:4%;translate:0 -50%}')


# 4. Clean light map: white walkways on soft grey blocks, white cards with
#    one coral accent, segmented floor switch, map-app style zoom.
SKINS['clean'] = dict(
    head='МАРШРУТ · 여행지',
    css='''
.hw{background:#eef1f4;color:#1f2a37;font-family:Pretendard,sans-serif}
.mb{background:#e2e6eb}
.hd,.tr,.fs p,.zc{background:#fff;box-shadow:0 .2em .9em #1f2a3717}
.hd{position:absolute;left:2.5%;top:3.5%;z-index:4;padding:.55em .95em;border-radius:.7em;font-size:1.1em;font-weight:700}
.hd:before{content:var(--co);display:block;font-size:.58em;font-weight:500;color:#8a95a3}
.tr{position:absolute;left:2.5%;top:calc(3.5% + 4.3em);z-index:4;display:flex;align-items:center;gap:.45em;padding:.35em .85em;border-radius:2em;font-size:.9em;font-weight:700}
.tr i{width:.6em;height:.6em;border-radius:50%;background:#ef6f6c}
.fs{position:absolute;left:2.5%;bottom:5%;z-index:4;width:20em;height:2.4em}
.fs p{inset:auto auto 0 0;display:flex;align-items:center;gap:.15em;padding:.25em;border-radius:.7em}
.fs p:before{content:"ЭТАЖ";padding:0 .5em;font-size:.6em;color:#8a95a3}
.fs label{padding:.35em .75em;border-radius:.5em;font-size:.85em;font-weight:600;color:#5b6675}
.fs :checked+label{background:#1f2a37;color:#fff}
.zc{position:absolute;left:70%;bottom:5%;translate:-100%;z-index:4;display:flex;flex-direction:column-reverse;align-items:center;gap:.3em;padding:.3em;border-radius:.7em}
.zm,.zp{display:grid;place-items:center;width:1.8em;height:1.8em;color:#c3cad3;font-weight:700}
.zm:before{content:"−"}.zp:before{content:"+"}.zm:before,.zp:before{grid-area:1/1}
.zm label,.zp label{grid-area:1/1;place-items:center;width:1.8em;height:1.8em;border-radius:.45em;color:#1f2a37;background:#f1f3f6}
.zc b{flex-direction:column-reverse;align-items:center;height:4.6em}
.zc b label{width:.35em;height:.35em;border-radius:50%;background:#d3d9e0}
.zc b:after{left:50%;bottom:calc(var(--zi)/3*(100% - .7em));width:.7em;height:.7em;margin-left:-.35em;border-radius:50%;background:#ef6f6c}
''',
    narrow='.zc{left:auto;right:3%;translate:none}')

# 5. White-night glass: the sky's pastel gradient around a framed map,
#    frosted cards, lilac-to-rose accent on the chosen place.
SKINS['dusk'] = dict(
    head='БЕЛЫЕ НОЧИ · 백야 여행',
    css='''
.hw{background:linear-gradient(135deg,#d6e2f5,#e5ddf2 45%,#f6dde4 80%,#fae6dc);color:#2c2a4a;font-family:Pretendard,sans-serif}
.mb{left:2%;top:50%;width:68%;translate:0 -50%;border-radius:1.1em;background:#dcd7ea;box-shadow:0 1em 2.4em #5a4a8a30}
.hd,.tr,.fs p,.zc{background:#ffffff8c;border:1px solid #ffffffc0;-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px)}
.hd{position:absolute;left:4%;top:7%;z-index:4;padding:.55em .95em;border-radius:.8em;font-size:1.1em;font-weight:700}
.hd:before{content:var(--co);display:block;font-size:.58em;font-weight:500;letter-spacing:.06em;color:#7b76a3}
.tr{position:absolute;left:4%;top:calc(7% + 4.4em);z-index:4;display:flex;align-items:center;gap:.45em;padding:.35em .85em;border-radius:2em;font-size:.9em;font-weight:700}
.tr i{width:.65em;height:.65em;border-radius:50%;background:linear-gradient(135deg,#8f86c9,#e98aa0)}
.fs{position:absolute;left:4%;bottom:7%;z-index:4;width:4.4em;height:9em}
.fs p{inset:auto 0 0;display:flex;flex-direction:column;gap:.15em;padding:.25em;border-radius:.8em}
.fs label{padding:.4em .2em;border-radius:.55em;text-align:center;font-size:.85em;font-weight:600;color:#5a577d}
.fs :checked+label{background:#2c2a4a;color:#fff}
.zc{position:absolute;left:68%;bottom:7%;translate:-100%;z-index:4;display:flex;flex-direction:column-reverse;align-items:center;gap:.3em;padding:.3em;border-radius:.8em}
.zm,.zp{display:grid;place-items:center;width:1.8em;height:1.8em;color:#bdb6d4;font-weight:700}
.zm:before{content:"−"}.zp:before{content:"+"}.zm:before,.zp:before{grid-area:1/1}
.zm label,.zp label{grid-area:1/1;place-items:center;width:1.8em;height:1.8em;border-radius:.5em;color:#2c2a4a;background:#ffffffb0}
.zc b{flex-direction:column-reverse;align-items:center;height:4.6em}
.zc b label{width:.35em;height:.35em;border-radius:50%;background:#c9c3dd}
.zc b:after{left:50%;bottom:calc(var(--zi)/3*(100% - .7em));width:.7em;height:.7em;margin-left:-.35em;border-radius:50%;background:linear-gradient(135deg,#8f86c9,#e98aa0)}
''',
    narrow='.mb{left:3%;top:3%;width:94%}.zc{left:auto;right:6%;translate:none}')

# 6. Dark minimal: night-mode map, quiet slate cards, one soft pink accent.
SKINS['nord'] = dict(
    head='МАРШРУТ · 여행지',
    css='''
.hw{background:#16191e;color:#e8ecf1;font-family:Pretendard,sans-serif}
.mb{background:#22272e}
.hd,.tr,.fs p,.zc{background:#1c2026e6;border:1px solid #2c323a}
.hd{position:absolute;left:2.5%;top:3.5%;z-index:4;padding:.55em .95em;border-radius:.7em;font-size:1.1em;font-weight:700}
.hd:before{content:var(--co);display:block;font-size:.58em;font-weight:500;color:#7f8a98}
.tr{position:absolute;left:2.5%;top:calc(3.5% + 4.3em);z-index:4;display:flex;align-items:center;gap:.45em;padding:.35em .85em;border-radius:2em;font-size:.9em;font-weight:700}
.tr i{width:.6em;height:.6em;border-radius:50%;background:#f4a3b4}
.fs{position:absolute;left:2.5%;bottom:5%;z-index:4;width:20em;height:2.4em}
.fs p{inset:auto auto 0 0;display:flex;align-items:center;gap:.15em;padding:.25em;border-radius:.7em}
.fs p:before{content:"ЭТАЖ";padding:0 .5em;font-size:.6em;color:#7f8a98}
.fs label{padding:.35em .75em;border-radius:.5em;font-size:.85em;font-weight:600;color:#aab4c0}
.fs :checked+label{background:#f4a3b4;color:#16191e}
.zc{position:absolute;left:70%;bottom:5%;translate:-100%;z-index:4;display:flex;flex-direction:column-reverse;align-items:center;gap:.3em;padding:.3em;border-radius:.7em}
.zm,.zp{display:grid;place-items:center;width:1.8em;height:1.8em;color:#3d4550;font-weight:700}
.zm:before{content:"−"}.zp:before{content:"+"}.zm:before,.zp:before{grid-area:1/1}
.zm label,.zp label{grid-area:1/1;place-items:center;width:1.8em;height:1.8em;border-radius:.45em;color:#e8ecf1;background:#2a3038}
.zc b{flex-direction:column-reverse;align-items:center;height:4.6em}
.zc b label{width:.35em;height:.35em;border-radius:50%;background:#3d4550}
.zc b:after{left:50%;bottom:calc(var(--zi)/3*(100% - .7em));width:.7em;height:.7em;margin-left:-.35em;border-radius:50%;background:#f4a3b4}
''',
    narrow='.zc{left:auto;right:3%;translate:none}')

# 7. Line-art guidebook: printed-city-guide map, big type, thin rules,
#    numbered places, a single red accent.
SKINS['line'] = dict(
    head='ПУТЕВОДИТЕЛЬ',
    css='''
.hw{background:#fff;color:#1d2433;font-family:Pretendard,sans-serif;counter-reset:st sn sm ss li}
.mb{left:2%;top:50%;width:68%;translate:0 -50%;background:#f1f3f6;outline:1px solid #1d2433;outline-offset:.35em}
.hd{position:absolute;left:4%;top:6%;z-index:4;padding:.4em .7em;background:#fff;font-size:1.3em;font-weight:800;letter-spacing:-.02em}
.hd:before{content:var(--co);display:block;font-size:.5em;font-weight:600;letter-spacing:.08em;color:#d94141}
.tr{position:absolute;left:4%;top:calc(6% + 5em);z-index:4;display:flex;align-items:center;gap:.45em;padding:.25em .7em;background:#fff;border:1px solid #1d2433;font-size:.85em;font-weight:700}
.tr i{width:.55em;height:.55em;background:#d94141}
.fs{position:absolute;left:4%;bottom:7%;z-index:4;width:20em;height:2.2em}
.fs p{inset:auto auto 0 0;display:flex;align-items:center;gap:.9em;padding:.35em .7em;background:#fff;border:1px solid #1d2433}
.fs p:before{content:"ЭТАЖ";font-size:.6em;letter-spacing:.1em;color:#7a8394}
.fs label{padding:.1em 0;font-size:.85em;font-weight:600;color:#7a8394;border-bottom:.15em solid #0000}
.fs :checked+label{color:#1d2433;border-bottom-color:#d94141}
.zc{position:absolute;left:67.5%;bottom:7%;translate:-100%;z-index:4;display:flex;align-items:center;gap:.5em;padding:.35em .6em;background:#fff;border:1px solid #1d2433}
.zm,.zp{display:grid;place-items:center;width:1.2em;height:1.2em;color:#c3c9d3;font-weight:700}
.zm:before{content:"−"}.zp:before{content:"+"}.zm:before,.zp:before{grid-area:1/1}
.zm label,.zp label{grid-area:1/1;place-items:center;width:1.2em;height:1.2em;color:#1d2433;background:#fff}
.zc b{width:6em;height:1em;align-items:center;background:linear-gradient(#1d2433 0 0) 50%/100% 1px no-repeat}
.zc b label{width:1px;height:.6em;background:#1d2433}
.zc b:after{top:50%;left:calc(var(--zi)/3*(100% - .6em));width:.6em;height:.6em;margin-top:-.3em;border-radius:50%;background:#d94141}
''',
    narrow='.mb{left:3%;top:3%;width:94%}.zc{left:auto;right:6%;translate:none}')

# ---- third batch: same clean approach, different layouts -----------------
# 8. Blueprint: list on the left, map on the right on a faint drafting grid,
#    hairline panels, one peach accent.
SKINS['blueprint'] = dict(
    head='ПЛАН ГОРОДА · 도면',
    css='''
.hw{background:#13244a;color:#e8f0fb;font-family:Pretendard,sans-serif}
.mb{background:#182e57}
.hv:after{content:"";position:absolute;left:0;top:0;width:72%;aspect-ratio:1.28;z-index:3;pointer-events:none;background:repeating-linear-gradient(#ffffff0c 0 1px,#0000 0 2.4em),repeating-linear-gradient(90deg,#ffffff0c 0 1px,#0000 0 2.4em)}
.hd,.tr,.fs p,.zc{background:#13244ae6;border:1px solid #9fb8de55}
.hd{position:absolute;left:2.5%;top:3.5%;z-index:4;padding:.55em .95em;font-size:1.1em;font-weight:700}
.hd:before{content:var(--co);display:block;font:500 .58em ui-monospace,Menlo,monospace;color:#ffb38a}
.tr{position:absolute;left:2.5%;top:calc(3.5% + 4.4em);z-index:4;display:flex;align-items:center;gap:.45em;padding:.3em .8em;font:700 .9em ui-monospace,Menlo,monospace}
.tr i{width:.6em;height:.6em;border:1px solid #ffb38a;rotate:45deg}
.fs{position:absolute;left:2.5%;bottom:5%;z-index:4;width:20em;height:2.3em}
.fs p{inset:auto auto 0 0;display:flex;align-items:center;gap:.15em;padding:.2em}
.fs p:before{content:"ЭТАЖ";padding:0 .5em;font:.6em ui-monospace,Menlo,monospace;color:#9fb8de}
.fs label{padding:.3em .75em;font-size:.85em;font-weight:600;color:#9fb8de}
.fs :checked+label{background:#ffb38a;color:#13244a}
.zc{position:absolute;left:70%;bottom:5%;translate:-100%;z-index:4;display:flex;flex-direction:column-reverse;align-items:center;gap:.3em;padding:.3em}
.zm,.zp{display:grid;place-items:center;width:1.7em;height:1.7em;color:#3c5d96;font-weight:700}
.zm:before{content:"−"}.zp:before{content:"+"}.zm:before,.zp:before{grid-area:1/1}
.zm label,.zp label{grid-area:1/1;place-items:center;width:1.7em;height:1.7em;border:1px solid #9fb8de;color:#e8f0fb}
.zc b{flex-direction:column-reverse;align-items:center;height:4.6em;width:1px;background:#9fb8de66;margin:.2em auto}
.zc b label{width:.5em;height:1px;background:#9fb8de}
.zc b:after{left:50%;bottom:calc(var(--zi)/3*(100% - .6em));width:.6em;height:.6em;margin-left:-.3em;background:#ffb38a;rotate:45deg}
''',
    narrow='.hv:after{width:100%}.zc{left:auto;right:3%;translate:none}')

# 9. Poster: regions as a tab bar across the top, the place name set large
#    beside the map like a travel poster, black lines and one red accent.
SKINS['poster'] = dict(
    head='',
    css='''
.hw{background:#fff;color:#1c1c1c;font-family:Pretendard,sans-serif}
.mb{background:#ececec;border-right:2px solid #1c1c1c}
.hd{position:absolute;left:74%;top:46%;right:2%;z-index:4;font-size:1.6em;font-weight:800;line-height:1.15;letter-spacing:-.03em}
.hd:before{content:var(--co);display:block;margin-bottom:.5em;padding-bottom:.4em;border-bottom:.12em solid #d7261e;font-size:.32em;font-weight:700;letter-spacing:.12em;color:#d7261e}
.tr{position:absolute;left:74%;top:67%;z-index:4;display:flex;align-items:center;gap:.5em;font-weight:800;font-size:1.2em}
.tr i{width:.7em;height:.7em;background:#d7261e}
.tr:after{content:"БАННЕРЫ";font-size:.5em;letter-spacing:.14em;color:#888}
.fs{position:absolute;left:74%;top:77%;right:2%;z-index:4;height:2.2em}
.fs p{display:flex;gap:.3em}
.fs label{padding:.35em .7em;border:2px solid #1c1c1c;font-size:.85em;font-weight:700}
.fs :checked+label{background:#1c1c1c;color:#fff}
.zc{position:absolute;left:74%;bottom:6%;z-index:4;display:flex;align-items:center;gap:.5em}
.zm,.zp{display:grid;place-items:center;width:1.7em;height:1.7em;border:2px solid #ddd;color:#ccc;font-weight:800}
.zm:before{content:"−"}.zp:before{content:"+"}.zm:before,.zp:before{grid-area:1/1}
.zm label,.zp label{grid-area:1/1;place-items:center;width:1.7em;height:1.7em;margin:-2px;border:2px solid #1c1c1c;color:#1c1c1c;background:#fff}
.zc b{width:6.5em;height:1em;align-items:center;background:linear-gradient(#1c1c1c 0 0) 50%/100% 2px no-repeat}
.zc b label{width:2px;height:.7em;background:#1c1c1c}
.zc b:after{top:50%;left:calc(var(--zi)/3*(100% - .7em));width:.7em;height:.7em;margin-top:-.35em;background:#d7261e}
''',
    narrow='.hd{font-size:1.4em;left:2.5%;top:3%;right:auto;padding:.3em .5em;background:#fff}.hd:before{display:none}.tr{left:2.5%;top:auto;bottom:16%;font-size:1em;background:#fff;padding:.2em .5em}.fs{left:2.5%;top:auto;bottom:4%}.zc{left:auto;right:3%;bottom:4%}')

# 10. White-night duotone: rose walkways on pale sky blocks, information in a
#     calm column beside the map, regions as a dock of cards underneath.
SKINS['duotone'] = dict(
    head='',
    css='''
.hw{background:#f7f9fc;color:#2b3346;font-family:Pretendard,sans-serif}
.mb{left:1.5%;top:50%;width:70%;translate:0 -50%;border-radius:1em;background:#e3ebf5}
.hd{position:absolute;left:74%;top:47%;right:2%;z-index:4;font-size:1.2em;font-weight:800}
.hd:before{content:var(--co);display:block;margin-bottom:.3em;font-size:.48em;font-weight:600;letter-spacing:.08em;color:#e2768c}
.tr{position:absolute;left:74%;top:63%;right:2%;z-index:4;display:flex;align-items:center;gap:.5em;padding:.6em .8em;border-radius:.8em;background:#fff;box-shadow:0 .2em .8em #2b334612;font-weight:800}
.tr i{width:.7em;height:.7em;border-radius:50%;background:#e2768c}
.tr:after{content:"모은 배너";margin-left:auto;font-size:.7em;font-weight:500;color:#8b93a6}
.fs{position:absolute;left:74%;top:75%;right:2%;z-index:4;height:2.6em}
.fs p{display:flex;gap:.25em;padding:.25em;border-radius:.8em;background:#fff;box-shadow:0 .2em .8em #2b334612}
.fs label{flex:1;padding:.4em 0;border-radius:.6em;text-align:center;font-size:.85em;font-weight:600;color:#8b93a6}
.fs :checked+label{background:#f6d3da;color:#b34a62}
.zc{position:absolute;left:74%;top:87%;right:2%;z-index:4;display:flex;align-items:center;gap:.6em;padding:.45em .6em;border-radius:.8em;background:#fff;box-shadow:0 .2em .8em #2b334612}
.zm,.zp{display:grid;place-items:center;width:1.6em;height:1.6em;color:#d5dbe5;font-weight:700}
.zm:before{content:"−"}.zp:before{content:"+"}.zm:before,.zp:before{grid-area:1/1}
.zm label,.zp label{grid-area:1/1;place-items:center;width:1.6em;height:1.6em;border-radius:50%;background:#f6d3da;color:#b34a62}
.zc b{flex:1;height:1em;align-items:center;background:linear-gradient(#e6eaf0 0 0) 50%/100% .25em no-repeat}
.zc b label{width:.35em;height:.35em;border-radius:50%;background:#cfd6e0}
.zc b:after{top:50%;left:calc(var(--zi)/3*(100% - .8em));width:.8em;height:.8em;margin-top:-.4em;border-radius:50%;background:#e2768c;box-shadow:0 0 0 .2em #fff}
''',
    narrow='.mb{left:3%;top:3%;width:94%}.hd,.tr,.fs,.zc{left:auto}.hd{left:5%;top:5%;right:auto;padding:.4em .7em;border-radius:.6em;background:#fffe;font-size:1.1em}.hd:before{display:none}.tr{left:5%;top:auto;bottom:6%;right:auto;padding:.3em .6em}.fs{top:auto;bottom:6%;right:5%;width:10em}.zc{display:none}')

# 11. Aurora night: the map in the middle, floors and zoom on a slim rail to
#     its left, places on the right, a faint aurora glow along the top.
SKINS['aurora'] = dict(
    head='СЕВЕРНОЕ СИЯНИЕ · 오로라',
    css='''
.hw{background:radial-gradient(60% 40% at 40% 0,#1f5a4f88,#0000),#0d1a20;color:#e2f1ef;font-family:Pretendard,sans-serif}
.mb{left:8%;top:50%;width:64%;translate:0 -50%;border-radius:.9em;background:#13262f;box-shadow:0 0 0 1px #2c4c55}
.hd{position:absolute;left:10%;top:7%;z-index:4;padding:.5em .9em;border-radius:.7em;background:#0d1a20d9;border:1px solid #2c4c55;font-size:1.1em;font-weight:700}
.hd:before{content:var(--co);display:block;font-size:.58em;font-weight:500;color:#7de3b8}
.tr{position:absolute;left:10%;top:calc(7% + 4.4em);z-index:4;display:flex;align-items:center;gap:.45em;padding:.3em .8em;border-radius:2em;background:#0d1a20d9;border:1px solid #2c4c55;font-size:.9em;font-weight:700}
.tr i{width:.6em;height:.6em;border-radius:50%;background:#7de3b8;box-shadow:0 0 .5em #7de3b8}
.fs{position:absolute;left:1.5%;top:12%;z-index:4;width:5%;height:46%}
.fs p{display:flex;flex-direction:column;gap:.25em}
.fs label{padding:.45em 0;border-radius:.5em;text-align:center;font-size:.8em;font-weight:700;color:#6f8f96;background:#13262f}
.fs :checked+label{background:#7de3b8;color:#0d1a20}
.zc{position:absolute;left:4%;bottom:12%;translate:-50%;z-index:4;display:flex;flex-direction:column-reverse;align-items:center;gap:.3em;padding:.3em;border-radius:2em;background:#13262f}
.zm,.zp{display:grid;place-items:center;width:1.6em;height:1.6em;color:#2c4c55;font-weight:700}
.zm:before{content:"−"}.zp:before{content:"+"}.zm:before,.zp:before{grid-area:1/1}
.zm label,.zp label{grid-area:1/1;place-items:center;width:1.6em;height:1.6em;border-radius:50%;background:#1e3a44;color:#e2f1ef}
.zc b{flex-direction:column-reverse;align-items:center;height:4.4em}
.zc b label{width:.3em;height:.3em;border-radius:50%;background:#2c4c55}
.zc b:after{left:50%;bottom:calc(var(--zi)/3*(100% - .65em));width:.65em;height:.65em;margin-left:-.325em;border-radius:50%;background:#7de3b8;box-shadow:0 0 .5em #7de3b8}
''',
    narrow='.mb{left:3%;top:3%;width:94%}.hd,.tr{left:5%}.fs{left:5%;top:auto;bottom:6%;width:3.2em;height:7.5em}.fs p{justify-content:flex-end}.zc{left:auto;right:6%;translate:none}')

# ---- fourth batch: more layouts -------------------------------------------
ZOOMBTN = ('.zm:before{content:"−"}.zp:before{content:"+"}.zm:before,.zp:before{grid-area:1/1}'
           '.zm label,.zp label{grid-area:1/1;place-items:center}')

# 12. Metro signage: full-width map, places as a strip of numbered line
#     badges under it, dark-blue wayfinding panels.
SKINS['metro'] = dict(
    head='',
    css='''
.hw{background:#fff;color:#14213d;font-family:Pretendard,sans-serif}
.mb{background:#eef1f5}
.hd{position:absolute;left:2.5%;top:3%;z-index:4;display:flex;align-items:center;gap:.6em;padding:.5em 1em .5em .55em;border-radius:.4em;background:#0b2f6b;color:#fff;font-size:1.1em;font-weight:700}
.hd:before{content:"";width:1.1em;height:1.1em;border:.28em solid #fff;border-radius:50%}
.tr{position:absolute;left:2.5%;top:calc(3% + 3.6em);z-index:4;display:flex;align-items:center;gap:.45em;padding:.35em .8em;border:2px solid #0b2f6b;border-radius:.4em;background:#fff;font-weight:800}
.tr i{width:.6em;height:.6em;background:#0b2f6b}
.fs{position:absolute;left:2.5%;bottom:4%;z-index:4;width:4em;height:9em}
.fs p{display:flex;flex-direction:column;justify-content:flex-end;gap:.3em}
.fs label{display:grid;place-items:center;height:2.2em;border:2px solid #0b2f6b;border-radius:1.1em;background:#fff;font-size:.85em;font-weight:800;color:#0b2f6b}
.fs :checked+label{background:#0b2f6b;color:#fff}
.zc{position:absolute;left:70%;bottom:4%;translate:-100%;z-index:4;display:flex;flex-direction:column-reverse;align-items:center;gap:.3em;padding:.3em;border-radius:.4em;background:#0b2f6b}
.zm,.zp{display:grid;place-items:center;width:1.8em;height:1.8em;color:#3a5a92;font-weight:800}
.zm label,.zp label{width:1.8em;height:1.8em;border-radius:.3em;background:#fff;color:#0b2f6b}
.zc b{flex-direction:column-reverse;align-items:center;height:4.4em}
.zc b label{width:.35em;height:.35em;border-radius:50%;background:#3a5a92}
.zc b:after{left:50%;bottom:calc(var(--zi)/3*(100% - .7em));width:.7em;height:.7em;margin-left:-.35em;border-radius:50%;background:#fff}
''' + ZOOMBTN,
    narrow='.zc{left:auto;right:3%;translate:none}')

# 13. Soft UI: map pressed into a soft panel, controls as raised buttons
#     floating on it, places on a bottom sheet.
SKINS['soft'] = dict(
    head='',
    css='''
.hw{background:#e7eaf0;color:#3a4256;font-family:Pretendard,sans-serif}
.mb{left:2%;top:50%;width:68%;translate:0 -50%;border-radius:1.4em;background:#e0e4ea;box-shadow:inset .3em .3em .8em #c5cad3,inset -.3em -.3em .8em #fff}
.hd,.tr,.fs p,.zc{background:#e7eaf0;box-shadow:.35em .35em .8em #c5cad3,-.35em -.35em .8em #fff}
.hd{position:absolute;left:5%;top:5%;z-index:4;padding:.6em 1em;border-radius:1em;font-size:1.1em;font-weight:700}
.hd:before{content:var(--co);display:block;font-size:.58em;font-weight:500;color:#9aa1b2}
.tr{position:absolute;left:5%;top:calc(5% + 4.6em);z-index:4;display:flex;align-items:center;gap:.45em;padding:.4em .9em;border-radius:2em;font-size:.9em;font-weight:700}
.tr i{width:.6em;height:.6em;border-radius:50%;background:#9a8cd8}
.fs{position:absolute;right:33%;top:7%;z-index:4;width:4.4em;height:10em}
.fs p{bottom:auto;display:flex;flex-direction:column;gap:.3em;padding:.35em;border-radius:1em}
.fs label{padding:.5em 0;border-radius:.7em;text-align:center;font-size:.85em;font-weight:700;color:#9aa1b2}
.fs :checked+label{box-shadow:inset .2em .2em .5em #c5cad3,inset -.2em -.2em .5em #fff;color:#7a6cc4}
.zc{position:absolute;right:33%;top:52%;z-index:4;display:flex;flex-direction:column-reverse;align-items:center;gap:.35em;padding:.4em;border-radius:1.4em}
.zm,.zp{display:grid;place-items:center;width:1.9em;height:1.9em;color:#c5cad3;font-weight:700}
.zm label,.zp label{width:1.9em;height:1.9em;border-radius:50%;color:#7a6cc4;background:#e7eaf0;box-shadow:.15em .15em .4em #c5cad3,-.15em -.15em .4em #fff}
.zc b{flex-direction:column-reverse;align-items:center;height:4.4em}
.zc b label{width:.35em;height:.35em;border-radius:50%;background:#cfd4dc}
.zc b:after{left:50%;bottom:calc(var(--zi)/3*(100% - .7em));width:.7em;height:.7em;margin-left:-.35em;border-radius:50%;background:#9a8cd8}
''' + ZOOMBTN,
    narrow='.mb{left:3%;top:3%;width:94%}.fs,.zc{right:6%}')

# 14. White-night sunset: the place name large in a left column with the
#     list under it, map on the right, peach-to-lilac accent on plum.
SKINS['sunset'] = dict(
    head='',
    css='''
.hw{background:linear-gradient(160deg,#2b1c37,#1c152e);color:#f6e9f0;font-family:Pretendard,sans-serif}
.mb{left:1.5%;top:50%;width:68%;translate:0 -50%;border-radius:1em;background:#2a1d38;box-shadow:0 0 0 1px #4a3658}
.hd{position:absolute;left:73.5%;top:48%;width:25%;z-index:4;font-size:1.5em;font-weight:800;line-height:1.2}
.hd:before{content:var(--co);display:block;margin-bottom:.4em;font-size:.36em;font-weight:600;letter-spacing:.1em;color:#f3a58f}
.tr{position:absolute;left:73.5%;top:calc(48% + 4.6em);z-index:4;display:flex;align-items:center;gap:.45em;font-weight:700}
.tr i{width:.6em;height:.6em;border-radius:50%;background:linear-gradient(135deg,#ff9a6b,#a77bf3)}
.tr:after{content:"BANNERS";font-size:.6em;letter-spacing:.14em;color:#a98fb3}
.fs{position:absolute;left:3%;bottom:6%;z-index:4;width:20em;height:2.4em}
.fs p{inset:auto auto 0 0;display:flex;gap:.2em;padding:.25em;border-radius:2em;background:#1c152ee6;border:1px solid #4a3658}
.fs label{padding:.35em .9em;border-radius:2em;font-size:.85em;font-weight:600;color:#c3a9c9}
.fs :checked+label{background:linear-gradient(90deg,#ff9a6b,#f06d9a);color:#fff}
.zc{position:absolute;left:68%;bottom:6%;translate:-100%;z-index:4;display:flex;flex-direction:column-reverse;align-items:center;gap:.3em;padding:.3em;border-radius:2em;background:#1c152ee6;border:1px solid #4a3658}
.zm,.zp{display:grid;place-items:center;width:1.7em;height:1.7em;color:#4a3658;font-weight:700}
.zm label,.zp label{width:1.7em;height:1.7em;border-radius:50%;background:#3a2a48;color:#f6e9f0}
.zc b{flex-direction:column-reverse;align-items:center;height:4.4em}
.zc b label{width:.3em;height:.3em;border-radius:50%;background:#4a3658}
.zc b:after{left:50%;bottom:calc(var(--zi)/3*(100% - .65em));width:.65em;height:.65em;margin-left:-.325em;border-radius:50%;background:linear-gradient(135deg,#ff9a6b,#a77bf3)}
''' + ZOOMBTN,
    narrow='.mb{left:3%;top:3%;width:94%}.hd{left:5%;top:5%;width:auto;padding:.3em .6em;border-radius:.5em;background:#1c152ee6;font-size:1.1em}.hd:before{display:none}.tr{left:5%;top:auto;bottom:16%}.fs{left:5%}.zc{left:auto;right:5%;translate:none}')

# 15. Sage toolbar: a title bar above the map, a toolbar below it with the
#     floors on the left, the places in the middle and the zoom on the right.
SKINS['sage'] = dict(
    head='',
    css='''
.hw{background:#f4f6f4;color:#2f3a35;font-family:Pretendard,sans-serif}
.hv{margin:3.4em 0 3.8em}.mb{background:#e1e7e3}
.hl{top:3.4em}
.hd{position:absolute;left:2.5%;top:-2.6em;z-index:4;display:flex;align-items:baseline;gap:.6em;font-size:1.15em;font-weight:800}
.hd:before{content:var(--co);order:1;font-size:.55em;font-weight:500;color:#7f948a}
.tr{position:absolute;right:29%;top:-2.6em;z-index:4;display:flex;align-items:center;gap:.45em;padding:.3em .8em;border-radius:2em;background:#e3ebe6;font-size:.9em;font-weight:700}
.tr i{width:.6em;height:.6em;border-radius:50%;background:#5f9a86}
.fs{position:absolute;left:2.5%;bottom:-3.1em;z-index:4;width:20em;height:2.4em}
.fs p{inset:auto auto 0 0;display:flex;gap:.15em;padding:.2em;border-radius:.6em;background:#e3ebe6}
.fs label{padding:.35em .8em;border-radius:.45em;font-size:.85em;font-weight:600;color:#6f857b}
.fs :checked+label{background:#fff;color:#2f3a35;box-shadow:0 .1em .3em #2f3a3522}
.zc{position:absolute;right:29%;bottom:-3.1em;z-index:4;display:flex;align-items:center;gap:.4em;padding:.2em .3em;border-radius:.6em;background:#e3ebe6}
.zm,.zp{display:grid;place-items:center;width:1.6em;height:1.6em;color:#b9cbc0;font-weight:700}
.zm label,.zp label{width:1.6em;height:1.6em;border-radius:.4em;background:#fff;color:#2f3a35}
.zc b{width:5em;height:1em;align-items:center;background:linear-gradient(#c9d6ce 0 0) 50%/100% .2em no-repeat}
.zc b label{width:.3em;height:.3em;border-radius:50%;background:#a9bfb3}
.zc b:after{top:50%;left:calc(var(--zi)/3*(100% - .7em));width:.7em;height:.7em;margin-top:-.35em;border-radius:50%;background:#5f9a86}
''' + ZOOMBTN,
    narrow='.tr,.zc{right:2.5%}')

def markup(skin, base):
    def floors(name, layers):
        o = ''
        for fid, key in layers:
            mk = ''.join('<i%s style=--x:%d;--y:%d>%s</i>' % (' class=' + m[3] if len(m) > 3 else '', round(m[1] / 12.8), round(m[2] / 10), m[0]) for m in MARKERS[key])
            o += '<div class=z><img src=%s%s.svg>%s</div>' % (base, key, mk)
        return o
    def fsel(cls, name, items):
        return '<p class=%s>%s</p>' % (cls, ''.join('<input type=radio name=%s id=%s%s><label for=%s>%s</label>' % (name, i, ' checked' if k == 0 else '', i, lab) for k, (i, lab) in enumerate(items)))
    zl = lambda ks, t: ''.join('<label for=z%d>%s</label>' % (k, t) for k in ks)
    return ('<div class=hw>' + ''.join('<input type=radio name=zz id=z%d%s>' % (k, ' checked' if k == 1 else '') for k in range(1, 5)) +
        '<div class=hv><div class=mb><div class=mi>'
        '<div class=mn>' + floors('n', [('n1', 'n1'), ('n2', 'n2')]) + '</div>'
        '<div class=mm>' + floors('m', [('m1', 'm1'), ('m2', 'm2')]) + '</div>'
        '<div class=ms>' + floors('s', [('s1', 's1'), ('s2', 's2'), ('s3', 's3')]) + '</div>'
        '</div></div><h4 class=hd></h4><div class=tr><i></i><b></b></div>'
        '<div class=fs>' + fsel('fn', 'n', [('n1', '1'), ('n2', 'B1')]) + fsel('fm', 'm', [('m1', '1'), ('m2', 'B1')]) +
        fsel('fx', 's', [('s1', '센가물'), ('s2', '현대물'), ('s3', '바다')]) + '</div>'
        '<div class=zc><span class=zm>' + zl((1, 2, 3), '−') + '</span><b>' + zl((1, 2, 3, 4), '') + '</b><span class=zp>' + zl((2, 3, 4), '+') + '</span></div></div>'
        '<div class=hl><b>✦ Карта звёздного пути ›</b><p>◈ 러시아</p>'
        '<input type=radio name=q id=q1 checked><label for=q1>노릴스크의 극야</label>'
        '<input type=radio name=q id=q2><label for=q2>노릴스크의 백야</label>'
        '<input type=radio name=q id=q3><label for=q3>모스크바의 거리</label><p>◈ 보금자리</p>'
        '<input type=radio name=q id=q4><label for=q4>소중한 이들과 만남</label></div></div>')

def build(skin, base):
    css = (BASE + SKINS[skin]['css']).replace('\n', '') + NARROW.replace('{SK}', SKINS[skin]['narrow'])
    return '<div class=hm><style>' + css + '</style>' + markup(skin, base) + '</div>'

if __name__ == '__main__':
    skin, base, out = sys.argv[1:4]
    s = build(skin, base)
    open(out, 'w', encoding='utf-8').write(s)
    real = build(skin, 'https://cdn.jsdelivr.net/gh/ryuksohyeon-stack/log@' + '0' * 40 + '/maps/' + skin + '/')
    print(skin, 'chars with real links:', len(real), 'utf16:', len(real.encode('utf-16-le')) // 2)
