def gerar(rng):
    casos = [["", "abc"], ["a", "a"], ["abc", "abc"], ["abcba", "abcbcba"], ["kata", "taka"]]
    casos.append(["".join(rng.choice("acgt") for _ in range(1000)), "".join(rng.choice("acgt") for _ in range(1000))])
    return casos
