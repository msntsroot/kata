def resolver(texto):
    f = {}
    for p in texto.lower().split():
        f[p] = f.get(p, 0) + 1
    return min(f, key=lambda p: (-f[p], p))
