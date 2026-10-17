/* 쿠킹마마 새우 두 마리 — 왼쪽 깐 새우, 오른쪽 까기 전 새우 (three.js r128)
   · 끌면 그쪽 새우가 어느 방향으로든 360° 돌아가요. 손을 떼고 잠시 두면 처음 자세로 천천히 돌아와요.
   · 톡 누르면 root 에 'pick' 이벤트 — detail.which 가 'shell'(까기 전) | 'peeled'(깐 후) | null(처음 화면)
     고른 새우를 한 번 더 누르거나 빈 곳을 누르면 null 로 돌아가요.
   · ck.pick('shell' | 'peeled' | null) 로 밖에서도 고를 수 있어요 (키보드 버튼용)
   · 질감은 잡음으로 한 점 한 점 칠해서, 쿠킹마마 소품처럼 반짝이고 몽글하게 */
function ckShrimpDuo(THREE, root, cfg) {
  'use strict';
  cfg = cfg || {};
  const canvas = root.querySelector('canvas');
  const R = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  R.outputEncoding = THREE.sRGBEncoding; R.setClearColor(0xffffff, 0);
  const V3 = THREE.Vector3, Q = THREE.Quaternion;
  const col = (h) => new THREE.Color(h).convertSRGBToLinear();
  const clamp = (v, a = 0, b = 1) => (v < a ? a : v > b ? b : v);
  const lerp = (a, b, t) => a + (b - a) * t;
  const ease = (t) => 1 - (1 - t) ** 3;
  const calm = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 잡음 ---------- */
  const H = (x, y, s) => { let h = (x * 374761393 + y * 668265263 + s * 1442695041) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967295; };
  function vn(x, y, s) { const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi, u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf); return lerp(lerp(H(xi, yi, s), H(xi + 1, yi, s), u), lerp(H(xi, yi + 1, s), H(xi + 1, yi + 1, s), u), v); }
  function fbm(x, y, s, o = 4) { let a = 0, f = 1, w = 0.5, t = 0; for (let i = 0; i < o; i++) { a += w * vn(x * f, y * f, s + i * 17); t += w; f *= 2.03; w *= 0.5; } return a / t; }
  const hex = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
  const mix = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
  const ramp = (stops, t) => { t = clamp(t); for (let i = 1; i < stops.length; i++) if (t <= stops[i][0]) return mix(stops[i - 1][1], stops[i][1], (t - stops[i - 1][0]) / (stops[i][0] - stops[i - 1][0])); return stops[stops.length - 1][1]; };
  const shade = (c, k) => [clamp(c[0] * k, 0, 255), clamp(c[1] * k, 0, 255), clamp(c[2] * k, 0, 255)];
  // 한 점씩 칠하기 — fn(x 0..1, y 0..1) 이 [r,g,b] 를 돌려줘요
  function paint(w, h, fn) { const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'), id = g.createImageData(w, h), d = id.data; for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const p = fn(x / w, y / h), k = (y * w + x) * 4; d[k] = p[0]; d[k + 1] = p[1]; d[k + 2] = p[2]; d[k + 3] = 255; } g.putImageData(id, 0, 0); return c; }
  function toTex(c) { const t = new THREE.CanvasTexture(c); t.encoding = THREE.sRGBEncoding; return t; }

  /* ---------- 질감 ---------- */
  // 몸통 한 장에 길이(아래 머리 → 위 꼬리) · 둘레(배 → 가운데 등 → 배)로 칠해요
  const SEG = 0.142, PLATES = 6, TAIL0 = 0.012 + 5 * SEG;
  const segOf = (s) => { const i = Math.max(0, Math.min(PLATES - 1, Math.floor((s - 0.012) / SEG))), s0 = 0.012 + i * SEG; return { i, ph: clamp((s - s0) / (i === PLATES - 1 ? 1 - s0 : SEG)) }; };
  // 쿠킹마마 익은 새우 껍질 — 복숭아빛 금색 바탕, 마디 뒤쪽으로 번지는 붉은 띠, 크림빛 하이라이트, 하얀 점, 거뭇한 그을음.
  // 그 위에 보내 준 그림처럼 조각조각 얼룩을 얹어요
  function shellCol(x, s) {
    const a = Math.abs(x - 0.5) * 2, { i, ph } = segOf(s);
    const n = fbm(x * 5, s * 7, 3), m1 = fbm(x * 14, s * 20, 71, 3), m2 = fbm(x * 18 + 7, s * 26, 77, 3), dk = fbm(x * 22, s * 32, 27, 3), sp = fbm(x * 56, s * 80, 9, 2);
    let c = ramp([[0, hex('#ee6c30')], [0.25, hex('#f78c48')], [0.5, hex('#fbb067')], [0.72, hex('#f89850')], [1, hex('#e85a2c')]], a + (n - 0.5) * 0.25);
    c = mix(c, hex('#ffd894'), clamp((1 - Math.hypot((ph - 0.3) * 2.2, (a - 0.45) * 2.0)) * 1.3) * 0.85);
    c = mix(c, hex('#ffe4b8'), clamp((m1 - 0.6) * 12) * 0.45);
    c = mix(c, hex('#ee5426'), clamp((m2 - 0.6) * 10) * 0.55);
    const band = clamp((ph - 0.48 + (m2 - 0.5) * 0.35) / 0.3);
    c = mix(c, mix(hex('#ea4a22'), hex('#cc2c14'), clamp(a * 0.8 + ph - 0.8)), band * 0.92);
    if (ph > 0.955 || ph < 0.02) c = mix(c, hex('#9a1e0e'), 0.5);
    if (i === PLATES - 1) c = mix(c, hex('#e0532a'), 0.55 + clamp(ph / 0.5) * 0.3);   // 꼬리 마디는 빨갛게
    if (dk > 0.74) c = mix(c, hex('#5a2414'), Math.min(0.6, (dk - 0.74) * 6) * (0.35 + a * 0.65));
    if (sp > 0.76) c = mix(c, hex('#fbf1dc'), Math.min(0.75, (sp - 0.76) * 8));
    return shade(c, 0.96 + (n - 0.5) * 0.16);
  }
  // 깐 살 — 하얗게 비치는 살에 등 쪽 마디마다 분홍빛 주홍 줄, 붉은 조각 · 하얀 조각 얼룩
  function fleshCol(x, s) {
    const th = Math.abs(x - 0.5) * 2, { ph } = segOf(s);
    const n = fbm(x * 5, s * 7, 41), m1 = fbm(x * 14, s * 20, 47, 3), m2 = fbm(x * 18 + 3, s * 26, 53, 3);
    let c = mix(hex('#fff3ee'), hex('#ffd0c2'), clamp(th * 0.8 + (n - 0.5) * 0.25));
    const back = clamp((0.78 - th) * 2.4), stripe = clamp(Math.sin(Math.PI * clamp((ph - 0.05) / 0.9)) * 2 - 0.3) * back;
    c = mix(c, hex('#ff9c7e'), stripe * 0.6);
    c = mix(c, hex('#f4684a'), clamp((m2 - 0.58) * 9) * (0.25 + stripe * 0.6));
    c = mix(c, hex('#ffffff'), clamp((m1 - 0.6) * 9) * 0.55);
    if (ph < 0.03 || ph > 0.97) c = mix(c, hex('#ffe6dc'), 0.5);
    return shade(c, 0.98 + (n - 0.5) * 0.08);
  }
  const bodyTex = (peeled) => toTex(paint(256, 512, (x, y) => { const s = 1 - y; return peeled && s < TAIL0 ? fleshCol(x, s) : shellCol(x, s); }));
  // 꼬리 — 짙은 빨강, 끝은 검붉게
  const tailTex = toTex(paint(128, 32, (x, y) => {
    const e = Math.abs(y - 0.5) * 2, n = fbm(x * 8, y * 6, 63, 3), st = fbm(x * 2, y * 18, 61, 2);
    let c = ramp([[0, hex('#e8642e')], [0.4, hex('#d8401e')], [0.75, hex('#a82414')], [1, hex('#3e0e08')]], x + (n - 0.5) * 0.16);
    c = mix(c, hex('#5a140a'), clamp((e - 0.7) * 3) * 0.7);
    c = mix(c, hex('#ffb07a'), clamp((st - 0.62) * 2.5) * (1 - x) * 0.5);
    return shade(c, 0.92 + (1 - e * e) * 0.12);
  }));

  /* ---------- 재질 — 쿠킹마마처럼 반짝이는 퐁 ---------- */
  const phong = (o) => new THREE.MeshPhongMaterial(Object.assign({ shininess: 24, specular: col('#5e4c40') }, o));
  const tailMat = phong({ map: tailTex, side: THREE.DoubleSide });

  /* ---------- 새우 뼈대 — 옆으로 누운 C 자 ---------- */
  // 머리 쪽이 굵고 꼬리로 갈수록 가늘어지며 안으로 감겨요
  const RC = 1.9, A0 = -1.25, AS = 4.7, RISE = 0.25;
  const spine = (s) => {
    const a = A0 + AS * s, r = RC * (1 - 0.2 * s), dr = -0.2 * RC, h = clamp((s - 0.5) / 0.5), y = RISE * h * h * (3 - 2 * h), dy = s > 0.5 ? (RISE * 6 * h * (1 - h)) / 0.5 : 0;
    const p = new V3(r * Math.sin(a), y, -r * Math.cos(a));
    const t = new V3(dr * Math.sin(a) + r * AS * Math.cos(a), dy, -dr * Math.cos(a) + r * AS * Math.sin(a)).normalize();
    const b = new V3(0, 1, 0).addScaledVector(t, -t.y).normalize();
    return { p, t, n: new V3().crossVectors(b, t), b };
  };
  const rad = (s) => { let d = (1.12 - 0.66 * s ** 1.5) * (1 + 0.05 * Math.exp(-(((s - 0.25) / 0.16) ** 2))); if (s < 0.025) d *= 0.96 + 0.04 * (s / 0.025); return { d, l: d * 0.9 }; };
  const at = (s, th, k = 1) => { const f = spine(s), r = rad(s), c = Math.cos(th); return f.p.clone().addScaledVector(f.n, k * r.d * c * (c < 0 ? 0.82 : 1)).addScaledVector(f.b, k * r.l * Math.sin(th)); };
  function mesh(P, U, I, mat) { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g.setIndex(I); g.computeVertexNormals(); return new THREE.Mesh(g, mat); }
  // 몸통 한 덩어리 — 마디마다 앞은 앞 마디 밑으로 쏙 들어가고 뒤는 불룩 튀어나와, 쿠킹마마 새우처럼 고리를 겹쳐 쌓은 모양.
  // 둘레는 14각이라 옛 게임처럼 살짝 각져 보여요. 깐 새우는 살이라 덜 울퉁불퉁하고, 꼬리 마디만 껍질째
  const NV = 14, PROF = [[0, 0.93], [0.12, 0.98], [0.42, 1.03], [0.72, 1.06], [0.9, 1.07], [0.975, 1.03]], PROF_T = [[0, 0.9], [0.1, 0.97], [0.35, 1.04], [0.7, 1.0], [1, 0.93]];
  function buildShrimp(peeled) {
    const g = new THREE.Group(), mat = phong({ map: bodyTex(peeled), shininess: peeled ? 40 : 28 });
    const K0 = peeled ? 0.9 : 0.93, rows = [[0, K0]];
    for (let i = 0; i < PLATES; i++) {
      const s0 = 0.012 + i * SEG, len = i === PLATES - 1 ? 1 - s0 : SEG, flesh = peeled && i < PLATES - 1;
      (i === PLATES - 1 ? PROF_T : PROF).forEach(([ph, k]) => rows.push([s0 + ph * len, flesh ? 0.95 + (k - 1) * 0.35 : k]));
    }
    const P = [], U = [], I = [], W = NV + 1;
    rows.forEach(([s, k]) => { for (let j = 0; j <= NV; j++) { const p = at(s, -Math.PI + (2 * Math.PI * j) / NV, k); P.push(p.x, p.y, p.z); U.push(j / NV, s); } });
    for (let r = 0; r < rows.length - 1; r++) for (let j = 0; j < NV; j++) { const a = r * W + j, b = a + W; I.push(a, a + 1, b, b, a + 1, b + 1); }
    g.add(mesh(P, U, I, mat));
    // 머리 쪽 끝 — 둥글게 닫아요
    const f0 = spine(0), r0 = rad(0), DP = [], DU = [], DI = [];
    for (let i = 0; i <= 4; i++) for (let j = 0; j <= NV; j++) { const w = (i / 4) * (Math.PI / 2), p = at(0, Math.PI - (2 * Math.PI * j) / NV, K0 * Math.cos(w)).addScaledVector(f0.t, -Math.sin(w) * r0.d * 0.5 * K0); DP.push(p.x, p.y, p.z); DU.push(0.5 + 0.2 * Math.cos(w) * Math.sin((2 * Math.PI * j) / NV), 0.03 + 0.012 * Math.cos(w) * Math.cos((2 * Math.PI * j) / NV)); }
    for (let i = 0; i < 4; i++) for (let j = 0; j < NV; j++) { const a = i * W + j, b = a + W; DI.push(a, a + 1, b, b, a + 1, b + 1); }
    g.add(mesh(DP, DU, DI, mat));
    // 꼬리 — 짧고 짙은 부채 셋
    const f1 = spine(1), e1 = f1.t.clone().addScaledVector(f1.n, 0.25).addScaledVector(f1.b, 0.12).normalize(), e2 = f1.n.clone().multiplyScalar(Math.cos(0.32)).addScaledVector(f1.b, Math.sin(0.32)).normalize(), e3 = new V3().crossVectors(e1, e2).normalize(); e2.crossVectors(e3, e1).normalize();
    const fan = (len, wid, ang, z, lift) => {
      const sh = new THREE.Shape();
      sh.moveTo(0, -wid * 0.32); sh.bezierCurveTo(len * 0.3, -wid * 0.62, len * 0.7, -wid * 0.5, len, -wid * 0.08); sh.lineTo(len * 0.94, wid * 0.1); sh.bezierCurveTo(len * 0.7, wid * 0.45, len * 0.3, wid * 0.5, 0, wid * 0.32); sh.lineTo(0, -wid * 0.32);
      const geo = new THREE.ExtrudeGeometry(sh, { depth: 0.05, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.035, bevelSegments: 1, curveSegments: 8 });
      const p = geo.attributes.position, uv = geo.attributes.uv;
      for (let k = 0; k < p.count; k++) { const t = p.getX(k) / len; uv.setXY(k, t, p.getY(k) / wid + 0.5); p.setZ(k, p.getZ(k) + lift * t * t + 0.08 * Math.sin(t * Math.PI)); }
      geo.computeVertexNormals();
      const d1 = e1.clone().multiplyScalar(Math.cos(ang)).addScaledVector(e2, Math.sin(ang)), d2 = new V3().crossVectors(e3, d1);
      geo.applyMatrix4(new THREE.Matrix4().makeBasis(d1, d2, e3).setPosition(f1.p.clone().addScaledVector(e1, -0.15).addScaledVector(e3, z)));
      return new THREE.Mesh(geo, tailMat);
    };
    g.add(fan(1.45, 0.78, 0.38, -0.02, 0.18), fan(1.45, 0.78, -0.38, -0.02, 0.18), fan(1.3, 0.52, 0, 0.06, 0.2));
    {   // 꼬리 끝 — 몸통 끝을 덮고 부채로 이어지는 짧은 마디
      const r1 = rad(1), geo = new THREE.CylinderGeometry(0.5, 1, 1, NV, 1, false), ax = f1.t.clone().add(e1).normalize();
      geo.scale(r1.d * 0.95, 0.5, r1.l * 1.02); geo.applyMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(new Q().setFromUnitVectors(new V3(0, 1, 0), ax))); geo.translate(...f1.p.clone().addScaledVector(ax, 0.12).toArray());
      g.add(new THREE.Mesh(geo, tailMat));
    }
    return g;
  }

  /* ---------- 장면 — 하얀 바탕, 양옆에 새우 ---------- */
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, col('#ffe4d8'), 0.6));
  const key = new THREE.DirectionalLight(0xffffff, 0.72); key.position.set(-6, 9, 14); scene.add(key);
  const rim = new THREE.DirectionalLight(col('#fff2e6'), 0.32); rim.position.set(8, 4, -9); scene.add(rim);
  const DIST = 46, HALF = 10.4;   // 새우 깊이에서 화면 가로 반폭
  const cam = new THREE.PerspectiveCamera(20, 1.43, 1, 200); cam.position.set(0, 0, DIST);
  const X = new V3(1, 0, 0), Y = new V3(0, 1, 0), Z = new V3(0, 0, 1);
  const qa = (axis, a) => new Q().setFromAxisAngle(axis, a);
  // 처음 자세 — 보내 준 그림처럼. 왼쪽(깐 새우)은 머리가 왼쪽 위, 시계 방향으로 감겨 꼬리가 왼쪽 아래로.
  // 오른쪽(까기 전)은 뒤집어 놓아서 머리가 왼쪽 위, 반시계 방향으로 감겨 꼬리가 오른쪽 위로 솟아요
  const SIZE = cfg.size || 7.3, GAP = cfg.x || 5.2;
  function make(peeled, x, base) {
    const orient = new THREE.Group(); orient.add(buildShrimp(peeled)); orient.quaternion.copy(base);
    const box = new THREE.Box3(), v = new V3(); orient.updateMatrixWorld(true);   // 꼭짓점으로 잰 딱 맞는 상자
    orient.traverse((o) => { if (o.isMesh) { const a = o.geometry.attributes.position; for (let i = 0; i < a.count; i++) box.expandByPoint(v.fromBufferAttribute(a, i).applyMatrix4(o.matrixWorld)); } });
    const sz = box.getSize(new V3()), k = SIZE / Math.max(sz.x, sz.y);
    orient.scale.setScalar(k); orient.position.copy(box.getCenter(new V3()).multiplyScalar(-k));
    const pivot = new THREE.Group(); pivot.add(orient); pivot.position.x = x; scene.add(pivot);
    pivot.userData = { which: peeled ? 'peeled' : 'shell', x, side: Math.sign(x), q: new Q(), wy: 0, wx: 0, last: -1e9, hop: 1, ph: peeled ? 0 : 2.1, r: (SIZE / 2) * 0.92 };
    return pivot;
  }
  const duo = [
    make(true, -GAP, qa(Z, cfg.rollL !== undefined ? cfg.rollL : -0.52).multiply(qa(X, Math.PI / 2))),
    make(false, GAP, qa(Z, cfg.rollR !== undefined ? cfg.rollR : 1.93).multiply(qa(Y, Math.PI)).multiply(qa(X, Math.PI / 2))),
  ];

  /* ---------- 돌리기 · 톡 누르기 ---------- */
  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
  function hitAt(e) {
    const r = canvas.getBoundingClientRect(); ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ndc, cam);
    let best = null, bd = Infinity;
    for (const p of duo) { const h = ray.intersectObject(p, true)[0]; if (h && h.distance < bd) { bd = h.distance; best = p; } }
    if (best) return best;
    // 살짝 빗나가도 새우 둘레 안이면 그 새우로 (손가락으로 누르기 쉽게)
    const perPx = (2 * DIST * Math.tan((cam.fov * Math.PI) / 360)) / r.height;
    for (const p of duo) { const c = new V3(p.userData.x, 0, 0).project(cam); if (Math.hypot(((c.x - ndc.x) * r.width) / 2, ((c.y - ndc.y) * r.height) / 2) * perPx < p.userData.r) return p; }
    return null;
  }
  const turn = (p, ay, ax) => { p.userData.q.premultiply(qa(X, ax)).premultiply(qa(Y, ay)); };
  let drag = null, sel = null, now = performance.now();
  canvas.addEventListener('pointerdown', (e) => {
    canvas.setPointerCapture(e.pointerId);
    const h = hitAt(e), r = canvas.getBoundingClientRect();
    const t = h || (e.clientX - r.left < r.width / 2 ? duo[0] : duo[1]);   // 빈 곳을 끌면 가까운 쪽 새우가 돌아가요
    drag = { x: e.clientX, y: e.clientY, x0: e.clientX, y0: e.clientY, moved: false, t, h };
    t.userData.wy = t.userData.wx = 0; t.userData.last = now;
  });
  canvas.addEventListener('pointermove', (e) => {
    if (!drag) { if (e.pointerType === 'mouse') canvas.style.cursor = hitAt(e) ? 'pointer' : 'grab'; return; }
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (Math.hypot(e.clientX - drag.x0, e.clientY - drag.y0) > 6) drag.moved = true;
    if (drag.moved) { const u = drag.t.userData; u.wy = dx * 0.012; u.wx = dy * 0.012; turn(drag.t, u.wy, u.wx); u.last = now; canvas.style.cursor = 'grabbing'; }
    drag.x = e.clientX; drag.y = e.clientY;
  });
  canvas.addEventListener('pointerup', () => {
    if (!drag) return;
    if (!drag.moved) pick(drag.h && drag.h.userData.which === sel ? null : drag.h ? drag.h.userData.which : null);
    drag = null; canvas.style.cursor = '';
  });
  canvas.addEventListener('pointercancel', () => { drag = null; });
  function pick(which) {
    sel = which || null;
    const p = duo.find((d) => d.userData.which === sel);
    if (p && !calm) p.userData.hop = 0;   // 고른 새우는 폴짝 뛰며 한 바퀴
    root.dispatchEvent(new CustomEvent('pick', { detail: { which: sel } }));
  }

  /* ---------- 그리기 ---------- */
  function size() {
    const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
    R.setPixelRatio(Math.min(2, window.devicePixelRatio || 1)); R.setSize(w, h, false); cam.aspect = w / h;
    cam.fov = (2 * Math.atan(HALF / (DIST * cam.aspect)) * 180) / Math.PI;   // 화면 폭이 바뀌어도 새우 둘이 늘 같은 자리에
    cam.updateProjectionMatrix();
    // 좁은 화면에서는 새우를 조금 작게, 바깥으로 — 가운데 글자리를 넓혀요
    const narrow = w < 520;
    duo.forEach((p) => { const u = p.userData, k = narrow ? 0.86 : 1; p.scale.setScalar(k); u.x = u.side * (narrow ? 5.9 : GAP); u.r = (SIZE / 2) * 0.92 * k; p.position.x = u.x; });
  }
  new ResizeObserver(size).observe(canvas); size();
  let last = now, visible = true, tt = 0;
  new IntersectionObserver((es) => { visible = es[0].isIntersecting; }).observe(canvas);
  const ID = new Q(), sway = new Q(), spin = new Q();
  function frame(t) {
    requestAnimationFrame(frame);
    now = t; const dt = Math.min(0.05, (t - last) / 1000); last = t;
    if (!visible) return;
    tt += dt;
    for (const p of duo) {
      const u = p.userData, held = drag && drag.t === p && drag.moved;
      if (!held && Math.abs(u.wy) + Math.abs(u.wx) > 1e-4) { turn(p, u.wy, u.wx); u.wy *= 0.93; u.wx *= 0.93; u.last = t; }
      if (!held && t - u.last > 4500) u.q.slerp(ID, 1 - Math.exp(-dt * 1.4));   // 한참 두면 처음 자세로
      u.hop = Math.min(1, u.hop + dt / 0.95);
      spin.setFromAxisAngle(Y, u.hop < 1 ? ease(u.hop) * Math.PI * 2 : 0);
      sway.setFromAxisAngle(Z, calm ? 0 : Math.sin(tt * 0.9 + u.ph) * 0.035);
      p.quaternion.copy(spin).multiply(sway).multiply(u.q);
      p.position.y = (calm ? 0 : Math.sin(tt * 1.3 + u.ph) * 0.1) + (u.hop < 1 ? Math.sin(Math.PI * u.hop) * 1.2 : 0);
    }
    R.render(scene, cam);
  }
  requestAnimationFrame(frame);
  return { pick, get which() { return sel; }, _dbg: { cam, scene, duo } };
}
