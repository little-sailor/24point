"""把 results/solutions.txt 中全部有解组合生成 A4 打印练习册 (HTML)。

每面 20 题: 两个纵栏, 每栏 10 题 (先左栏 1-10, 后右栏 11-20)。
题目只有 4 个数字, 每题下方留作答区域。随机打乱 (固定种子)。

用法: python make_workbook.py
输出: results/24point_workbook.html  (浏览器打开后 Ctrl+P 打印成 A4 PDF)
"""
import os
import random
import math

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, 'results')
SRC = os.path.join(RESULTS, 'solutions.txt')
OUT = os.path.join(RESULTS, '24point_workbook.html')

PAGE_SIZE = 20
SEED = 24

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>24 点练习册</title>
<style>
  @page {{ size: A4; margin: 12mm; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: "Segoe UI", "Microsoft YaHei", sans-serif; color: #222; }}
  .sheet {{
    width: 186mm;
    height: 273mm;
    page-break-after: always;
    display: flex;
    flex-direction: column;
  }}
  .sheet:last-child {{ page-break-after: auto; }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding-bottom: 2mm;
    margin-bottom: 3mm;
    border-bottom: 1px solid #999;
  }}
  .header .title {{ font-size: 14pt; font-weight: 700; }}
  .header .pageno {{ font-size: 10pt; color: #555; }}
  .grid {{
    flex: 1;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: repeat(10, 1fr);
    grid-auto-flow: column;
    column-gap: 10mm;
  }}
  .item {{
    display: flex;
    flex-direction: column;
    min-height: 0;
  }}
  .q {{
    text-align: center;
    font-size: 14pt;
    font-weight: 700;
  }}
  .num {{ display: inline-block; margin: 0 3mm; }}
  .answer {{
    flex: 1;
    margin-top: 1.2mm;
    border: 1px solid #ccc;
    border-radius: 1.5mm;
  }}
</style>
</head>
<body>
__SHEETS__
</body>
</html>
"""

SHEET_TEMPLATE = """  <section class="sheet">
    <div class="header">
      <span class="title">24 点练习</span>
      <span class="pageno">第 {page} 面</span>
    </div>
    <div class="grid">
{cards}
    </div>
  </section>
"""

ITEM_TEMPLATE = """      <div class="item"><div class="q"><span class="num">{d0}</span><span class="num">{d1}</span><span class="num">{d2}</span><span class="num">{d3}</span></div><div class="answer"></div></div>"""


def load_combos(path):
    combos = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            combo = line.split(' | ', 1)[0]
            nums = [int(x) for x in combo.split(',')]
            combos.append(nums)
    return combos


def build_html(combos):
    chunks = [combos[i:i + PAGE_SIZE] for i in range(0, len(combos), PAGE_SIZE)]
    sheets = []
    for idx, chunk in enumerate(chunks, start=1):
        cards = '\n'.join(ITEM_TEMPLATE.format(d0=c[0], d1=c[1], d2=c[2], d3=c[3]) for c in chunk)
        sheets.append(SHEET_TEMPLATE.format(page=idx, cards=cards))
    return HTML_TEMPLATE.replace('__SHEETS__', '\n'.join(sheets))


def main():
    combos = load_combos(SRC)
    assert len(combos) == 1362, f'应有 1362 个有解组合, 实际 {len(combos)}'
    random.Random(SEED).shuffle(combos)

    pages = math.ceil(len(combos) / PAGE_SIZE)
    html = build_html(combos)

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)

    num_count = html.count('class="num"')
    sheet_count = html.count('<section class="sheet">')
    item_count = html.count('class="item"')
    answer_count = html.count('class="answer"')
    last = len(combos) % PAGE_SIZE
    print(f'有解组合: {len(combos)}')
    print(f'页数(面): {pages}')
    print(f'题目数: {item_count} (应为 {len(combos)})')
    print(f'作答区数: {answer_count} (应为 {len(combos)})')
    print(f'数字出现次数: {num_count} (应为 {len(combos) * 4})')
    print(f'sheet 数: {sheet_count} (应为 {pages})')
    print(f'最后一面题数: {last if last else PAGE_SIZE}')
    print(f'输出: {OUT}')


if __name__ == '__main__':
    main()
