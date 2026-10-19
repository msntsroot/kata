def resolver(nums, x):
    ini, fim, resp = 0, len(nums) - 1, -1
    while ini <= fim:
        m = (ini + fim) // 2
        if nums[m] >= x:
            if nums[m] == x:
                resp = m
            fim = m - 1
        else:
            ini = m + 1
    return resp
