def resolver(pesos, valores, cap):
    m = [0] * (cap + 1)
    for p, v in zip(pesos, valores):
        for c in range(cap, p - 1, -1):
            if m[c - p] + v > m[c]:
                m[c] = m[c - p] + v
    return m[cap]
