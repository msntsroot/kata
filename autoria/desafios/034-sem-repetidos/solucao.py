def resolver(nums):
    res = []
    for x in nums:
        if x not in res:
            res.append(x)
    return res
