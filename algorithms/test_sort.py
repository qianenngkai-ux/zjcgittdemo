"""sort.py 中六种排序算法的测试。

用标准库 unittest，无需 pip install —— 与仓库其余部分「零依赖」的约定一致。

运行：
    python3 -m unittest discover -s algorithms -p 'test_*.py' -v
"""

import random
import unittest
from functools import total_ordering

# 兼容两种运行方式：
#   1. 当作包导入（-m unittest algorithms.test_sort、根目录 discover）
#   2. 直接运行本文件（python3 algorithms/test_sort.py）—— 此时
#      sys.path 里是 algorithms/ 而非仓库根目录，包名导入会失败。
try:
    from algorithms.sort import (
        bubble_sort, merge_sort, quick_sort,
        insertion_sort, selection_sort, heap_sort,
    )
except ModuleNotFoundError:
    from sort import (
        bubble_sort, merge_sort, quick_sort,
        insertion_sort, selection_sort, heap_sort,
    )


@total_ordering
class Ranked:
    """自定义可比较类型，用于验证「元素可排序」这一契约。

    - 只实现 `__eq__` 与 `__lt__`，其余四个比较运算符由 total_ordering 补全
    - `order` 记录原始位置，用于检验稳定性：相等元素的 order 应保持递增

    之所以需要这个类型：内置的 int / float / str 天然支持全部运算符，
    用它们做测试无法发现「某个算法多要求了一个运算符」这类问题。
    """

    def __init__(self, key, order=0):
        self.key = key
        self.order = order

    def __eq__(self, other):
        return self.key == other.key

    def __lt__(self, other):
        return self.key < other.key

    def __repr__(self):
        return f"<{self.key}#{self.order}>"


class SortContractMixin:
    """六种排序算法共有的行为契约。

    子类只需提供 `sort` 属性指向被测函数，即可继承下面全部用例。
    这样六个算法跑的是同一套边界条件，任何一个实现有缺口都会立刻暴露。
    """

    sort = None

    # ---- 基础边界 ----

    def test_empty_list(self):
        self.assertEqual(self.sort([]), [])

    def test_single_element(self):
        self.assertEqual(self.sort([42]), [42])

    def test_two_elements_ordered(self):
        self.assertEqual(self.sort([1, 2]), [1, 2])

    def test_two_elements_reversed(self):
        self.assertEqual(self.sort([2, 1]), [1, 2])

    # ---- 典型排列 ----

    def test_already_sorted(self):
        self.assertEqual(self.sort([1, 2, 3, 4, 5]), [1, 2, 3, 4, 5])

    def test_reverse_sorted(self):
        self.assertEqual(self.sort([5, 4, 3, 2, 1]), [1, 2, 3, 4, 5])

    def test_unsorted(self):
        self.assertEqual(self.sort([3, 1, 4, 1, 5, 9, 2, 6]), [1, 1, 2, 3, 4, 5, 6, 9])

    # ---- 重复值与负数 ----

    def test_all_duplicates(self):
        self.assertEqual(self.sort([7, 7, 7, 7]), [7, 7, 7, 7])

    def test_duplicates_preserved(self):
        self.assertEqual(self.sort([2, 3, 2, 1, 3]), [1, 2, 2, 3, 3])

    def test_negative_numbers(self):
        self.assertEqual(self.sort([3, -1, 0, -5, 2]), [-5, -1, 0, 2, 3])

    def test_floats(self):
        self.assertEqual(self.sort([2.5, 0.1, -1.5]), [-1.5, 0.1, 2.5])

    # ---- 不修改原列表 ----

    def test_does_not_mutate_input(self):
        original = [3, 1, 2]
        snapshot = list(original)
        self.sort(original)
        self.assertEqual(original, snapshot, "排序函数不应修改传入的列表")

    def test_returns_new_list_not_alias(self):
        """返回值必须是新列表。

        单元素输入是最容易漏的一条路径：实现若省略拷贝并直接返回入参，
        这里就会拿到原列表的别名，调用方一改返回值就污染了原数据。
        """
        original = [1]
        result = self.sort(original)
        self.assertIsNot(result, original, "返回值不应是传入列表的别名")
        self.assertEqual(result, [1])

    def test_result_is_independent_of_input(self):
        """改动返回值不应影响原列表。"""
        original = [2, 1]
        result = self.sort(original)
        result.append(99)
        self.assertEqual(original, [2, 1], "修改返回值不应影响原列表")

    # ---- 自定义可比较类型 ----
    #
    # 下面两条盯住模块 docstring 里的「元素可排序」契约。历史教训：测试
    # 若只用 int / float / str，则「某个算法悄悄多依赖了一个比较运算符」
    # 不会被发现 —— 而这正是曾经真实存在的问题（merge/quick 需要 __le__，
    # heap 需要 >=，只定义 __lt__ 的类型会抛 TypeError）。

    def test_sorts_custom_comparable_type(self):
        items = [Ranked(3), Ranked(1), Ranked(2)]
        self.assertEqual([x.key for x in self.sort(items)], [1, 2, 3])

    def test_sorts_custom_type_with_duplicates(self):
        items = [Ranked(2), Ranked(1), Ranked(2), Ranked(0)]
        self.assertEqual([x.key for x in self.sort(items)], [0, 1, 2, 2])

    # ---- 规模与随机性 ----

    def test_larger_random_list(self):
        rng = random.Random(20260916)  # 固定种子，失败可复现
        data = [rng.randint(-1000, 1000) for _ in range(500)]
        self.assertEqual(self.sort(data), sorted(data))

    def test_many_duplicates_random(self):
        rng = random.Random(7)
        data = [rng.choice([0, 1, 2]) for _ in range(200)]
        self.assertEqual(self.sort(data), sorted(data))

    # ---- 最坏情况回归测试 ----
    #
    # 固定取末位作基准的分区，在有序输入下每次划分都极不平衡，递归深度
    # 退化为 O(n)，会撞上 Python 默认的递归上限（1000）直接崩溃。
    # 下面三条用例专门盯住这个最坏情况，规模取 2000 以留出安全余量。
    #
    # 必须对全部六个算法运行 —— 尤其 quick_sort，它正是当初崩溃的那个。

    def test_large_already_sorted(self):
        """已排序的大输入 —— 快排的经典最坏情况。"""
        data = list(range(2000))
        self.assertEqual(self.sort(data), data)

    def test_large_reverse_sorted(self):
        """逆序的大输入 —— 另一个最坏情况。"""
        data = list(range(2000, 0, -1))
        self.assertEqual(self.sort(data), list(range(1, 2001)))

    def test_large_all_identical(self):
        """元素全部相同 —— 分区会把它们全划到同一侧。"""
        data = [5] * 2000
        self.assertEqual(self.sort(data), data)


