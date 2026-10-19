def gerar(rng):
    casos = [["abc", ""], ["kitten", "sitting"], ["intention", "execution"], ["igual", "igual"], ["ab", "ba"]]
    casos.append(["".join(rng.choice("abc") for _ in range(800)), "".join(rng.choice("abc") for _ in range(800))])
    return casos
