def gerar(rng):
    casos = [[["."]], [["#"]], [["...."]], [["..", ".."]], [["." * 18] * 18]]
    for t, p in ((10, .15), (100, .05)):
        g = [["#" if rng.random() < p else "." for _ in range(t)] for _ in range(t)]
        g[0][0] = g[-1][-1] = "."
        casos.append([["".join(l) for l in g]])
    return casos
