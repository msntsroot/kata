def resolver(eventos):
    fim = None
    c = 0
    for a, b in sorted(eventos, key=lambda e: e[1]):
        if fim is None or a >= fim:
            c += 1
            fim = b
    return c
