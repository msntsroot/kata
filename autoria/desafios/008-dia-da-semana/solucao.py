def resolver(hoje, n):
    dias = ["dom", "seg", "ter", "qua", "qui", "sex", "sab"]
    return dias[(dias.index(hoje) + n) % 7]
