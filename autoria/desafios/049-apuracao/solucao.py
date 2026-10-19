def resolver(votos):
    f = {}
    for v in votos:
        f[v] = f.get(v, 0) + 1
    return [[c, n] for c, n in sorted(f.items(), key=lambda p: (-p[1], p[0]))]
