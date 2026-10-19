def resolver(frase):
    s = frase.replace(" ", "").lower()
    return s == s[::-1]
