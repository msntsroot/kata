def eh_primo(k):
    if k < 2:
        return False
    d = 2
    while d * d <= k:
        if k % d == 0:
            return False
        d += 1
    return True

def resolver(n):
    return [k for k in range(2, n + 1) if eh_primo(k)]
