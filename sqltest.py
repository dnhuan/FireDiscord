import sqlite3 as sl

con = sl.connect("employment.db")
cur = con.cursor()
print(type(con))
print(type(cur))

# res = cur.execute(
#     """
#         ---sql
#         INSERT INTO EMPLOYMENT(discordID, discordHandle, isHired, hireCount)
#         SELECT 0000, 'test_subject#0000', 1, 1
#             WHERE NOT EXISTS( SELECT * FROM EMPLOYMENT WHERE discordID = 0000);"""
# ).fetchone()
data = (90, "gas", 1, 1)
con.execute("INSERT INTO EMPLOYMENT VALUES (?,?,?,?)", data)
con.commit()
print("ok")
