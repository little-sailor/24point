"""solver 自测, 直接运行: python test_solver.py"""
from itertools import combinations_with_replacement

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

    print('全部测试通过')


if __name__ == '__main__':
    main()
