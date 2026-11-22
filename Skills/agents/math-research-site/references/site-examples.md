# 两个站点的实际路径

以下路径分别相对于各自的站点仓库。可用示例中的声明名、论文编号和案例 ID 核对当前导出，避免沿用旧版首页的计数。

## Lusztig a-function：从一个定理追到原文和 Lean

从 `#/book` 打开概念 `#/c/chen-hu-main-theorem`。陈述中的量词解释了为什么逐个计算群元素还不足以给出统一的界；正文再把证明拆成删除序列、相交集和大小估计。其前置概念取自 `content/registry.yaml`，章内位置来自 `content/book.yaml`。给定理换章只需改目录，已有概念链接可以继续使用。

在这节打开 Chen–Hu v10 的 Theorem 1.3，应到 `#/paper/chen-hu-v10?p=3`。阅读器在第 3 页提供回到概念和 Lean 条目的入口。`#/lean/item/thm-1-3` 展示 `LusztigBound.theorem_1_3`，源码入口定位到导出版本的 `lean/Challenge/Main.lean`。若页码偏了，查 `content/paper-index.json` 与 PDF 版本；若源码行偏了，查 `lean/docs/formalization.json` 的 `source.commit` 并对照该版本的声明。

交互图跟着推理放在正文里。例如 `content/concepts/fold-paths.md` 的 `widget folds` 区块让读者操作折叠路径。`src/widgets/load.js` 在图靠近视口时装载模块，装载失败时仍保留静态内容。适合读者通过改动一步来理解证明的场景。

## Odd Singular Vector：让证明与计算分别可查

从 `#/c/theorem-1` 打开 LLW 的 Theorem 1，对应 arXiv v1 的 PDF 第 4 页（`#/paper/llw-2019?p=4`）。正文把零化、权、非零、唯一性及 Hom 空间分别对应到声明。`content/concepts/theorem-1.md` 用 `{{lean:theorem_1_unique}}` 等标记读取当前形式化状态。一条声明获认证后，检查受影响的标记和条目，保留其他分项各自的状态。

计算有两种取数方式。外部 SageMath 案例由 `scripts/sync-sage.mjs` 从数据目录无未提交修改的上游检出导入，生成 `content/sage/source.json` 记录提交。仓库内的例外型演算由 `computations/exceptional/worked.py` 生成站点 JSON，例如 `#/worked/g3-d` 通过 `src/worked.js` 按需读取 `computations/exceptional/site/g3-d.json`。中英文共用这一份带 `computed` 状态的结果，读者可以把选定根、超平面条件和系数逐项对上。更新这页时，从生成程序重算相应产物，并对照页面上的公式和状态。
