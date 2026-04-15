import sqlite3
conn=sqlite3.connect(chr(101)+chr(120)+chr(97)+chr(109)+chr(115)+chr(112)+chr(104)+chr(101)+chr(114)+chr(101)+chr(46)+chr(100)+chr(98))
cur=conn.cursor()
print("=== USERS ===")
cur.execute("SELECT user_id,name,email,role FROM Users")
for r in cur.fetchall(): print(r)
