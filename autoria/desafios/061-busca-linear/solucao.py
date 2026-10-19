def resolver(nums, x):
    for i, v in enumerate(nums):
        if v == x:
            return i
    return -1
