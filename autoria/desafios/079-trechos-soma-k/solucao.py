def resolver(nums, k):
    vistos = {0: 1}
    p = c = 0
    for x in nums:
        p += x
        c += vistos.get(p - k, 0)
        vistos[p] = vistos.get(p, 0) + 1
    return c
