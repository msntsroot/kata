def resolver(moedas, valor):
    inf = float("inf")
    m = [0] + [inf] * valor
    for v in range(1, valor + 1):
        for c in moedas:
            if c <= v and m[v - c] + 1 < m[v]:
                m[v] = m[v - c] + 1
    return -1 if m[valor] == inf else m[valor]
