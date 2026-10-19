def resolver(nums, consultas):
    p = [0]
    for x in nums:
        p.append(p[-1] + x)
    return [p[j + 1] - p[i] for i, j in consultas]
