"""把全部有解组合的解按套路归类, 生成 results/classification.md。

分类口径 (每个解只归一类, 按序判定):
    F 分数型      运算过程中出现非整数中间值, 如 8/(3-8/3)
    E 除法型      含除法且中间值全为整数, 如 6*8/(1+1)
    B 直乘型      纯乘法且化简后恰 2 个因子, 如 3*8
    A 连乘型      纯乘法且化简后 3 个及以上因子, 如 1*2*3*4
    C 凑乘数型    顶层相乘且乘数由加减凑出, 如 (1+11)*(1+1)、12*(3-1)
    D 乘后调整型  顶层为加减且链中含乘法, 如 3*8+1-1、5*5-1
    X 加减凑数型  纯加减, 如 6+6+6+6、13+13-1-1

组合主类按「从简到繁」取: B > A > C > D > X > E > F。
去重口径: 先消去中性项 (x*1、x/1、x+0、x-0), 再按规范化串合并同义解,
每个等价类保留最短表达式串作为代表解。

用法: python classify_solutions.py
输出: results/classification.md
"""
import os

from solver import _canon, _fmt, evaluate, solve_trees

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'results', 'solutions.txt')
OUT = os.path.join(HERE, 'results', 'classification.md')

# 解级判定顺序: 从特殊到一般, 保证每个解唯一归类
CLASSIFY_ORDER = ('F', 'E', 'B', 'A', 'C', 'D', 'X')
# 组合主类优先级: 从简到繁
MAIN_ORDER = ('B', 'A', 'C', 'D', 'X', 'E', 'F')

CAT_INFO = {
    'B': ('直乘型', '两数直接相乘得 24, 其余牌作中性消去', 'x×y=24'),
    'A': ('连乘型', '三个及以上数连乘得 24', 'a×b×c×d=24'),
    'C': ('凑乘数型', '先用加减凑出一个乘数, 再相乘得 24', '(a±b)×c=24'),
    'D': ('乘后调整型', '先乘出一个数, 再加减调整到 24', 'a×b±c±d=24'),
    'X': ('加减凑数型', '纯加减凑出 24', 'a+b+c+d=24'),
    'E': ('除法型', '用到除法, 中间结果全为整数', 'a×b÷c=24'),
    'F': ('分数型', '运算过程中出现分数, 需分数技巧', 'c÷(a-b÷d)=24'),
}


def simplify_tree(node):
    """递归消去中性项: x*1、x/1、x+0、x-0。"""
    if not isinstance(node, tuple):
        return node
    op, left, right = node
    left = simplify_tree(left)
    right = simplify_tree(right)
    if op == '*':
        if left == 1:
            return right
        if right == 1:
            return left
    elif op == '/':
        if right == 1:
            return left
    elif op == '+':
        if left == 0:
            return right
        if right == 0:
            return left
    elif op == '-':
        if right == 0:
            return left
    return (op, left, right)


def _has_fraction(node):
    """树中是否存在求值为非整数的子树。"""
    if not isinstance(node, tuple):
        return False
    if evaluate(node).denominator != 1:
        return True
    return _has_fraction(node[1]) or _has_fraction(node[2])


def _contains_op(node, ops):
    """树中是否出现指定运算符。"""
    if not isinstance(node, tuple):
        return False
    if node[0] in ops:
        return True
    return _contains_op(node[1], ops) or _contains_op(node[2], ops)


def _mul_factors(node):
    """纯乘树返回叶子因子列表, 否则返回 None。"""
    if not isinstance(node, tuple):
        return [node]
    if node[0] != '*':
        return None
    left = _mul_factors(node[1])
    if left is None:
        return None
    right = _mul_factors(node[2])
    if right is None:
        return None
    return left + right


def classify_tree(tree):
    """单个解的表达式树 -> 类别代码 (F/E/B/A/C/D/X)。"""
    if not isinstance(tree, tuple):
        return 'X'
    if _has_fraction(tree):
        return 'F'
    if _contains_op(tree, '/'):
        return 'E'
    factors = _mul_factors(tree)
    if factors is not None:
        return 'B' if len(factors) == 2 else 'A'
    if tree[0] == '*':
        return 'C'
    return 'D' if _contains_op(tree, '*') else 'X'


def analyze_combo(cards):
    """求解并归类一张牌组。

    返回 dict:
        sols      [(代表解串, 类别)], 按判定顺序与解串排序
        classes   该组合的可用套路集合
        main      主类 (从简到繁取最简)
        rep_main  主类解中最短的代表解串
    """
    groups = {}
    for tree in solve_trees(cards).values():
        s = simplify_tree(tree)
        assert evaluate(s) == 24, _fmt(s) + ' 不等于 24'
        key = _canon(s)
        if key in groups:
            groups[key][1].add(_fmt(s))
        else:
            groups[key] = (s, {_fmt(s)})
    sols = []
    for tree, fmts in groups.values():
        rep = min(fmts, key=lambda s: (len(s), s))
        sols.append((rep, classify_tree(tree)))
    order_idx = {c: i for i, c in enumerate(CLASSIFY_ORDER)}
    sols.sort(key=lambda t: (order_idx[t[1]], t[0]))
    classes = {c for _, c in sols}
    assert classes, f'{cards} 无可用套路'
    main = next(c for c in MAIN_ORDER if c in classes)
    rep_main = min((s for s, c in sols if c == main), key=lambda s: (len(s), s))
    return {'sols': sols, 'classes': classes, 'main': main, 'rep_main': rep_main}


