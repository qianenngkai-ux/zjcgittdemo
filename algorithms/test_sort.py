"""sort.py 中三种排序算法的测试。

用标准库 unittest，无需 pip install —— 与仓库其余部分「零依赖」的约定一致。

运行：
    python3 -m unittest discover -s algorithms -p 'test_*.py' -v
"""

import random
import unittest

# 兼容两种运行方式：
#   1. 当作包导入（-m unittest algorithms.test_sort、根目录 discover）
#   2. 直接运行本文件（python3 algorithms/test_sort.py）—— 此时
#      sys.path 里是 algorithms/ 而非仓库根目录，包名导入会失败。
try:
    from algorithms.sort import bubble_sort, merge_sort, quick_sort
except ModuleNotFoundError:
    from sort import bubble_sort, merge_sort, quick_sort


class SortContractMixin:
    """三种排序算法共有的行为契约。

    子类只需提供 `sort` 属性指向被测函数，即可继承下面全部用例。
    这样三个算法跑的是同一套边界条件，任何一个实现有缺口都会立刻暴露。
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


class TestBubbleSort(SortContractMixin, unittest.TestCase):
    sort = staticmethod(bubble_sort)


class TestMergeSort(SortContractMixin, unittest.TestCase):
    sort = staticmethod(merge_sort)


class TestQuickSort(SortContractMixin, unittest.TestCase):
    sort = staticmethod(quick_sort)


if __name__ == "__main__":
    unittest.main()
