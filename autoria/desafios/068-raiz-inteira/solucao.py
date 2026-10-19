def resolver(n):
    ini, fim, r = 0, n, 0
    while ini <= fim:
        m = (ini + fim) // 2
        if m * m <= n:
            r = m
            ini = m + 1
        else:
            fim = m - 1
    return r
