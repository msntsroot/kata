def gerar(rng):
    casos = [[[], 1], [[5], 10], [[1, 4, 4, 1], 5], [[0, -3, 3, 0], 0]]
    nums = [rng.randint(-10**6, 10**6) for _ in range(50000)]
    casos.append([nums, nums[30000] + nums[49000]])
    casos.append([list(range(0, 100000, 2)), 3])
    return casos
