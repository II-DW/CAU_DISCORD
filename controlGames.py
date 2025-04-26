import csv

def ReadDataBase () :
    DataBase = []
    f_R = open('livegames.csv', 'r')
    rdr = csv.reader(f_R)
    for line in list(rdr) :
        DataBase.append(line)
    f_R.close()
    return DataBase

def AppendDataBase (line) :
    f_A = open('livegames.csv', 'a')
    wr = csv.writer(f_A)
    wr.writerow(line)
    f_A.close()

def WriteDataBase (line) :
    f_W = open('livegames.csv', 'w')
    wr = csv.writer(f_W)
    wr.writerows(line)
    f_W.close()

def AddDatabase (GaneName, NumberOfTeam1, NumberOfTeam2) :
    items = [GaneName, NumberOfTeam1, NumberOfTeam2, []]
    DataBase = ReadDataBase()
    for line in DataBase :
        if line[0] == GaneName :
            return False
    AppendDataBase(items)
    return True

def DeleteDatabase (GameName) :
    DataBase = ReadDataBase()
    for line in DataBase :
        if line[0] == GameName :
            DataBase.remove(line)
            WriteDataBase(DataBase)
            return True
    return False

def AddPlayer (GameName, name) :
    import database
    DataBase_User = database.ReadDataBase()
    DataBase = ReadDataBase()
    for line in DataBase_User :
        if line[0] == name :
            for l in DataBase :

                if l[0] == GameName :
                    L = eval(l[3])
                    if len(L) == int(l[1])+int(l[2]) :
                        return False
                    DataBase.remove(l)
                    L = eval(l[3])
                    L.append(line)
                    l[3] = L
                    DataBase.append(l)
                    WriteDataBase(DataBase)
                    return True
            return False
    return False

def DeleteUser (GameName, name) :
    import database
    DataBase_User = database.ReadDataBase()
    for line in DataBase_User :
        if line[0] == name :
            DataBase = ReadDataBase()
            for l in DataBase :
                if l[0] == GameName :              
                    DataBase.remove(l)
                    L = eval(l[3])
                    L.remove(line)
                    l[3] = L
                    
                    DataBase.append(l)
                    WriteDataBase(DataBase)
                    return True
            return False
    return False


