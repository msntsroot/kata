def resolver(n):
    return 1 if n == 0 else n * resolver(n - 1)
