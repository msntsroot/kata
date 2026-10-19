def gerar(rng):
    casos = [[[], 1], [[7, 7, 7], 7], [[1, 1, 2], 2], [[1, 2, 2], 0], [[5], 6]]
    grande = sorted(rng.randint(0, 1000) for _ in range(1000000))
    casos.append([grande, grande[777777]])
    casos.append([[3] * 1000000, 3])
    return casos
