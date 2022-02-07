# This bot fires people
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

import sqlite3 as sl
import os
from dotenv import load_dotenv
from Person import Person

load_dotenv()
TOKEN = os.getenv("FIRE_BOT_TOKEN")
TEST_SERVER_ID = 933226891970764821
SERVER_ID_205 = 929888989765312512

# Bot setup
SERVER_ID = TEST_SERVER_ID
SERVER_ID_LIST = [TEST_SERVER_ID, SERVER_ID_205]
con = sl.connect("employment.db")
cur = con.cursor()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(bot, sync_commands=True)

# Main driver code
@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))

    # Create schema
    cur.execute(
        """ 
        ---sql
        CREATE TABLE IF NOT EXISTS EMPLOYMENT(
            discordID INTEGER NOT NULL PRIMARY KEY,
            discordHandle TEXT NOT NULL,
            isHired INTEGER NOT NULL,
            fireCount INTEGER NOT NULL
        ); """
    )

    # Insert placeholder
    cur.execute(
        """
        ---sql
        INSERT INTO EMPLOYMENT(discordID, discordHandle, isHired, fireCount) 
        SELECT 0000, 'test_subject#0000', 1, 0
            WHERE NOT EXISTS( SELECT * FROM EMPLOYMENT WHERE discordID = 0000);"""
    )

    con.commit()


@slash.slash(
    name="fire",
    description="Fire employee",
    options=[
        {
            "name": "employee_name",
            "description": "name of the employee you want to fire",
            "type": 6,
            "required": True,
        },
        {
            "name": "reason",
            "description": "reason for firing",
            "type": 3,
            "required": False,
        },
    ],
    guild_ids=SERVER_ID_LIST,
)
async def fire(ctx: SlashContext, employee_name: discord.User, reason: str = ""):
    employer: Person = Person(con, ctx.author)
    employee: Person = Person(con, employee_name)

    if employer.discordID == employee.discordID:
        await ctx.send("You can't fire yourself! <:kekw:938670241846796338>")
        return

    if employer.isHired == 0:
        await ctx.send("You are unemployed, you can't fire anybody")
        return

    if employee.isHired == 0:
        message = "**{0}** was already fired, you can't fire **{0}** anymore!".format(
            employee.display_name
        )
        await ctx.send(message)
        return

    # Else
    employee.beFired()
    if reason == "":
        reason = "no reason"
    message = "**{0}** just fired **{1}** for *{2}*".format(
        employer.display_name, employee.display_name, reason
    )
    await ctx.send(message)


@slash.slash(
    name="hire",
    description="Hire employee",
    options=[
        {
            "name": "employee_name",
            "description": "name of the employee you want to hire",
            "type": 6,
            "required": True,
        }
    ],
    guild_ids=SERVER_ID_LIST,
)
async def hire(ctx: SlashContext, employee_name: discord.User):
    employer: Person = Person(con, ctx.author)
    employee: Person = Person(con, employee_name)

    if employer.discordID == employee.discordID:
        await ctx.send("You can't hire yourself! <a:kekwlaugh:940043484805627924>")
        return

    if employer.isHired == 0:
        message = (
            "You are unemployed, you can't hire anybody. You can't even get a job!"
        )
        await ctx.send(message)
        return

    if employee.isHired == 1:
        message = "**{0}** was already hired".format(employee.display_name)
        if employer.isHired == 0:
            message = message + ", unlike ***you***!"
        await ctx.send(message)
        return

    # Else
    employee.beHired()
    message = "**{0}** just hired **{1}**".format(
        employer.display_name, employee.display_name
    )
    await ctx.send(message)


@slash.slash(
    name="status",
    description="Display employment status",
    options=[
        {
            "name": "employee_name",
            "description": "name of the employee",
            "type": 6,
            "required": True,
        }
    ],
    guild_ids=SERVER_ID_LIST,
)
async def status(ctx: SlashContext, employee_name: discord.Member):
    employee: Person = Person(con, employee_name)

    # Status
    message = "**{0}** is currently ".format(employee.display_name)
    if employee.isHired == 1:
        message = message + "*employed*. "
    else:
        message = message + "*unemployed*. "

    # Fire count
    message = message + "**{0}** was fired {1} time".format(
        employee.display_name, employee.fireCount
    )

    # Plural for time(s)
    if employee.fireCount >= 2:
        message = message + "s"

    await ctx.send(message)


@slash.slash(
    name="leaderboard",
    description="Display unemployment leaderboard",
    guild_ids=SERVER_ID_LIST,
)
async def leaderboard(ctx: SlashContext):
    cur = con.cursor()
    database_result = cur.execute(
        "SELECT * FROM EMPLOYMENT ORDER BY fireCount DESC LIMIT 5"
    ).fetchall()
    leaderboard_text = leaderboard_parser(ctx, database_result)
    embed = discord.Embed(
        title="Unemployment Leaderboard", description=leaderboard_text
    )
    await ctx.send(embed=embed)


def leaderboard_parser(ctx: SlashContext, database_result):
    guild = ctx.guild

    res = ""

    for idx, val in enumerate(database_result):
        # Extract info
        id = int(val[0])
        try:
            member: discord.Member = guild.get_member(id)
            name = member.display_name
        except:
            continue
        fireCount = val[3]

        # if count == 0 then skip
        if fireCount == 0:
            continue

        res = res + "{0}. {1} - {2} time".format(idx + 1, name, fireCount)
        if fireCount >= 2:
            res = res + "s"  # plural for times
        res = res + "\n"

    return res


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("Can't find that person.")
    else:
        print(error)
        await ctx.send("I don't undestand that.")


bot.run(TOKEN)
