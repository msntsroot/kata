def mover(n, de, para, aux, res):
    if n == 0:
        return
    mover(n - 1, de, aux, para, res)
    res.append([de, para])
    mover(n - 1, aux, para, de, res)

def resolver(n):
    res = []
    mover(n, 1, 3, 2, res)
    return res
