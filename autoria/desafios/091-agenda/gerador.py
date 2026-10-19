def gerar(rng):
    casos = [[[[1, 2]]], [[[1, 10], [2, 3], [3, 4]]], [[[1, 5], [1, 5], [1, 5]]], [[[5, 6], [1, 2], [3, 4]]]]
    for n in (20, 50000):
        ev = []
        for _ in range(n):
            a = rng.randint(0, 10 ** 6)
            ev.append([a, a + rng.randint(1, 5000)])
        casos.append([ev])
    return casos
