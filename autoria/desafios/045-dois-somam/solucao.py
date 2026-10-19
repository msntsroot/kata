def resolver(nums, alvo):
    pos = {}
    for j, x in enumerate(nums):
        if alvo - x in pos:
            return [pos[alvo - x], j]
        if x not in pos:
            pos[x] = j
    return []
