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


class getScore:
    def __init__(self):
        self.dbPath = os.path.abspath(os.path.join(os.getenv(
            "APPDATA"), os.pardir, "LocalLow\\statespace\\aimlab_tb\\klutch.bytes"))

        self.data = []
        self.readDB()
        self.index = self.getLast()[0]

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
        res = cur.execute("SELECT * FROM TaskData")
        out = res.fetchall()
        self.data = out

    def getLast(self):
        return self.data[-1]


def launchTask(ID):
    url = 'aimlab://workshop?id='
    url += str(ID)
    webbrowser.open(url)


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
