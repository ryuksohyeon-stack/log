"""Builds the Star Rail style floor maps used by star-rail-map.html.
Run: python3 build.py [n1 n2 ...]   (writes <name>.svg next to this file)

Canvas is 1280 x 1000, the same 1.28 aspect as the map box in the widget,
so a point (x, y) here sits at left:x/12.8%  top:y/10% in the widget."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import Map
from pl import rect, cham, ngon, circ, poly, line, ring

def far(m, boxes):
    for b in boxes: m.add('f', rect(*b))

def benches(m, x0, x1, y, step, w=18, h=8):
    x = x0
    while x + w <= x1:
        m.holes(rect(x, y, w, h)); x += step

def pylons(m, x0, x1, y, w, h, gap):
    x = x0
    while x + w <= x1:
        m.holes(rect(x, y, w, h)); x += w + gap

def stalls(m, x0, x1, y0, y1, step):
    x = x0
    while x <= x1:
        m.add('t', line((x, y0), (x, y1))); x += step

# ===================== Norilsk, street level =====================
def norilsk1():
    m = Map()
    far(m, [(20, 110, 170, 60), (380, 20, 300, 50), (740, 30, 230, 60), (1030, 20, 230, 50), (1240, 210, 40, 400)])
    m.add('v', poly([(0, 900), (180, 884), (420, 892), (640, 878), (860, 896), (1080, 882), (1280, 890), (1280, 1000), (0, 1000)]))
    for y, x0, x1 in ((925, 60, 380), (948, 300, 560), (930, 720, 1010), (955, 880, 1200), (975, 120, 420)):
        m.add('vw', line((x0, y), (x1, y)))
    # buildings: closed courtyard blocks typical of Norilsk
    m.court(510, 250, 220, 190, 560, 290, 140, 110)
    m.court(790, 250, 160, 190, 820, 290, 100, 110)
    m.court(510, 540, 220, 230, 560, 580, 140, 140)
    m.court(790, 540, 160, 230, 820, 580, 100, 140)
    m.flat(510, 90, 220, 100, 10, 5, 2)
    m.hip(790, 110, 160, 80)
    m.flat(1010, 90, 230, 100, 10, 6, 2)
    m.hip(370, 250, 80, 190); m.hip(370, 540, 80, 230)
    m.hip(60, 250, 140, 120); m.flat(275, 250, 75, 110, 8)
    m.flat(60, 620, 140, 170, 10, 2, 3); m.hip(275, 620, 75, 170)
    m.flat(1010, 250, 220, 110, 10); m.dome(1170, 305, 38, 12); m.add('r', rect(1030, 270, 60, 70), line((1030, 305), (1090, 305)))
    m.flat(1010, 630, 220, 140, 10, 4, 2)
    # walkable network
    m.add('w', circ(240, 490, 115))
    m.add('w', rect(340, 450, 720, 80), rect(40, 450, 90, 80), rect(1215, 450, 65, 80),
          cham(1040, 370, 180, 240, 45), rect(220, 250, 40, 130), cham(170, 185, 140, 70, 18),
          rect(220, 600, 40, 220),
          rect(460, 130, 40, 320), rect(460, 530, 40, 290), rect(740, 200, 40, 250), rect(740, 530, 40, 290),
          rect(960, 200, 40, 250), rect(960, 530, 40, 290), rect(400, 200, 640, 40),
          cham(560, 290, 140, 110, 14), rect(615, 400, 30, 50), cham(820, 290, 100, 110, 14), rect(855, 400, 30, 50),
          cham(560, 580, 140, 140, 14), rect(615, 530, 30, 50), cham(820, 580, 100, 140, 14), rect(855, 530, 30, 50),
          rect(200, 820, 1020, 44), rect(600, 864, 40, 50), ngon(620, 945, 52, 8))
    # Gvardeyskaya square: stepped plinth with the monument
    m.holes(ngon(240, 490, 40, 4, math.pi / 4))
    m.add('r', ngon(240, 490, 28, 4, math.pi / 4), ring(240, 490, 12), line((222, 472), (258, 508)), line((258, 472), (222, 508)))
    m.add('t', ring(240, 490, 62), ring(240, 490, 88), ngon(240, 490, 50, 4, math.pi / 4))
    for k in range(8):
        a = math.pi / 8 + k * math.pi / 4
        m.add('t', line((round(240 + 62 * math.cos(a), 1), round(490 + 62 * math.sin(a), 1)), (round(240 + 105 * math.cos(a), 1), round(490 + 105 * math.sin(a), 1))))
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        m.steps(240 + dx * 41, 490 + dy * 41, 240 + dx * 54, 490 + dy * 54, 34, '3 4')
    # Metallurgists' square: fountain, kiosks
    m.holes(circ(1130, 490, 34)); m.add('r', ring(1130, 490, 24), ring(1130, 490, 10))
    m.add('t', ngon(1130, 490, 70, 8), ngon(1130, 490, 98, 8))
    for x, y in ((1075, 392), (1160, 392), (1075, 578), (1160, 578)):
        m.holes(rect(x, y, 26, 18)); m.add('r', line((x, y + 9), (x + 26, y + 9)))
    # boulevard medians with trees, benches on the embankment
    m.isl(370, 481, 70, 18, 3); m.isl(530, 481, 190, 18, 7); m.isl(800, 481, 140, 18, 5)
    m.add('t', line((355, 462), (1045, 462)), line((355, 518), (1045, 518)))
    m.add('l', line((410, 220), (1030, 220)), line((480, 140), (480, 192)), line((480, 248), (480, 440)), line((480, 540), (480, 770)),
          line((760, 248), (760, 440)), line((760, 540), (760, 770)), line((980, 248), (980, 440)), line((980, 540), (980, 770)))
    for x in (480, 760, 980):
        m.steps(x, 452, x, 528, 34, '6 6')
    benches(m, 290, 1200, 846, 70)
    m.add('t', line((210, 856), (1215, 856)))
    m.add('d', line((230, 830), (1210, 830)))
    # courtyards: playground, benches, parking
    m.holes(rect(590, 320, 20, 20), rect(650, 320, 20, 20), rect(596, 362, 68, 10))
    m.add('t', cham(572, 302, 116, 86, 8), ring(870, 345, 22), ring(870, 345, 10))
    m.add('t', cham(572, 592, 116, 116, 8), ring(630, 650, 34), ring(630, 650, 16))
    m.holes(rect(612, 690, 36, 10))
    stalls(m, 834, 906, 600, 640, 18); stalls(m, 834, 906, 660, 700, 18)
    m.add('t', line((830, 650), (910, 650)))
    # pier and the lookout
    m.holes(circ(620, 945, 14)); m.add('t', ngon(620, 945, 36, 8))
    for x, w in ((240, 40), (480, 40), (760, 40), (980, 40)):
        m.steps(x, 780, x, 820, w)
    m.steps(620, 866, 620, 898, 40)
    m.steps(240, 252, 240, 284, 40)
    m.add('d', line((205, 200), (305, 200)))
    return m

# ===================== Norilsk, B1 mine =====================
def norilsk2():
    m = Map()
    m.add('f', poly([(40, 60), (420, 40), (470, 150), (380, 210), (60, 230)]), poly([(860, 40), (1240, 70), (1250, 230), (880, 220)]),
          poly([(40, 790), (430, 770), (470, 900), (60, 960)]), poly([(860, 790), (1240, 780), (1260, 960), (840, 950)]))
    # galleries and chambers
    m.add('w', rect(130, 465, 420, 60), rect(730, 465, 400, 60), circ(640, 495, 96),
          rect(615, 180, 50, 225), cham(500, 90, 280, 100, 25), rect(615, 585, 50, 150), cham(470, 730, 340, 130, 30),
          cham(130, 270, 240, 140, 30), rect(225, 405, 50, 65), cham(900, 270, 250, 140, 30), rect(1000, 405, 50, 65),
          cham(150, 600, 240, 150, 30), rect(240, 520, 50, 85), cham(890, 600, 260, 150, 30), rect(990, 520, 50, 85),
          rect(225, 190, 50, 85), rect(1000, 190, 50, 85), cham(60, 470, 80, 50, 14), cham(1120, 470, 100, 50, 14))
    # shaft hall: hoist cage, four columns
    m.holes(rect(605, 460, 70, 70)); m.add('r', rect(613, 468, 54, 54), line((613, 468), (667, 522)), line((667, 468), (613, 522)))
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        m.holes(rect(640 + dx * 62 - 8, 495 + dy * 62 - 8, 16, 16))
    m.add('t', ring(640, 495, 50), ring(640, 495, 80))
    # rails with sleepers along the haulage gallery
    for x0, x1 in ((140, 545), (735, 1120)):
        m.steps(x0, 495, x1, 495, 30, '4 10')
        m.add('t', line((x0, 486), (x1, 486)), line((x0, 504), (x1, 504)))
    m.steps(640, 195, 640, 395, 30, '4 10'); m.add('t', line((631, 195), (631, 395)), line((649, 195), (649, 395)))
    # ore carts on the rails
    for x in (330, 880):
        m.holes(rect(x, 481, 46, 28)); m.add('r', rect(x + 6, 487, 34, 16))
    # north chamber: winding engine, cable drums
    m.holes(rect(560, 112, 60, 50), rect(660, 112, 60, 50))
    m.add('r', ring(590, 137, 16), ring(690, 137, 16))
    # canteen: tables and serving counter
    for r_ in range(2):
        for c in range(3):
            m.holes(rect(170 + c * 60, 300 + r_ * 50, 36, 22))
    m.holes(rect(160, 392, 180, 10))
    # banya: pools of water
    m.add('v', rect(920, 630, 90, 60), circ(1090, 670, 34))
    m.add('w', rect(920, 630, 90, 60, True), circ(1090, 670, 34, True))
    m.add('t', rect(910, 620, 110, 80), ring(1090, 670, 44))
    m.holes(rect(930, 712, 70, 14))
    # tool store and pump room
    for c in range(4):
        m.holes(rect(175 + c * 50, 630, 24, 50))
    m.holes(rect(930, 300, 50, 50), rect(1000, 300, 50, 50), rect(1070, 300, 50, 50))
    m.add('r', ring(955, 325, 14), ring(1025, 325, 14), ring(1095, 325, 14))
    # south chamber: ore bunkers
    for c in range(4):
        m.holes(ngon(530 + c * 75, 795, 26, 6))
    m.add('t', line((490, 760), (790, 760)), line((490, 830), (790, 830)))
    # exits to the surface
    m.steps(250, 192, 250, 268, 50); m.steps(1025, 192, 1025, 268, 50)
    m.steps(80, 495, 128, 495, 50); m.steps(1132, 495, 1200, 495, 50)
    m.add('d', line((660, 600), (660, 720)), line((620, 600), (620, 720)))
    return m

# ===================== Moscow, street level =====================
def moscow1():
    m = Map()
    far(m, [(10, 80, 120, 140), (1240, 230, 40, 380), (10, 700, 80, 120)])
    bank = [(0, 860), (300, 820), (640, 880), (960, 850), (1280, 790)]
    m.add('v', poly(bank + [(1280, 890), (960, 950), (640, 980), (300, 920), (0, 960)]))
    for (x0, y0), (x1, y1) in zip(bank, bank[1:]):
        m.add('vw', line((x0 + 40, y0 + 45), (x1 - 40, y1 + 45)))
    # Kremlin: wall, towers, palaces, cathedrals
    Kout = [(150, 250), (470, 190), (535, 575), (450, 680), (190, 660), (105, 430)]
    Kin = [(170, 270), (455, 216), (512, 572), (437, 656), (204, 638), (128, 432)]
    m.add('b', poly(Kout)); m.add('r', poly(Kin))
    for x, y in Kout + [(310, 220), (502, 380), (320, 670), (128, 340)]:
        m.add('b', rect(x - 18, y - 18, 36, 36)); m.add('r', line((x - 18, y - 18), (x + 18, y + 18)), line((x + 18, y - 18), (x - 18, y + 18)))
    m.add('w', poly(Kin))
    m.holes(rect(190, 470, 170, 90)); m.add('r', rect(200, 480, 150, 70), rect(240, 500, 70, 30))
    m.holes(poly([(360, 250), (450, 236), (430, 330)])); m.dome(412, 272, 18, 8)
    m.holes(rect(180, 290, 160, 34)); m.add('r', rect(188, 298, 144, 18))
    for cx, cy, r in ((300, 390, 26), (375, 430, 20), (270, 420, 16), (330, 450, 14)):
        m.holes(circ(cx, cy, r)); m.dome(cx, cy, r, 8)
    m.holes(ngon(345, 375, 14, 8)); m.add('r', ring(345, 375, 7))
    m.holes(cham(380, 560, 100, 70, 12)); m.add('r', ring(410, 595, 12), ring(450, 595, 12))
    # Alexander garden along the west wall
    m.add('w', poly([(36, 456), (84, 222), (330, 176), (335, 202), (106, 248), (62, 460)]))
    m.add('d', line((60, 440), (98, 236), (318, 192)))
    # Red Square with the mausoleum, Lobnoye Mesto, monument
    m.add('w', rect(545, 230, 120, 390))
    m.holes(rect(550, 370, 40, 54)); m.add('r', rect(556, 376, 28, 42), rect(562, 384, 16, 26))
    m.holes(circ(605, 585, 16)); m.add('r', ring(605, 585, 8))
    m.holes(rect(512, 640, 30, 24)); m.add('r', rect(518, 646, 18, 12))
    for y in range(260, 611, 35):
        m.add('t', line((600, y), (660, y)))
    m.add('t', line((600, 240), (600, 360)), line((600, 432), (600, 560)))
    # Vasilyevsky descent and St Basil's
    m.add('w', rect(500, 620, 230, 125))
    m.holes(circ(625, 682, 52)); m.dome(625, 682, 22, 8)
    for k in range(8):
        a = k * math.pi / 4
        m.dome(round(625 + 36 * math.cos(a), 1), round(682 + 36 * math.sin(a), 1), 10, 6)
    m.add('w', rect(580, 745, 70, 255))
    m.add('w', poly(bank[:1] + [(300, 772), (640, 832), (960, 802), (1280, 742), (1280, 790), (960, 850), (640, 880), (300, 820), (0, 860), (0, 812)]))
    m.steps(615, 746, 615, 790, 70)
    # Manezhnaya square with the mall domes, Resurrection gate passage
    m.add('w', poly([(360, 70), (530, 70), (530, 215), (400, 185)]))
    for cx in (420, 470):
        m.holes(circ(cx, 120, 18)); m.dome(cx, 120, 18, 8)
    m.holes(rect(440, 160, 60, 12))
    m.add('w', rect(520, 200, 30, 36))
    # Historical museum, GUM, Middle trading rows, Bolshoi
    m.hip(540, 130, 130, 70); m.add('r', rect(546, 136, 22, 22), rect(642, 136, 22, 22))
    m.flat(675, 230, 135, 160, 8)
    for x in (705, 742, 779):
        m.add('r', rect(x - 6, 240, 12, 140))
        for y in range(250, 381, 20): m.add('r', line((x - 6, y), (x + 6, y)))
    m.dome(742, 310, 16, 8)
    m.flat(675, 430, 135, 160, 8, 3, 3)
    m.flat(700, 50, 130, 110, 8); m.add('r', rect(716, 66, 98, 50))
    for x in range(716, 815, 14): m.add('r', ring(x, 136, 4))
    # Kitay-gorod streets and blocks
    m.add('w', rect(660, 190, 620, 32), rect(660, 395, 620, 30), rect(660, 595, 620, 30), rect(815, 160, 30, 465))
    m.add('w', cham(690, 160, 120, 30, 8))
    m.add('l', line((860, 206), (1270, 206)), line((860, 410), (1270, 410)), line((860, 610), (1270, 610)))
    m.court(855, 232, 170, 155, 905, 275, 70, 70)
    m.add('w', cham(905, 275, 70, 70, 10), rect(930, 345, 20, 50))
    m.hip(1035, 232, 95, 155); m.flat(1140, 232, 100, 155, 8, 2, 3)
    m.flat(855, 432, 80, 155, 8, 2, 4); m.hip(945, 432, 80, 155)
    m.court(1035, 432, 205, 155, 1085, 470, 100, 80)
    m.add('w', cham(1085, 470, 100, 80, 10), rect(1125, 425, 20, 45))
    m.add('t', ring(1135, 510, 22), ring(940, 310, 18))
    m.hip(860, 40, 170, 120); m.flat(1050, 40, 190, 120, 10, 6, 2)
    # Zaryadye park with the concert hall, amphitheatre and floating bridge
    park = [(700, 640), (1280, 640), (1280, 742), (960, 802), (700, 770)]
    m.add('b', poly(park))
    m.add('d', line((720, 700), (820, 668), (920, 700), (1020, 664), (1140, 690), (1260, 668)), line((820, 668), (850, 760)), line((1020, 664), (1060, 760)))
    m.hip(1120, 700, 130, 60); m.add('r', ring(900, 735, 30), ring(900, 735, 18))
    m.add('w', poly([(960, 800), (1040, 940), (1090, 940), (1010, 795)]))
    m.add('t', line((1000, 820), (1062, 928)))
    for x in (570, 715):
        m.steps(x, 228, x, 190, 30)
    return m

# ===================== Moscow, B1 metro =====================
def station(m, x, y, w):
    """Deep pylon station: two platforms and a central hall, tracks outside."""
    for ty in (y - 44, y + 164):
        m.add('b', rect(x - 60, ty, w + 120, 40))
        m.add('r', line((x - 60, ty + 12), (x + w + 60, ty + 12)), line((x - 60, ty + 28), (x + w + 60, ty + 28)))
        for k in range(x - 52, x + w + 60, 16): m.add('r', line((k, ty + 6), (k, ty + 34)))
    m.add('w', rect(x, y, w, 160))
    pylons(m, x + 16, x + w - 16, y + 40, 34, 18, 28); pylons(m, x + 16, x + w - 16, y + 102, 34, 18, 28)
    m.add('t', line((x + 8, y + 6), (x + w - 8, y + 6)), line((x + 8, y + 154), (x + w - 8, y + 154)))
    for k in range(x + 40, x + w - 20, 60): m.add('t', ring(k, y + 80, 9))
    m.add('t', line((x + 20, y + 80), (x + w - 20, y + 80)))

def moscow2():
    m = Map()
    m.add('f', poly([(30, 40), (560, 30), (600, 240), (40, 260)]), poly([(40, 600), (560, 640), (580, 960), (30, 960)]), poly([(1160, 200), (1270, 180), (1270, 560), (1180, 580)]))
    station(m, 160, 340, 400)
    station(m, 700, 140, 380)
    station(m, 700, 620, 380)
    # transfer corridors
    m.add('w', poly([(551, 406), (686, 266), (714, 294), (579, 434)]), rect(870, 300, 40, 320))
    m.steps(610, 362, 655, 315, 40, '4 4')
    m.steps(890, 380, 890, 540, 40, '4 4')
    # escalators and vestibules
    m.add('w', rect(110, 400, 52, 40), ngon(80, 420, 52, 8))
    m.steps(124, 420, 160, 420, 40, '3 3')
    m.holes(circ(80, 420, 15)); m.add('t', ngon(80, 420, 36, 8))
    m.add('w', rect(1078, 680, 92, 40), ngon(1200, 700, 66, 8))
    m.steps(1080, 700, 1150, 700, 40, '3 3')
    m.holes(circ(1200, 700, 18)); m.add('t', ngon(1200, 700, 46, 8), ring(1200, 700, 28))
    for k in range(8):
        a = k * math.pi / 4
        m.holes(rect(round(1200 + 54 * math.cos(a) - 5, 1), round(700 + 54 * math.sin(a) - 5, 1), 10, 10))
    m.add('w', rect(870, 20, 40, 122)); m.steps(890, 30, 890, 130, 40, '3 3')
    return m

# ===================== Home: superpower headquarters =====================
def jag(cx, cy, pts):
    return poly([(cx + x, cy + y) for x, y in pts])

def home1():
    m = Map()
    far(m, [(20, 40, 300, 80), (1100, 760, 170, 200), (20, 900, 400, 80)])
    # headquarters footprint
    m.add('b', cham(360, 120, 560, 620, 80))
    m.add('r', cham(380, 140, 520, 580, 70), line((360, 200), (380, 210)), line((920, 200), (900, 210)))
    # command hall with the emblem
    m.add('w', ngon(640, 430, 140, 8))
    m.holes(circ(640, 430, 46)); m.dome(640, 430, 46, 12); m.add('r', ngon(640, 430, 20, 6, 0))
    m.add('t', ngon(640, 430, 110, 8), ring(640, 430, 76))
    for k in range(8):
        a = math.pi / 8 + k * math.pi / 4
        m.add('t', line((round(640 + 80 * math.cos(a), 1), round(430 + 80 * math.sin(a), 1)), (round(640 + 125 * math.cos(a), 1), round(430 + 125 * math.sin(a), 1))))
    # corridors and wings
    m.add('w', cham(500, 150, 280, 80, 16), rect(615, 228, 50, 75), rect(770, 405, 60, 50), rect(450, 405, 60, 50),
          cham(820, 250, 80, 360, 16), cham(380, 250, 80, 360, 16), rect(615, 560, 50, 180), cham(520, 740, 240, 100, 20))
    for y in range(280, 600, 60):
        m.holes(rect(852, y, 16, 16), rect(412, y, 16, 16))
    for x in range(520, 760, 50):
        m.holes(rect(x + 8, 166, 30, 14))
    m.holes(rect(560, 200, 160, 12))
    m.add('t', line((640, 576), (640, 696)))
    m.steps(640, 700, 640, 742, 50)
    # gate plaza and road
    m.add('t', cham(536, 756, 208, 68, 14)); m.holes(rect(600, 776, 80, 20))
    m.add('w', rect(0, 860, 1280, 56)); m.add('l', line((10, 888), (1270, 888)))
    m.add('w', rect(590, 836, 100, 28)); m.steps(640, 838, 640, 862, 100, '4 4')
    # training ground: targets and cover walls
    m.add('w', cham(60, 260, 250, 330, 30), rect(305, 405, 80, 50))
    for cy in (330, 520):
        m.add('t', ring(130, cy, 34), ring(130, cy, 18)); m.holes(circ(130, cy, 7))
    m.holes(rect(200, 300, 60, 12), rect(230, 400, 12, 60), rect(190, 520, 70, 12))
    m.add('t', rect(80, 280, 210, 290))
    # helipad
    m.add('w', circ(1080, 200, 84), rect(900, 180, 100, 40))
    m.add('t', ring(1080, 200, 62), line((1060, 175), (1060, 225)), line((1100, 175), (1100, 225)), line((1060, 200), (1100, 200)))
    # ruined district: broken blocks standing in a rubble field, a crater
    m.add('w', poly([(940, 330), (1240, 320), (1262, 700), (980, 712), (930, 560)]))
    b1 = jag(1000, 370, [(0, 0), (120, -20), (130, 40), (100, 60), (140, 100), (60, 120), (20, 90), (-10, 60)])
    b2 = jag(1100, 560, [(20, -40), (110, -30), (120, 60), (60, 120), (0, 90), (30, 40)])
    m.holes(b1, b2)
    m.add('r', line((1010, 375), (1060, 430)), line((1110, 360), (1085, 440)), line((1005, 425), (1100, 395)),
          line((1130, 540), (1180, 640)), line((1205, 535), (1160, 660)))
    m.holes(jag(960, 500, [(0, 0), (40, -10), (30, 25)]), jag(1045, 660, [(0, 0), (50, 10), (20, 40)]),
            jag(1180, 420, [(0, 0), (30, 10), (10, 30)]), jag(1200, 680, [(0, 0), (26, -8), (18, 16)]))
    m.add('t', ring(1020, 590, 50), ring(1020, 590, 26), line((975, 560), (995, 578)), line((1060, 545), (1043, 568)), line((1065, 630), (1043, 610)))
    # intact buildings around
    m.hip(80, 650, 200, 120); m.flat(120, 120, 180, 100, 10, 4, 2); m.flat(1000, 760, 180, 80, 10, 4, 1)
    return m

# ===================== Home: modern city =====================
def plus(m, cx, cy, a, b):
    pts = [(cx - b, cy - a), (cx + b, cy - a), (cx + b, cy - b), (cx + a, cy - b), (cx + a, cy + b), (cx + b, cy + b),
           (cx + b, cy + a), (cx - b, cy + a), (cx - b, cy + b), (cx - a, cy + b), (cx - a, cy - b), (cx - b, cy - b)]
    m.add('b', poly(pts)); m.add('r', rect(cx - b + 8, cy - b + 8, 2 * b - 16, 2 * b - 16), line((cx, cy - a + 8), (cx, cy + a - 8)), line((cx - a + 8, cy), (cx + a - 8, cy)))

def home2():
    m = Map()
    far(m, [(20, 40, 260, 120), (1180, 420, 100, 80)])
    # roads, lanes and crossings
    m.add('w', rect(0, 430, 1280, 80), rect(560, 0, 70, 430), rect(560, 510, 70, 490), rect(900, 510, 50, 330))
    m.add('l', line((10, 470), (550, 470)), line((640, 470), (1270, 470)), line((595, 10), (595, 420)), line((595, 520), (595, 990)))
    for x in (520, 670, 925):
        m.steps(x, 432, x, 508, 60, '10 8')
    m.steps(595, 400, 595, 428, 70, '10 8'); m.steps(595, 512, 595, 540, 70, '10 8')
    # company tower and its plaza
    m.add('w', cham(680, 60, 560, 330, 30))
    m.holes(rect(830, 100, 240, 220))
    m.add('r', rect(846, 116, 208, 188), rect(870, 140, 160, 140), ring(950, 210, 48), line((935, 190), (935, 230)), line((965, 190), (965, 230)), line((935, 210), (965, 210)))
    m.holes(circ(740, 300, 32)); m.dome(740, 300, 32, 8)
    for x in range(700, 820, 40): m.holes(rect(x, 100, 22, 22))
    for y in range(110, 360, 50): m.holes(rect(1110, y, 22, 22))
    m.add('t', rect(696, 76, 528, 298), line((950, 320), (950, 386)))
    m.holes(rect(900, 330, 100, 14))
    m.add('w', rect(1170, 150, 110, 40)); m.add('d', line((1180, 170), (1270, 170)))
    # cafe with terrace
    m.hip(300, 200, 220, 150)
    m.add('w', rect(300, 350, 220, 80))
    for x in range(320, 510, 45):
        m.holes(circ(x + 10, 375, 9), circ(x + 10, 410, 9))
    # school, schoolyard and track
    m.add('b', poly([(110, 550), (530, 550), (530, 640), (220, 640), (220, 790), (110, 790)]))
    m.add('r', poly([(122, 562), (518, 562), (518, 628), (208, 628), (208, 778), (122, 778)]))
    for x in range(160, 520, 40): m.add('r', line((x, 562), (x, 628)))
    for y in range(600, 790, 40): m.add('r', line((122, y), (208, y)))
    m.add('w', rect(240, 660, 300, 300), rect(530, 600, 30, 40))
    m.holes(circ(390, 810, 96, ry=66))
    m.add('r', ring(390, 810, 26), line((390, 744), (390, 876)), rect(294, 780, 26, 60), rect(460, 780, 26, 60))
    m.add('t', ring(390, 810, 114, 84), ring(390, 810, 130, 100))
    m.steps(545, 620, 560, 620, 40)
    # convenience store with awning, parking lot
    m.flat(650, 540, 140, 90, 8); m.add('r', line((650, 560), (790, 560)))
    for x in range(656, 790, 16): m.add('r', line((x, 540), (x, 560)))
    m.add('w', rect(680, 510, 80, 30))
    m.add('w', rect(650, 660, 230, 220))
    stalls(m, 666, 866, 670, 740, 28); stalls(m, 666, 866, 800, 870, 28)
    m.add('t', line((660, 770), (870, 770)))
    # apartment towers (cross plan) and their paths
    m.add('w', rect(950, 560, 330, 44), rect(950, 760, 330, 44), rect(1100, 604, 40, 156))
    for cx, cy in ((1030, 680), (1210, 680), (1030, 880), (1210, 880)):
        plus(m, cx, cy, 62, 26)
    m.add('d', line((960, 582), (1270, 582)), line((960, 782), (1270, 782)))
    return m

# ===================== Home: the ship =====================
def home3():
    m = Map()
    m.add('v', rect(0, 0, 1280, 1000))
    for y, x0, x1 in ((80, 80, 400), (130, 500, 900), (60, 940, 1220), (220, 60, 260), (250, 1000, 1240), (720, 1060, 1260), (980, 300, 900)):
        m.add('vw', line((x0, y), (x1, y)))
    hull = [(120, 370), (200, 320), (900, 320), (1060, 380), (1200, 495), (1060, 610), (900, 670), (200, 670), (120, 620)]
    m.add('w', poly(hull))
    m.add('t', poly([(140, 378), (208, 338), (896, 338), (1050, 394), (1176, 495), (1050, 596), (896, 652), (208, 652), (140, 612)]))
    # superstructure with bridge, funnel and mast
    m.holes(rect(280, 390, 330, 210))
    m.add('r', rect(292, 402, 306, 186), rect(520, 410, 70, 170))
    for y in range(420, 581, 20): m.add('r', line((530, y), (580, y)))
    m.dome(410, 495, 44, 12); m.add('r', ring(320, 440, 12), ring(320, 550, 12))
    # lifeboats on davits
    for x in (300, 450):
        for y in (336, 638):
            m.holes(cham(x, y, 120, 26, 10)); m.add('r', line((x + 14, y + 13), (x + 106, y + 13)))
    # cargo hatches and crane posts
    for y in (410, 515):
        m.holes(rect(680, y, 100, 72)); m.add('r', rect(688, y + 8, 84, 56), line((730, y + 8), (730, y + 64)))
    for x, y in ((830, 420), (830, 570), (650, 495)):
        m.holes(circ(x, y, 16)); m.add('r', ring(x, y, 7))
    # foredeck: gun mount, anchor winches and chains
    m.holes(circ(960, 495, 34)); m.dome(960, 495, 34, 8)
    for y in (465, 525):
        m.holes(circ(1060, y, 14)); m.add('r', ring(1060, y, 6))
        m.add('d', line((1074, y), (1150, 495)))
    for x in range(880, 1031, 30):
        m.add('t', line((x, 350), (x, 440)), line((x, 550), (x, 640)))
    # stern helipad
    m.add('t', ring(200, 495, 64), ring(200, 495, 50), line((182, 470), (182, 520)), line((218, 470), (218, 520)), line((182, 495), (218, 495)))
    # gangway and pier with bollards and mooring lines
    m.add('w', rect(500, 670, 60, 120), rect(0, 790, 1280, 120))
    m.steps(530, 674, 530, 786, 60, '5 5')
    m.add('t', line((0, 800), (1280, 800)), line((0, 900), (1280, 900)))
    m.add('l', line((0, 860), (1280, 860)))
    for x in (140, 360, 760, 980, 1180):
        m.holes(circ(x, 820, 10))
    m.add('t', line((140, 812), (230, 662)), line((360, 812), (300, 670)), line((760, 812), (820, 668)), line((980, 812), (950, 660)))
    m.flat(860, 920, 260, 70, 8, 5, 1); m.flat(120, 920, 260, 70, 8, 5, 1)
    return m

MAPS = {'n1': norilsk1, 'n2': norilsk2, 'm1': moscow1, 'm2': moscow2, 's1': home1, 's2': home2, 's3': home3}

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    for k, f in MAPS.items():
        if len(sys.argv) > 1 and k not in sys.argv[1:]: continue
        s = f().svg()
        open(os.path.join(here, k + '.svg'), 'w').write(s)
        print(k, len(s))
