def resolver(mapa):
    h, w = len(mapa), len(mapa[0]) if mapa else 0
    vis = set()
    ilhas = 0
    for i in range(h):
        for j in range(w):
            if mapa[i][j] == "1" and (i, j) not in vis:
                ilhas += 1
                pilha = [(i, j)]
                vis.add((i, j))
                while pilha:
                    a, b = pilha.pop()
                    for x, y in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                        if 0 <= x < h and 0 <= y < w and mapa[x][y] == "1" and (x, y) not in vis:
                            vis.add((x, y))
                            pilha.append((x, y))
    return ilhas
