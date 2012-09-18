## Copyright 2009-2012 Joey
## 
## Jobot is released under Affero GPL. Please read the license before continuing.
## 
## The latest source can be found here:
##	 https://github.com/MOSW/wallybot
##
import sqlite3

conn = sqlite3.connect('bucket.sql')

cur = conn.cursor()

cur.execute("""SELECT COUNT(*) FROM `factoids`""")
tempFactoid = cur.fetchone()

print("wally has", tempFactoid[0], "factoids")

conn.close()

input()
