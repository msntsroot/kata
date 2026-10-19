def gerar(rng):
    casos = [[[0], 0], [[0, 0, 0], 0], [[1, -1, 1, -1], 0], [[3, 4, 7, 2, -3, 1, 4, 2], 7], [[5], 3]]
    casos.append([[rng.randint(-5, 5) for _ in range(100000)], 3])
    casos.append([[1] * 100000, 50000])
    return casos
