import csv
import config


def read_database():
    with open('data.csv', 'r', newline='', encoding='utf-8') as f:
        return list(csv.reader(f))


def write_database(rows):
    with open('data.csv', 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(rows)


def add_user(name, nickname, tier):
    rows = read_database()
    for r in rows:
        if r[0] == name and r[1] == nickname:
            return False
    init_mmr = config.TierList.get(tier, 0)
    rows.append([name, nickname, tier, str(init_mmr), '0', '0'])  # mmr, wins, losses
    write_database(rows)
    return True


def delete_user(name, nickname):
    rows = read_database()
    new = [r for r in rows if not (r[0] == name and r[1] == nickname)]
    if len(new) == len(rows):
        return False
    write_database(new)
    return True


def modify_user(name, old_nick, new_nick, new_tier):
    rows = read_database()
    for r in rows:
        if r[0] == name and r[1] == old_nick:
            r[1] = new_nick
            r[2] = new_tier
            write_database(rows)
            return True
    return False


def record_result(winner, loser):
    rows = read_database()
    for r in rows:
        if r[0] == winner:
            r[4] = str(int(r[4]) + 1)
            r[3] = str(int(r[3]) + 10)
        if r[0] == loser:
            r[5] = str(int(r[5]) + 1)
            r[3] = str(int(r[3]) - 5)
    write_database(rows)

def record_group_result(winners: list[str], losers: list[str]):
    rows = read_database()
    for r in rows:
        if r[0] in winners:
            r[4] = str(int(r[4]) + 1)
            r[3] = str(int(r[3]) + 0.5)
        if r[0] in losers:
            r[5] = str(int(r[5]) + 1)
            r[3] = str(int(r[3]) - 0.5)
    write_database(rows)