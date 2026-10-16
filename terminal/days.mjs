// 터미널 프로필의 날짜 그림 두 장을 오늘 날짜로 다시 그려요. luvlinks 프로필 CSS(terminal/profile.css)가 불러가요.
//   anniv.png — Anniversary 상자:  D+238 · since 2026-02-22  /  가장 가까운 다가올 기념일 하나 (100일 단위 · 1년 단위 중)
//   dates.png — Uptime / Date 상자: 노릴스크 날짜  /  한국 날짜
// 사귄 날을 1일로 세요. 기념일은 100일마다(300 days …)와 해마다(1 year, 2 years …)예요. 오늘이 기념일이면 (TODAY).
//   node terminal/days.mjs                        → 지금
//   DD_NOW=2026-10-17T16:00:00Z node terminal/days.mjs → 그 시각으로 (확인용)
//   DD_OUT=다른/폴더 → 그림을 그 폴더에 저장 (기본: 이 파일 옆)
//   DD_FONT_FILE=글꼴.woff2 → 글꼴을 내려받지 않고 이 파일로 (인터넷이 막힌 곳에서 확인할 때)
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const START = '2026-02-22';   // 사귄 날
const INK = '#f3f6f4';        // 글자색 — profile.css 의 값 글자와 같아요
// profile.css 의 값 글자와 같은 글꼴 · 굵기(600) · 크기(칸의 1.07배, 자간 -0.07칸) · 줄 높이(2.05칸)로 그려야 딱 맞아요
const FONT = 'https://cdn.jsdelivr.net/npm/@fontsource/cascadia-mono@5.2.3/files/cascadia-mono-latin-600-normal.woff2';
const CH = 20, LR = 2.05;

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = process.env.DD_OUT || here;
const { chromium } = await import(process.env.PW || 'playwright');

const now = process.env.DD_NOW ? new Date(process.env.DD_NOW) : new Date();
const pad = (n) => String(n).padStart(2, '0');
const ymd = (d) => `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}`;
function localDay(tz) {   // 그 도시의 오늘 → UTC 자정 Date
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: 'numeric', day: 'numeric' }).formatToParts(now).map((x) => [x.type, x.value]));
  return new Date(Date.UTC(+p.year, +p.month - 1, +p.day));
}
const WD = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const kr = localDay('Asia/Seoul'), nor = localDay('Asia/Krasnoyarsk');
const start = new Date(START + 'T00:00:00Z');
const day = Math.round((kr - start) / 864e5) + 1;            // 한국 날짜로 센 디데이
// 다가올 기념일 — 100일 단위 하나(100일째 = 사귄 날 + 99일), 1년 단위 하나(같은 월일)
const left = (d) => { const n = Math.round((d - kr) / 864e5); return n ? `D-${n}` : 'TODAY'; };
const k = Math.max(100, Math.ceil(day / 100) * 100);
const next100 = new Date(start.getTime() + (k - 1) * 864e5);
let y = 1, nextY;
while ((nextY = new Date(Date.UTC(start.getUTCFullYear() + y, start.getUTCMonth(), start.getUTCDate()))) < kr) y++;
// 둘 중 먼저 오는 것 하나만 (같은 날이면 해 단위로)
const next = nextY <= next100 ? { d: nextY, t: `${y} year${y > 1 ? 's' : ''}` } : { d: next100, t: `${k} days` };
const anniv = [day > 0 ? `D+${day} · since ${START}` : `D${day - 1} · from ${START}`, `${next.t} · ${ymd(next.d)} (${left(next.d)})`];
const dates = [`${ymd(nor)} ${WD[nor.getUTCDay()]} (UTC+7)`, `${ymd(kr)} ${WD[kr.getUTCDay()]} (UTC+9)`];

const block = (id, lines, cols) => `<div id="${id}" style="width:${cols * CH}px;height:${lines.length * LR * CH}px">${lines.join('\n')}</div>`;
const html = `<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:T;font-weight:600;src:url(${FONT}) format("woff2")}
*{margin:0}html,body{background:transparent}
div{font:600 ${(CH / 0.5859) * 1.07}px/${LR * CH}px T;letter-spacing:${-0.07 * CH}px;color:${INK};white-space:pre;overflow:hidden;margin-bottom:10px}
</style>${block('anniv', anniv, 30)}${block('dates', dates, 22)}`;

const args = process.env.HTTPS_PROXY ? ['--proxy-server=' + process.env.HTTPS_PROXY] : [];
const browser = await chromium.launch({ args });
const page = await browser.newPage({ viewport: { width: 800, height: 400 } });
if (process.env.DD_FONT_FILE) await page.route(FONT, (r) => r.fulfill({ path: process.env.DD_FONT_FILE, contentType: 'font/woff2' }));
await page.setContent(html, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
// 글꼴을 못 받았으면 다른 글꼴로 그려져 칸이 어긋나요 — 그런 그림은 저장하지 않아요
if (!(await page.evaluate(() => document.fonts.check('600 20px T')))) throw new Error('Cascadia Mono 글꼴을 불러오지 못했어요');
for (const id of ['anniv', 'dates']) await page.locator('#' + id).screenshot({ path: path.join(outDir, id + '.png'), omitBackground: true });
await browser.close();
console.log(`days  ${anniv.join(' / ')}  |  ${dates.join(' / ')}`);
