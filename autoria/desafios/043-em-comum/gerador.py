def gerar(rng):
    casos = [[[], [1]], [[5, 5], [5]]]
    for t in (10, 100, 20000):
        casos.append([[rng.randint(0, t) for _ in range(t)], [rng.randint(0, t) for _ in range(t)]])
    return casos
