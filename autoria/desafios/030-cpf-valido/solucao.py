def digito(nums, peso):
    s = sum(n * p for n, p in zip(nums, range(peso, 1, -1)))
    r = s * 10 % 11
    return 0 if r == 10 else r

def resolver(cpf):
    nums = [int(c) for c in cpf if c.isdigit()]
    if len(nums) != 11 or len(set(nums)) == 1:
        return False
    return digito(nums[:9], 10) == nums[9] and digito(nums[:10], 11) == nums[10]
