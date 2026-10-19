def resolver(nums):
    p = s = None
    for x in nums:
        if p is None or x > p:
            p, s = x, p
        elif x != p and (s is None or x > s):
            s = x
    return s
