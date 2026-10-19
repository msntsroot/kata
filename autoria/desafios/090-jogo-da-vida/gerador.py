def gerar(rng):
    casos = [[[[1]], 1], [[[0, 0, 0], [1, 1, 1], [0, 0, 0]], 2], [[[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0], [0, 0, 0]], 4]]
    for t, n in ((8, 3), (30, 10), (60, 20)):
        casos.append([[[1 if rng.random() < .35 else 0 for _ in range(t)] for _ in range(t)], n])
    return casos
