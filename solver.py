"""24 点求解器。

规则: 4 张牌(点数 1-13), 用 + - * / 和括号算出 24。
中间值允许分数, 使用 fractions.Fraction 精确计算。

解的去重口径:
- 表达式树节点为 (op, left, right), 叶子为整数
- 对交换律运算 (+, *) 的同级链排序并展平 (结合律), 如 (a+b)+c 与 a+(b+c) 视为同一解
- 减/除保留两个方向 (a-b, b-a), 除数为 0 的分支跳过

用法:
    python solver.py 3 3 8 8
"""
import sys
from fractions import Fraction

TARGET = Fraction(24)
_PREC = {'+': 1, '-': 1, '*': 2, '/': 2}


def _flatten(node, op):
    """把同级运算链展平成操作数列表: (a+b)+c -> [a, b, c]"""
    if isinstance(node, tuple) and node[0] == op:
        return _flatten(node[1], op) + _flatten(node[2], op)
    return [node]


def _canon(node):
    """表达式的规范化串, 作为去重 key。"""
    if not isinstance(node, tuple):
        return str(node)
    op, left, right = node
    if op in '+*':
        parts = sorted(_canon(x) for x in _flatten(node, op))
        return '(' + op.join(parts) + ')'
    return '(' + _canon(left) + op + _canon(right) + ')'


def _fmt(node):
    """带最小括号的表达式串。"""
    if not isinstance(node, tuple):
        return str(node)
    op, left, right = node
    ls, rs = _fmt(left), _fmt(right)
    if isinstance(left, tuple) and _PREC[left[0]] < _PREC[op]:
        ls = '(' + ls + ')'
    if isinstance(right, tuple) and (_PREC[right[0]] < _PREC[op]
            or (_PREC[right[0]] == _PREC[op] and op in '-/')):
        rs = '(' + rs + ')'
    return ls + op + rs


def evaluate(node):
    """按 Fraction 精确求值表达式树。"""
    if not isinstance(node, tuple):
        return Fraction(node)
    op, left, right = node
    a, b = evaluate(left), evaluate(right)
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    return a / b


def solve_trees(cards):
    """求解一张牌组, 返回 {规范化串: 表达式树}。"""
    results = {}

    def rec(values, exprs):
        if len(values) == 1:
            if values[0] == TARGET:
                results[_canon(exprs[0])] = exprs[0]
            return
        n = len(values)
        for i in range(n - 1):
            for j in range(i + 1, n):
                a, b = values[i], values[j]
                ea, eb = exprs[i], exprs[j]
                rest_v = [values[k] for k in range(n) if k != i and k != j]
                rest_e = [exprs[k] for k in range(n) if k != i and k != j]
                cands = [
                    ('+', a + b, ('+', ea, eb)),
                    ('*', a * b, ('*', ea, eb)),
                    ('-', a - b, ('-', ea, eb)),
                    ('-', b - a, ('-', eb, ea)),
                ]
                if b != 0:
                    cands.append(('/', a / b, ('/', ea, eb)))
                if a != 0:
                    cands.append(('/', b / a, ('/', eb, ea)))
                for _, v, e in cands:
                    rec(rest_v + [v], rest_e + [e])

    rec([Fraction(c) for c in cards], list(cards))
    return results


def solve(cards):
    """求解一张牌组, 返回排序后的全部不同解法表达式串。"""
    return sorted(_fmt(t) for t in solve_trees(cards).values())


def main(argv):
    if len(argv) != 5:
        print('用法: python solver.py <数字1> <数字2> <数字3> <数字4>  (1-13)')
        return 1
    try:
        nums = [int(x) for x in argv[1:]]
    except ValueError:
        print('数字必须为整数')
        return 1
    if any(n < 1 or n > 13 for n in nums):
        print('每个数字必须在 1-13 范围内')
        return 1
    sols = solve(nums)
    print(f'组合: {nums}  解数: {len(sols)}')
    for s in sols:
        print('  ' + s)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
