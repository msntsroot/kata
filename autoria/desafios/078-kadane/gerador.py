def gerar(rng):
    casos = [[[5]], [[-1]], [[1, 2, 3]], [[2, -10, 3]], [[0, 0, 0]], [[-2, -3, 4, -1, -2, 1, 5, -3]]]
    casos.append([[rng.randint(-1000, 1000) for _ in range(200000)]])
    return casos
