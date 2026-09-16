"""三种排序算法的实现。

三个函数遵循同一套约定：

    sort(items) -> list

- 返回一个**新的已排序列表**，不修改传入的 items
- 只要求元素之间可比较（`<` / `<=`），因此数字、字符串都适用
- 均为稳定或非稳定排序，各自在下方的 docstring 中说明

复杂度一览：

    算法          平均        最坏        额外空间    稳定
    bubble_sort   O(n²)      O(n²)      O(n)       是
    merge_sort    O(n log n) O(n log n) O(n)       是
    quick_sort    O(n log n) O(n²)      O(log n)   否
"""


def bubble_sort(items):
    """冒泡排序。

    反复比较相邻元素并交换，每一轮把当前最大值「冒」到末尾。
    加了提前退出：某一轮没有发生任何交换，说明已经有序。

    稳定：只在 `>` 时交换，相等元素保持原有相对顺序。

    >>> bubble_sort([3, 1, 2])
    [1, 2, 3]
    """
    result = list(items)
    n = len(result)

    for i in range(n - 1):
        swapped = False
        # 末尾 i 个元素已经就位，无需再比
        for j in range(n - 1 - i):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        if not swapped:
            break

    return result


def merge_sort(items):
    """归并排序（分治）。

    把列表对半切开，分别排好序后再合并。合并时依次取两个子列表
    头部较小的那个，因此是稳定的。

    稳定：合并时用 `<=` 优先取左半边，相等元素保持原有相对顺序。

    >>> merge_sort([3, 1, 2])
    [1, 2, 3]
    """
    result = list(items)
    if len(result) <= 1:
        return result

    mid = len(result) // 2
    left = merge_sort(result[:mid])
    right = merge_sort(result[mid:])

    return _merge(left, right)


def _merge(left, right):
    """合并两个已排序列表，返回新的已排序列表。"""
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # 其中一个先取完，把另一个剩下的直接接上
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(items):
    """快速排序（分治，原地分区）。

    选一个基准值，把列表分成「不大于基准」和「大于基准」两部分，
    再对两部分递归。这里用 Lomuto 分区，取末位元素作基准。

    非稳定：分区时的远距离交换会打乱相等元素的相对顺序。

    注意最坏情况：当输入已经有序或逆序时，每次分区都极度不平衡，
    退化为 O(n²) 且递归深度为 n。改进办法是随机选基准或三数取中。

    >>> quick_sort([3, 1, 2])
    [1, 2, 3]
    """
    result = list(items)
    _quick_sort_in_place(result, 0, len(result) - 1)
    return result


def _quick_sort_in_place(arr, low, high):
    """对 arr[low..high] 区间原地排序。"""
    if low >= high:
        return

    pivot_index = _partition(arr, low, high)
    _quick_sort_in_place(arr, low, pivot_index - 1)
    _quick_sort_in_place(arr, pivot_index + 1, high)


def _partition(arr, low, high):
    """Lomuto 分区：以 arr[high] 为基准，返回基准最终所在下标。"""
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
