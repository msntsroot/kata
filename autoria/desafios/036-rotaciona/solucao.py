def resolver(nums, k):
    if not nums:
        return []
    k %= len(nums)
    return nums[len(nums) - k:] + nums[:len(nums) - k]
