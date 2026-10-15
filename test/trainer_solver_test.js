'use strict';
/* 校验 trainer.html 内嵌 JS 求解器与 results/solutions.txt 完全一致。
   用法: node test/trainer_solver_test.js  */
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'trainer.html'), 'utf8');
const MARK_BEGIN = '/* ==SOLVER-BEGIN== */';
const MARK_END = '/* ==SOLVER-END== */';
const i1 = html.indexOf(MARK_BEGIN);
const i2 = html.indexOf(MARK_END);
if (i1 < 0 || i2 < 0 || i2 <= i1) {
  console.error('FAIL: 未在 trainer.html 中找到求解器代码块标记');
  process.exit(1);
}
const code = html.slice(i1 + MARK_BEGIN.length, i2);
(0, eval)(code);

const lines = fs.readFileSync(path.join(root, 'results', 'solutions.txt'), 'utf8')
  .split(/\r?\n/)
  .filter(l => l.trim());

let checked = 0;
let solTotal = 0;
let fails = 0;
for (const line of lines) {
  const parts = line.split(' | ');
  const combo = parts[0].split(',').map(Number);
  const expectedCount = Number(parts[1]);
  const expected = parts[2] ? parts[2].split('; ') : [];
  const got = solveSorted(combo);
  checked++;
  solTotal += got.length;
  let ok = got.length === expectedCount && got.length === expected.length;
  if (ok) {
    for (let i = 0; i < got.length; i++) {
      if (got[i] !== expected[i]) { ok = false; break; }
    }
  }
  if (!ok) {
    fails++;
    if (fails <= 5) {
      console.error('MISMATCH', combo.join(','));
      console.error('  expected:', JSON.stringify(expected));
      console.error('  got     :', JSON.stringify(got));
    }
  }
}

const { solvable, unsolvableCount } = enumerateAll();
const totalCombos = solvable.length + unsolvableCount;
console.log('组合数校验: 有解 ' + solvable.length + ' (期望 1362), 无解 ' + unsolvableCount + ' (期望 458), 总计 ' + totalCombos + ' (期望 1820)');
console.log('逐组合比对: ' + checked + ' 个, 解法总数 ' + solTotal + ' (期望 13456)');
if (fails === 0 && checked === 1362 && solvable.length === checked && unsolvableCount === 458 && totalCombos === 1820 && solTotal === 13456) {
  console.log('PASS: JS 求解器与 results/solutions.txt 完全一致');
} else {
  console.error('FAIL: ' + fails + ' 个组合不一致');
  process.exit(1);
}
