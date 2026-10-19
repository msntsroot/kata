def resolver(n):
    if n < 2:
        return 0
    e = [True] * (n + 1)
    e[0] = e[1] = False
    p = 2
    while p * p <= n:
        if e[p]:
            e[p * p::p] = [False] * len(range(p * p, n + 1, p))
        p += 1
    return sum(e)
