def resolver(m):
    res = []
    if not m:
        return res
    t, b, e, d = 0, len(m) - 1, 0, len(m[0]) - 1
    while t <= b and e <= d:
        for j in range(e, d + 1):
            res.append(m[t][j])
        t += 1
        for i in range(t, b + 1):
            res.append(m[i][d])
        d -= 1
        if t <= b:
            for j in range(d, e - 1, -1):
                res.append(m[b][j])
            b -= 1
        if e <= d:
            for i in range(b, t - 1, -1):
                res.append(m[i][e])
            e += 1
    return res
