import sqlite3
import os
from functionGenerator import func as func

exampleDefinition2 = {
    'inputRanges': [-1, -0.3, 0, 0.3, 1],
    'outputRanges': [0.05, 0.7, 1, 1.5, 1.8],
    'scales': [0, -1, 1, -1, 1]
}

f = func(exampleDefinition2)

f.plotFunction()

AIMLAB_DB_PATH = os.path.abspath(os.path.join(os.getenv(
    "APPDATA"), os.pardir, "LocalLow\\statespace\\aimlab_tb\\klutch.bytes"))

con = sqlite3.connect(AIMLAB_DB_PATH)
cur = con.cursor()
res = cur.execute("SELECT * FROM TaskData")
out = res.fetchall()
print(out)
