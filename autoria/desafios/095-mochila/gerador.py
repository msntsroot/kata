def gerar(rng):
    casos = [[[], [], 10], [[1, 1, 1], [5, 5, 5], 2], [[10, 20, 30], [60, 100, 120], 50]]
    for n, cap in ((10, 50), (100, 5000)):
        casos.append([[rng.randint(1, cap // 4) for _ in range(n)], [rng.randint(1, 1000) for _ in range(n)], cap])
    return casos
