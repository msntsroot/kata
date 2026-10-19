def fb(i):
    if i % 15 == 0:
        return "FizzBuzz"
    if i % 3 == 0:
        return "Fizz"
    if i % 5 == 0:
        return "Buzz"
    return str(i)

def resolver(n):
    return [fb(i) for i in range(1, n + 1)]
