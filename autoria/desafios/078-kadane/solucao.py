def resolver(nums):
    atual = melhor = nums[0]
    for x in nums[1:]:
        atual = max(x, atual + x)
        melhor = max(melhor, atual)
    return melhor
