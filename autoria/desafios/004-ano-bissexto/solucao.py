def resolver(ano):
    if ano % 400 == 0:
        return True
    if ano % 100 == 0:
        return False
    return ano % 4 == 0
