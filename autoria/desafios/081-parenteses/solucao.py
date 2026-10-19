def resolver(s):
    par = {")": "(", "]": "[", "}": "{"}
    pilha = []
    for c in s:
        if c in "([{":
            pilha.append(c)
        elif not pilha or pilha.pop() != par[c]:
            return False
    return not pilha
