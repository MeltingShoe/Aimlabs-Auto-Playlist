import sqlite3
import os

AIMLAB_DB_PATH = os.path.abspath(os.path.join(os.getenv(
    "APPDATA"), os.pardir, "LocalLow\\statespace\\aimlab_tb\\klutch.bytes"))

con = sqlite3.connect(AIMLAB_DB_PATH)
cur = con.cursor()
res = cur.execute("SELECT * FROM TaskData")
out = res.fetchall()
print(out)
