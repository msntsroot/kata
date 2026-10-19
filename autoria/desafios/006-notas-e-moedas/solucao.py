def resolver(centavos):
    valores = [10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5, 1]
    res = []
    for v in valores:
        res.append(centavos // v)
        centavos %= v
    return res
