import sqlite3 as sl
import discord


class Person:
    def __init__(self, con: sl.Connection, discordProfile: discord.Member) -> None:
        # set db connection
        self.con = con
        self.discordProfile = discordProfile
        self.display_name = discordProfile.display_name

        # Query DB
        cur = con.cursor()
        result = cur.execute(
            "SELECT * FROM EMPLOYMENT WHERE discordID = ?", (discordProfile.id,)
        ).fetchone()

        # Insert if not existed
        if result is None:
            result = (discordProfile.id, discordProfile.display_name, 1, 0)
            cur.execute("INSERT INTO EMPLOYMENT VALUES (?,?,?,?)", result)

        # Map db data to object
        (self.discordID, self.discordHandle, self.isHired, self.fireCount) = result

        # Commit DB
        con.commit()

    def beFired(self):
        with self.con as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE EMPLOYMENT SET isHired = ?, fireCount = ? WHERE discordID = ?",
                (0, self.fireCount + 1, self.discordID),
            )
            con.commit()

    def beHired(self):
        with self.con as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE EMPLOYMENT SET isHired = ? WHERE discordID = ?",
                (1, self.discordID),
            )
            con.commit()

