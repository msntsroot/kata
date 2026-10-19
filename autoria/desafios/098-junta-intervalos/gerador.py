def gerar(rng):
    casos = [[[]], [[[5, 5]]], [[[1, 10], [2, 3], [4, 5]]], [[[6, 8], [1, 2], [3, 4]]], [[[1, 2], [2, 3], [3, 4]]]]
    iv = []
    for _ in range(30000):
        a = rng.randint(0, 10 ** 6)
        iv.append([a, a + rng.randint(0, 40)])
    casos.append([iv])
    return casos
