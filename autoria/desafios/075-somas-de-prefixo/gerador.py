def gerar(rng):
    casos = [[[7], [[0, 0]]], [[1, -1, 1, -1], [[0, 3], [1, 2], [0, 0]]]]
    nums = [rng.randint(-100, 100) for _ in range(100000)]
    cons = []
    for _ in range(100000):
        a, b = sorted((rng.randrange(100000), rng.randrange(100000)))
        cons.append([a, b])
    casos.append([nums, cons])
    casos.append([list(range(100000)), [[0, 99999]] * 100000])
    casos.append([[5, 5, 5, 5, 5, 5], [[0, 5], [2, 3]]])
    return casos
