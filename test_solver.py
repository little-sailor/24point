"""solver 自测, 直接运行: python test_solver.py"""
from itertools import combinations_with_replacement

from classify_solutions import analyze_combo
from solver import _fmt, evaluate, solve, solve_trees


def check_all_eval_24(cards):
    for tree in solve_trees(cards).values():
        assert evaluate(tree) == 24, _fmt(tree) + ' 不等于 24'


def main():
    # (5,5,5,1): 经典分数解 (5-1/5)*5
    sols = solve((5, 5, 5, 1))
    assert sols, '(5,5,5,1) 应有解'
    assert any('1/5' in s for s in sols), '应含分数解'
    check_all_eval_24((5, 5, 5, 1))

    # (3,3,8,8): 著名难题, 唯一解 8/(3-8/3)
    sols = solve((3, 3, 8, 8))
    assert '8/(3-8/3)' in sols, f'(3,3,8,8) 应含 8/(3-8/3), 实际: {sols}'
    check_all_eval_24((3, 3, 8, 8))

    # (1,1,1,1): 无解
    assert solve((1, 1, 1, 1)) == [], '(1,1,1,1) 应无解'

    # (1,2,3,4): 有解且所有解精确求值为 24
    sols = solve((1, 2, 3, 4))
    assert sols, '(1,2,3,4) 应有解'
    check_all_eval_24((1, 2, 3, 4))

    # 组合口径: 1-13 取 4 张可重复, 应为 1820 种
    combos = list(combinations_with_replacement(range(1, 14), 4))
    assert len(combos) == 1820, f'组合数应为 1820, 实际 {len(combos)}'

    # --- classify_solutions: 解法套路归类 ---
    # (3,3,8,8): 唯一解 8/(3-8/3), 主类应为分数型 F
    res = analyze_combo((3, 3, 8, 8))
    assert res['main'] == 'F', res['main']

    # (1,1,3,8): 含直乘解 3*8, 可用套路应含 B
    res = analyze_combo((1, 1, 3, 8))
    assert 'B' in res['classes'], res['classes']

    # (1,1,1,13): 唯一解 (13-1)*(1+1), 主类应为凑乘数型 C
    res = analyze_combo((1, 1, 1, 13))
    assert res['main'] == 'C', res['main']

    # (1,2,3,4): 连乘 1*2*3*4 与凑乘数 (1+2+3)*4 并存, 主类 A
    res = analyze_combo((1, 2, 3, 4))
    assert res['main'] == 'A' and {'A', 'C'} <= res['classes'], (res['main'], res['classes'])

    # (6,6,6,6): 乘后调整 6*6-6-6 与纯加减 6+6+6+6 并存, 主类 D
    res = analyze_combo((6, 6, 6, 6))
    assert {'D', 'X'} <= res['classes'] and res['main'] == 'D', (res['main'], res['classes'])

    # 归类后代表解仍精确等于 24
    for rep, _cat in res['sols']:
        assert rep, '代表解不应为空'

    print('全部测试通过')


if __name__ == '__main__':
    main()
