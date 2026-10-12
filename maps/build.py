"""Builds the Star Rail style floor maps used by star-rail-map.html.
Run: python3 build.py [n1 n2 ...]   (writes <name>.svg next to this file)

Canvas is 1280 x 1000, the same 1.28 aspect as the map box in the widget,
so a point (x, y) here sits at left:x/12.8%  top:y/10% in the widget.

Drawing follows the in-game maps: a near-black walkable surface with no
outline and only large faint floor inlays, mid-grey for other levels
(terraces, quays, landings) with light stair stripes, light grey pillars
and objects, and soft low-contrast blocks for everything else."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import Map
from pl import rect, rr, cham, ngon, circ, poly, line, ring, fillet

def pt(cx, cy, r, a):
    return (round(cx + r * math.cos(a), 1), round(cy + r * math.sin(a), 1))

def inlay(m, cx, cy, rings=(), spokes=0, r0=0, r1=0, rot=0):
    """Large faint floor pattern: concentric rings and spokes."""
    for q in rings: m.add('t', ring(cx, cy, q))
    for k in range(spokes):
        a = rot + 2 * math.pi * k / spokes
        m.add('t', line(pt(cx, cy, r0, a), pt(cx, cy, r1, a)))

def pillars(m, pts, size=16):
    for x, y in pts: m.holes(rect(x - size / 2, y - size / 2, size, size))

# ===================== Norilsk, street level =====================
def norilsk1():
    m = Map(11)
    m.far_city()
    m.add('v', poly([(0, 900), (180, 884), (420, 892), (640, 878), (860, 896), (1080, 882), (1280, 890), (1280, 1000), (0, 1000)]))
    for y, x0, x1 in ((925, 60, 380), (948, 300, 560), (930, 720, 1010), (955, 880, 1200), (975, 120, 420)):
        m.add('vw', line((x0, y), (x1, y)))
    # closed courtyard blocks typical of Norilsk
    m.court(510, 250, 220, 190, 560, 290, 140, 110)
    m.court(790, 250, 160, 190, 820, 290, 100, 110)
    m.court(510, 540, 220, 230, 560, 580, 140, 140)
    m.court(790, 540, 160, 230, 820, 580, 100, 140)
    m.flat(510, 90, 220, 100, 10, 5, 2); m.hip(790, 110, 160, 80); m.flat(1010, 90, 230, 100, 10, 6, 2)
    m.hip(370, 250, 80, 190); m.hip(370, 540, 80, 230)
    m.hip(60, 250, 140, 120); m.flat(275, 250, 75, 110, 8)
    m.flat(60, 620, 140, 170, 10, 2, 3); m.hip(275, 620, 75, 170)
    m.flat(1010, 250, 220, 110, 10); m.dome(1170, 305, 38, 12); m.add('r', rect(1030, 270, 60, 70), line((1030, 305), (1090, 305)))
    m.flat(1010, 630, 220, 140, 10, 4, 2)
    # Gvardeyskaya square with four bays
    m.add('w', circ(240, 490, 115))
    for a in (math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4):
        m.apse(*pt(240, 490, 108, a), 22)
    m.holes(ngon(240, 490, 40, 4, math.pi / 4))
    m.add('r', ngon(240, 490, 28, 4, math.pi / 4), ring(240, 490, 12))
    inlay(m, 240, 490, (62, 88, 104), 8, 62, 104, math.pi / 8)
    m.add('t', ngon(240, 490, 52, 4, math.pi / 4))
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        m.steps(240 + dx * 41, 490 + dy * 41, 240 + dx * 54, 490 + dy * 54, 34, '3 4')
    # Leninsky prospekt and the street grid
    m.wr(340, 450, 720, 80); m.wr(40, 450, 90, 80); m.wr(1215, 450, 65, 80)
    m.wr(220, 250, 40, 130); m.wr(220, 600, 40, 220)
    m.wr(460, 130, 40, 320); m.wr(460, 530, 40, 290); m.wr(740, 200, 40, 250); m.wr(740, 530, 40, 290)
    m.wr(960, 200, 40, 250); m.wr(960, 530, 40, 290); m.wr(400, 200, 640, 40)
    m.add('w', cham(170, 185, 140, 70, 18))
    m.isl(370, 481, 70, 18, 3); m.isl(530, 481, 190, 18, 7); m.isl(800, 481, 140, 18, 5)
    m.add('t', line((355, 462), (1045, 462)), line((355, 518), (1045, 518)))
    # Metallurgists' square
    m.add('w', cham(1040, 370, 180, 240, 45))
    m.apse(1130, 370, 36); m.apse(1130, 610, 36)
    m.holes(circ(1130, 490, 34)); m.add('r', ring(1130, 490, 24), ring(1130, 490, 10))
    inlay(m, 1130, 490, (60, 84)); m.add('t', ngon(1130, 490, 100, 8))
    pillars(m, ((1075, 405), (1185, 405), (1075, 575), (1185, 575)), 18)
    # courtyards with arches to the prospekt and round bays
    for cx, cy, cw, ch, ax in ((560, 290, 140, 110, 615), (820, 290, 100, 110, 855), (560, 580, 140, 140, 615), (820, 580, 100, 140, 855)):
        m.add('w', cham(cx, cy, cw, ch, 14))
        m.wr(ax, cy + ch if cy < 450 else 530, 30, 50)
        m.apse(cx + cw / 2, cy if cy < 450 else cy + ch, 18)
        inlay(m, cx + cw / 2, cy + ch / 2, (min(cw, ch) * .3, min(cw, ch) * .16))
    pillars(m, ((600, 330), (660, 330), (600, 680), (660, 680)), 18)
    # lower embankment promenade, pier and the lookout
    m.add('w2', rect(200, 822, 1020, 42), rect(880, 864, 40, 40), ngon(900, 945, 52, 8))
    for x in range(260, 1200, 120): m.add('t', line((x, 826), (x, 860)))
    for x in (240, 480, 760, 980):
        m.wr(x - 20, 780, 40, 42)
        m.steps(x, 790, x, 822, 40)
    m.holes(circ(900, 945, 14)); m.add('t', ngon(900, 945, 36, 8))
    m.steps(900, 866, 900, 896, 40)
    m.steps(240, 252, 240, 284, 40)
    m.add('d', line((940, 945), (1040, 930), (1140, 922)))
    m.auto_fillets(14)
    return m

# ===================== Norilsk, B1 mine =====================
def norilsk2():
    m = Map(12)
    m.far_rock(70)
    m.wr(130, 465, 420, 60); m.wr(730, 465, 400, 60)
    m.add('w', circ(640, 495, 96))
    m.wr(615, 180, 50, 225); m.wr(615, 585, 50, 150)
    m.add('w', cham(500, 90, 280, 100, 25), cham(470, 730, 340, 130, 30),
          cham(130, 270, 240, 140, 30), cham(900, 270, 250, 140, 30), cham(150, 600, 240, 150, 30), cham(890, 600, 260, 150, 30))
    m.wr(225, 405, 50, 65); m.wr(1000, 405, 50, 65); m.wr(240, 520, 50, 85); m.wr(990, 520, 50, 85)
    m.apse(640, 860, 40); m.apse(130, 340, 30); m.apse(1150, 340, 30); m.apse(270, 750, 30); m.apse(1020, 750, 30)
    # shaft hall: hoist cage, four columns, floor rings
    m.holes(rect(605, 460, 70, 70)); m.add('r', rect(613, 468, 54, 54), line((613, 468), (667, 522)), line((667, 468), (613, 522)))
    pillars(m, [(640 + dx * 62, 495 + dy * 62) for dx in (-1, 1) for dy in (-1, 1)], 18)
    inlay(m, 640, 495, (50, 80), 8, 50, 80)
    # rails along the haulage gallery and the north drift
    for x0, x1 in ((140, 545), (735, 1120)):
        m.add('t', line((x0, 486), (x1, 486)), line((x0, 504), (x1, 504)))
    m.add('t', line((631, 195), (631, 395)), line((649, 195), (649, 395)))
    for x in (330, 880):
        m.holes(rect(x, 481, 46, 28)); m.add('r', rect(x + 6, 487, 34, 16))
    # winding engine drums, canteen counter, pump room, ore bunkers, banya pools
    m.holes(rect(560, 112, 60, 50), rect(660, 112, 60, 50)); m.add('r', ring(590, 137, 16), ring(690, 137, 16))
    m.holes(rect(160, 380, 180, 18))
    pillars(m, ((200, 320), (250, 320), (300, 320)), 18)
    m.holes(rect(930, 300, 50, 50), rect(1000, 300, 50, 50), rect(1070, 300, 50, 50))
    m.add('r', ring(955, 325, 14), ring(1025, 325, 14), ring(1095, 325, 14))
    for c in range(4):
        m.holes(ngon(530 + c * 75, 795, 26, 6))
    m.add('v', rect(920, 630, 90, 60), circ(1090, 670, 34))
    m.add('w', rect(920, 630, 90, 60, True), circ(1090, 670, 34, True))
    inlay(m, 1090, 670, (46,)); m.add('t', rect(910, 620, 110, 80))
    m.holes(rect(175, 630, 60, 50), rect(255, 630, 60, 50)); m.add('r', rect(185, 640, 40, 30), rect(265, 640, 40, 30))
    # shafts up to the surface: landings on another level
    m.add('w2', rect(225, 190, 50, 85), rect(1000, 190, 50, 85), cham(60, 470, 80, 50, 14), cham(1120, 470, 100, 50, 14))
    m.steps(250, 200, 250, 266, 50); m.steps(1025, 200, 1025, 266, 50)
    m.steps(90, 495, 128, 495, 50); m.steps(1132, 495, 1190, 495, 50)
    m.add('d', line((640, 590), (640, 730)))
    m.auto_fillets(14)
    return m

# ===================== Moscow, street level =====================
def moscow1():
    m = Map(21)
    m.far_city()
    bank = [(0, 860), (300, 820), (640, 880), (960, 850), (1280, 790)]
    m.add('v', poly(bank + [(1280, 890), (960, 950), (640, 980), (300, 920), (0, 960)]))
    for (x0, y0), (x1, y1) in zip(bank, bank[1:]):
        m.add('vw', line((x0 + 40, y0 + 45), (x1 - 40, y1 + 45)))
    # Kremlin: wall with towers, palaces and cathedrals
    Kout = [(150, 250), (470, 190), (535, 575), (450, 680), (190, 660), (105, 430)]
    Kin = [(170, 270), (455, 216), (512, 572), (437, 656), (204, 638), (128, 432)]
    m.add('b2', poly(Kout)); m.add('r', poly(Kin))
    for x, y in Kout + [(310, 220), (502, 380), (320, 670), (128, 340)]:
        m.add('b', rect(x - 18, y - 18, 36, 36)); m.add('r', rect(x - 10, y - 10, 20, 20), line((x - 18, y - 18), (x + 18, y + 18)), line((x + 18, y - 18), (x - 18, y + 18)))
    m.add('w', poly(Kin))
    m.holes(rect(190, 470, 170, 90)); m.add('r', rect(200, 480, 150, 70), rect(240, 500, 70, 30))
    m.holes(poly([(360, 250), (450, 236), (430, 330)])); m.dome(412, 272, 18, 8)
    m.holes(rect(180, 290, 160, 34)); m.add('r', rect(188, 298, 144, 18))
    for cx, cy, r in ((300, 390, 26), (375, 430, 20), (270, 420, 16), (330, 450, 14)):
        m.holes(circ(cx, cy, r)); m.dome(cx, cy, r, 8)
    m.holes(ngon(345, 375, 14, 8)); m.add('r', ring(345, 375, 7))
    m.holes(cham(380, 560, 100, 70, 12)); m.add('r', ring(410, 595, 12), ring(450, 595, 12))
    # Alexander garden walk outside the west wall
    m.add('w', poly([(36, 456), (84, 222), (330, 176), (335, 202), (106, 248), (62, 460)]))
    # Red Square
    m.wr(545, 230, 120, 390)
    m.holes(rect(550, 370, 40, 54)); m.add('r', rect(556, 376, 28, 42), rect(562, 384, 16, 26))
    m.holes(circ(605, 585, 16)); m.add('r', ring(605, 585, 8))
    m.holes(rect(512, 640, 30, 24))
    for y in range(265, 611, 70):
        m.add('t', line((600, y), (660, y)))
    m.add('t', line((600, 240), (600, 360)), line((600, 432), (600, 560)))
    # Vasilyevsky descent with St Basil's
    m.add('w', rect(500, 620, 230, 125)); m.apse(500, 682, 30)
    m.holes(circ(625, 682, 52)); m.dome(625, 682, 22, 8)
    for k in range(8):
        m.dome(*pt(625, 682, 36, k * math.pi / 4), 10, 6)
    # bridge on the upper level, embankment below it
    m.wr(580, 745, 70, 255)
    m.add('w2', poly([(0, 812), (300, 772), (640, 832), (960, 802), (1280, 742), (1280, 790), (960, 850), (640, 880), (300, 820), (0, 860)]))
    m.wr(510, 745, 50, 40); m.wr(680, 745, 50, 40)
    m.add('w2', rect(510, 782, 50, 40), rect(680, 782, 50, 48))
    m.steps(535, 772, 535, 818, 50); m.steps(705, 772, 705, 826, 50)
    # Manezhnaya square, Resurrection gate, Historical museum, GUM, rows, Bolshoi
    m.add('w', poly([(360, 70), (530, 70), (530, 215), (400, 185)]))
    for cx in (420, 470):
        m.holes(circ(cx, 120, 18)); m.dome(cx, 120, 18, 8)
    m.wr(520, 200, 30, 36)
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
    m.wr(660, 190, 620, 32); m.wr(660, 395, 620, 30); m.wr(660, 595, 620, 30); m.wr(815, 160, 30, 465)
    m.add('w', cham(690, 160, 120, 30, 8))
    m.court(855, 232, 170, 155, 905, 275, 70, 70)
    m.add('w', cham(905, 275, 70, 70, 10)); m.wr(930, 345, 20, 50); m.apse(940, 275, 14)
    m.hip(1035, 232, 95, 155); m.flat(1140, 232, 100, 155, 8, 2, 3)
    m.flat(855, 432, 80, 155, 8, 2, 4); m.hip(945, 432, 80, 155)
    m.court(1035, 432, 205, 155, 1085, 470, 100, 80)
    m.add('w', cham(1085, 470, 100, 80, 10)); m.wr(1125, 425, 20, 45); m.apse(1135, 550, 16)
    inlay(m, 1135, 510, (22,)); inlay(m, 940, 310, (18,))
    m.hip(860, 40, 170, 120); m.flat(1050, 40, 190, 120, 10, 6, 2)
    # Zaryadye park: lawn with paths, concert hall, amphitheatre, floating bridge
    m.add('b', poly([(700, 640), (1280, 640), (1280, 742), (960, 802), (700, 770)]))
    m.add('d', line((720, 700), (820, 668), (920, 700), (1020, 664), (1140, 690), (1260, 668)), line((820, 668), (850, 760)), line((1020, 664), (1060, 760)))
    m.hip(1120, 700, 130, 60); m.add('r', ring(900, 735, 30), ring(900, 735, 18))
    m.add('w', poly([(960, 800), (1040, 940), (1090, 940), (1010, 795)]))
    for x in (570, 715):
        m.steps(x, 228, x, 196, 30)
    m.auto_fillets(12)
    return m

# ===================== Moscow, B1 metro =====================
def station(m, x, y, w):
    """Deep pylon station: two platforms and a central hall, tracks outside."""
    for ty in (y - 44, y + 164):
        m.add('b2', rect(x - 60, ty, w + 120, 40))
        m.add('r', line((x - 60, ty + 12), (x + w + 60, ty + 12)), line((x - 60, ty + 28), (x + w + 60, ty + 28)))
        for k in range(x - 52, x + w + 60, 16): m.add('r', line((k, ty + 6), (k, ty + 34)))
    m.wr(x, y, w, 160)
    for row in (y + 40, y + 102):
        k = x + 16
        while k + 34 <= x + w - 16:
            m.obj(rect(k, row, 34, 18)); k += 62
    m.add('t', line((x + 8, y + 6), (x + w - 8, y + 6)), line((x + 8, y + 154), (x + w - 8, y + 154)), line((x + 20, y + 80), (x + w - 20, y + 80)))
    for k in range(x + 40, x + w - 20, 60): m.add('t', ring(k, y + 80, 9))

def moscow2():
    m = Map(22)
    m.far_rock(70)
    station(m, 160, 340, 400)
    station(m, 700, 140, 380)
    station(m, 700, 620, 380)
    # transfer passages
    m.add('w', poly([(551, 406), (686, 266), (714, 294), (579, 434)]))
    m.wr(870, 300, 40, 320)
    m.add('t', line((878, 310), (878, 610)), line((902, 310), (902, 610)))
    # escalator tubes on another level, round vestibules
    m.add('w2', poly([(590, 392), (650, 330), (668, 348), (608, 410)]), rect(870, 380, 40, 160), rect(110, 400, 52, 40), rect(1078, 680, 92, 40), rect(870, 20, 40, 122))
    m.steps(612, 380, 650, 340, 40, '4 4'); m.steps(890, 390, 890, 530, 40, '4 4')
    m.steps(116, 420, 160, 420, 40, '3 3'); m.steps(1082, 700, 1150, 700, 40, '3 3'); m.steps(890, 30, 890, 130, 40, '3 3')
    m.add('w', ngon(80, 420, 52, 8), ngon(1200, 700, 66, 8))
    m.holes(circ(80, 420, 15)); m.add('t', ngon(80, 420, 36, 8))
    m.holes(circ(1200, 700, 18)); m.add('t', ngon(1200, 700, 46, 8), ring(1200, 700, 28))
    pillars(m, [pt(1200, 700, 54, k * math.pi / 4) for k in range(8)], 10)
    m.auto_fillets(12)
    return m

# ===================== Home: superpower headquarters =====================
def jag(cx, cy, pts):
    return poly([(cx + x, cy + y) for x, y in pts])

def home1():
    m = Map(31)
    m.far_city()
    m.add('b2', cham(360, 120, 560, 620, 80))
    m.add('r', cham(380, 140, 520, 580, 70), cham(400, 160, 480, 540, 60))
    # command hall with the emblem
    m.add('w', ngon(640, 430, 140, 8))
    m.holes(circ(640, 430, 46)); m.dome(640, 430, 46, 12); m.add('r', ngon(640, 430, 20, 6, 0))
    m.add('t', ngon(640, 430, 112, 8)); inlay(m, 640, 430, (76,), 8, 80, 126, math.pi / 8)
    pillars(m, [pt(640, 430, 96, k * math.pi / 6) for k in range(12)], 12)
    # corridors and wings with bays
    m.add('w', cham(500, 150, 280, 80, 16), cham(820, 250, 80, 360, 16), cham(380, 250, 80, 360, 16))
    m.wr(615, 228, 50, 75); m.wr(770, 405, 60, 50); m.wr(450, 405, 60, 50); m.wr(615, 560, 50, 180)
    m.apse(640, 150, 30); m.apse(900, 430, 26); m.apse(380, 430, 26)
    pillars(m, [(860, y) for y in range(290, 590, 60)] + [(420, y) for y in range(290, 590, 60)], 16)
    for x in range(536, 760, 50): m.holes(rect(x, 166, 30, 14))
    m.add('t', line((640, 576), (640, 696)))
    for x0 in (380, 820):
        for y in (320, 400, 480, 560): m.add('t', line((x0 + 10, y), (x0 + 70, y)))
    # gate terrace one level down, the road beyond
    m.add('w2', cham(520, 740, 240, 100, 20), rect(590, 836, 100, 28))
    m.steps(640, 700, 640, 742, 50); m.steps(640, 838, 640, 862, 100, '4 4')
    m.holes(rect(600, 776, 80, 20))
    m.wr(0, 860, 1280, 56)
    # training ground: targets and cover walls
    m.add('w', cham(60, 260, 250, 330, 30)); m.wr(305, 405, 80, 50); m.apse(60, 425, 30)
    for cy in (330, 520):
        inlay(m, 130, cy, (34, 18)); m.holes(circ(130, cy, 7))
    m.holes(rect(200, 300, 60, 12), rect(230, 400, 12, 60), rect(190, 520, 70, 12))
    m.add('t', rect(80, 280, 210, 290), line((70, 470), (300, 470)))
    # helipad
    m.add('w', circ(1080, 200, 84)); m.wr(900, 180, 100, 40)
    m.add('t', ring(1080, 200, 62), line((1060, 175), (1060, 225)), line((1100, 175), (1100, 225)), line((1060, 200), (1100, 200)))
    m.add('d', ring(1080, 200, 74))
    # ruined district: broken blocks in a rubble field, a crater
    m.add('w', poly([(940, 330), (1240, 320), (1262, 700), (980, 712), (930, 560)]))
    m.holes(jag(1000, 370, [(0, 0), (120, -20), (130, 40), (100, 60), (140, 100), (60, 120), (20, 90), (-10, 60)]),
            jag(1100, 560, [(20, -40), (110, -30), (120, 60), (60, 120), (0, 90), (30, 40)]))
    m.add('r', line((1010, 375), (1060, 430)), line((1110, 360), (1085, 440)), line((1005, 425), (1100, 395)),
          line((1130, 540), (1180, 640)), line((1205, 535), (1160, 660)))
    m.holes(jag(960, 500, [(0, 0), (40, -10), (30, 25)]), jag(1045, 660, [(0, 0), (50, 10), (20, 40)]),
            jag(1180, 420, [(0, 0), (30, 10), (10, 30)]))
    inlay(m, 1020, 590, (50, 26))
    m.add('t', line((975, 560), (995, 578)), line((1060, 545), (1043, 568)), line((1065, 630), (1043, 610)))
    m.hip(80, 650, 200, 120); m.flat(120, 120, 180, 100, 10, 4, 2); m.flat(1000, 760, 180, 80, 10, 4, 1)
    m.auto_fillets(12)
    return m

# ===================== Home: modern city =====================
def plus(m, cx, cy, a, b):
    pts = [(cx - b, cy - a), (cx + b, cy - a), (cx + b, cy - b), (cx + a, cy - b), (cx + a, cy + b), (cx + b, cy + b),
           (cx + b, cy + a), (cx - b, cy + a), (cx - b, cy + b), (cx - a, cy + b), (cx - a, cy - b), (cx - b, cy - b)]
    m.add('b', poly(pts)); m.add('r', rect(cx - b + 8, cy - b + 8, 2 * b - 16, 2 * b - 16), line((cx, cy - a + 8), (cx, cy + a - 8)), line((cx - a + 8, cy), (cx + a - 8, cy)))

def home2():
    m = Map(32)
    m.far_city()
    m.wr(0, 430, 1280, 80); m.wr(560, 0, 70, 430); m.wr(560, 510, 70, 490); m.wr(900, 510, 50, 330)
    m.add('t', line((0, 470), (550, 470)), line((640, 470), (1280, 470)))
    # company tower on its plaza
    m.add('w', cham(680, 60, 560, 330, 30)); m.apse(680, 225, 34)
    m.holes(rect(830, 100, 240, 220))
    m.add('r', rect(846, 116, 208, 188), rect(870, 140, 160, 140), ring(950, 210, 48), line((935, 190), (935, 230)), line((965, 190), (965, 230)), line((935, 210), (965, 210)))
    m.holes(circ(740, 300, 32)); m.dome(740, 300, 32, 8); inlay(m, 740, 300, (50,))
    pillars(m, [(712 + k * 40, 112) for k in range(3)] + [(1122, y) for y in range(122, 360, 50)], 22)
    m.add('t', rect(696, 76, 528, 298), line((950, 320), (950, 386)))
    m.wr(1170, 150, 110, 40)
    # cafe with a terrace a step down
    m.hip(300, 200, 220, 150)
    m.add('w2', rect(300, 350, 220, 80)); m.steps(410, 352, 410, 428, 160, '4 6')
    # school, schoolyard and track
    m.add('b', poly([(110, 550), (530, 550), (530, 640), (220, 640), (220, 790), (110, 790)]))
    m.add('r', poly([(122, 562), (518, 562), (518, 628), (208, 628), (208, 778), (122, 778)]))
    for x in range(160, 520, 40): m.add('r', line((x, 562), (x, 628)))
    for y in range(600, 790, 40): m.add('r', line((122, y), (208, y)))
    m.add('w', rect(240, 660, 300, 300)); m.wr(530, 600, 30, 40)
    m.holes(circ(390, 810, 96, ry=66))
    m.add('r', ring(390, 810, 26), line((390, 744), (390, 876)), rect(294, 780, 26, 60), rect(460, 780, 26, 60))
    m.add('t', ring(390, 810, 114, 84), ring(390, 810, 130, 100), rect(258, 676, 60, 34), rect(462, 676, 60, 34))
    # convenience store, parking deck a level down, apartment towers
    m.flat(650, 540, 140, 90, 8); m.add('r', line((650, 560), (790, 560)))
    for x in range(656, 790, 16): m.add('r', line((x, 540), (x, 560)))
    m.wr(680, 510, 80, 30)
    m.add('w2', rect(650, 660, 230, 220))
    for x in range(666, 870, 28): m.add('t', line((x, 670), (x, 740)), line((x, 800), (x, 870)))
    m.steps(765, 642, 765, 662, 80)
    m.wr(725, 630, 80, 30)
    m.wr(950, 560, 330, 44); m.wr(950, 760, 330, 44); m.wr(1100, 604, 40, 156)
    for cx, cy in ((1030, 680), (1210, 680), (1030, 880), (1210, 880)):
        plus(m, cx, cy, 62, 26)
    m.add('d', line((960, 582), (1270, 582)), line((960, 782), (1270, 782)))
    m.auto_fillets(16)
    return m

# ===================== Home: the ship =====================
def home3():
    m = Map(33)
    m.add('v', rect(0, 0, 1280, 1000))
    R = m.rng
    for _ in range(70):
        x = R.uniform(0, 1240); y = R.uniform(0, 1000); L = R.uniform(30, 160)
        if 300 < y < 690 and 100 < x < 1220: continue
        m.add('vw', line((round(x, 1), round(y, 1)), (round(x + L, 1), round(y, 1))))
    hull = [(120, 370), (200, 320), (900, 320), (1060, 380), (1200, 495), (1060, 610), (900, 670), (200, 670), (120, 620)]
    m.add('w', poly(hull))
    m.add('t', poly([(140, 378), (208, 338), (896, 338), (1050, 394), (1176, 495), (1050, 596), (896, 652), (208, 652), (140, 612)]))
    # superstructure with bridge, funnel and mast
    m.holes(rect(280, 390, 330, 210))
    m.add('r', rect(292, 402, 306, 186), rect(520, 410, 70, 170))
    for y in range(420, 581, 20): m.add('r', line((530, y), (580, y)))
    m.dome(410, 495, 44, 12); m.add('r', ring(320, 440, 12), ring(320, 550, 12))
    for x in (300, 450):
        for y in (336, 638):
            m.holes(cham(x, y, 120, 26, 10)); m.add('r', line((x + 14, y + 13), (x + 106, y + 13)))
    for y in (410, 515):
        m.holes(rect(680, y, 100, 72)); m.add('r', rect(688, y + 8, 84, 56), line((730, y + 8), (730, y + 64)))
    pillars(m, ((830, 420), (830, 570), (650, 495)), 24)
    m.holes(circ(960, 495, 34)); m.dome(960, 495, 34, 8)
    pillars(m, ((1060, 465), (1060, 525)), 20)
    m.add('d', line((1074, 465), (1150, 495)), line((1074, 525), (1150, 495)))
    for x in range(880, 1031, 30):
        m.add('t', line((x, 350), (x, 440)), line((x, 550), (x, 640)))
    m.add('t', ring(200, 495, 64), ring(200, 495, 50), line((182, 470), (182, 520)), line((218, 470), (218, 520)), line((182, 495), (218, 495)))
    m.add('d', poly([(150, 380), (205, 348), (895, 348), (1045, 404), (1160, 495), (1045, 586), (895, 642), (205, 642), (150, 610)]))
    # gangway down to the quay, which sits a level lower
    m.add('w2', rect(500, 670, 60, 120), rect(0, 790, 1280, 120))
    m.steps(530, 674, 530, 786, 60, '5 5')
    m.add('t', line((0, 800), (1280, 800)), line((0, 900), (1280, 900)))
    for x in (140, 360, 760, 980, 1180):
        m.obj(circ(x, 820, 10))
    m.add('t', line((140, 812), (230, 662)), line((360, 812), (300, 670)), line((760, 812), (820, 668)), line((980, 812), (950, 660)))
    for k, x in enumerate(range(640, 1240, 46)):
        if 740 < x < 790: continue
        y = 852 + (k % 2) * 6
        m.obj(rect(x, y, 40, 28)); m.add('or', line((x + 10, y), (x + 10, y + 28)), line((x + 20, y), (x + 20, y + 28)), line((x + 30, y), (x + 30, y + 28)))
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
