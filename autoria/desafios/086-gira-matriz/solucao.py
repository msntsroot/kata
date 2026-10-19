def resolver(m):
    n = len(m)
    return [[m[n - 1 - i][j] for i in range(n)] for j in range(n)]
