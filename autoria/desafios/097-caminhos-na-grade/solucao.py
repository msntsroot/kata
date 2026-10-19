def resolver(g):
    h, w = len(g), len(g[0])
    c = [[0] * w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            if g[i][j] == "#":
                continue
            if i == 0 and j == 0:
                c[i][j] = 1
            else:
                c[i][j] = (c[i - 1][j] if i else 0) + (c[i][j - 1] if j else 0)
    return c[-1][-1]
