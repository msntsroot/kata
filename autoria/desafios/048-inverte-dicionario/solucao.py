def resolver(d):
    inv = {}
    for k, v in d.items():
        inv.setdefault(v, []).append(k)
    return {v: sorted(ks) for v, ks in inv.items()}
