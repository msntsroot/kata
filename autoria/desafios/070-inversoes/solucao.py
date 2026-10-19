def conta(nums):
    if len(nums) <= 1:
        return list(nums), 0
    m = len(nums) // 2
    a, x = conta(nums[:m])
    b, y = conta(nums[m:])
    i = j = 0
    r, inv = [], x + y
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            r.append(a[i])
            i += 1
        else:
            r.append(b[j])
            j += 1
            inv += len(a) - i
    return r + a[i:] + b[j:], inv

def resolver(nums):
    return conta(nums)[1]
