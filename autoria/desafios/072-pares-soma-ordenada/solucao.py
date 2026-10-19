def resolver(nums, alvo):
    i, j, c = 0, len(nums) - 1, 0
    while i < j:
        s = nums[i] + nums[j]
        if s == alvo:
            c += 1
            i += 1
            j -= 1
        elif s < alvo:
            i += 1
        else:
            j -= 1
    return c
