def resolver(texto):
    f = {}
    for c in texto:
        f[c] = f.get(c, 0) + 1
    for c in texto:
        if f[c] == 1:
            return c
    return ""
