import sqlite3
from utils import openYAML, saveYAML
import os

config = openYAML('userConfig.yaml')
dbPath = os.path.abspath(os.path.join(os.getenv(
    "APPDATA"), os.pardir, config['dbPath']))
con = sqlite3.connect(dbPath)
cur = con.cursor()
res = cur.execute(
    "SELECT * FROM TaskData WHERE taskName LIKE '%meltingshoe%'")
out = res.fetchall()
data = []
for i in out:
    row = []
    for line in i:
        row.append(line)
    data.append(row)
saveYAML(data, 'bussinData.yaml')