class StableSortMixin:
    """稳定排序额外要满足的保证：相等元素保持原有相对顺序。

    只被声明为「稳定」的三个算法继承（bubble / insertion / merge）。

    另外三个声明为非稳定 —— 但「非稳定」意味着**不保证**顺序，而不是
    「一定会打乱」，所以对它们断言顺序变化属于依赖具体实现的测试，
    不能当作契约。它们只继承上面的通用契约。
    """

    sort = None

    def test_preserves_order_of_equal_elements(self):
        items = [Ranked(1, 0), Ranked(1, 1), Ranked(1, 2)]
        out = self.sort(items)
        self.assertEqual([x.order for x in out], [0, 1, 2],
                         "相等元素应保持原有相对顺序")

    def test_preserves_order_with_interleaved_elements(self):
        items = [Ranked(2, 0), Ranked(1, 1), Ranked(2, 2), Ranked(1, 3), Ranked(0, 4)]
        out = self.sort(items)
        self.assertEqual([x.order for x in out if x.key == 2], [0, 2])
        self.assertEqual([x.order for x in out if x.key == 1], [1, 3])

    def test_preserves_order_on_large_input_with_many_duplicates(self):
        rng = random.Random(11)
        items = [Ranked(rng.randint(0, 3), i) for i in range(200)]
        out = self.sort(items)
        for key in {x.key for x in items}:
            orders = [x.order for x in out if x.key == key]
            self.assertEqual(orders, sorted(orders), f"key={key} 的相等元素顺序被打乱")


# 声明为「稳定」的三个算法，额外继承稳定性契约。
# 另外三个（selection / quick / heap）声明为非稳定，只继承通用契约。


class TestBubbleSort(SortContractMixin, StableSortMixin, unittest.TestCase):
    sort = staticmethod(bubble_sort)


class TestMergeSort(SortContractMixin, StableSortMixin, unittest.TestCase):
    sort = staticmethod(merge_sort)


class TestQuickSort(SortContractMixin, unittest.TestCase):
    sort = staticmethod(quick_sort)


# ---- 第二批：简单排序与堆排序 ----
#
# 这三种是 O(n²) / O(n log n) 里另外三个代表，与上面的冒泡/归并/快排
# 共用同一套契约测试，因此边界行为完全对齐。


class TestInsertionSort(SortContractMixin, StableSortMixin, unittest.TestCase):
    sort = staticmethod(insertion_sort)


class TestSelectionSort(SortContractMixin, unittest.TestCase):
    sort = staticmethod(selection_sort)


class TestHeapSort(SortContractMixin, unittest.TestCase):
    sort = staticmethod(heap_sort)


if __name__ == "__main__":
    unittest.main()
