def gerar(rng):
    casos = [[[1]], [[2, 1]], [[3, 3, 3]], [list(range(10, 0, -1))]]
    casos.append([[rng.randint(-10 ** 6, 10 ** 6) for _ in range(50000)]])
    casos.append([list(range(50000, 0, -1))])
    return casos
