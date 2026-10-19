def eh_primo(n):
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True

def resolver(nums):
    return [x for x in nums if eh_primo(x)]
