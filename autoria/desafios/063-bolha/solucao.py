def resolver(nums, k):
    nums = list(nums)
    for _ in range(k):
        for i in range(len(nums) - 1):
            if nums[i] > nums[i + 1]:
                nums[i], nums[i + 1] = nums[i + 1], nums[i]
    return nums
