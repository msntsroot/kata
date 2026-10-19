def bissexto(ano):
    return ano % 400 == 0 or (ano % 4 == 0 and ano % 100 != 0)

def resolver(dia, mes, ano):
    if ano < 1 or not 1 <= mes <= 12:
        return False
    dias = [31, 29 if bissexto(ano) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return 1 <= dia <= dias[mes - 1]
