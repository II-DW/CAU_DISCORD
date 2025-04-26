import csv

def ReadDataBase () :
    DataBase = []
    f_R = open('data.csv', 'r')
    rdr = csv.reader(f_R)
    for line in list(rdr) :
        DataBase.append(line)
    f_R.close()
    return DataBase

def AppendDataBase (line) :
    f_A = open('data.csv', 'a')
    wr = csv.writer(f_A)
    wr.writerow(line)
    f_A.close()

def WriteDataBase (line) :
    f_W = open('data.csv', 'w')
    wr = csv.writer(f_W)
    wr.writerows(line)
    f_W.close()

def AddDatabase (name, nickname, tier) :
    items = [name, nickname, tier]
    DataBase = ReadDataBase()
    for line in DataBase :
        if line == items :
            return False
    AppendDataBase(items)
    return True

def DeleteDatabase (name, nickname, tier) :
    items = [name, nickname, tier]
    DataBase = ReadDataBase ()
    for line in DataBase :
        if line == items :
            DataBase.remove(items)
            WriteDataBase(DataBase)
            return True
    return False

def ModifyDatabase (name, nickname, tier, new_name, new_nickname, new_tier) :
    items = [name, nickname, tier]
    new_items = [new_name, new_nickname, new_tier]
    DataBase = ReadDataBase ()
    for line in DataBase :
        if line == items :
            DataBase.remove(items)
            DataBase.append(new_items)
            WriteDataBase(DataBase)
            return True
    return False

    