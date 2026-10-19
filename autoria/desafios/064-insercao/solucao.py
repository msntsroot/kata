def resolver(nums, k):
    nums = list(nums)
    for i in range(1, min(k + 1, len(nums))):
        x = nums[i]
        j = i - 1
        while j >= 0 and nums[j] > x:
            nums[j + 1] = nums[j]
            j -= 1
        nums[j + 1] = x
    return nums
