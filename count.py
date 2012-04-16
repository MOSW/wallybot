import sqlite3

conn = sqlite3.connect('bucket.sql')

cur = conn.cursor()

cur.execute("""SELECT COUNT(*) FROM `factoids`""")
tempFactoid = cur.fetchone()

print("wally has", tempFactoid[0], "factoids")

conn.close()

input()
