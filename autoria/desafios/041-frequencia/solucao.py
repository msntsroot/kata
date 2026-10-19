def resolver(texto):
    f = {}
    for c in texto.lower():
        if c.isalpha():
            f[c] = f.get(c, 0) + 1
    return f
