def gerar(rng):
    casos = [[[5], 1], [[1, 2, 3], 3], [[3, -1, 4, -1, 5], 2], [[-5, -4, -3], 2]]
    nums = [rng.randint(-1000, 1000) for _ in range(200000)]
    casos.append([nums, 100000])
    casos.append([nums, 1])
    return casos
