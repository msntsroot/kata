from collections import deque

def resolver(lab):
    h, w = len(lab), len(lab[0])
    if lab[0][0] == "#" or lab[h - 1][w - 1] == "#":
        return -1
    dist = {(0, 0): 0}
    q = deque([(0, 0)])
    while q:
        a, b = q.popleft()
        if (a, b) == (h - 1, w - 1):
            return dist[(a, b)]
        for x, y in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
            if 0 <= x < h and 0 <= y < w and lab[x][y] == "." and (x, y) not in dist:
                dist[(x, y)] = dist[(a, b)] + 1
                q.append((x, y))
    return -1
