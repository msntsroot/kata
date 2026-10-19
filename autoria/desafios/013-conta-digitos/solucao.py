def resolver(n):
    n = abs(n)
    if n == 0:
        return 1
    c = 0
    while n > 0:
        n //= 10
        c += 1
    return c
