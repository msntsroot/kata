def resolver(a, b):
    return a if b == 0 else resolver(b, a % b)
