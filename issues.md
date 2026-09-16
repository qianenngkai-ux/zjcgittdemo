# 代码问题清单

分析对象：`dev` 分支（相对 `main` 的改动 + 项目整体）
分析日期：2026-09-16

> **适用范围说明**：本文件只覆盖 `dev` 分支的代码状态。
> `dev2` 分支在此基础上新增了插入/选择/堆三种排序算法，另有一份
> 独立分析在 [`issues-dev2.md`](issues-dev2.md)。若你正在看 `dev2`
> 或更靠后的分支，请以那份为准。

结论速览：**1 个真实缺陷会导致程序崩溃**，1 处模板文件开箱即坏，其余为健壮性、无障碍与文档一致性问题。算法本身的正确性经模糊测试验证无问题。

> ## 修复状态（2026-09-16 更新）
>
> | # | 问题 | 状态 | 修复方式 |
> |---|---|---|---|
> | 1 | `quick_sort` 递归崩溃 | ✅ 已修复 | 三数取中选基准 + 只对较小一侧递归，栈深度钳在 O(log n)；补 3 条最坏情况回归测试 |
> | 2 | `template.html` 打开即坏 | ✅ 已修复 | 移至 `posts/_template.html`，路径自然对齐，直接打开也正常 |
> | 3 | 首页缺 `<h1>` | ✅ 已修复 | 站点标题改为 `<h1>`（仅首页），CSS 清零 h1 默认外边距 |
> | 4 | 测试运行方式受限 | ✅ 已修复 | 加 `algorithms/__init__.py` + 导入兼容，4 种运行方式全部可用 |
> | 5 | 空状态死代码 | ✅ 已移除 | 删除元素、JS 引用与 CSS 规则，渲染检查项同步替换 |
> | 6 | README 遗漏 `docs/` | ✅ 已补 | 目录树补上 `docs/`，并同步模板新路径与测试运行方式 |
> | 7 | `var` / `const` 不一致 | ✅ 已统一 | `theme.js` 改用 `const` / `let` |
> | 8 | `docs/` 已公开 | ⏸ 保持现状 | 经确认保留公开 |
> | 9 | `.pyc` 残留在历史 | ⏸ 保持现状 | 经确认不改写公开历史 |
>
> 修复后验证：Python **57** 项、JS **35** 项、渲染检查 **21** 项，全部通过。



| # | 严重程度 | 问题 | 位置 |
|---|---|---|---|
| 1 | 🔴 高 | `quick_sort` 在有序输入下 `RecursionError` 崩溃 | `algorithms/sort.py` |
| 2 | 🟠 中 | `template.html` 直接打开时链接与样式全断 | `template.html` |
| 3 | 🟠 中 | 首页缺少 `<h1>`，标题层级从 h2 开始 | `index.html` |
| 4 | 🟠 中 | 测试只能以一种特定方式运行 | `algorithms/test_sort.py` |
| 5 | 🟡 低 | 空状态元素不可达（死代码） | `assets/js/home.js` |
| 6 | 🟡 低 | README 目录树遗漏 `docs/` | `README.md` |
| 7 | 🟡 低 | 代码风格不一致（`var` vs `const`） | `assets/js/theme.js` |
| 8 | ⚪ 提示 | 设计文档与实现计划已随仓库公开 | `docs/` |
| 9 | ⚪ 提示 | `.pyc` 字节码残留在 git 历史中 | git 历史 |

---

## 1. 🔴 `quick_sort` 在有序输入下崩溃

**位置**：`algorithms/sort.py` — `_quick_sort_in_place` / `_partition`

**现象**：对已排序、逆序或元素全部相同的列表调用时抛出 `RecursionError`。

**复现**：

```bash
python3 -c "
import sys; sys.path.insert(0,'algorithms')
from sort import quick_sort
quick_sort(list(range(1000)))
"
# RecursionError: maximum recursion depth exceeded
```

