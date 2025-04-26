import random
import math


def calculate_std(scores):
    mean = sum(scores) / len(scores)
    var = sum((x - mean) ** 2 for x in scores) / len(scores)
    return math.sqrt(var)


def make_random_balanced_teams(players, k=1.0, max_attempts=10000):
    scores = [p[1] for p in players]
    max_diff = calculate_std(scores) * k
    half = len(players) // 2
    for _ in range(max_attempts):
        random.shuffle(players)
        t1 = players[:half]
        t2 = players[half:]
        s1 = sum(p[1] for p in t1)
        s2 = sum(p[1] for p in t2)
        if abs(s1 - s2) <= max_diff:
            return t1, t2
    return players[:half], players[half:]
