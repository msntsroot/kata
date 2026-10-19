def resolver(tokens):
    p = []
    for t in tokens:
        if t in "+-*/" and len(t) == 1:
            b, a = p.pop(), p.pop()
            p.append(a + b if t == "+" else a - b if t == "-" else a * b if t == "*" else int(a / b))
        else:
            p.append(int(t))
    return p[0]
