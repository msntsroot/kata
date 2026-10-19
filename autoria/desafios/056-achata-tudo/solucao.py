def resolver(lista):
    res = []
    for x in lista:
        if isinstance(x, list):
            res.extend(resolver(x))
        else:
            res.append(x)
    return res
