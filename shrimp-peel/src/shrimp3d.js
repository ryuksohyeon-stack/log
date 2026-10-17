/* 껍질 까는 새우 — 쿠킹마마 소품처럼 (three.js r128)
   · 껍질 마디를 톡 누르면 한 장씩 벗겨지고, 안에 적힌 글이 드러나요. 끌면 새우를 돌려 볼 수 있어요.
   · 질감은 잡음으로 한 점 한 점 칠해서(얼룩 · 반점 · 결), 쿠킹마마 음식처럼 그림 같은 사실감을 내요.
   · cfg.setting: 'square'(흰 네모 접시 · 민트 냅킨) | 'round'(노란 테 둥근 접시) | 'mat'(노란 체크 매트 · 나무 식탁 · 파란 그릇)
   · cfg.mode: 'flesh'(속살에 글) | 'shell'(껍질 안쪽에 글 — 벗긴 껍질이 펴지며 낱말이 돼요) */
function ckPeel(THREE, root, cfg) {
  'use strict';
  const canvas = root.querySelector('canvas');
  const R = new THREE.WebGLRenderer({ canvas, antialias: true });
  R.outputEncoding = THREE.sRGBEncoding;
  const V3 = THREE.Vector3;
  const col = (h) => new THREE.Color(h).convertSRGBToLinear();
  const clamp = (v, a = 0, b = 1) => (v < a ? a : v > b ? b : v);
  const lerp = (a, b, t) => a + (b - a) * t;
  const ease = (t) => 1 - (1 - t) ** 3;
  const FONT = cfg.font || 'Pretendard';

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
  function toTex(c, rep) { const t = new THREE.CanvasTexture(c); t.encoding = THREE.sRGBEncoding; t.anisotropy = R.capabilities.getMaxAnisotropy(); if (rep) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]); } return t; }

  /* ---------- 질감 ---------- */
  // 익은 새우 껍질 — x 둘레(배 끝 → 등 0.5 → 배 끝), y 위가 마디 뒤쪽.
  // 마디마다 앞쪽은 크림색 띠, 뒤쪽은 주홍 → 진홍 띠 (쿠킹마마 새우 줄무늬). 배 쪽(안쪽 굽이)은 흰 띠가 넓어요
  const shellTex = toTex(paint(512, 256, (x, y) => {
    const a = Math.abs(x - 0.5) * 2, back = 1 - y;
    const n = fbm(x * 7, y * 4, 3), streak = fbm(x * 2.2, y * 34, 9, 3), grain = fbm(x * 70, y * 36, 13, 2);
    const edge = 0.24 + 0.26 * a ** 1.6 + (n - 0.5) * 0.14;   // 크림 띠가 끝나는 자리
    const t = clamp((back - edge) / 0.09);   // 0 크림 → 1 주홍
    let red = ramp([[0, hex('#ff9a5a')], [0.2, hex('#ff6f30')], [0.65, hex('#f04620')], [1, hex('#cc2e14')]], (back - edge) / (1 - edge) + (n - 0.5) * 0.2);
    if (streak > 0.6) red = mix(red, hex('#c2240f'), Math.min(0.55, (streak - 0.6) * 2.4));   // 진홍 결
    red = mix(red, hex('#ffb994'), clamp((a - 0.84) * 2.4));   // 배 끝은 옅게
    const cream = mix(hex('#fff4ea'), hex('#ffd6c8'), clamp(back / Math.max(0.05, edge) * 0.8 + (n - 0.5) * 0.4));
    let c = mix(cream, red, t);
    let k = 0.92 + (grain - 0.5) * 0.14 + (n - 0.5) * 0.1;
    if (back < 0.07) k *= 0.8 + back * 2.8;   // 앞 마디 밑으로 들어가는 그늘
    if (back > 0.95) k *= 0.88;
    return shade(c, k);
  }));
  // 껍질 안쪽 — 하얗고 매끈 (글을 쓰는 면)
  const innerBase = paint(512, 128, (x, y) => mix(hex('#fff3e8'), hex('#ffd2b8'), clamp(Math.abs(y - 0.5) * 1.6 + (fbm(x * 18, y * 6, 21, 3) - 0.5) * 0.5)));
  // 껍질 두께 (잘린 단면)
  const edgeTex = toTex(paint(64, 16, (x, y) => mix(hex('#ffe9cf'), hex('#ffb37a'), clamp(y + (fbm(x * 30, y * 4, 33, 2) - 0.5) * 0.6))));
  // 속살 — x 길이(머리 → 꼬리), y 둘레(위 배 → 가운데 등 → 아래 배). 익은 새우 살 — 흰 살에 마디마다 등에서 옆으로 번지는 주홍 줄
  const fleshBase = paint(1024, 512, (x, y) => {
    const th = Math.abs(y - 0.5) * 2, seg = (((x - 0.012) / 0.142) % 1 + 1) % 1;
    const n = fbm(x * 6, y * 8, 41), fib = fbm(x * 3, y * 60, 43, 3), blot = fbm(x * 12, y * 6, 47);
    let c = mix(hex('#fff8f2'), hex('#ffe3d8'), clamp(th * 0.6 + (n - 0.5) * 0.3));
    const band = clamp((0.62 - th * 0.85 + (blot - 0.5) * 0.35) * 2.6) * clamp((seg - 0.3 + (blot - 0.5) * 0.2) * 3.2) * clamp((1.02 - seg) * 8);
    c = mix(c, ramp([[0, hex('#ffb08a')], [0.5, hex('#ff7a4c')], [1, hex('#f0532c')]], clamp(band * 1.2 + (blot - 0.5) * 0.4)), band * 0.85);
    let k = 0.94 + fib * 0.1;
    if (seg < 0.05 || seg > 0.97) k *= 0.86;   // 마디 사이 홈
    return shade(c, k);
  });
  function fleshTex(lines) {
    const c = document.createElement('canvas'); c.width = 2048; c.height = 1024; const g = c.getContext('2d');
    g.drawImage(fleshBase, 0, 0, 2048, 1024);
    if (lines && lines.length) {
      const fs = 92; g.font = `700 ${fs}px ${FONT}, sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.lineJoin = 'round';
      const cy0 = 1024 * (cfg.textY || 0.66), y0 = cy0 - ((lines.length - 1) * fs * 1.22) / 2;
      const cx = 2048 * 0.46, cy = cy0; g.translate(cx, cy); g.rotate(Math.PI); g.translate(-cx, -cy);   // 새우가 돌아 누워 있어서 글도 거꾸로
      lines.forEach((ln, i) => { g.lineWidth = 12; g.strokeStyle = 'rgba(255,248,240,.9)'; g.strokeText(ln, cx, y0 + i * fs * 1.22, 2048 * 0.66); g.fillStyle = '#6e1e12'; g.fillText(ln, cx, y0 + i * fs * 1.22, 2048 * 0.66); });
    }
    return toTex(c);
  }
  const cutTex = toTex(paint(128, 128, (x, y) => { const r = Math.hypot(x - 0.5, y - 0.5) * 2, n = fbm(x * 10, y * 10, 51, 3); return mix(mix(hex('#fffaf4'), hex('#ffcdbd'), clamp(r * 1.1 + (n - 0.5) * 0.4)), hex('#e8553a'), clamp((r - 0.82) * 5)); }));
  // 꼬리 — x 밑동 → 끝. 노랑 → 주황 → 빨강 → 검붉은 끝, 길이 방향 줄무늬
  const tailTex = toTex(paint(256, 64, (x, y) => {
    const st = fbm(x * 2, y * 26, 61, 3), n = fbm(x * 10, y * 10, 63, 3);
    let c = ramp([[0, hex('#ffcf7a')], [0.3, hex('#ff8a33')], [0.62, hex('#f0461f')], [0.88, hex('#b8180e')], [1, hex('#6e0d08')]], x + (n - 0.5) * 0.18);
    c = mix(c, hex('#ffe0a0'), clamp((st - 0.62) * 2.5) * (1 - x) * 0.8);
    const e = Math.abs(y - 0.5) * 2;
    return shade(c, 0.82 + 0.25 * (1 - e * e) + (st - 0.5) * 0.25);
  }));
  const legTex = toTex(paint(64, 16, (x) => ramp([[0, hex('#ffb066')], [0.6, hex('#f2501f')], [1, hex('#b81c10')]], x)));
  const blobC = document.createElement('canvas'); blobC.width = blobC.height = 128;
  { const g = blobC.getContext('2d'), gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(90,20,40,.5)'); gr.addColorStop(0.5, 'rgba(90,20,40,.22)'); gr.addColorStop(1, 'rgba(90,20,40,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); }
  // 바탕 — 쿠킹마마 식탁처럼 칸 가장자리가 부드러운 깅엄
  const ging = (a, b, rep, w = 0.5) => toTex(paint(128, 128, (x, y) => { const k = clamp((Math.cos(x * Math.PI * 8) * 0.5) * 3 + 0.5), m = clamp((Math.cos(y * Math.PI * 8) * 0.5) * 3 + 0.5); return mix(hex(a), hex(b), clamp((k + m) * w + (fbm(x * 40, y * 40, 71, 2) - 0.5) * 0.12)); }), rep);
  const wallTex = (a, b) => toTex(paint(8, 256, (x, y) => (y < 0.2 ? mix(hex('#fbf3e6'), hex('#d9eef6'), y / 0.2) : y < 0.23 ? hex('#a9d6ea') : mix(mix(hex(a), hex(b), (y - 0.23) / 0.77), [255, 255, 255], Math.max(0, 0.42 - Math.abs(y - 0.55) * 3.2)))));
  const woodTex = (rep) => toTex(paint(256, 256, (x, y) => { const pl = Math.floor(y * 4), n = fbm(x * 3, y * 60 + pl * 9, 81, 4), base = [hex('#e6a46a'), hex('#d99a5d'), hex('#eaae78'), hex('#dc955a')][pl]; return shade(base, 0.82 + n * 0.32 - ((y * 4) % 1 > 0.97 ? 0.25 : 0)); }), rep);
  const fabric = (a, b, rep) => toTex(paint(128, 128, (x, y) => mix(hex(a), hex(b), clamp(fbm(x * 64, y * 64, 91, 2) * 0.4 + (fbm(x * 3 + y * 2, y * 3 - x, 93, 3) - 0.5) * 1.2 + 0.2))), rep);
  const ceramic = (c1, c2) => toTex(paint(256, 256, (x, y) => { const r = Math.hypot(x - 0.5, y - 0.48) * 2; return mix(hex(c1), hex(c2), clamp(r * r * 0.9 + (fbm(x * 8, y * 8, 101, 3) - 0.5) * 0.08)); }));

  /* ---------- 재질 — 쿠킹마마처럼 반짝이는 퐁 ---------- */
  const phong = (o) => new THREE.MeshPhongMaterial(Object.assign({ shininess: 70, specular: col('#555555') }, o));
  const M = {
    shell: phong({ map: shellTex, specular: col('#5e5550'), shininess: 70 }),
    edge: phong({ map: edgeTex, shininess: 30, side: THREE.DoubleSide }),
    tail: phong({ map: tailTex, specular: col('#ffd8c0'), shininess: 90, side: THREE.DoubleSide }),
    leg: phong({ map: legTex, side: THREE.DoubleSide, shininess: 60 }),
    cut: phong({ map: cutTex, shininess: 50 }),
    blob: new THREE.MeshBasicMaterial({ map: toTex(blobC), transparent: true, depthWrite: false }),
  };

  /* ---------- 새우 뼈대 — 옆으로 누운 C 자 ---------- */
  const RC = 3.05, A0 = -1.0, AS = 2.85;
  const spine = (s) => { const a = A0 + AS * s; return { p: new V3(RC * Math.sin(a), 0, -RC * Math.cos(a)), t: new V3(Math.cos(a), 0, Math.sin(a)), n: new V3(Math.sin(a), 0, -Math.cos(a)), b: new V3(0, 1, 0) }; };
  const rad = (s) => { let d = (1.5 - 0.72 * s ** 1.35) * (1 + 0.06 * Math.exp(-(((s - 0.25) / 0.16) ** 2))); if (s < 0.025) d *= 0.96 + 0.04 * (s / 0.025); return { d, l: d * 0.88 }; };
  const at = (s, th, k = 1) => { const f = spine(s), r = rad(s), c = Math.cos(th); return f.p.clone().addScaledVector(f.n, k * r.d * c * (c < 0 ? 0.82 : 1)).addScaledVector(f.b, k * r.l * Math.sin(th)); };
  function grid(nu, nv, pos, uvf) {
    const P = [], U = [], I = [];
    for (let i = 0; i <= nu; i++) for (let j = 0; j <= nv; j++) { const u = i / nu, v = j / nv, p = pos(u, v), t = uvf(u, v); P.push(p.x, p.y, p.z); U.push(t[0], t[1]); }
    for (let i = 0; i < nu; i++) for (let j = 0; j < nv; j++) { const a = i * (nv + 1) + j, b = a + nv + 1; I.push(a, a + 1, b, b, a + 1, b + 1); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g.setIndex(I); g.computeVertexNormals(); return g;
  }
  const S_END = 0.995, PLATES = 6, SEG = 0.142, NU = 22, NV = 44, TH = 0.07;
  // 껍질 한 장 — 겉 · 안 · 두께 네 면을 한 덩어리로. f(0 말린 모양 → 1 펼친 카드)로 모양을 바꿔요
  function plateSpec(i) {
    const s0 = 0.012 + i * SEG, s1 = Math.min(S_END, s0 + SEG + 0.03), sm = (s0 + s1) / 2, fm = spine(sm), rm = rad(sm).d * 1.02;
    const Th = (u) => Math.PI * (0.79 + 0.09 * Math.sin(Math.PI * u));
    const K = (u) => 1.04 + 0.025 * u + 0.055 * Math.sin(Math.PI * u) ** 0.8;
    const P = (u, v, d, f) => {
      const th = -Th(u) + 2 * Th(u) * v, c = at(lerp(s0, s1, u), th, K(u) - d * TH);
      if (!f) return c;
      return c.lerp(fm.p.clone().addScaledVector(fm.b, th * rm).addScaledVector(fm.t, (u - 0.5) * (s1 - s0) * RC * AS).addScaledVector(fm.n, rm + 0.35 * Math.cos(th / 2.2) - d * TH * rm), f);
    };
    return { s0, s1, fm, rm, P };
  }
  function plateVerts(sp, f, ctr) {   // 겉 · 안(같은 격자) · 테두리 네 줄 — 늘 같은 순서로
    const out = [], push = (p) => out.push(p.x - ctr.x, p.y - ctr.y, p.z - ctr.z);
    for (const d of [0, 1]) for (let i = 0; i <= NU; i++) for (let j = 0; j <= NV; j++) push(sp.P(i / NU, j / NV, d, f));
    for (const [fn, n] of [[(t) => [0, t], NV], [(t) => [1, t], NV], [(t) => [t, 0], NU], [(t) => [t, 1], NU]]) for (let k = 0; k <= n; k++) { const [u, v] = fn(k / n); push(sp.P(u, v, 0, f)); push(sp.P(u, v, 1, f)); }
    return out;
  }
  function plateGeo(sp, ctr) {
    const g = new THREE.BufferGeometry(), I = [], U = [], W = NV + 1, half = (NU + 1) * W;
    for (const d of [0, 1]) for (let i = 0; i <= NU; i++) for (let j = 0; j <= NV; j++) U.push(j / NV, i / NU);
    for (let i = 0; i < NU; i++) for (let j = 0; j < NV; j++) { const a = i * W + j, b = a + W; I.push(a, a + 1, b, b, a + 1, b + 1); }
    const nOuter = I.length;
    for (let i = 0; i < NU; i++) for (let j = 0; j < NV; j++) { const a = half + i * W + j, b = a + W; I.push(a, b, a + 1, b, b + 1, a + 1); }
    const nInner = I.length - nOuter, rimStart = I.length;
    let base = half * 2;
    [NV, NV, NU, NU].forEach((n, r) => { for (let k = 0; k <= n; k++) U.push(k / n, 0, k / n, 1); for (let k = 0; k < n; k++) { const a = base + k * 2, b = a + 2; if (r === 1 || r === 2) I.push(a, b, a + 1, b, b + 1, a + 1); else I.push(a, a + 1, b, b, a + 1, b + 1); } base += (n + 1) * 2; });
    g.setAttribute('position', new THREE.Float32BufferAttribute(plateVerts(sp, 0, ctr), 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g.setIndex(I);
    g.addGroup(0, nOuter, 0); g.addGroup(nOuter, nInner, 1); g.addGroup(rimStart, I.length - rimStart, 2);
    g.computeVertexNormals(); return g;
  }
  function buildShrimp(fleshMat) {
    const g = new THREE.Group();
    const body = new THREE.Mesh(grid(150, 64, (u, v) => { const s = u * S_END, th = -Math.PI + 2 * Math.PI * v, ph = (((s - 0.012) / SEG) % 1 + 1) % 1; return at(s, th, 0.955 * (1 + 0.035 * Math.sin(Math.PI * ph) - 0.03 * Math.exp(-((ph / 0.06) ** 2)))); }, (u, v) => [u, 1 - v]), fleshMat);
    body.name = 'body'; g.add(body);
    const cg = new THREE.BufferGeometry(), cp = [], cu = [], c0 = spine(0).p, ring = [];
    for (let j = 0; j <= 48; j++) ring.push(at(0, -Math.PI + (2 * Math.PI * j) / 48, 0.955));
    for (let j = 0; j < 48; j++) { cp.push(c0.x, c0.y, c0.z, ring[j + 1].x, ring[j + 1].y, ring[j + 1].z, ring[j].x, ring[j].y, ring[j].z); const a1 = (2 * Math.PI * (j + 1)) / 48, a0 = (2 * Math.PI * j) / 48; cu.push(0.5, 0.5, 0.5 + 0.5 * Math.cos(a1), 0.5 + 0.5 * Math.sin(a1), 0.5 + 0.5 * Math.cos(a0), 0.5 + 0.5 * Math.sin(a0)); }
    cg.setAttribute('position', new THREE.Float32BufferAttribute(cp, 3)); cg.setAttribute('uv', new THREE.Float32BufferAttribute(cu, 2)); cg.computeVertexNormals();
    const cap = new THREE.Mesh(cg, M.cut); cap.name = 'body'; g.add(cap);
    const plates = [];
    for (let i = 0; i < PLATES; i++) {
      const sp = plateSpec(i), ctr = sp.P(0.5, 0.5, 0.5, 0);
      const inMat = phong({ map: toTex(innerBase), shininess: 40 });
      const mesh = new THREE.Mesh(plateGeo(sp, ctr), [M.shell, inMat, M.edge]); mesh.name = 'plate';
      const grp = new THREE.Group(); grp.position.copy(ctr); grp.add(mesh);
      if (cfg.legs) {   // 헤엄다리 한 쌍 (익은 새우는 없이)
        const sm = (sp.s0 + sp.s1) / 2, f = spine(sm);
        [-1, 1].forEach((side) => {
          const ls = new THREE.Shape(); ls.moveTo(-0.12, 0); ls.quadraticCurveTo(-0.17, -0.55, -0.02, -0.95); ls.quadraticCurveTo(0.11, -0.55, 0.12, 0); ls.lineTo(-0.12, 0);
          const lgeo = new THREE.ShapeGeometry(ls, 6), lu = lgeo.attributes.uv, lp = lgeo.attributes.position; for (let k = 0; k < lp.count; k++) { lu.setXY(k, -lp.getY(k) / 0.95, 0.5); lp.setZ(k, 0.1 * Math.sin((-lp.getY(k) / 0.95) * Math.PI)); }
          const lg = new THREE.Mesh(lgeo, M.leg);
          lg.position.copy(at(sm, side * Math.PI * 0.86, 1.0).sub(ctr));
          lg.quaternion.setFromUnitVectors(new V3(0, -1, 0), f.n.clone().multiplyScalar(-1).addScaledVector(f.t, -0.75).addScaledVector(f.b, side * 0.12 - 0.25).normalize());
          lg.name = 'leg'; grp.add(lg);
        });
      }
      grp.userData = { i, sp, ctr: ctr.clone(), mesh, inMat, peeled: false, frame: sp.fm };
      g.add(grp); plates.push(grp);
    }
    // 꼬리 — 쿠킹마마 새우튀김 꼬리처럼 뾰족하게 갈라진 불꽃 모양, 끝이 살짝 들려요
    const f1 = spine(1), e1 = f1.t.clone(), e2 = f1.n.clone().multiplyScalar(Math.cos(0.32)).addScaledVector(f1.b, Math.sin(0.32)).normalize(), e3 = new V3().crossVectors(e1, e2);
    const fan = (len, wid, ang, z, lift) => {
      const sh = new THREE.Shape();
      sh.moveTo(0, -wid * 0.32); sh.bezierCurveTo(len * 0.3, -wid * 0.62, len * 0.7, -wid * 0.42, len, -wid * 0.04); sh.lineTo(len * 0.96, wid * 0.06); sh.bezierCurveTo(len * 0.7, wid * 0.4, len * 0.3, wid * 0.5, 0, wid * 0.32); sh.lineTo(0, -wid * 0.32);
      const geo = new THREE.ExtrudeGeometry(sh, { depth: 0.05, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.035, bevelSegments: 2, curveSegments: 16 });
      const p = geo.attributes.position, uv = geo.attributes.uv;
      for (let k = 0; k < p.count; k++) { const t = p.getX(k) / len; uv.setXY(k, t, p.getY(k) / wid + 0.5); p.setZ(k, p.getZ(k) + lift * t * t + 0.08 * Math.sin(t * Math.PI)); }
      geo.computeVertexNormals();
      const d1 = e1.clone().multiplyScalar(Math.cos(ang)).addScaledVector(e2, Math.sin(ang)), d2 = new V3().crossVectors(e3, d1);
      const m = new THREE.Mesh(geo, M.tail); m.matrixAutoUpdate = false;
      m.matrix.makeBasis(d1, d2, e3).setPosition(f1.p.clone().addScaledVector(e1, -0.2).addScaledVector(e3, z)); m.name = 'tail';
      return m;
    };
    g.add(fan(2.5, 0.72, 0.36, -0.03, 0.55), fan(2.5, 0.72, -0.36, -0.03, 0.55), fan(2.75, 0.78, 0.13, 0.02, 0.7), fan(2.75, 0.78, -0.13, 0.02, 0.7), fan(2.1, 0.42, 0, 0.08, 0.8));
    const box = new THREE.Box3().setFromObject(g), c = box.getCenter(new V3()), bodyBox = new THREE.Box3().setFromObject(body);
    g.children.forEach((ch) => { if (ch.matrixAutoUpdate) ch.position.sub(c); else { ch.matrix.elements[12] -= c.x; ch.matrix.elements[13] -= c.y; ch.matrix.elements[14] -= c.z; } });
    plates.forEach((p) => p.userData.ctr.sub(c));
    g.userData = { plates, low: bodyBox.min.y - c.y - 0.08, c };
    return g;
  }

  /* ---------- 장면 — 보내 준 쿠킹마마 화면의 식탁 그대로 ---------- */
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, col('#f1c4cf'), 0.56));
  const key = new THREE.DirectionalLight(0xffffff, 0.62); key.position.set(-5, 14, 11); scene.add(key);
  const rimL = new THREE.DirectionalLight(col('#fff3e6'), 0.2); rimL.position.set(9, 7, -9); scene.add(rimL);
  const cam = new THREE.PerspectiveCamera(24, 1.25, 0.5, 300);
  function rounded(w, d, h, r, bev) {
    const s = new THREE.Shape(), x = -w / 2, y = -d / 2;
    s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r); s.lineTo(x + w, y + d - r); s.quadraticCurveTo(x + w, y + d, x + w - r, y + d);
    s.lineTo(x + r, y + d); s.quadraticCurveTo(x, y + d, x, y + d - r); s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
    const g = new THREE.ExtrudeGeometry(s, { depth: Math.max(0.01, h - 2 * bev), bevelEnabled: true, bevelThickness: bev, bevelSize: bev, bevelSegments: 5, curveSegments: 12 });
    g.rotateX(-Math.PI / 2); g.translate(0, bev, 0);
    const uv = g.attributes.uv, p = g.attributes.position; for (let i = 0; i < p.count; i++) uv.setXY(i, p.getX(i) / w + 0.5, p.getZ(i) / d + 0.5);
    return g;
  }
  const plane = (w, h, mat, y = 0) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat); m.rotation.x = -Math.PI / 2; m.position.y = y; return m; };
  const lathe = (pts, mat, seg = 80) => new THREE.Mesh(new THREE.LatheGeometry(pts.map(([a, b]) => new THREE.Vector2(a, b)), seg), mat);
  let floorY = 0;
  const setting = cfg.setting || 'flower';
  // 무궁화 닮은 하와이 꽃(히비스커스) — 접시 · 냅킨 무늬
  function hibiscus(g, x, y, r, rot, fill, line, vein) {
    g.save(); g.translate(x, y); g.rotate(rot);
    for (let i = 0; i < 5; i++) {
      g.rotate((Math.PI * 2) / 5); g.beginPath(); g.moveTo(0, 0);
      g.bezierCurveTo(r * 0.2, -r * 0.32, r * 0.62, -r * 0.62, r * 0.98, -r * 0.22); g.bezierCurveTo(r * 1.08, r * 0.12, r * 0.62, r * 0.32, 0, 0);
      if (fill) { g.fillStyle = fill; g.fill(); }
      if (line) { g.strokeStyle = line; g.lineWidth = Math.max(1.5, r * 0.07); g.stroke(); }
      if (vein) { g.strokeStyle = vein; g.lineWidth = Math.max(1, r * 0.035); g.beginPath(); g.moveTo(r * 0.15, -r * 0.05); g.quadraticCurveTo(r * 0.5, -r * 0.2, r * 0.82, -r * 0.18); g.stroke(); }
    }
    g.fillStyle = line || vein || '#fff'; g.beginPath(); g.arc(0, 0, r * 0.13, 0, 7); g.fill();
    g.restore();
  }
  const rr = (() => { let q = 99; return () => ((q = (q * 1664525 + 1013904223) >>> 0) / 4294967296); })();
  const flowerPlateTex = () => {
    const c = document.createElement('canvas'); c.width = c.height = 1024; const g = c.getContext('2d');
    const gr = g.createRadialGradient(512, 512, 40, 512, 512, 512); gr.addColorStop(0, '#ffffff'); gr.addColorStop(0.7, '#f6f9fc'); gr.addColorStop(1, '#e3eaf2'); g.fillStyle = gr; g.fillRect(0, 0, 1024, 1024);
    const pal = [['#8ec0ef', '#5f97d6'], ['#b5ddf4', '#7fb7e0'], ['#a5dcbc', '#5fb07f'], ['#86cfd9', '#4aa6b8'], ['#c9e6f7', '#8dbfe0']];
    for (let i = 0; i < 46; i++) {   // 테두리를 따라 촘촘히
      const a = rr() * Math.PI * 2, r0 = 512 * (0.66 + rr() * 0.3), p = pal[i % pal.length];
      hibiscus(g, 512 + Math.cos(a) * r0, 512 + Math.sin(a) * r0, 58 + rr() * 36, rr() * 6, p[0], null, p[1]);
    }
    for (let i = 0; i < 10; i++) { const a = rr() * Math.PI * 2, r0 = 512 * (0.18 + rr() * 0.4), p = pal[(i + 2) % pal.length]; hibiscus(g, 512 + Math.cos(a) * r0, 512 + Math.sin(a) * r0, 40 + rr() * 26, rr() * 6, p[0], null, p[1]); }
    g.globalAlpha = 0.12; g.fillStyle = '#ffffff'; g.fillRect(0, 0, 1024, 1024); g.globalAlpha = 1;
    return toTex(c);
  };
  const napkinTex = () => {
    const c = document.createElement('canvas'); c.width = c.height = 512; const g = c.getContext('2d');
    g.fillStyle = '#fffafc'; g.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 16; i++) hibiscus(g, rr() * 512, rr() * 512, 34 + rr() * 30, rr() * 6, i % 3 ? null : '#ffd6e4', '#ff9fbf', null);
    g.strokeStyle = 'rgba(255,170,200,.5)'; g.lineWidth = 6; g.strokeRect(10, 10, 492, 492);
    return toTex(c);
  };
  const leafTex = toTex(paint(256, 64, (x, y) => { const v = Math.abs(y - 0.5) * 2, n = fbm(x * 20, y * 6, 111, 3); let c = mix(hex('#3f9c3e'), hex('#1f5f25'), clamp(v * 0.8 + (n - 0.5) * 0.4)); if (v < 0.06) c = mix(c, hex('#b8e69a'), 0.8); if (Math.abs(((x * 9) % 1) - (1 - v) * 0.45) < 0.03 && v < 0.85) c = mix(c, hex('#8fd07a'), 0.6); return c; }));
  function sprig(len, n, sc) {   // 톱니 잎 줄기 하나
    const g = new THREE.Group(), stem = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.08, len, 6), phong({ color: col('#4c8a2e') })); stem.rotation.z = Math.PI / 2; stem.position.x = len / 2; g.add(stem);
    const leafGeo = (() => { const sh = new THREE.Shape(), L = 2.2 * sc, W = 0.55 * sc, pts = 14; sh.moveTo(0, 0); for (let i = 1; i <= pts; i++) { const t = i / pts, w = W * Math.sin(Math.PI * t) ** 0.8 * (i % 2 ? 1 : 0.8); sh.lineTo(L * t, w); } for (let i = pts - 1; i >= 0; i--) { const t = i / pts, w = W * Math.sin(Math.PI * t) ** 0.8 * (i % 2 ? 1 : 0.8); sh.lineTo(L * t, -w); } const geo = new THREE.ShapeGeometry(sh), uv = geo.attributes.uv, pp = geo.attributes.position; for (let k = 0; k < pp.count; k++) { uv.setXY(k, pp.getX(k) / L, pp.getY(k) / (2 * W) + 0.5); pp.setZ(k, 0.25 * (pp.getY(k) / W) ** 2 * sc); } geo.rotateX(-Math.PI / 2); geo.computeVertexNormals(); return geo; })();
    const lm = phong({ map: leafTex, side: THREE.DoubleSide, shininess: 60 });
    for (let i = 0; i < n; i++) { const t = (i + 1) / (n + 0.5); [-1, 1].forEach((sd) => { if (i === n - 1 && sd > 0) return; const l = new THREE.Mesh(leafGeo, lm); l.position.set(len * t, 0.05, 0); l.rotation.y = i === n - 1 ? 0 : sd * (0.95 - t * 0.3); l.scale.setScalar(0.75 + 0.35 * t); g.add(l); }); }
    const tip = new THREE.Mesh(leafGeo, lm); tip.position.set(len, 0.05, 0); g.add(tip);
    return g;
  }
  function lemon(sc) {   // 레몬 한 조각 — 배 모양 껍질 + 과육 단면
    const g = new THREE.Group();
    const rind = new THREE.Mesh(new THREE.SphereGeometry(1, 36, 18, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), phong({ map: toTex(paint(64, 64, (x, y) => mix(hex('#ffe34a'), hex('#ffc400'), fbm(x * 30, y * 30, 121, 2)))), shininess: 90, specular: col('#fff6c0') }));
    rind.scale.set(2.2, 1.05, 0.95);
    const fc = document.createElement('canvas'); fc.width = 256; fc.height = 128; const fg = fc.getContext('2d'); fg.fillStyle = '#fff1a0'; fg.fillRect(0, 0, 256, 128);
    fg.fillStyle = 'rgba(255,222,90,.75)'; for (let i = 0; i < 9; i++) { fg.beginPath(); fg.moveTo(128, 128); fg.lineTo(i * 32 + 6, 6); fg.lineTo(i * 32 + 26, 6); fg.closePath(); fg.fill(); }
    fg.strokeStyle = '#fffbe6'; fg.lineWidth = 10; fg.strokeRect(0, 0, 256, 128);
    const face = new THREE.Mesh(new THREE.CircleGeometry(1, 36), phong({ map: toTex(fc), shininess: 100, side: THREE.DoubleSide }));
    const fu = face.geometry.attributes.uv, fp = face.geometry.attributes.position; for (let i = 0; i < fp.count; i++) fu.setXY(i, (fp.getX(i) + 1) / 2, Math.abs(fp.getY(i)));
    face.rotation.x = -Math.PI / 2; face.scale.set(2.15, 0.9, 1); face.position.y = 0.01;
    g.add(rind, face); g.rotation.x = 1.05; const w = new THREE.Group(); w.add(g); g.position.y = 0.9; w.scale.setScalar(sc); return w;
  }
  const pinkRoom = () => {
    scene.background = col('#ffa3ba');
    const tb = plane(140, 62, new THREE.MeshLambertMaterial({ map: ging('#ffd3de', '#ffb3c6', [30, 13], 0.4) })); tb.position.z = 15; scene.add(tb);
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(200, 15), new THREE.MeshBasicMaterial({ map: wallTex('#ffb3c6', '#ff93ae') })); wall.position.set(0, 7.5, -16); scene.add(wall);
  };
  if (setting === 'flower') {   // 새우 요리 화면 — 분홍 깅엄 매트 · 꽃무늬 냅킨 · 하와이 꽃 접시 · 잎 줄기 · 레몬
    pinkRoom();
    scene.add(new THREE.Mesh(rounded(33, 22, 0.1, 1.2, 0.04), new THREE.MeshLambertMaterial({ color: col('#ffc3d2') })));
    scene.add(new THREE.Mesh(rounded(31.6, 20.6, 0.12, 0.9, 0.04), new THREE.MeshLambertMaterial({ map: ging('#ffe6ed', '#ff9fba', [9, 6]) })));
    const nm = new THREE.MeshLambertMaterial({ map: napkinTex(), side: THREE.DoubleSide });
    [[-8.5, 3.2, 0.75], [8.0, -2.4, 0.55], [-2.0, 6.0, -0.2]].forEach(([x, z, r], i) => { const n = plane(12.5, 12.5, nm, 0.14 + i * 0.01); n.position.x = x; n.position.z = z; n.rotation.z = r; scene.add(n); });
    const lg = new THREE.LatheGeometry([[0.01, 0.1], [6.0, 0.1], [7.0, 0.35], [8.2, 0.9], [8.7, 1.05], [8.85, 0.95], [8.4, 0.6], [6.8, 0.08], [6.2, 0]].map(([a, b]) => new THREE.Vector2(a, b)), 96);
    const pu = lg.attributes.uv, pp = lg.attributes.position; for (let i = 0; i < pp.count; i++) pu.setXY(i, pp.getX(i) / 17.7 + 0.5, 0.5 - pp.getZ(i) / 17.7);
    const pl = new THREE.Mesh(lg, phong({ map: flowerPlateTex(), shininess: 120, specular: col('#9a9a9a'), side: THREE.DoubleSide })); pl.position.y = 0.16; pl.scale.set(1, 1, 0.92); scene.add(pl);
    const s1 = sprig(9, 4, 1.0); s1.position.set(-6.5, 0.3, 1.6); s1.rotation.y = Math.PI * 0.86; scene.add(s1);
    const s2 = sprig(8, 4, 0.95); s2.position.set(6.6, 0.3, -2.2); s2.rotation.y = -0.18; scene.add(s2);
    const lm = lemon(1.0); lm.position.set(-6.0, 0.3, 3.2); lm.rotation.set(0, -0.9, 0.35); scene.add(lm);
    floorY = 0.26;
  } else if (setting === 'square') {   // 랍스터 그라탱 화면 — 흰 네모 접시 · 민트 냅킨 · 분홍 깅엄 받침
    pinkRoom();
    const under = new THREE.Mesh(rounded(29, 21, 0.1, 1.2, 0.04), new THREE.MeshLambertMaterial({ map: ging('#ffd1dd', '#ff9ab5', [7, 5]) })); under.rotation.y = 0.05; scene.add(under);
    const cloth = new THREE.Mesh(rounded(22.5, 17, 0.12, 0.6, 0.04), new THREE.MeshLambertMaterial({ map: fabric('#2fb9c3', '#7fe0e4', [3, 2]) })); cloth.position.y = 0.1; cloth.rotation.y = 0.32; scene.add(cloth);
    const pl = new THREE.Mesh(rounded(17.5, 12.5, 0.75, 1.3, 0.3), phong({ map: ceramic('#ffffff', '#dfe5ec'), shininess: 110, specular: col('#8a8a8a') })); pl.position.y = 0.24; pl.rotation.y = -0.08; scene.add(pl);
    floorY = 0.99;
  } else if (setting === 'round') {   // 함박스테이크 화면 — 노란 테 두 줄 둥근 접시
    pinkRoom();
    const cloth = new THREE.Mesh(rounded(28, 22, 0.1, 0.5, 0.04), new THREE.MeshLambertMaterial({ map: fabric('#fbe7f3', '#a9d8ee', [2, 2]) })); cloth.rotation.y = -0.5; scene.add(cloth);
    const pl = lathe([[0.01, 0.12], [7.6, 0.12], [8.6, 0.32], [10.6, 0.95], [11.4, 1.1], [11.55, 0.98], [11.2, 0.75], [9.4, 0.12], [8.4, 0]], phong({ color: col('#ffffff'), shininess: 110, specular: col('#8a8a8a'), side: THREE.DoubleSide })); pl.position.y = 0.1; pl.scale.set(0.86, 1, 0.72); scene.add(pl);
    const band = (a, b, c) => { const m = lathe([a, b].map((r) => [r, lerp(0.32, 0.95, clamp((r - 8.6) / 2)) + 0.03]), phong({ color: col(c), shininess: 90, side: THREE.DoubleSide })); m.position.y = 0.1; m.scale.copy(pl.scale); scene.add(m); };
    band(9.9, 10.5, '#ffcc33'); band(9.15, 9.4, '#ffa51f');
    floorY = 0.22;
  } else {   // 라자냐 화면 — 나무 식탁 · 노란 테 체크 매트 · 파란 오븐 그릇
    scene.background = col('#e2a066');
    scene.add(plane(140, 100, new THREE.MeshLambertMaterial({ map: woodTex([9, 7]) })));
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(200, 44), new THREE.MeshBasicMaterial({ map: woodTex([12, 3]) })); wall.position.set(0, 20, -30); scene.add(wall);
    scene.add(new THREE.Mesh(rounded(32, 23, 0.12, 1.4, 0.05), new THREE.MeshLambertMaterial({ color: col('#ffd23d') })));
    scene.add(new THREE.Mesh(rounded(29.5, 20.5, 0.14, 1.0, 0.05), new THREE.MeshLambertMaterial({ map: ging('#fff7c9', '#ffe47a', [5, 3.5], 0.35) })));
    const check = new THREE.Mesh(rounded(20, 15, 0.16, 0.4, 0.05), new THREE.MeshLambertMaterial({ map: ging('#fff8f1', '#f2b98e', [7, 5]) })); check.rotation.y = 0.04; scene.add(check);
    const dish = lathe([[0.01, 0.15], [9.2, 0.15], [9.8, 0.4], [10.8, 1.6], [11.25, 2.0], [11.45, 1.85], [10.6, 0.6], [9.6, 0]], phong({ color: col('#36a6e6'), shininess: 120, specular: col('#9adfff'), side: THREE.DoubleSide })); dish.scale.set(0.86, 1, 0.56); dish.position.y = 0.2; scene.add(dish);
    const lip = lathe([[11.0, 1.96], [11.5, 2.02], [11.6, 1.9]], phong({ color: col('#ffffff'), shininess: 100, side: THREE.DoubleSide })); lip.scale.copy(dish.scale); lip.position.y = 0.2; scene.add(lip);
    const inside = new THREE.Mesh(new THREE.CircleGeometry(9.3, 64), phong({ map: ceramic('#ffffff', '#e8eef4'), shininess: 80 })); inside.rotation.x = -Math.PI / 2; inside.scale.set(0.86, 0.56, 1); inside.position.y = 0.37; scene.add(inside);
    floorY = 0.38;
  }

  /* ---------- 새우 놓기 ---------- */
  const fleshMat = phong({ map: fleshTex(cfg.mode === 'flesh' ? cfg.fleshText || [] : []), shininess: 55, specular: col('#4a3a36') });
  const shrimp = buildShrimp(fleshMat), SC = cfg.scale || 1.32, YAW0 = cfg.yaw0 !== undefined ? cfg.yaw0 : 2.75;
  shrimp.scale.setScalar(SC);
  const holder = new THREE.Group(); holder.add(shrimp); scene.add(holder);
  const restY = floorY - shrimp.userData.low * SC + 0.02;
  holder.position.set(0, restY, 0.4);
  cam.position.set(0, restY + 17.5, 26.5); cam.lookAt(0, restY - 0.8, -1.6);
  const blob = plane(12, 9, M.blob, floorY + 0.03); blob.position.z = 0.4; scene.add(blob);
  const plates = shrimp.userData.plates;
  plates.forEach((g) => { g.userData.home = { p: g.position.clone(), q: g.quaternion.clone() }; });

  /* ---------- 글 (껍질 안쪽 모드) — 벗긴 순서대로 한 낱말씩 ---------- */
  const words = cfg.mode === 'shell' ? cfg.words || [] : [];
  let peelCount = 0;
  function writeInside(grp, text) {
    const c = document.createElement('canvas'); c.width = 512; c.height = 128; const g = c.getContext('2d');
    g.drawImage(innerBase, 0, 0);
    g.save(); g.translate(0, c.height); g.scale(1, -1);   // 안쪽에서 보면 위아래가 뒤집혀 보여서 거꾸로 써 둬요
    g.fillStyle = '#7e2416'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.font = `700 62px ${FONT}, sans-serif`;
    g.fillText(text, c.width / 2, c.height / 2 + 4, c.width * 0.86); g.restore();
    grp.userData.inMat.map = toTex(c); grp.userData.inMat.needsUpdate = true;
  }

  /* ---------- 돌리기 · 톡 누르기 ---------- */
  let yaw = 0, pitch = 0, vy = 0, vp = 0, drag = null, touched = false, tIdle = 0, wiggle = 0;
  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
  canvas.addEventListener('pointerdown', (e) => { canvas.setPointerCapture(e.pointerId); drag = { x: e.clientX, y: e.clientY, x0: e.clientX, y0: e.clientY, moved: false }; touched = true; vy = vp = 0; });
  canvas.addEventListener('pointermove', (e) => {
    if (!drag) return;
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (Math.hypot(e.clientX - drag.x0, e.clientY - drag.y0) > 6) drag.moved = true;
    if (drag.moved) { yaw += dx * 0.011; pitch = clamp(pitch + dy * 0.009, -1.25, 1.25); vy = dx * 0.011; vp = dy * 0.009; }
    drag.x = e.clientX; drag.y = e.clientY;
  });
  canvas.addEventListener('pointerup', (e) => {
    if (!drag) return;
    if (!drag.moved) {
      const r = canvas.getBoundingClientRect(); ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
      ray.setFromCamera(ndc, cam);
      const hits = ray.intersectObject(shrimp, true);
      let grp = null;
      for (const h of hits) { let o = h.object; while (o && o.parent !== shrimp) o = o.parent; if (o && o.userData && o.userData.mesh) { if (!o.userData.peeled) { grp = o; break; } } else break; }
      if (!grp && hits.length) grp = plates.find((p) => !p.userData.peeled);
      if (grp) peel(grp); else if (hits.length) wiggle = 1;
    }
    drag = null;
  });
  canvas.addEventListener('pointercancel', () => { drag = null; });

  /* ---------- 껍질 벗기기 ---------- */
  const flying = [];
  function peel(grp) {
    grp.userData.peeled = true; peelCount++;
    const order = peelCount - 1;
    if (words.length) writeInside(grp, words[order % words.length]);
    scene.attach(grp);
    const from = { p: grp.position.clone(), q: grp.quaternion.clone() };
    let to;
    if (cfg.mode === 'shell') {   // 카메라 앞에 세 칸씩 두 줄 — 펴진 껍질 안쪽 글이 보이게
      const f = grp.userData.frame, fwd = cam.getWorldDirection(new V3()), right = new V3().crossVectors(fwd, cam.up).normalize(), upv = new V3().crossVectors(right, fwd);
      const c = fwd.clone().negate(), u = new V3().crossVectors(right, c);
      const dst = new THREE.Matrix4().makeBasis(right, u, c.clone().negate()), src = new THREE.Matrix4().makeBasis(f.b, f.t, f.n);
      const q = new THREE.Quaternion().setFromRotationMatrix(dst.multiply(src.invert()));
      const k = order % 3, row = Math.floor(order / 3);
      // 펼친 카드의 가운데는 grp 원점에서 등 쪽으로 떨어져 있어서 그만큼 빼 줘요
      const off = f.p.clone().sub(shrimp.userData.c).addScaledVector(f.n, grp.userData.sp.rm).sub(grp.userData.ctr).applyQuaternion(q).multiplyScalar(0.36);
      const p = cam.position.clone().addScaledVector(fwd, 21).addScaledVector(right, (k - 1) * 3.0).addScaledVector(upv, row ? 0.8 : 2.15).sub(off.multiplyScalar(0.92));
      to = { p, q, s: 0.33 };
      grp.children.forEach((ch) => { if (ch.name === 'leg') ch.visible = false; });
    } else {   // 껍질은 접시 앞 양옆으로 툭
      const side = order % 2 ? 1 : -1, k2 = Math.floor(order / 2), f = grp.userData.frame, ps = 1.8 - order * 0.9 + side;
      const h1 = new V3(Math.cos(ps), 0, -Math.sin(ps)), h2 = new V3(-Math.sin(ps), 0, -Math.cos(ps));
      const q = new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(h1, h2, new V3(0, 1, 0)).multiply(new THREE.Matrix4().makeBasis(f.b, f.t, f.n).invert()));
      const ang = [2.45, 0.7, 3.1, 0.04, 1.95, 1.2][order % 6], p = new V3(Math.cos(ang) * 7.0, 0, -Math.sin(ang) * 5.6 + 0.9), sc = SC * 0.52;
      const keep = [grp.position.clone(), grp.quaternion.clone(), grp.scale.clone()];
      grp.position.copy(p); grp.quaternion.copy(q); grp.scale.setScalar(sc); grp.updateMatrixWorld(true);
      p.y += floorY + 0.03 - new THREE.Box3().setFromObject(grp.userData.mesh).min.y;
      grp.position.copy(keep[0]); grp.quaternion.copy(keep[1]); grp.scale.copy(keep[2]);
      to = { p, q, s: sc };
    }
    flying.push({ grp, from, to, t: 0, unroll: cfg.mode === 'shell' });
    root.dispatchEvent(new CustomEvent('peel', { detail: { count: peelCount, total: PLATES, word: words[order] } }));
  }
  function setShape(grp, f) { const geo = grp.userData.mesh.geometry, sp = grp.userData.sp; geo.attributes.position.array.set(plateVerts(sp, f, sp.P(0.5, 0.5, 0.5, 0))); geo.attributes.position.needsUpdate = true; geo.computeVertexNormals(); }
  function reset() {
    flying.length = 0; peelCount = 0;
    plates.forEach((g) => {
      shrimp.attach(g); g.userData.peeled = false; g.scale.setScalar(1); g.position.copy(g.userData.home.p); g.quaternion.copy(g.userData.home.q);
      g.userData.inMat.map = toTex(innerBase); g.userData.inMat.needsUpdate = true; g.children.forEach((ch) => { ch.visible = true; }); setShape(g, 0);
    });
    root.dispatchEvent(new CustomEvent('peel', { detail: { count: 0, total: PLATES } }));
  }

  /* ---------- 그리기 ---------- */
  function size() {
    const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
    R.setPixelRatio(Math.min(2, window.devicePixelRatio || 1)); R.setSize(w, h, false); cam.aspect = w / h;
    cam.fov = Math.max(26, (2 * Math.atan(Math.tan((13 * Math.PI) / 180) * 1.6 / cam.aspect) * 180) / Math.PI);   // 좁은 화면에서도 접시 폭이 다 보이게
    cam.updateProjectionMatrix();
  }
  new ResizeObserver(size).observe(canvas); size();
  let last = performance.now(), visible = true;
  new IntersectionObserver((es) => { visible = es[0].isIntersecting; }).observe(canvas);
  function frame(now) {
    requestAnimationFrame(frame);
    const dt = Math.min(0.05, (now - last) / 1000); last = now;
    if (!visible) return;
    tIdle += dt;
    if (!drag) { yaw += vy; pitch += vp; vy *= 0.92; vp *= 0.92; if (!touched) yaw = Math.sin(tIdle * 0.6) * 0.35; pitch *= 0.985; }
    wiggle = Math.max(0, wiggle - dt * 3);
    holder.rotation.set(pitch + Math.sin(wiggle * 18) * wiggle * 0.08, yaw + YAW0, 0, 'YXZ');
    holder.position.y = restY + Math.abs(Math.sin(pitch)) * 2.2;
    for (let i = flying.length - 1; i >= 0; i--) {
      const f = flying[i]; f.t += Math.min(0.25, (now - (f.last || now)) / 1000 || dt) / 0.85; f.last = now; const u = ease(clamp(f.t));
      const mid = f.from.p.clone().lerp(f.to.p, u); mid.y += Math.sin(Math.PI * clamp(f.t)) * 3.2;
      f.grp.position.copy(mid); f.grp.quaternion.copy(f.from.q).slerp(f.to.q, u); f.grp.scale.setScalar(lerp(1, f.to.s, u));
      if (f.unroll) setShape(f.grp, ease(clamp(f.t * 1.2 - 0.15)));
      if (f.t >= 1) flying.splice(i, 1);
    }
    R.render(scene, cam);
  }
  requestAnimationFrame(frame);
  return { peel: () => { const g = plates.find((p) => !p.userData.peeled); if (g) peel(g); }, reset, plates, get count() { return peelCount; } };
}
