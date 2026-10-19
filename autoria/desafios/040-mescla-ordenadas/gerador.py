def gerar(rng):
    casos = [[[], []], [[1, 1], [1]], [[5], [1, 2, 3]]]
    for ta, tb in ((3, 7), (50, 50), (5000, 4000)):
        casos.append([sorted(rng.randint(-99, 99) for _ in range(ta)), sorted(rng.randint(-99, 99) for _ in range(tb))])
    return casos
