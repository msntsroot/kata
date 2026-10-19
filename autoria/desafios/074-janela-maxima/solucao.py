def resolver(nums, k):
    s = sum(nums[:k])
    m = s
    for i in range(len(nums) - k):
        s += nums[i + k] - nums[i]
        if s > m:
            m = s
    return m
