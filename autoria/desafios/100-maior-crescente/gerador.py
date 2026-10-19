def gerar(rng):
    casos = [[[]], [[1]], [[1, 2, 3]], [[3, 2, 1]], [[0, 1, 0, 3, 2, 3]], [[4, 10, 4, 3, 8, 9]]]
    casos.append([[rng.randint(0, 10 ** 6) for _ in range(3000)]])
    casos.append([list(range(3000))])
    return casos
