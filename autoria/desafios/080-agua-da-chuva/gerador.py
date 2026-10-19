def gerar(rng):
    casos = [[[]], [[5]], [[1, 2, 3]], [[3, 2, 1]], [[2, 0, 2]], [[5, 0, 0, 0, 1]], [[0, 7, 1, 4, 6]]]
    casos.append([[rng.randint(0, 10000) for _ in range(200000)]])
    return casos
