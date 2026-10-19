def resolver(s):
    ult = {}
    ini = melhor = 0
    for i, c in enumerate(s):
        if c in ult and ult[c] >= ini:
            ini = ult[c] + 1
        ult[c] = i
        melhor = max(melhor, i - ini + 1)
    return melhor
