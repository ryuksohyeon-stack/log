// 노릴스크(Asia/Krasnoyarsk, UTC+7) 오늘 날짜로 달력 그림 세 장을 그려요.
// luvlinks 프로필 CSS가 이 그림을 불러와서, 날짜가 매일 저절로 바뀌어요.
//   node norilsk/calendar.mjs                  → 오늘 날짜
//   NR_DATE=2026-10-16 node norilsk/calendar.mjs → 그 날짜로 (확인용)
//   NR_OUT=다른/폴더 → 그림을 그 폴더에 저장 (기본: 이 파일 옆)
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const TZ = 'Asia/Krasnoyarsk';
const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = process.env.NR_OUT || here;
const { chromium } = await import(process.env.PW || 'playwright');

function today() {
  if (process.env.NR_DATE) { const [y, m, d] = process.env.NR_DATE.split('-').map(Number); return { y, m, d }; }
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: 'numeric', day: 'numeric' }).formatToParts(new Date()).map((x) => [x.type, x.value]));
  return { y: +p.year, m: +p.month, d: +p.day };
}
const { y, m, d } = today();
const wd = (new Date(Date.UTC(y, m - 1, d)).getUTCDay() + 6) % 7;   // 월요일 = 0
const days = new Date(Date.UTC(y, m, 0)).getUTCDate();
const first = (new Date(Date.UTC(y, m - 1, 1)).getUTCDay() + 6) % 7;
const MON = ['ЯНВАРЬ', 'ФЕВРАЛЬ', 'МАРТ', 'АПРЕЛЬ', 'МАЙ', 'ИЮНЬ', 'ИЮЛЬ', 'АВГУСТ', 'СЕНТЯБРЬ', 'ОКТЯБРЬ', 'НОЯБРЬ', 'ДЕКАБРЬ'];
const MS = ['ЯНВ', 'ФЕВ', 'МАР', 'АПР', 'МАЙ', 'ИЮН', 'ИЮЛ', 'АВГ', 'СЕН', 'ОКТ', 'НОЯ', 'ДЕК'];
const WD = ['ПОНЕДЕЛЬНИК', 'ВТОРНИК', 'СРЕДА', 'ЧЕТВЕРГ', 'ПЯТНИЦА', 'СУББОТА', 'ВОСКРЕСЕНЬЕ'];
const WS = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС'];
const EN = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
const dd = String(d).padStart(2, '0');

const base = `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=IBM+Plex+Mono:wght@500;600&display=block">
<style>*{box-sizing:border-box;margin:0}html,body{background:transparent}body{--ink:#151515;--ac:#ff4f14;--pa:#fbfbf8;--mu:#7d8392;font-family:'IBM Plex Mono',monospace;color:var(--ink)}
.o{font-family:Oswald,sans-serif}#c{position:relative;display:inline-block}</style>`;

// 1 · 일력 — 한 장씩 뜯는 달력
const d1 = `<div id="c" style="width:120px;height:154px;padding:4px 4px 8px">
<div style="height:100%;background:var(--pa);box-shadow:0 2px 0 #0000000d,0 6px 12px #00000026;clip-path:polygon(0 0,100% 0,100% 96%,92% 100%,84% 96%,76% 100%,68% 96%,60% 100%,52% 96%,44% 100%,36% 96%,28% 100%,20% 96%,12% 100%,4% 96%,0 100%)">
 <div style="position:relative;height:30px;background:var(--ac);color:#fff;font:600 9px/30px 'IBM Plex Mono';letter-spacing:.22em;text-align:center">${MON[m - 1]}
  <i style="position:absolute;top:5px;left:14px;width:7px;height:7px;border-radius:50%;background:#151515aa"></i><i style="position:absolute;top:5px;right:14px;width:7px;height:7px;border-radius:50%;background:#151515aa"></i></div>
 <div class="o" style="font-weight:600;font-size:64px;line-height:1;text-align:center;margin-top:8px;letter-spacing:-.02em">${d}</div>
 <div style="text-align:center;font:600 8.5px/1 'IBM Plex Mono';letter-spacing:.14em;margin-top:7px">${WD[wd]}</div>
 <div style="text-align:center;font:500 7.5px/1 'IBM Plex Mono';letter-spacing:.18em;color:var(--mu);margin-top:5px">${EN[wd]} · ${y}</div>
</div></div>`;