实测崩溃边界（Python 3.12.7，默认递归上限 1000）：

| 输入形态 | n=500 | n=900 | n=1000 | n=1500 |
|---|---|---|---|---|
| 已排序 | 正常 | 正常 | ❌ 崩溃 | ❌ 崩溃 |
| 逆序 | 正常 | — | ❌ 崩溃 | — |
| 全部相同 | 正常 | — | ❌ 崩溃 | — |
| **随机** | 正常 | 正常 | 正常（20000 个仅 0.013s） | 正常 |

**原因**：`_partition` 用 Lomuto 分区且固定取末位元素作基准。当输入已经有序时，每次分区都是「1 个元素 + 其余全部」的极不平衡划分，递归深度退化为 O(n)，直接超过 Python 的递归上限。元素全部相同时同理（`<=` 使所有元素都划到左侧）。

**影响**：1000 个元素是很普通的规模。虽然 docstring 已注明「最坏情况退化为 O(n²)」，但实际后果是**直接崩溃**而非仅仅变慢，这一点没有体现。

**测试为何没发现**：`test_sort.py` 中规模最大的用例 `test_larger_random_list` 用的是 **500 个随机数**，随机输入不会触发最坏情况；`test_already_sorted` 只用了 5 个元素。两者叠加导致这条路径完全没有覆盖。

**建议修复**（任选其一）：

```python
# 方案 A：三数取中选基准，避免有序输入下的极不平衡划分
def _partition(arr, low, high):
    mid = (low + high) // 2
    # 把中位数换到末尾
    if arr[mid] < arr[low]: arr[low], arr[mid] = arr[mid], arr[low]
    if arr[high] < arr[low]: arr[low], arr[high] = arr[high], arr[low]
    if arr[high] < arr[mid]: arr[mid], arr[high] = arr[high], arr[mid]
    ...
```

```python
# 方案 B：随机选基准（期望复杂度稳定在 O(n log n)）
import random
r = random.randint(low, high)
arr[r], arr[high] = arr[high], arr[r]
```

无论选哪种，都应**补一条大规模有序输入的回归测试**，例如：

```python
def test_large_sorted_input(self):
    self.assertEqual(self.sort(list(range(2000))), list(range(2000)))
```

---

## 2. 🟠 `template.html` 直接打开时链接与样式全断

**位置**：`template.html`

**现象**：从仓库根目录直接打开该文件，页面无任何样式，且内部链接全部失效。

实测（从 `template.html` 自身所在位置解析）：

- 5 个 `<a href>` 全部指向不存在的路径
- 5 个资源引用（`../assets/css/main.css`、`../assets/js/*.js`）全部 404

**原因**：模板里的路径刻意写成了 `../` 前缀，那是**面向复制后的 `posts/` 位置**的。文件本身却在仓库根目录，所以相对路径全部落空。

**这是一处刻意的权衡**：设计目标是「复制 `template.html` 到 `posts/<slug>.html` 后零改动即可用」，因此路径按目的地而非模板自身的位置来写。README 里也有说明。

**影响**：熟悉项目的人不受影响，但初次接触者直接双击模板会看到一个坏页面，容易误判为项目坏了。

**建议**（任选其一，成本递增）：

1. 文件开头的注释里显式写明「本模板需复制到 `posts/` 后使用；在根目录直接打开样式会失效」
2. 把模板移到 `posts/_template.html`，路径自然对齐，直接打开也正常
3. 反过来写成根目录可用的路径，复制时用脚本自动改写前缀

---

## 3. 🟠 首页缺少 `<h1>`

**位置**：`index.html`

**现象**：首页渲染后只有 3 个 `<h2>`（文章标题），**没有任何 `<h1>`**。站点标题是 `<a class="site-title">`，不是标题元素。

```
index.html                        → (无 h1，仅 3 个 h2)
about.html                        → 1 个 h1，3 个 h2   ✅
posts/understanding-closures.html → 1 个 h1，3 个 h2   ✅
```

