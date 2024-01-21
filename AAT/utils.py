import yaml
import os
import sqlite3
import webbrowser
import ast
from logger import log, logLevel, debug, info, warning, error, critical, logInit


@log
def configPath(path):
    exists = os.path.isfile(os.path.abspath(os.path.join(
        os.getcwd(), os.pardir, 'config', path)))
    if exists:
        path = os.path.abspath(os.path.join(
            os.getcwd(), os.pardir, 'config', path))
    else:
        path = os.path.abspath(os.path.join(
            os.getcwd(), os.pardir, 'config/modelConfig', path))
    return path


@log
def saveYAML(config, path):
    path = configPath(path)
    file = open(path, "w")
    yaml.dump(config, file)
    file.close()
    print("YAML file saved.")


@log
def openYAML(path):
    path = configPath(path)
    with open(path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


config = openYAML('devConfig.yaml')
block = config['blockTaskLaunch']
confirm = config['confirmToRunBlockedFunctions']


@log
def devBlock(func):
    if not block:
        return func
    if not confirm:
        def nop(*args, **kwargs):
            pass
        return nop

    def wrap(*args, **kwargs):
        if YN('Function blocked, run function?'):
            func(*args, **kwargs)
    return wrap


class rawDB:
    @logInit
    def __init__(self, resetPoint=0):
        self.dbPath = os.path.abspath(os.path.join(os.getenv(
            "APPDATA"), os.pardir, "LocalLow\\statespace\\aimlab_tb\\klutch.bytes"))

        self.data = []
        self.readDB()
        self.index = self.getLast()[0]
        self.lastScore = resetPoint
        self.unreadScores = []
        self.allScores = []

    @log
    def getInitScores(self):
        self.readDB()
        names = []
        for run in self.data:
            name = run[3]
            if self.checkValid(run):
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

    @log
    def addScore(self, score):
        self.allScores.append(score)
        self.unreadScores.append(score)

    @log
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

    @log
    def readDB(self):
        con = sqlite3.connect(self.dbPath)
        cur = con.cursor()
        # right here make it select things after last ID and update ID
        res = cur.execute("SELECT * FROM TaskData")
        out = res.fetchall()
        self.data = out
        return out

    @log
    def getLast(self):
        return self.data[-1]

    @log
    def checkValid(self, score):
        name = score[3]
        if ('meltingshoe' in name) or ('hartrean' in name):
            return True
        else:
            return False

    @log
    def getUnprocessedScores(self):
        self.readDB()  # eventually change this to just select items over a certain ID, prolly not hard with SQL. Could be part of the readDB()
        while self.lastScore < len(self.data):
            score = self.data[self.lastScore]
            if self.checkValid(score):
                self.addScore(score)
            self.lastScore += 1

    @log
    def getNextScore(self):
        self.getUnprocessedScores()
        if len(self.unreadScores) > 0:
            return self.format(self.unreadScores.pop(0))
        else:
            return False

    @log
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

    @log
    def __call__(self):
        return self.getNextScore()

    @log
    def addScore(self, score):
        self.allScores.append(score)
        self.unreadScores.append(score)

    @log
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

    @log
    def getNextScore(self):
        self.processScores()
        if len(self.unreadScores) > 0:
            a = self.unreadScores.pop(0)
            return a
        else:
            return False


@devBlock
def launchTask(ID):
    url = 'aimlab://workshop?id='
    url += str(ID)
    webbrowser.open(url)


@log
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


def weightedSelect(inputList):
    total = 0
    for item in inputList:
        total += item[0]
    key = random.uniform(0, total)
    for item in inputList:
        if key < item[0]:
            return item[1]
        key -= item[0]
    raise Exception('selection failed somehow')


def main():
    print('theres nothing here...')


if __name__ == '__main__':
    main()
