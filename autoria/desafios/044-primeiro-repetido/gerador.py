def gerar(rng):
    casos = [[[]], [[7, 7]], [[1, 2, 1, 2]], [[3, 1, 2, 1, 3]]]
    grande = list(range(50000))
    rng.shuffle(grande)
    casos.append([grande + [grande[40000]]])
    casos.append([grande])
    return casos
