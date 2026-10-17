// 시안 파일 만들기 — src/ 의 공통 조각(엔진 · 무대 · 글)을 시안 틀에 끼워 붙여 넣기용 HTML 한 장으로 만들어요.
// 실행: node shrimp-tempura/build.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = dirname(fileURLToPath(import.meta.url));
const src = (f) => readFileSync(join(dir, 'src', f), 'utf8');
const parts = {
  ENGINE_CSS: src('engine.css').trim(),
  ENGINE_JS: src('engine.js').trim(),
  STAGE: src('stage.html').trim(),
  ARTICLE: src('article.html').trim(),
  MEMO: src('memo.html').trim(),
};
// 위 화면에 제목이 따로 있는 시안(B)은 요리판 시작 화면에서 제목을 빼요
parts.STAGE_NOTITLE = parts.STAGE.replace('data-mode="title"', 'data-mode="title" data-title="off"');

for (const name of ['a-pink', 'b-ds', 'c-note']) {
  let html;
  try { html = src(name + '.html'); } catch { continue; }
  html = html.replace(/\/\*@(\w+)@\*\//g, (m, k) => parts[k] ?? m);
  writeFileSync(join(dir, name + '.html'), html);
  console.log(`${name}.html  ${(Buffer.byteLength(html) / 1024).toFixed(1)} KB`);
}
