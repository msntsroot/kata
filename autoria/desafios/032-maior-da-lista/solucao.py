def resolver(nums):
    m = nums[0]
    for x in nums:
        if x > m:
            m = x
    return m
