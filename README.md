# 24 点工具集与训练器

24 点（24 Game）练习工具集：精确求解器、全组合枚举、解法套路分类、A4 打印练习册，以及一个开箱即用的**交互式网页训练器**（电脑 / 手机通用）。

## 网页训练器（trainer.html）

无需安装任何依赖，双击 `trainer.html` 即可在浏览器中打开（也可部署到 GitHub Pages 等任意静态托管，手机直接访问）。

- **限时挑战**：每轮 10 题，倒计时 10 分钟，可提前结束
- **点击作答**：点一个数字 → 点一个运算符 → 点另一个数字，两两合并为中间结果（可以是分数）；中间结果继续参与运算，用全部 4 个数算出 24
- **精准判题**：分数用整数对精确运算（非浮点近似），与 24 点规则完全一致
- **难度分级**：按去重解法数分级——易（≥9 种解法）、中（3–8 种）、难（≤2 种）、混合随机；题库覆盖全部 1362 种有解组合
- **宽松练习**：答错抖动提示并自动撤销一步，支持撤销 / 清空 / 跳过 / 看答案
- **成绩记录**：本局总结（每题对错、用时、参考解法），各难度最佳纪录本地保存

自检：访问 `trainer.html?selftest=1` 可运行内置断言（组合数、解法总数、经典用例等）。

## 命令行工具（Python 3，无第三方依赖）

| 命令 | 说明 |
| --- | --- |
| `python solver.py 3 3 8 8` | 求解一组牌（1–13），列出全部去重解法，如 `8/(3-8/3)` |
| `python solve_all.py` | 枚举 1–13 全部 1820 种组合并逐一求解，输出到 `results/` |
| `python classify_solutions.py` | 将全部解按套路归类（分数型 / 直乘型 / 凑乘数型等 7 类），生成 `results/classification.md` |
| `python make_workbook.py` | 用全部有解组合生成 A4 打印练习册 `results/24point_workbook.html`（浏览器打开后 Ctrl+P 导出 PDF） |
| `python make_data.py` | 校验 `results/solutions.txt` 并将全量题库数据注入 `trainer.html`（重复运行幂等；trainer.html 首次使用前需运行一次） |
| `python test_solver.py` | 求解器自测（经典分数解、无解判定、全解精确等于 24） |

求解器基于 `fractions.Fraction` 精确运算，中间结果允许分数；对加 / 乘按结合律展平去重，减 / 除保留两个方向，保证解法列表不重不漏。

## results/ 数据文件

- `solutions.txt` — 1362 个有解组合的全部去重解法（`组合 | 解数 | 解1; 解2; …`）
- `unsolvable.txt` — 458 个无解组合清单
- `summary.txt` — 统计汇总（共 13456 种去重解法）
- `classification.md` — 解法套路分类报告
- `24point_workbook.html` — 可打印练习册

## 测试

```bash
python test_solver.py              # Python 求解器自测
node test/trainer_solver_test.js   # 网页内嵌 JS 求解器与 results/solutions.txt 全量比对
```
