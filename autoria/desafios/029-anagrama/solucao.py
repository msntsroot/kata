def resolver(a, b):
    a = a.replace(" ", "").lower()
    b = b.replace(" ", "").lower()
    if len(a) != len(b):
        return False
    for c in a:
        if a.count(c) != b.count(c):
            return False
    return True
