// 연인 디데이 그림(terminal/dday.png)을 오늘(한국 시간) 기준으로 다시 그려요.
// luvlinks 프로필 CSS(terminal/profile.css)가 이 그림을 불러와서, 디데이 숫자가 매일 저절로 바뀌어요.
// 그림에는 두 줄이 들어가요: 「D+238」(UPTIME) · 「2026-10-17」(DATE, 오늘). 사귄 날을 1일로 세요.
//   node terminal/dday.mjs                    → 오늘
//   DD_DATE=2026-10-16 node terminal/dday.mjs → 그 날짜로 (확인용)
//   DD_OUT=다른/폴더 → 그림을 그 폴더에 저장 (기본: 이 파일 옆)
//   DD_FONT_FILE=글꼴.woff2 → 글꼴을 내려받지 않고 이 파일로 (인터넷이 막힌 곳에서 확인할 때)
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const START = '2026-02-22';   // 사귄 날
const TZ = 'Asia/Seoul';
const INK = '#f4f6f6';        // 글자색 — profile.css 의 --t-fg 와 같아야 해요
// profile.css 의 @font-face 와 같은 글꼴 · 같은 줄 높이(--L 1.3)로 그려야 글자 크기와 줄이 딱 맞아요
const FONT = 'https://cdn.jsdelivr.net/npm/@fontsource/cascadia-mono@5.2.3/files/cascadia-mono-latin-400-normal.woff2';
const PX = 40;

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = process.env.DD_OUT || here;
const { chromium } = await import(process.env.PW || 'playwright');

function today() {
  if (process.env.DD_DATE) { const [y, m, d] = process.env.DD_DATE.split('-').map(Number); return { y, m, d }; }
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: 'numeric', day: 'numeric' }).formatToParts(new Date()).map((x) => [x.type, x.value]));
  return { y: +p.year, m: +p.month, d: +p.day };
}
const { y, m, d } = today();
const [sy, sm, sd] = START.split('-').map(Number);
const days = Math.round((Date.UTC(y, m - 1, d) - Date.UTC(sy, sm - 1, sd)) / 864e5) + 1;
const pad = (n) => String(n).padStart(2, '0');
const lines = [days > 0 ? `D+${days}` : `D${days - 1}`, `${y}-${pad(m)}-${pad(d)}`];

const html = `<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:T;src:url(${FONT}) format("woff2")}
*{margin:0}html,body{background:transparent}
#c{display:inline-block;width:${Math.max(...lines.map((l) => l.length))}ch;font:400 ${PX}px/1.3 T;color:${INK};white-space:pre}
</style><div id="c">${lines.join('\n')}</div>`;

const args = process.env.HTTPS_PROXY ? ['--proxy-server=' + process.env.HTTPS_PROXY] : [];
const browser = await chromium.launch({ args });
const page = await browser.newPage({ viewport: { width: 800, height: 300 } });
if (process.env.DD_FONT_FILE) await page.route(FONT, (r) => r.fulfill({ path: process.env.DD_FONT_FILE, contentType: 'font/woff2' }));
await page.setContent(html, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
// 글꼴을 못 받았으면 다른 글꼴로 그려져 줄이 어긋나요 — 그런 그림은 저장하지 않아요
if (!(await page.evaluate((px) => document.fonts.check(`${px}px T`), PX))) throw new Error('Cascadia Mono 글꼴을 불러오지 못했어요');
await page.locator('#c').screenshot({ path: path.join(outDir, 'dday.png'), omitBackground: true });
await browser.close();
console.log(`dday ${lines.join(' · ')}`);
