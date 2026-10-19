def resolver(intervalos):
    res = []
    for a, b in sorted(intervalos):
        if res and a <= res[-1][1]:
            res[-1][1] = max(res[-1][1], b)
        else:
            res.append([a, b])
    return res
