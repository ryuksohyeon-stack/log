"""Tiny SVG path builder + minifier. Shapes are authored in absolute
coordinates; walkable/fill shapes are clockwise, holes counter-clockwise
(nonzero fill rule)."""
import math

def area(pts):
    return sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))/2

def poly(pts, hole=False):
    pts=list(pts)
    cw = area(pts) > 0          # screen coords: positive area = clockwise
    if cw == hole: pts.reverse()
    return [('M',pts[0])]+[('L',p) for p in pts[1:]]+[('Z',)]

def rect(x,y,w,h,hole=False): return poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],hole)
def cham(x,y,w,h,c,hole=False):
    return poly([(x+c,y),(x+w-c,y),(x+w,y+c),(x+w,y+h-c),(x+w-c,y+h),(x+c,y+h),(x,y+h-c),(x,y+c)],hole)
def ngon(cx,cy,r,n=8,rot=None,hole=False):
    rot = math.pi/n if rot is None else rot
    return poly([(round(cx+r*math.cos(rot+2*math.pi*k/n),1),round(cy+r*math.sin(rot+2*math.pi*k/n),1)) for k in range(n)],hole)
def circ(cx,cy,r,hole=False,ry=None):
    ry = r if ry is None else ry
    s = 0 if hole else 1
    return [('M',(cx-r,cy)),('A',r,ry,s,(cx+r,cy)),('A',r,ry,s,(cx-r,cy)),('Z',)]
def rr(x,y,w,h,q,hole=False):
    """Rounded rectangle; q is the corner radius."""
    q = min(q, w/2, h/2)
    c = [('M',(x+q,y)),('L',(x+w-q,y)),('A',q,q,1,(x+w,y+q),0),('L',(x+w,y+h-q)),('A',q,q,1,(x+w-q,y+h),0),
         ('L',(x+q,y+h)),('A',q,q,1,(x,y+h-q),0),('L',(x,y+q)),('A',q,q,1,(x+q,y),0),('Z',)]
    c = [k for i,k in enumerate(c) if not (k[0]=='L' and c[i-1][0]=='A' and k[1]==c[i-1][4])]
    return reverse(c) if hole else c
def reverse(sh):
    """Same outline, opposite winding (turns a fill shape into a hole)."""
    pts=[sh[0][1]]; segs=[]
    for k in sh[1:]:
        if k[0]=='Z': break
        segs.append(k); pts.append(k[1] if k[0]=='L' else k[4])
    out=[('M',pts[0])]
    if pts[-1]!=pts[0]: out.append(('L',pts[-1]))
    for i in reversed(range(len(segs))):
        k=segs[i]
        out.append(('L',pts[i]) if k[0]=='L' else ('A',k[1],k[2],1-k[3],pts[i],k[5] if len(k)>5 else 1))
    return out+[('Z',)]
def fillet(x,y,q,corner):
    """Concave quarter-round filling the inside corner at (x,y); corner in 'tl','tr','bl','br'
    says which way the filler extends from the corner point."""
    sx = 1 if corner[1]=='r' else -1; sy = 1 if corner[0]=='b' else -1
    a=(x+sx*q,y); b=(x,y+sy*q)
    sh = [('M',(x,y)),('L',a),('A',q,q,1 if sx*sy<0 else 0,b,0),('Z',)]
    return reverse(sh) if sx*sy<0 else sh   # keep every fillet clockwise
def line(*pts): return [('M',pts[0])]+[('L',p) for p in pts[1:]]
def ring(cx,cy,r,ry=None):  # open circle for detail strokes
    ry = r if ry is None else ry
    return [('M',(cx-r,cy)),('A',r,ry,1,(cx+r,cy)),('A',r,ry,1,(cx-r,cy))]
def block(x,y,w,h,i=1.2):   # building footprint with inset roof line
    return rect(x,y,w,h)+rect(x+i,y+i,w-2*i,h-2*i)

def fmt(n):
    n = round(n,2)
    if n == int(n): s = str(int(n))
    else: s = ('%.2f' % n).rstrip('0')
    if s.startswith('0.'): s = s[1:]
    elif s.startswith('-0.'): s = '-'+s[2:]
    return s

def nums(vals):
    out=''
    for v in vals:
        t=fmt(v)
        if out and not t.startswith('-') and not (t.startswith('.') and '.' in out.split(' ')[-1].split('-')[-1] and out[-1].isdigit()) :
            # need a separator unless next starts with '-' or ('.' after a number already holding a '.')
            last = out
            # find last number token
            j=len(last)
            while j>0 and (last[j-1].isdigit() or last[j-1]=='.'): j-=1
            tok=last[j:]
            if t.startswith('.') and '.' in tok: pass
            else: out+=' '
        out+=t
    return out

def minify(cmds):
    out=[]; cur=(0,0); start=(0,0); last=None
    def emit(letter, vals):
        nonlocal last
        body = nums(vals)
        if letter == last and letter not in 'Mm':
            # implicit repeat: needs separator unless body starts with '-'
            prev = out[-1]
            sep = '' if body.startswith('-') or (body.startswith('.') and '.' in prev.split()[-1].lstrip('-').split('-')[-1] and prev[-1].isdigit()) else ' '
            out.append(sep+body)
        else:
            out.append(letter+body)
        last = letter
    for c in cmds:
        k=c[0]
        if k=='Z':
            out.append('z'); last='z'; cur=start; continue
        if k=='M':
            x,y=c[1]; a=nums([x,y]); r=nums([x-cur[0],y-cur[1]])
            (emit('m',[x-cur[0],y-cur[1]]) if len(r)<len(a) else emit('M',[x,y]))
            cur=start=(x,y); continue
        if k=='L':
            x,y=c[1]
            if y==cur[1]:
                a,r=[x],[x-cur[0]]; L='H'
            elif x==cur[0]:
                a,r=[y],[y-cur[1]]; L='V'
            else:
                a,r=[x,y],[x-cur[0],y-cur[1]]; L='L'
            (emit(L.lower(),r) if len(nums(r))<=len(nums(a)) else emit(L,a))
            cur=(x,y); continue
        if k=='A':
            rx,ry,s,(x,y)=c[1],c[2],c[3],c[4]; lg = c[5] if len(c)>5 else 1
            r=[rx,ry,0,lg,s,x-cur[0],y-cur[1]]; a=[rx,ry,0,lg,s,x,y]
            (emit('a',r) if len(nums(r))<=len(nums(a)) else emit('A',a))
            cur=(x,y); continue
    return ''.join(out)

def P(*shapes):
    cmds=[]
    for s in shapes: cmds+=s
    return minify(cmds)
