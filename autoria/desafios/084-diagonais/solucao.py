def resolver(m):
    n = len(m)
    s = sum(m[i][i] + m[i][n - 1 - i] for i in range(n))
    return s - m[n // 2][n // 2] if n % 2 else s
