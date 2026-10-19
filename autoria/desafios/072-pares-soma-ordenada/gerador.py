def gerar(rng):
    casos = [[[], 0], [[5], 10], [[-3, -1, 0, 1, 3], 0], [[1, 3, 5], 8]]
    nums = sorted(rng.sample(range(-10 ** 6, 10 ** 6), 200000))
    casos.append([nums, 0])
    casos.append([nums, nums[100] + nums[-100]])
    casos.append([list(range(200000)), 199999])
    return casos
