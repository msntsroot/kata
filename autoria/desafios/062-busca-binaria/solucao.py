def busca(nums, x):
    ini, fim = 0, len(nums) - 1
    while ini <= fim:
        meio = (ini + fim) // 2
        if nums[meio] == x:
            return meio
        if nums[meio] < x:
            ini = meio + 1
        else:
            fim = meio - 1
    return -1

def resolver(nums, consultas):
    return [busca(nums, x) for x in consultas]
