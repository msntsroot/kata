def resolver(texto):
    if not texto:
        return ""
    res, atual, n = "", texto[0], 0
    for c in texto:
        if c == atual:
            n += 1
        else:
            res += f"{atual}{n}"
            atual, n = c, 1
    return res + f"{atual}{n}"
