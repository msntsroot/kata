def gerar(rng):
    casos = [[[], [1]], [[5], [5, 4, 6]], [[1, 2], [1, 2, 3, 0]]]
    nums = sorted(rng.sample(range(10 ** 7), 100000))
    casos.append([nums, [rng.choice(nums) if rng.random() < .5 else rng.randrange(10 ** 7) for _ in range(100000)]])
    return casos
