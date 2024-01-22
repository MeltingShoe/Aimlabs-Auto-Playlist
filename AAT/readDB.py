import sqlite3
from utils import openYAML
from logger import log, logLevel, debug, info, warning, error, critical
import os


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
        testID = 1700
        con = sqlite3.connect(self.dbPath)
        cur = con.cursor()
        res = cur.execute(
            "SELECT taskId, klutchId, createDate, taskName, score, performance FROM TaskData WHERE taskId > 1500 AND taskName LIKE '%meltingshoe%' OR taskId > 1500 AND taskName LIKE '%hartrean%'")
        out = res.fetchall()
        warning(out)
        self.data = out
        return out


def main():
    db = readAimlabsDB()

    for item in db():
        warning(item)


if __name__ == '__main__':
    main()