// 2 · 한 달 달력 — 오늘에 동그라미
let cells = '';
for (let i = 0; i < first; i++) cells += '<span></span>';
for (let k = 1; k <= days; k++) {
  const col = (first + k - 1) % 7, we = col >= 5, on = k === d;
  cells += `<span style="${we ? 'color:var(--ac);' : ''}${on ? 'background:var(--ac);color:#fff;border-radius:50%;font-weight:600;' : ''}">${k}</span>`;
}
const d2 = `<div id="c" style="width:156px;padding:4px">
 <div style="display:flex;align-items:baseline;justify-content:space-between;border-bottom:2px solid var(--ac);padding-bottom:4px"><b class="o" style="font-weight:600;font-size:19px;letter-spacing:.02em">${MON[m - 1]}</b><span style="font:600 11px 'IBM Plex Mono';letter-spacing:.06em">${y}</span></div>
 <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:2px 0;margin-top:6px;text-align:center;font:600 8px/13px 'IBM Plex Mono';color:var(--mu);letter-spacing:0">${WS.map((w, i) => `<span style="${i >= 5 ? 'color:var(--ac)' : ''}">${w}</span>`).join('')}</div>
 <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:2px 1px;margin-top:2px;text-align:center;font:600 11px/19px 'IBM Plex Mono'">${cells}</div>
</div>`;

// 3 · 플립 시계 — 넘어가는 숫자판
const tile = (t, w, h, cut = true) => `<span style="position:relative;display:grid;place-items:center;width:${w}px;height:${h}px;border-radius:4px;background:linear-gradient(#262626 0 50%,#1b1b1b 50%);color:#f4f4f2;box-shadow:0 3px 6px #00000040">${t}${cut ? '<i style="position:absolute;left:0;right:0;top:50%;height:1px;background:#000;box-shadow:0 1px 0 #ffffff14"></i>' : ''}<i style="position:absolute;left:-2px;top:calc(50% - 3px);width:3px;height:6px;border-radius:1px;background:#3a3a3a"></i><i style="position:absolute;right:-2px;top:calc(50% - 3px);width:3px;height:6px;border-radius:1px;background:#3a3a3a"></i></span>`;
const d3 = `<div id="c" style="width:150px;padding:6px">
 <div class="o" style="display:flex;gap:6px;font-weight:600;font-size:52px;line-height:1">${tile(dd[0], 66, 78)}${tile(dd[1], 66, 78)}</div>
 <div style="display:flex;gap:6px;margin-top:6px;font:600 10px/1 'IBM Plex Mono';letter-spacing:.16em">${tile(MS[m - 1], 66, 24, false)}${tile(WS[wd], 66, 24, false)}</div>
 <div style="display:flex;align-items:center;gap:6px;margin-top:7px;font:500 7.5px/1 'IBM Plex Mono';letter-spacing:.2em;color:var(--mu)"><i style="width:6px;height:6px;border-radius:50%;background:var(--ac)"></i>${y} · ${EN[wd]}</div>
</div>`;

const args = process.env.HTTPS_PROXY ? ['--proxy-server=' + process.env.HTTPS_PROXY] : [];
const browser = await chromium.launch({ args });
const page = await browser.newPage({ deviceScaleFactor: 3, viewport: { width: 400, height: 400 } });
for (const [n, html] of [[1, d1], [2, d2], [3, d3]]) {
  await page.setContent(`<!doctype html><meta charset="utf-8">${base}${html}`, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.locator('#c').screenshot({ path: path.join(outDir, `cal-${n}.png`), omitBackground: true });
}
await browser.close();
console.log(`norilsk ${y}-${String(m).padStart(2, '0')}-${dd} (${EN[wd]}) → cal-1..3.png`);
