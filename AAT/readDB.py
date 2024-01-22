import os
import sqlite3
from utils import openYAML
from logger import log, logLevel, debug, info, warning, error, critical


class readAimlabsDB:
    @log
    def __init__(self):
        config = openYAML('userConfig.yaml')
        self.dbPath = os.path.abspath(os.path.join(os.getenv(
            "APPDATA"), os.pardir, config['dbPath']))

    @log
    def __call__(self):
        return self.readDB()

    @log
    def readDB(self):
        testID = 1500
        con = sqlite3.connect(self.dbPath)
        cur = con.cursor()
        res = cur.execute(
            "SELECT taskId, klutchId, createDate, taskName, score, performance FROM TaskData WHERE taskId > " + str(testID) + " AND taskName LIKE '%meltingshoe%' OR taskId > " + str(testID) + " AND taskName LIKE '%hartrean%'")
        out = res.fetchall()
        warning(out)
        self.data = out
        return out


def main():
    db = readAimlabsDB()
    out = db.readDB()
    for item in out:
        warning(item)


if __name__ == '__main__':
    main()
