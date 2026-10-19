def gerar(rng):
    casos = []
    for tam in (0, 1, 2, 5, 20, 1000):
        casos.append([[rng.randint(-50, 50) for _ in range(tam)]])
    return casos
