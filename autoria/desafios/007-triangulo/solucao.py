def resolver(a, b, c):
    if a >= b + c or b >= a + c or c >= a + b:
        return "invalido"
    if a == b == c:
        return "equilatero"
    if a == b or b == c or a == c:
        return "isosceles"
    return "escaleno"
