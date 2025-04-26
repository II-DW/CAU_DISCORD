import random
import math

def calculate_std(scores):
    mean = sum(scores) / len(scores)
    variance = sum((x - mean) ** 2 for x in scores) / len(scores)
    std_dev = math.sqrt(variance)
    return std_dev

def make_random_balanced_teams_math(players, k=1.0, max_attempts=10000):
    scores = [player[1] for player in players]
    std_dev = calculate_std(scores)
    max_diff = std_dev * k

    for _ in range(max_attempts):
        random.shuffle(players)
        team1 = players[:len(players)//2]
        team2 = players[len(players)//2:]

        score1 = sum(p[1] for p in team1)
        score2 = sum(p[1] for p in team2)

        if abs(score1 - score2) <= max_diff:
            return team1, team2

    return None  # 실패
