def resolver(s):
    if len(s) < 2:
        return True
    return s[0] == s[-1] and resolver(s[1:-1])