**影响**：标题层级从 h2 起始，跳过了 h1。屏幕阅读器用户依赖标题层级导航页面结构，搜索引擎也用它判断内容主次。这不影响视觉呈现，因此容易被忽略。

**建议**：把站点标题改为 `<h1>`（需相应调整 CSS 重置默认字号与外边距），或为首页加一个视觉隐藏的 `<h1>我的技术博客</h1>`。

---

## 4. 🟠 测试只能以一种特定方式运行

**位置**：`algorithms/test_sort.py`、`algorithms/` 缺少 `__init__.py`

**现象**：README 里给出的命令可以跑，但换成其他常见写法就失败。

```bash
$ python3 -m unittest discover -s algorithms -p 'test_*.py'   # ✅ 48 tests OK
$ python3 algorithms/test_sort.py                             # ✅ 48 tests OK
$ python3 -m unittest algorithms.test_sort                    # ❌ ModuleNotFoundError: No module named 'sort'
```

**原因**：测试文件用的是 `from sort import bubble_sort, ...` —— 这依赖 `algorithms/` 目录本身位于 `sys.path`。`discover -s algorithms` 恰好会把该目录加进去，所以能跑；而 `-m unittest algorithms.test_sort` 把 `algorithms` 当作包导入，`sort` 就不在搜索路径里了。

**影响**：用常见方式运行测试的人会撞上 `ModuleNotFoundError`，并可能误判为环境问题。

**建议**：加 `algorithms/__init__.py`，并把导入改为 `from algorithms.sort import ...`。这样 `-m unittest discover`（默认从根目录递归）、`-m unittest algorithms.test_sort` 等方式都能工作。

**补充**：当前 `.gitignore` 已忽略 `__pycache__/`，但历史上已提交过 `.pyc`（见问题 9）。

---

## 5. 🟡 空状态元素不可达（死代码）

**位置**：`index.html` 的 `#empty-state` + `assets/js/home.js`

**现象**：`这个标签下还没有文章。` 这段提示永远不会显示。

**原因**：`home.js` 中 `activeTag` 只可能是两种情况 —— `null`，或 `allTags` 里确实存在的标签。而 `allTags` 是从所有文章的 `tags` 中提取的，每个标签必然至少对应一篇文章，因此 `filterByTag` 的返回值永远非空，`emptyEl.hidden = visible.length > 0` 恒为真。

实测数据：

```
标签全集: CSS, JavaScript, TypeScript
  CSS        -> 1 篇
  JavaScript -> 2 篇
  TypeScript -> 1 篇
```

（访问 `index.html#tag=Rust` 时，由于 `Rust` 不在 `allTags` 中会被忽略，页面显示全部 3 篇而非空状态。）

**影响**：无害。仅当将来引入「文章可以没有标签」或新增其他筛选维度时才会变成活代码。清理或保留均可，但保留时应知道它测不到。

---

## 6. 🟡 README 目录树遗漏 `docs/`

**位置**：`README.md` 的「目录结构」段落

**现象**：树中列出了 `index.html`、`about.html`、`template.html`、`posts/`、`algorithms/`、`assets/`、`tests/`，但没有 `docs/`。实际上项目里有 `docs/superpowers/plans/` 与 `docs/superpowers/specs/` 两个含设计文档的目录。

**影响**：读者对项目结构的认知不完整。（`README.md` 与 `.gitignore` 自身未列出属常见做法，不必改。）

**建议**：补一行 `└── docs/  设计与实现文档`。

---

## 7. 🟡 代码风格不一致

**位置**：`assets/js/theme.js` 与 `assets/js/home.js`

**现象**：`theme.js` 全程使用 `var`，`home.js` 使用 `const` / `let`。同一项目的两个脚本风格不统一。

**原因**：`theme.js` 需要兼容极老的浏览器（防 FOUC 需同步执行），`var` 是有意为之；但这层理由没有写在注释里。

