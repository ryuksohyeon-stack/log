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
  const SEG = 0.142;
  // 익은 새우 껍질 — x 둘레(배 끝 → 등 0.5 → 배 끝), y 위가 마디 뒤쪽.
  // 쿠킹마마 익은 새우처럼: 등은 주홍, 옆은 황금빛 살구에 크림빛 하이라이트, 마디 뒤쪽은 매끈한 빨간 띠, 마디 사이 진한 선, 하얀 작은 점.
  // 일부러 작은 그림을 부드럽게 늘려 써서, 옛 게임 같은 몽글한 질감을 내요
  const shellTex = toTex(paint(128, 96, (x, y) => {
    const a = Math.abs(x - 0.5) * 2, back = 1 - y;
    const n = fbm(x * 4, y * 3, 3), n2 = fbm(x * 26, y * 20, 9, 2), n3 = fbm(x * 7, y * 4, 15, 3), st = fbm(x * 40, y * 3, 19, 2);
    let c = ramp([[0, hex('#e4532a')], [0.2, hex('#f6834a')], [0.42, hex('#fbad78')], [0.6, hex('#fcbf90')], [0.8, hex('#f8965e')], [1, hex('#de3e1e')]], a + (n - 0.5) * 0.18);
    c = mix(c, hex('#fddcae'), clamp((1 - Math.hypot((back - 0.32) * 2.6, (a - 0.5) * 2.3)) * 1.4) * 0.8);
    c = mix(c, hex('#fdc28c'), clamp((st - 0.55) * 3) * 0.3);
    const red = clamp((back - 0.62) / 0.18) ** 1.2 * (0.92 + (n3 - 0.5) * 0.3) + clamp((0.07 - back) / 0.07) * 0.55;
    c = mix(c, mix(hex('#e7351b'), hex('#c4200f'), clamp(a * 0.7 + (back - 0.8) * 2)), clamp(red) * 0.95);
    if (back > 0.92) c = mix(c, hex('#a01206'), clamp((back - 0.92) / 0.08) * 0.75);
    if (n2 > 0.75 && back > 0.15 && back < 0.72) c = mix(c, hex('#fff0d8'), Math.min(0.55, (n2 - 0.75) * 6));
    if (a < 0.25 && back > 0.2 && back < 0.65 && fbm(x * 30, y * 22, 27, 2) > 0.76) c = mix(c, hex('#ae521d'), 0.5);
    return shade(c, 0.97 + (n - 0.5) * 0.14);
  }));
  // 껍질 안쪽 · 두께 (잘린 단면)
  const innerTex = toTex(paint(64, 16, (x, y) => mix(hex('#fff3e8'), hex('#ffd2b8'), clamp(Math.abs(y - 0.5) * 1.6 + (fbm(x * 18, y * 6, 21, 3) - 0.5) * 0.5))));
  const edgeTex = toTex(paint(64, 16, (x, y) => mix(hex('#ffd2ae'), hex('#c8321c'), clamp(y * 1.3 - 0.15 + (fbm(x * 30, y * 4, 33, 2) - 0.5) * 0.4))));
  // 깐 살 — x 길이(머리 → 꼬리), y 둘레(배 → 가운데 등 → 배). 하얀 살에 마디마다 등 쪽으로 주홍 줄무늬, 마디 사이는 하얗게
  const fleshTex = toTex(paint(512, 256, (x, y) => {
    const th = Math.abs(y - 0.5) * 2, seg = (((x - 0.012) / SEG) % 1 + 1) % 1;
    const n = fbm(x * 6, y * 8, 41), blot = fbm(x * 14, y * 7, 47);
    let c = mix(hex('#fff4ef'), hex('#ffd3c6'), clamp(th * 0.8 + (n - 0.5) * 0.25));
    const across = clamp((0.72 - th + (blot - 0.5) * 0.3) * 2.6);
    const along = clamp(Math.sin(Math.PI * clamp((seg - 0.05) / 0.9)) * 2.2 - 0.25);
    const band = across * along;
    c = mix(c, ramp([[0, hex('#ffbfa6')], [0.55, hex('#ff8d68')], [1, hex('#f46c47')]], band + (blot - 0.5) * 0.25), band * 0.85);
    if (seg < 0.04 || seg > 0.97) c = shade(c, 0.94);
    return shade(c, 0.98 + (n - 0.5) * 0.08);
  }));
  // 꼬리 — x 밑동 → 끝. 주황 → 빨강 → 검붉은 끝, 가장자리도 진하게
  const tailTex = toTex(paint(128, 32, (x, y) => {
    const e = Math.abs(y - 0.5) * 2, n = fbm(x * 8, y * 6, 63, 3), st = fbm(x * 2, y * 18, 61, 2);
    let c = ramp([[0, hex('#f4924e')], [0.35, hex('#ec5a2c')], [0.72, hex('#d03620')], [1, hex('#6e1a10')]], x + (n - 0.5) * 0.16);
    c = mix(c, hex('#7a1c10'), clamp((e - 0.72) * 3) * 0.7);
    c = mix(c, hex('#ffc08a'), clamp((st - 0.6) * 2.5) * (1 - x) * 0.6);
    return shade(c, 0.92 + (1 - e * e) * 0.12);
  }));

  /* ---------- 재질 — 쿠킹마마처럼 반짝이는 퐁 ---------- */
  const phong = (o) => new THREE.MeshPhongMaterial(Object.assign({ shininess: 40, specular: col('#3a302a') }, o));
  const M = {
    shell: phong({ map: shellTex, shininess: 30 }),
    inner: phong({ map: innerTex }),
    edge: phong({ map: edgeTex, side: THREE.DoubleSide }),
    flesh: phong({ map: fleshTex, shininess: 55, specular: col('#4a403c') }),
    tail: phong({ map: tailTex, specular: col('#3a2a24'), shininess: 30, side: THREE.DoubleSide }),
  };

  /* ---------- 새우 뼈대 — 옆으로 누운 C 자 ---------- */
  // 머리 쪽이 굵고 꼬리로 갈수록 가늘어지며 안으로 감겨요. 꼬리는 결을 따라 쭉 뻗고
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
  function grid(nu, nv, pos, uvf) {
    const P = [], U = [], I = [];
    for (let i = 0; i <= nu; i++) for (let j = 0; j <= nv; j++) { const u = i / nu, v = j / nv, p = pos(u, v), t = uvf(u, v); P.push(p.x, p.y, p.z); U.push(t[0], t[1]); }
    for (let i = 0; i < nu; i++) for (let j = 0; j < nv; j++) { const a = i * (nv + 1) + j, b = a + nv + 1; I.push(a, a + 1, b, b, a + 1, b + 1); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g.setIndex(I); g.computeVertexNormals(); return g;
  }
  const S_END = 0.995, PLATES = 6, NU = 5, NV = 20, TH = 0.07;
  // 껍질 한 장 — 겉 · 안 · 두께 네 면을 한 덩어리로. 마디 뒤쪽이 다음 마디를 살짝 덮어요
  function plateGeo(i) {
    const s0 = 0.012 + i * SEG, s1 = i === PLATES - 1 ? 1.0 : Math.min(S_END, s0 + SEG + 0.03);
    const Th = (u) => Math.PI * (0.94 + 0.04 * Math.sin(Math.PI * u));
    const K = (u) => 1.03 + 0.06 * u + 0.05 * Math.sin(Math.PI * u) ** 0.8;
    const P = (u, v, d) => at(lerp(s0, s1, u), -Th(u) + 2 * Th(u) * v, K(u) - d * TH);
    const pos = [], U = [], I = [], W = NV + 1, half = (NU + 1) * W;
    for (const d of [0, 1]) for (let i2 = 0; i2 <= NU; i2++) for (let j = 0; j <= NV; j++) { const p = P(i2 / NU, j / NV, d); pos.push(p.x, p.y, p.z); U.push(j / NV, i2 / NU); }
    for (let i2 = 0; i2 < NU; i2++) for (let j = 0; j < NV; j++) { const a = i2 * W + j, b = a + W; I.push(a, a + 1, b, b, a + 1, b + 1); }
    const nOuter = I.length;
    for (let i2 = 0; i2 < NU; i2++) for (let j = 0; j < NV; j++) { const a = half + i2 * W + j, b = a + W; I.push(a, b, a + 1, b, b + 1, a + 1); }
    const nInner = I.length - nOuter, rimStart = I.length;
    let base = half * 2;
    [[(t) => [0, t], NV], [(t) => [1, t], NV], [(t) => [t, 0], NU], [(t) => [t, 1], NU]].forEach(([fn, n], r) => {
      for (let k = 0; k <= n; k++) { const [u, v] = fn(k / n), a = P(u, v, 0), b = P(u, v, 1); pos.push(a.x, a.y, a.z, b.x, b.y, b.z); U.push(k / n, 0, k / n, 1); }
      for (let k = 0; k < n; k++) { const a = base + k * 2, b = a + 2; if (r === 1 || r === 2) I.push(a, b, a + 1, b, b + 1, a + 1); else I.push(a, a + 1, b, b, a + 1, b + 1); }
      base += (n + 1) * 2;
    });
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g.setIndex(I);
    g.addGroup(0, nOuter, 0); g.addGroup(nOuter, nInner, 1); g.addGroup(rimStart, I.length - rimStart, 2);
    g.computeVertexNormals(); return g;
  }
  // peeled: 깐 새우 — 살만 남고, 꼬리 마디와 꼬리 부채는 그대로
  function buildShrimp(peeled) {
    const g = new THREE.Group();
    g.add(new THREE.Mesh(grid(60, 18, (u, v) => { const s = u * S_END, th = -Math.PI + 2 * Math.PI * v, ph = (((s - 0.012) / SEG) % 1 + 1) % 1; return at(s, th, 0.955 * (1 + 0.035 * Math.sin(Math.PI * ph) - 0.03 * Math.exp(-((ph / 0.06) ** 2)))); }, (u, v) => [u, 1 - v]), M.flesh));
    // 머리 쪽 끝 — 둥근 살. 까기 전 새우는 껍질 첫 장에 둥근 뚜껑이 붙어 있어요
    const f0 = spine(0), r0 = rad(0);
    const dome = (K, uvf) => grid(4, 24, (u, v) => { const w = (u * Math.PI) / 2; return at(0, Math.PI - 2 * Math.PI * v, K * Math.cos(w)).addScaledVector(f0.t, -Math.sin(w) * r0.d * 0.5 * K); }, uvf);
    g.add(new THREE.Mesh(dome(0.955, (u, v) => [0.004, v]), M.flesh));
    for (let i = peeled ? PLATES - 1 : 0; i < PLATES; i++) g.add(new THREE.Mesh(plateGeo(i), [M.shell, M.inner, M.edge]));
    if (!peeled) g.add(new THREE.Mesh(dome(1.03, (u, v) => [1 - v, 0.56 + u * 0.04]), M.shell));
    // 꼬리 — 뾰족하게 갈라진 부채 셋, 결을 따라 쭉 뻗어요
    const f1 = spine(1), e1 = f1.t.clone().addScaledVector(f1.n, 0.25).addScaledVector(f1.b, 0.12).normalize(), e2 = f1.n.clone().multiplyScalar(Math.cos(0.32)).addScaledVector(f1.b, Math.sin(0.32)).normalize(), e3 = new V3().crossVectors(e1, e2).normalize(); e2.crossVectors(e3, e1).normalize();
    const fan = (len, wid, ang, z, lift) => {
      const sh = new THREE.Shape();
      sh.moveTo(0, -wid * 0.32); sh.bezierCurveTo(len * 0.3, -wid * 0.62, len * 0.7, -wid * 0.42, len, -wid * 0.04); sh.lineTo(len * 0.96, wid * 0.06); sh.bezierCurveTo(len * 0.7, wid * 0.4, len * 0.3, wid * 0.5, 0, wid * 0.32); sh.lineTo(0, -wid * 0.32);
      const geo = new THREE.ExtrudeGeometry(sh, { depth: 0.05, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.035, bevelSegments: 2, curveSegments: 16 });
      const p = geo.attributes.position, uv = geo.attributes.uv;
      for (let k = 0; k < p.count; k++) { const t = p.getX(k) / len; uv.setXY(k, t, p.getY(k) / wid + 0.5); p.setZ(k, p.getZ(k) + lift * t * t + 0.08 * Math.sin(t * Math.PI)); }
      geo.computeVertexNormals();
      const d1 = e1.clone().multiplyScalar(Math.cos(ang)).addScaledVector(e2, Math.sin(ang)), d2 = new V3().crossVectors(e3, d1);
      geo.applyMatrix4(new THREE.Matrix4().makeBasis(d1, d2, e3).setPosition(f1.p.clone().addScaledVector(e1, -0.2).addScaledVector(e3, z)));
      return new THREE.Mesh(geo, M.tail);
    };
    g.add(fan(2.4, 0.8, 0.3, -0.02, 0.25), fan(2.4, 0.8, -0.3, -0.02, 0.25), fan(2.1, 0.52, 0, 0.06, 0.28));
    {   // 꼬리 마디 — 마지막 껍질 끝을 덮고 꼬리 부채로 이어지는 빨간 끝마디
      const r1 = rad(1), geo = new THREE.CylinderGeometry(0.45, 1, 1, 16, 1, false), ax = f1.t.clone().add(e1).normalize();
      geo.scale(r1.d * 1.1, 0.7, r1.l * 1.15); geo.applyMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(new Q().setFromUnitVectors(new V3(0, 1, 0), ax))); geo.translate(...f1.p.clone().addScaledVector(ax, 0.22).toArray());
      g.add(new THREE.Mesh(geo, M.tail));
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
