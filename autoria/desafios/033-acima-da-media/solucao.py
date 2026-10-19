def resolver(nums):
    media = sum(nums) / len(nums)
    return sum(1 for x in nums if x > media)
