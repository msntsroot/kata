def resolver(pessoas):
    return [p[0] for p in sorted(pessoas, key=lambda p: (-p[1], p[0]))]