**影响**：纯风格问题，无功能影响。建议统一为 `const` / `let`（现代浏览器均支持），或在 `theme.js` 顶部注明为何刻意使用 `var`。

---

## 8. ⚪ 设计文档与实现计划已随仓库公开

**位置**：`docs/superpowers/`

**说明**：`2026-09-16-personal-tech-blog-design.md`（设计文档）与 `2026-09-16-personal-tech-blog.md`（1973 行的实现计划）已推送到公开仓库。实现计划中逐字包含了每个任务的实现代码与当时的决策记录。

**影响**：非缺陷，但属于「是否希望公开」的决策。若博客将来用于展示，这些内部文档可能不适合作为公开内容的一部分。

**处理**：若不想公开，可 `git rm -r --cached docs/` 并加入 `.gitignore`（注意历史中仍会保留）。

---

## 9. ⚪ `.pyc` 字节码残留在 git 历史中

**位置**：git 历史（提交 `9a5de7e`）

**说明**：首次提交排序算法时误将 `algorithms/__pycache__/*.pyc` 一并入库并推送。随后已用提交 `ec0225a` 修复：从跟踪中移除，并在 `.gitignore` 中加入 `__pycache__/` 与 `*.pyc`。

**当前状态**：远程最新提交的文件树已不含 `.pyc`，`.gitignore` 生效（运行测试重新生成缓存后 `git status` 依然干净）。

**遗留**：那两个 `.pyc` 的 blob 仍永久保留在 git 历史里（合计约 12KB）。由于该分支已公开，清理需要改写历史并 force-push，会破坏他人已有的引用，不建议执行。

---

## 已验证无问题的部分

以下方面经过实际验证，未发现缺陷，记录在此以免重复排查：

**算法正确性** — 模糊测试，5 种输入形态（随机 / 近序 / 重复多 / 浮点 / 单值）× 7 种规模（0,1,2,3,10,60,300）× 3 个算法 = **105 组比对**，结果全部与 Python 内置 `sorted()` 一致，且均未改动入参。

**边界条件** — 空列表、单元素、双元素、全重复、负数、浮点、单元素返回值非入参别名，均有测试覆盖且通过。

**性能特征**（符合各算法理论预期，非缺陷）：

| 算法 | 输入 | 规模 | 用时 |
|---|---|---|---|
| merge_sort | 有序 | 50,000 | 0.043s |
| quick_sort | 随机 | 20,000 | 0.013s |
| bubble_sort | 随机 | 10,000 | 2.114s（O(n²) 固有） |

**安全性** — 全仓库扫描未发现凭据、API key、私钥等敏感信息。

**仓库卫生** — 无误入库的二进制文件；最大文件为 58KB 的设计文档；提交历史中仅一个邮箱。

**前端链路** — `index.html`、`about.html`、`posts/*.html` 的全部内部链接与资源引用均有效；首页标签筛选、URL hash 恢复、主题切换与持久化、防 FOUC 均实测正常。博客部分的 35 项单元测试与 20 项无头 Chrome 渲染检查全部通过。

---

## 附：本次分析的验证方式

所有结论均来自可复现的实际执行，而非静态阅读：

- 崩溃边界由二分规模的实跑确定（n=500/900 正常，n=1000 崩溃）
- 断链由脚本按文件实际所在位置解析相对路径后统计
- 标题层级由无头 Chrome 执行 JS 后 dump 出的真实 DOM 判定
- 死代码由标签全集与各标签文章数推导
- 正确性由 105 组模糊测试比对
- 测试缺口由读取测试文件中的实际规模参数确认

注：分析过程中我的两条检查脚本自身出过 bug（`realpath -m` 在 macOS 不可用导致误报全部断链；模糊测试把「排序结果」与「原始数据」比较导致误报修改入参），均已修正后重跑，上表结论取自修正后的结果。
