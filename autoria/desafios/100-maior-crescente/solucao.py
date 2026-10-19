def resolver(nums):
    finais = []
    for x in nums:
        ini, fim = 0, len(finais)
        while ini < fim:
            m = (ini + fim) // 2
            if finais[m] < x:
                ini = m + 1
            else:
                fim = m
        if ini == len(finais):
            finais.append(x)
        else:
            finais[ini] = x
    return len(finais)
