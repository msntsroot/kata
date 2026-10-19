def mesclar(a, b):
    i = j = 0
    r = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            r.append(a[i])
            i += 1
        else:
            r.append(b[j])
            j += 1
    return r + a[i:] + b[j:]

def resolver(nums):
    if len(nums) <= 1:
        return list(nums)
    m = len(nums) // 2
    return mesclar(resolver(nums[:m]), resolver(nums[m:]))
