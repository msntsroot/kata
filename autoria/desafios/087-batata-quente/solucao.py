from collections import deque

def resolver(n, k):
    q = deque(range(1, n + 1))
    res = []
    while q:
        q.rotate(-(k - 1))
        res.append(q.popleft())
    return res
