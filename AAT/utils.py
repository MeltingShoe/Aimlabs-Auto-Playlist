import yaml
import os
import sqlite3
import webbrowser
import ast


def saveYAML(config, path):
    path = os.path.abspath(os.path.join(
        os.getcwd(), os.pardir, 'config', path))
    file = open(path, "w")
    yaml.dump(config, file)
    file.close()
    print("YAML file saved.")


def openYAML(path):
    path = os.path.abspath(os.path.join(
        os.getcwd(), os.pardir, 'config', path))
    with open(path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


class rawDB:
    def __init__(self, resetPoint=0):
        self.dbPath = os.path.abspath(os.path.join(os.getenv(
            "APPDATA"), os.pardir, "LocalLow\\statespace\\aimlab_tb\\klutch.bytes"))

        self.data = []
        self.readDB()
        self.index = self.getLast()[0]
        self.lastScore = resetPoint
        self.unreadScores = []
        self.allScores = []

    def getInitScores(self):
        self.readDB()
        names = []
        for run in self.data:
            name = run[3]
            if 'meltingshoe' in name:
                y = run[12]
                y = ast.literal_eval(y)
                out = {
                    'ID': run[0],
                    'name': name,
                    'score': run[4],
                    'data': y,
                    'hits': y['hitsTotal'],
                    'misses': y['missesTotal']
                }
                names.append(out)
        return names

    def addScore(self, score):
        self.allScores.append(score)
        self.unreadScores.append(score)

    def score(self):
        self.readDB()
        newIndex = self.getLast()[0]
        isNew = newIndex > self.index
        if isNew:
            self.index = newIndex
        x = self.getLast()

        y = x[12]
        y = ast.literal_eval(y)
        out = {
            'name': x[3],
            'score': x[4],
            'data': y,
            'hits': y['hitsTotal'],
            'misses': y['missesTotal']
        }

        return isNew, out

    def readDB(self):
        con = sqlite3.connect(self.dbPath)
        cur = con.cursor()
        # right here make it select things after last ID and update ID
        res = cur.execute("SELECT * FROM TaskData")
        out = res.fetchall()
        self.data = out
        return out

    def getLast(self):
        return self.data[-1]

    def checkValid(self, score):
        name = score[3]
        if 'meltingshoe' in name:
            return True
        else:
            return False

    def getUnprocessedScores(self):
        self.readDB()  # eventually change this to just select items over a certain ID, prolly not hard with SQL. Could be part of the readDB()
        while self.lastScore < len(self.data):
            score = self.data[self.lastScore]
            valid = self.checkValid(score)
            if valid:
                self.addScore(score)
            self.lastScore += 1

    def getNextScore(self):
        self.getUnprocessedScores()
        if len(self.unreadScores) > 0:
            return self.format(self.unreadScores.pop(0))
        else:
            return False

    def format(self, score):
        x = score
        y = x[12]
        y = ast.literal_eval(y)
        out = {
            'name': x[3],
            'score': x[4],
            'data': y,
            'hits': y['hitsTotal'],
            'misses': y['missesTotal']
        }
        return out


class scoreDB:
    def __init__(self, names, resetPoint=0):
        self.db = rawDB(resetPoint=resetPoint)
        self.taskNames = names
        self.allScores = []
        self.unreadScores = []
        self.unprocessedScores = []
        self.processScores()

    def __call__(self):
        return self.getNextScore()

    def addScore(self, score):
        self.allScores.append(score)
        self.unreadScores.append(score)

    def processScores(self):

        while True:
            score = self.db.getNextScore()
            if score == False:
                break
            entryName = score['name']
            for taskName in self.taskNames:
                if taskName == entryName:
                    self.addScore(score)
                    break

    def getNextScore(self):
        self.processScores()
        if len(self.unreadScores) > 0:
            return self.unreadScores.pop(0)
        else:
            return False


def launchTask(ID):
    url = 'aimlab://workshop?id='
    url += str(ID)
    # webbrowser.open(url)


def YN(prompt):
    if type(prompt) != str:
        print('bad prompt type')
        exit()
    print(prompt, '(Y/N)')
    a = input()
    a = a.casefold()
    if a == 'y' or a == 'yes':
        return True
    if a == 'n' or a == 'no':
        return False
    print('invalid input. Enter Y or N')
    out = YN(prompt)
    return out


def main():
    sb = rawDB()
    while True:
        data = sb.getNextScore()
        print(data)
        if data == False:
            break
    print('broke')
    names = ['CsLevel.meltingshoe.1W6TPOP .S6BRCL']
    betterDB = scoreDB(names)
    while True:
        data = betterDB.getNextScore()
        print(data)
        if data == False:
            break
    print('broke again')


if __name__ == '__main__':
    main()
