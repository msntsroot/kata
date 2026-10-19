def resolver(nums):
    vistos = set()
    for x in nums:
        if x in vistos:
            return x
        vistos.add(x)
    return None
