def resolver(romano):
    v = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    t = 0
    for i, s in enumerate(romano):
        if i + 1 < len(romano) and v[s] < v[romano[i + 1]]:
            t -= v[s]
        else:
            t += v[s]
    return t
