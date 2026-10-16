// luvlinks 터미널 프로필 — 노릴스크 · 한국 날짜와 시간 그림 (Cloudflare Worker)
// profile.css 의 Hardware 맨 위 두 줄(NORILSK · KOREA)이 이 워커 주소를 그림으로 불러가요.
// 그림 안에서 분 · 시 · 날짜가 스스로 넘어가요 — 페이지를 열어 둔 채로도 시계가 흘러가요.
//   https://<워커 주소>/                         → 지금
//   https://<워커 주소>/?at=2026-10-17T14:59:50Z  → 그 시각으로 (확인용)

const ZONES = [7, 9];   // 노릴스크 UTC+7, 한국 UTC+9 (둘 다 서머타임 없음)
const INK = '#f3f6f4';  // 글자색 — profile.css 의 값 글자와 같아요
// 한 칸 폭 · 줄 높이 · 글자 바닥선 · 글자 크기 — profile.css 의 글자와 같은 비율
const CH = 20, LH = 41, BASE = 33.16, SIZE = (CH / 0.5859) * 1.07;
const WD = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
// Cascadia Mono 600 — 시계에 쓰는 글자만 남긴 글꼴. 그림 속 글꼴은 그림 안에 넣어야 해서, 한 번 받아 두고 계속 써요
const FONT_URL = 'https://raw.githubusercontent.com/ryuksohyeon-stack/log/3a826e17e4b643b0e6db3b0180b1ae4e6799907f/terminal/clock-font.woff2';
let font = '';

async function loadFont() {
  if (font) return font;
  try {
    const r = await fetch(FONT_URL);
    if (r.ok) {
      let s = '';
      for (const b of new Uint8Array(await r.arrayBuffer())) s += String.fromCharCode(b);
      font = btoa(s);
    }
  } catch (e) {}
  return font;   // 못 받으면 빈 값 — 그때는 기본 고정폭 글꼴로 그려요
}

const pad = (n) => String(n).padStart(2, '0');
// 글자마다 제 칸에 (col 번째 칸부터)
const text = (s, col, y) => `<text x="${[...s].map((_, i) => (col + i) * CH).join(' ')}" y="${y}">${s}</text>`;
// 글자 띠 — 보일 것들을 세로로 쌓아 두고 dur 초 동안 한 칸씩 올려요. 이미 지난 초(past)만큼 앞당겨 시작해 지금 칸에 맞춰요
function strip(items, col, row, dur, past, once) {
  const top = row * LH;
  return `<g clip-path="url(#r${row})"><g>${items.map((s, k) => text(s, col, top + BASE + k * LH)).join('')}`
    + `<animateTransform attributeName="transform" type="translate" calcMode="discrete" values="${items.map((_, k) => `0 ${-k * LH}`).join(';')}"`
    + ` dur="${dur}s" begin="${(-past).toFixed(3)}s" ${once ? 'fill="freeze"' : 'repeatCount="indefinite"'}/></g></g>`;
}
// 한 줄: 2026-10-17 Sat 14:32 (UTC+7)
function line(now, tz, row) {
  const t = now / 1000 + tz * 3600;              // 그 도시 시각(초)
  const sec = ((t % 86400) + 86400) % 86400;      // 그 도시 자정부터 지난 초
  const days = [0, 1, 2].map((k) => new Date((Math.floor(t / 86400) + k) * 86400e3));
  const ymd = (d) => `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}`;
  return strip(days.map(ymd), 0, row, 3 * 86400, sec, true)
    + strip(days.map((d) => WD[d.getUTCDay()]), 11, row, 3 * 86400, sec, true)
    + strip(Array.from({ length: 24 }, (_, h) => pad(h)), 15, row, 86400, sec)
    + text(':', 17, row * LH + BASE)
    + strip([...'012345'], 18, row, 3600, sec % 3600)
    + strip([...'0123456789'], 19, row, 600, sec % 600)
    + text(`(UTC+${tz})`, 21, row * LH + BASE);
}
function svg(now, f) {
  const W = 29 * CH, H = ZONES.length * LH;   // 28칸 + 끝 글자 여유 한 칸
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`
    + `<style>${f ? `@font-face{font-family:C;src:url(data:font/woff2;base64,${f}) format("woff2")}` : ''}text{font:600 ${SIZE.toFixed(3)}px C,monospace;fill:${INK}}</style>`
    + `<defs>${ZONES.map((_, r) => `<clipPath id="r${r}"><rect y="${r * LH}" width="${W}" height="${LH}"/></clipPath>`).join('')}</defs>`
    + ZONES.map((tz, r) => line(now, tz, r)).join('') + '</svg>';
}

export default {
  async fetch(request) {
    const at = Date.parse(new URL(request.url).searchParams.get('at') || '');
    return new Response(svg(Number.isNaN(at) ? Date.now() : at, await loadFont()), {
      headers: { 'content-type': 'image/svg+xml; charset=utf-8', 'cache-control': 'no-store' },   // 늘 새로 — 묵은 시각이 남지 않게
    });
  },
};
