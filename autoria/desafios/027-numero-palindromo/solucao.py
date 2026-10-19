def resolver(n):
    orig, inv = n, 0
    while n > 0:
        inv = inv * 10 + n % 10
        n //= 10
    return inv == orig
