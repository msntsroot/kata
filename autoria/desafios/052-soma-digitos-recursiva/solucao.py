def resolver(n):
    return 0 if n == 0 else n % 10 + resolver(n // 10)
