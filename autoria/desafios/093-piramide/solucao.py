def resolver(p):
    abaixo = list(p[-1])
    for linha in reversed(p[:-1]):
        abaixo = [v + min(abaixo[j], abaixo[j + 1]) for j, v in enumerate(linha)]
    return abaixo[0]
