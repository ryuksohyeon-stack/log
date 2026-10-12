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
            rx,ry,s,(x,y)=c[1],c[2],c[3],c[4]
            r=[rx,ry,0,1,s,x-cur[0],y-cur[1]]; a=[rx,ry,0,1,s,x,y]
            (emit('a',r) if len(nums(r))<=len(nums(a)) else emit('A',a))
            cur=(x,y); continue
    return ''.join(out)

def P(*shapes):
    cmds=[]
    for s in shapes: cmds+=s
    return minify(cmds)
