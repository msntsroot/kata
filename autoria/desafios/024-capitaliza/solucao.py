def resolver(frase):
    return " ".join(p[:1].upper() + p[1:].lower() for p in frase.split(" "))
