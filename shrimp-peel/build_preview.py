# 시안 미리보기 만들기 — src/preview.html 에 새우 3D(src/shrimp3d.js)와 Pretendard(쓰는 글자만 잘라 넣은 것)를 끼워
# preview.html 한 장으로 만들어요.
# 실행: python3 shrimp-peel/build_preview.py <Pretendard woff2 폴더> [내보낼 파일]   (예: pretendard 패키지의 dist/web/static/woff2)
import base64, io, os, re, sys
from fontTools import subset
from fontTools.ttLib import TTFont

here = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(here, 'src')
page = open(os.path.join(src, 'preview.html'), encoding='utf-8').read()
mod = open(os.path.join(src, 'shrimp3d.js'), encoding='utf-8').read()
chars = set(page) | set(re.sub(r'/\*.*?\*/', '', mod, flags=re.S)) | set(chr(c) for c in range(32, 127)) | set('…·—')
text = ''.join(sorted(c for c in chars if ord(c) >= 32))
faces = []
for w, f in [(300, 'Pretendard-Light.woff2'), (400, 'Pretendard-Regular.woff2'), (600, 'Pretendard-SemiBold.woff2')]:
    font = TTFont(os.path.join(sys.argv[1], f))
    opt = subset.Options(); opt.flavor = 'woff2'; opt.layout_features = ['*']
    sub = subset.Subsetter(opt); sub.populate(text=text); sub.subset(font)
    buf = io.BytesIO(); font.flavor = 'woff2'; font.save(buf)
    faces.append("@font-face{font-family:'Pretendard';font-weight:%d;font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')}" % (w, base64.b64encode(buf.getvalue()).decode()))
out = page.replace('/*@FONT@*/', '\n'.join(faces)).replace('/*@SHRIMP@*/', mod)
dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, 'preview.html')
open(dst, 'w', encoding='utf-8').write(out)
print(dst, len(out.encode()) // 1024, 'KB')
