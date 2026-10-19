def resolver(a, b):
    ant = [0] * (len(b) + 1)
    for ca in a:
        cur = [0]
        for j, cb in enumerate(b):
            cur.append(ant[j] + 1 if ca == cb else max(ant[j + 1], cur[j]))
        ant = cur
    return ant[-1]
