def resolver(a, b):
    res = []
    n = min(len(a), len(b))
    for i in range(n):
        res += [a[i], b[i]]
    return res + a[n:] + b[n:]
