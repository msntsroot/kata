def resolver(texto, k):
    res = ""
    for c in texto:
        if "a" <= c <= "z":
            c = chr((ord(c) - 97 + k) % 26 + 97)
        res += c
    return res
