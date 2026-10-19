def gerar(rng):
    casos = [[[[1], [2, 3]]], [[[1], [1, 1], [1, 1, 1]]], [[[5], [-1, 9], [9, -1, 9]]]]
    for n in (10, 500):
        casos.append([[[rng.randint(-50, 99) for _ in range(i + 1)] for i in range(n)]])
    return casos
