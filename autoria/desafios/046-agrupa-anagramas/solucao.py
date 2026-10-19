def resolver(palavras):
    g = {}
    for p in palavras:
        g.setdefault("".join(sorted(p)), []).append(p)
    return sorted(sorted(v) for v in g.values())
