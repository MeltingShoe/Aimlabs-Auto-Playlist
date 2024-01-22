import os
import sqlite3
from utils import openYAML
from logger import log, logLevel, debug, info, warning, error, critical
import ast
import time


class readAimlabsDB:
    @log
    def __init__(self):
        config = openYAML('userConfig.yaml')
        self.dbPath = os.path.abspath(os.path.join(os.getenv(
            "APPDATA"), os.pardir, config['dbPath']))
        mainConfig = openYAML('config.yaml')
        # this is how much of the db we've already parsed.
        self.readIndex = mainConfig['resetPoint']
        self.con = sqlite3.connect(self.dbPath)
        self.cur = self.con.cursor()
        self.scoreData = {}

    @log
    def __call__(self, nameList, startID=0):
        return self.getScores(nameList, startID)

    @log
    def getLastID(self):
        res = self.cur.execute(
            "SELECT taskId FROM TaskData ORDER BY taskId DESC LIMIT 1")
        out = res.fetchall()[0][0]
        return out

    @log
    def getScores(self, nameList, startID=0):
        lastID = self.getLastID()
        if lastID > self.readIndex:
            rawScores = self.readDB(nameList)
            newScores = []
            for score in rawScores:
                score = self.packageOutput(score)
                key = score['taskId']
                newScores.append((key, score))
            newDict = dict(newScores)
            allScores = self.scoreData | newDict
            self.scoreData = allScores
        if startID > 0:
            keysList = list(self.scoreData.keys())
            unreadKeys = [i for i in keysList if i > startID]
            out = {}
            for key in unreadKeys:
                out[key] = self.scoreData[key]
            return out
        return {'scores': self.scoreData, 'lastID': lastID}

    @log
    def list2list(self, nameList):  # need to convert our namelist to a string
        nameList = str(nameList)
        nameList = nameList[1:-1]
        return '(' + nameList + ')'

    @log
    def readDB(self, nameList):
        nameList = self.list2list(nameList)
        columns = 'taskId, klutchId, createDate, taskName, score, performance'
        query = "SELECT %s FROM TaskData WHERE taskId > %s AND taskName IN %s" % (
            columns, self.readIndex, nameList)
        res = self.cur.execute(query)
        out = res.fetchall()
        self.readIndex = self.getLastID()
        return out

    @log
    def packageOutput(self, row):
        performance = ast.literal_eval(row[5])
        out = {'taskId': row[0], 'klutchId': row[1], 'createDate': row[2], 'taskName': row[3], 'score': row[4], "shotsTotal": performance['shotsTotal'], "hitsTotal": performance['hitsTotal'], "missesTotal": performance['missesTotal'], "avgDist": performance['avgDist'],
               "damageTotal": performance['damageTotal'], "timePerKill": performance['timePerKill'], "killTotal": performance['killTotal'], "targetsTotal": performance['targetsTotal'], "accTotal": performance['accTotal'], "headshots": performance['headshots'], "bodyshots": performance['bodyshots']}
        return out


def main():
    db = readAimlabsDB()
    out = db(startID=1570)
    for item in out:
        warning(out[item])


if __name__ == '__main__':
    main()
