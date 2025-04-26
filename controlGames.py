import csv
import json
import database


def read_games():
    with open('livegames.csv', 'r', newline='', encoding='utf-8') as f:
        return list(csv.reader(f))


def write_games(rows):
    with open('livegames.csv', 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(rows)


def add_game(game_name, t1, t2):
    rows = read_games()
    for r in rows:
        if r[0] == game_name:
            return False
    rows.append([game_name, str(t1), str(t2), json.dumps([])])
    write_games(rows)
    return True


def delete_game(game_name):
    rows = read_games()
    new = [r for r in rows if r[0] != game_name]
    if len(new) == len(rows):
        return False
    write_games(new)
    return True


def add_player(game_name, user_name):
    rows = read_games()
    for r in rows:
        if r[0] == game_name:
            players = json.loads(r[3])
            users = database.read_database()
            for u in users:
                if u[0] == user_name:
                    if len(players) >= int(r[1]) + int(r[2]):
                        return False
                    players.append(u)
                    r[3] = json.dumps(players)
                    write_games(rows)
                    return True
            return False
    return False


def remove_player(game_name, user_name):
    rows = read_games()
    for r in rows:
        if r[0] == game_name:
            players = json.loads(r[3])
            new = [p for p in players if p[0] != user_name]
            if len(new) == len(players):
                return False
            r[3] = json.dumps(new)
            write_games(rows)
            return True
    return False