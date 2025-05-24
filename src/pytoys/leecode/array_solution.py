from typing import List


def remove_ordered_array_duplicates(nums: List[int]) -> int:
    """删除有序数组中的重复项

    给定一个非严格递增排列的数组 nums ，原地 删除重复出现的元素，使每个元素只出现一次，
    返回删除后数组的新长度。元素的相对顺序保持一致。

    >>> nums = [0,0,1,1,1,2,2,3,3,4]
    >>> remove_ordered_array_duplicates(nums)
    5
    >>> nums[:5]
    [0, 1, 2, 3, 4]
    """
    k = 1
    for i in range(1, len(nums)):
        if nums[i] != nums[i - 1]:
            nums[k] = nums[i]
            k += 1
    return k


def remove_ordered_array_duplicates_v2(nums: List[int]) -> int:
    """删除有序数组中的重复项(另一个版本)

    >>> nums = [0,0,1,1,1,2,2,3,3,4]
    >>> remove_ordered_array_duplicates_v2(nums)
    5
    >>> nums[:5]
    [0, 1, 2, 3, 4]
    """
    nums[:] = list(set(nums))
    return len(nums)
