import sqlite3

con = sqlite3.connect('klutch.bytes')
cur = con.cursor()
res = cur.execute("SELECT taskName, score FROM TaskData")
out = res.fetchall()
print(out)
