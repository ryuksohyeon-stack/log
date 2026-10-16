// luvlinks 터미널 프로필 — 노릴스크 · 한국 날짜와 시간 그림 (Cloudflare Worker)
// profile.css 의 Hardware 상자 맨 위 두 줄(NORILSK · KOREA)이 이 워커 주소를 그림으로 불러가요.
// 그림 안에서 분 · 시 · 날짜가 스스로 넘어가요(SVG 애니메이션) — 페이지를 열어 둔 채로도 시계가 흘러가요.
//   https://<워커 주소>/                              → 지금
//   https://<워커 주소>/?at=2026-10-17T14:59:50Z       → 그 시각으로 (확인용)
// 바꿀 일이 생기면 ZONES(도시마다 UTC 와의 시차)만 고치면 돼요. 줄 이름(NORILSK · KOREA)은 profile.css 에 있어요.

const ZONES = [7, 9];                    // 노릴스크 UTC+7, 한국 UTC+9 — 둘 다 서머타임이 없어요
const INK = '#f3f6f4';                   // 글자색 — profile.css 의 값 글자와 같아요
// 한 칸 폭 · 줄 높이 · 글자 바닥선 — profile.css 의 글자(칸의 1.07배 크기, 줄 높이 2.05칸)와 같은 비율
const CH = 20, LH = 41, BASE = 33.16, SIZE = (CH / 0.5859) * 1.07;
const WD = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
// Cascadia Mono 600 — 시계에 쓰는 글자만 남긴 woff2 (그림 속 글꼴은 바깥에서 못 받아와서 안에 넣어 둬요)
const FONT = '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';

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
  const t = now / 1000 + tz * 3600;                  // 그 도시 시각(초)
  const sec = ((t % 86400) + 86400) % 86400;          // 그 도시 자정부터 지난 초
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
function svg(now) {
  const W = 29 * CH, H = ZONES.length * LH;   // 28칸 + 끝 글자 여유 한 칸
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`
    + `<style>@font-face{font-family:C;src:url(data:font/woff2;base64,${FONT}) format("woff2")}text{font:600 ${SIZE.toFixed(3)}px C,monospace;fill:${INK}}</style>`
    + `<defs>${ZONES.map((_, r) => `<clipPath id="r${r}"><rect y="${r * LH}" width="${W}" height="${LH}"/></clipPath>`).join('')}</defs>`
    + ZONES.map((tz, r) => line(now, tz, r)).join('') + '</svg>';
}

export default {
  async fetch(request) {
    const at = Date.parse(new URL(request.url).searchParams.get('at') || '');
    return new Response(svg(Number.isNaN(at) ? Date.now() : at), {
      headers: { 'content-type': 'image/svg+xml; charset=utf-8', 'cache-control': 'no-store' },   // 늘 새로 — 묵은 시각이 남지 않게
    });
  },
};
