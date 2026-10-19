def passo(g):
    h, w = len(g), len(g[0])
    novo = [[0] * w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            v = 0
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if (di or dj) and 0 <= i + di < h and 0 <= j + dj < w:
                        v += g[i + di][j + dj]
            novo[i][j] = 1 if v == 3 or (g[i][j] and v == 2) else 0
    return novo

def resolver(g, geracoes):
    for _ in range(geracoes):
        g = passo(g)
    return g
