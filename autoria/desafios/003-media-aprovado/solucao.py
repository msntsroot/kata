def resolver(n1, n2, n3):
    media = (n1 + n2 + n3) / 3
    if media >= 7:
        return "aprovado"
    elif media >= 5:
        return "recuperacao"
    return "reprovado"
