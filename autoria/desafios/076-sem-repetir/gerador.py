def gerar(rng):
    casos = [[""], ["a"], ["abcdef"], ["abba"], ["dvdf"], ["tmmzuxt"]]
    casos.append(["".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(200000))])
    casos.append(["".join(rng.choice("ab") for _ in range(200000))])
    return casos