def _pick_examples(records, cat, want):
    """挑代表例题: 优先「全部解都属该类」且解数少的组合。"""
    pool = [r for r in records if r['main'] == cat]
    pure = sorted((r for r in pool if r['classes'] == {cat}),
                  key=lambda r: (len(r['sols']), r['combo']))
    picked = [(r['combo'], r['rep_main']) for r in pure[:want]]
    if len(picked) < want:
        used = {c for c, _ in picked}
        rest = sorted((r for r in pool if r['combo'] not in used),
                      key=lambda r: (len(r['sols']), r['combo']))
        picked += [(r['combo'], r['rep_main']) for r in rest[:want - len(picked)]]
    return picked


def _fmt_cell(items):
    if not items:
        return '—'
    return '; '.join(f'{",".join(map(str, c))} → {rep}' for c, rep in items)


def build_report(records):
    n_orig_total = sum(r['n_orig'] for r in records)
    n_dedup = sum(len(r['sols']) for r in records)
    main_counts = {c: 0 for c in MAIN_ORDER}
    cover_counts = {c: 0 for c in MAIN_ORDER}
    for r in records:
        main_counts[r['main']] += 1
        for c in r['classes']:
            cover_counts[c] += 1

    lines = [
        '# 24 点有解题目解法归类报告',
        '',
        f'- 数据来源: `results/solutions.txt`, 共 {len(records)} 个有解组合,'
        f' 原始解 {n_orig_total} 个。',
        f'- 去重口径: 每个解先消去中性项 (×1、÷1、+0、-0), 再按规范化串合并同义解,'
        f' 余 {n_dedup} 个不同解。',
        '- 分类口径: 一个解只归一类 (判定顺序 F > E > B/A > C > D > X);'
        ' 组合主类按「从简到繁」取 (B > A > C > D > X > E > F),'
        ' 清单中同时列出该组合全部可用套路。',
        '- 套路代码: B 直乘型 / A 连乘型 / C 凑乘数型 / D 乘后调整型 /'
        ' X 加减凑数型 / E 除法型 / F 分数型。',
        '',
        '## 总览',
        '',
        '| 套路 | 定义 | 公式模板 | 主类组合数 | 覆盖组合数 | 典型例题 |',
        '|---|---|---|---:|---:|---|',
    ]
    for cat in MAIN_ORDER:
        name, desc, formula = CAT_INFO[cat]
        examples = _pick_examples(records, cat, 2)
        lines.append(f'| {cat} {name} | {desc} | {formula} | {main_counts[cat]} |'
                     f' {cover_counts[cat]} | {_fmt_cell(examples)} |')
    lines += [
        '',
        '> 注: 分数型 (F) 按「出现非整数中间值」判定, 其中含少量形如 `1/(1/(2*12))`'
        ' 的形式分数解 (数学上等价于连乘), 不影响组合主类。',
    ]
    for cat in MAIN_ORDER:
        name, desc, formula = CAT_INFO[cat]
        rows = [r for r in records if r['main'] == cat]
        lines += [
            '',
            f'## {cat} {name} — {len(rows)} 个组合',
            '',
            f'{desc}。公式模板: `{formula}`。',
        ]
        examples = _pick_examples(records, cat, 3)
        if examples:
            lines += ['', '典型例题: ' + _fmt_cell(examples)]
        if rows:
            lines += ['', '| 组合 | 去重解数 | 可用套路 | 代表解 |', '|---|---:|---|---|']
            for r in rows:
                cls = ','.join(c for c in MAIN_ORDER if c in r['classes'])
                lines.append(f'| {",".join(map(str, r["combo"]))} | {len(r["sols"])}'
                             f' | {cls} | {r["rep_main"]} |')
        else:
            lines += ['', '本类暂无组合。']
    lines += [
        '',
        '---',
        '',
        f'校验: 主类组合数合计 {sum(main_counts.values())} = 有解组合总数 {len(records)};'
        ' 全部解经 `solver.evaluate` 精确求值均为 24。',
    ]
    return '\n'.join(lines)


def load_combos(path):
    combos, n_orig = [], {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(' | ')
            combo = tuple(int(x) for x in parts[0].split(','))
            combos.append(combo)
            n_orig[combo] = int(parts[1])
    return combos, n_orig


def main():
    combos, n_orig = load_combos(SRC)
    assert len(combos) == 1362, f'应有 1362 个有解组合, 实际 {len(combos)}'
    records = []
    for combo in combos:
        r = analyze_combo(combo)
        r['combo'] = combo
        r['n_orig'] = n_orig[combo]
        records.append(r)
    records.sort(key=lambda r: r['combo'])

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(build_report(records) + '\n')

    main_counts = {c: 0 for c in MAIN_ORDER}
    cover_counts = {c: 0 for c in MAIN_ORDER}
    for r in records:
        main_counts[r['main']] += 1
        for c in r['classes']:
            cover_counts[c] += 1
    print(f'有解组合: {len(records)}')
    print(f'原始解: {sum(r["n_orig"] for r in records)}')
    print(f'去重后解: {sum(len(r["sols"]) for r in records)}')
    for cat in MAIN_ORDER:
        name = CAT_INFO[cat][0]
        print(f'  {cat} {name}: 主类 {main_counts[cat]:4d} 组合,'
              f' 覆盖 {cover_counts[cat]:4d} 组合')
    print(f'输出: {OUT}')


if __name__ == '__main__':
    main()
