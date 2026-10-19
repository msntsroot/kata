def resolver(h):
    i, j = 0, len(h) - 1
    me = md = agua = 0
    while i < j:
        if h[i] < h[j]:
            me = max(me, h[i])
            agua += me - h[i]
            i += 1
        else:
            md = max(md, h[j])
            agua += md - h[j]
            j -= 1
    return agua
