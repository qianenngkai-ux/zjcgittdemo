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
    再对两部分递归。这里用 Lomuto 分区 + 三数取中选基准。

    非稳定：分区时的远距离交换会打乱相等元素的相对顺序。

    最坏情况仍是 O(n²)（例如大量重复元素），但**不会**因递归过深而崩溃：
    递归只在较小的一侧进行，较大的一侧改用循环，栈深度恒为 O(log n)。

    >>> quick_sort([3, 1, 2])
    [1, 2, 3]
    """
    result = list(items)
    _quick_sort_in_place(result, 0, len(result) - 1)
    return result


def _quick_sort_in_place(arr, low, high):
    """对 arr[low..high] 区间原地排序。

    用循环而非双递归：每次只对较小的一侧递归，较大的一侧留在循环里继续处理。
    这样无论划分多么不平衡，栈深度都不超过 O(log n)。
    若两侧都递归，遇到有序输入或大量重复元素时会退化到 O(n) 深度，
    进而触发 Python 的 RecursionError。
    """
    while low < high:
        pivot_index = _partition(arr, low, high)

        left_size = pivot_index - low
        right_size = high - pivot_index

        if left_size < right_size:
            _quick_sort_in_place(arr, low, pivot_index - 1)
            low = pivot_index + 1
        else:
            _quick_sort_in_place(arr, pivot_index + 1, high)
            high = pivot_index - 1


def _partition(arr, low, high):
    """Lomuto 分区：以 arr[high] 为基准，返回基准最终所在下标。

    基准由「三数取中」选出：取首、中、尾三个元素的中位数并换到末位。
    固定取末位的话，已排序或逆序的输入会让每次划分都极度不平衡。
    """
    mid = (low + high) // 2

    # 三步比较后，三者有序：arr[low] <= arr[mid] <= arr[high]
    if arr[mid] < arr[low]:
        arr[low], arr[mid] = arr[mid], arr[low]
    if arr[high] < arr[low]:
        arr[low], arr[high] = arr[high], arr[low]
    if arr[high] < arr[mid]:
        arr[mid], arr[high] = arr[high], arr[mid]

    # 中位数现在位于 arr[mid]，换到末位作为基准
    arr[mid], arr[high] = arr[high], arr[mid]

    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
