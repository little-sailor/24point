"""枚举 1-13 全部 4 张牌组合(可重复, 1820 种)并逐一求解。

输出到 results/:
    solutions.txt   每行: 组合 | 解数 | 解1; 解2; ...
    unsolvable.txt  无解组合清单
    summary.txt     统计汇总

用法: python solve_all.py
"""
import os
import time
from itertools import combinations_with_replacement

from solver import solve

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, 'results')


def main():
    combos = list(combinations_with_replacement(range(1, 14), 4))
    assert len(combos) == 1820
    os.makedirs(OUT_DIR, exist_ok=True)

    t0 = time.time()
    solvable = 0
    unsolvable = []
    total_solutions = 0
    dist = {}
    top = []

    with open(os.path.join(OUT_DIR, 'solutions.txt'), 'w', encoding='utf-8') as f:
        for combo in combos:
            sols = solve(combo)
            if not sols:
                unsolvable.append(combo)
                continue
            solvable += 1
            total_solutions += len(sols)
            dist[len(sols)] = dist.get(len(sols), 0) + 1
            top.append((len(sols), combo))
            f.write(f"{','.join(map(str, combo))} | {len(sols)} | {'; '.join(sols)}\n")

    with open(os.path.join(OUT_DIR, 'unsolvable.txt'), 'w', encoding='utf-8') as f:
        for combo in unsolvable:
            f.write(','.join(map(str, combo)) + '\n')

    elapsed = time.time() - t0
    top.sort(key=lambda x: (-x[0], x[1]))
    lines = [
        f'总组合数: {len(combos)}',
        f'有解组合: {solvable}',
        f'无解组合: {len(unsolvable)}',
        f'解法总数(去重): {total_solutions}',
        f'运行耗时: {elapsed:.1f}s',
        '',
        '解数分布 (一个组合的不同解数 -> 组合数):',
    ]
    for k in sorted(dist):
        lines.append(f'  {k:4d} 解: {dist[k]:4d} 个组合')
    lines += ['', '解最多的前 10 个组合:']
    for cnt, combo in top[:10]:
        lines.append(f'  {",".join(map(str, combo))}: {cnt} 解')
    summary = '\n'.join(lines)

    with open(os.path.join(OUT_DIR, 'summary.txt'), 'w', encoding='utf-8') as f:
        f.write(summary + '\n')
    print(summary)


if __name__ == '__main__':
    main()
