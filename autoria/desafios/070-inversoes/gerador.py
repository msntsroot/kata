def gerar(rng):
    casos = [[[]], [[1]], [[2, 1]], [[1, 1, 1]], [[5, 4, 3, 2, 1, 0]]]
    casos.append([[rng.randint(0, 10 ** 6) for _ in range(100000)]])
    casos.append([list(range(100000, 0, -1))])
    return casos
