def resolver(b, e, m):
    if e == 0:
        return 1 % m
    meia = resolver(b, e // 2, m)
    r = meia * meia % m
    return r * b % m if e % 2 else r
