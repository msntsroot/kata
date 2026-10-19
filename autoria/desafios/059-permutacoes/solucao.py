def resolver(s):
    if s == "":
        return [""]
    res = set()
    for i, c in enumerate(s):
        for p in resolver(s[:i] + s[i + 1:]):
            res.add(c + p)
    return sorted(res)
