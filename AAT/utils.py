import yaml
import os
import sqlite3
import webbrowser
import ast


def format_list_as_table(row):
    formatted_string = "| " + " | ".join(map(str, row)) + " |\n"
    return formatted_string


def padNum(num):
    if not isinstance(num, (float, int)):
        raise ValueError("Input must be a float or an int")

    formatted_num = "{:07.4f}".format(float(num))
    return formatted_num


def format_nested_list(nested_list):
    formatted_list = []

    for sublist in nested_list:
        formatted_sublist = []

        for element in sublist:
            formatted_sublist.append(padNum(element))

        formatted_list.append(formatted_sublist)

    return formatted_list


def isMatrix(input_list):
    if not isinstance(input_list, list):
        return False

    if not all(isinstance(sublist, list) for sublist in input_list):
        return False

    if not input_list:
        # Empty list is considered valid
        return True

    length_of_first_sublist = len(input_list[0])

    return all(len(sublist) == length_of_first_sublist for sublist in input_list[1:])


def processMatrix(input_matrix):
    if not isMatrix(input_matrix):
        raise ValueError("Input is not a valid matrix")

    formatted_nested_list = format_nested_list(input_matrix)

    # Applying format_list_as_table to every sublist and concatenating the results
    formatted_table = ''.join(format_list_as_table(sublist)
                              for sublist in formatted_nested_list)

    return formatted_table


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


def saveYAML(config, path):
    path = configPath(path)
    file = open(path, "w")
    yaml.dump(config, file)
    file.close()
    print("YAML file saved.")


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


@devBlock
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


def main():
    print('theres nothing here...')


if __name__ == '__main__':
    main()
