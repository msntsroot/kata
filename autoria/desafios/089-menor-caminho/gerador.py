def gerar(rng):
    casos = []
    for (h, w, p) in ((1, 1, 0), (2, 2, .0), (5, 5, .3), (10, 20, .25), (200, 200, .2), (200, 200, .35)):
        g = [["#" if rng.random() < p else "." for _ in range(w)] for _ in range(h)]
        g[0][0] = g[-1][-1] = "."
        casos.append(["".join(l) for l in g])
    return [[c] for c in casos] + [[["." * 200] * 200]]
