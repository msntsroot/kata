def gerar(rng):
    casos = []
    for (h, w, p) in ((1, 1, .5), (3, 4, .5), (6, 6, .4), (20, 30, .45), (150, 150, .6), (150, 150, .3)):
        casos.append([["".join("1" if rng.random() < p else "0" for _ in range(w)) for _ in range(h)]])
    casos.append([["1" * 150] * 150])
    return casos
