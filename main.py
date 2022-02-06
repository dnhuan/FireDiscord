# This bot fires people
from email import message
from click import option
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
SERVER_ID_205 = 933226891970764821

# Bot setup
SERVER_ID = TEST_SERVER_ID
con = sl.connect("employment.db")
cur = con.cursor()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(
    bot, sync_commands=True, debug_guild=SERVER_ID, delete_from_unused_guilds=True,
)

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
            hireCount INTEGER NOT NULL
        ); """
    )

    # Insert placeholder
    cur.execute(
        """
        ---sql
        INSERT INTO EMPLOYMENT(discordID, discordHandle, isHired, hireCount) 
        SELECT 0000, 'test_subject#0000', 1, 1 
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
    guild_ids=[SERVER_ID],
)
async def fire(ctx: commands.Context, employee_name: discord.User, reason: str = ""):
    print(employee_name.id)
    print(reason)
    employer: Person = Person(con, ctx.author)
    employee: Person = Person(con, employee_name)

    if employer.discordID == employee.discordID:
        await ctx.send("You can't fire yourself!")
        return

    pass

    # print(type(employee.id))
    # reason = " ".join(reason) if len(reason) != 0 else "no reason"
    # await ctx.send(
    #     "{0} fired {1} for {2}".format(ctx.author.mention, employee.mention, reason)
    # )


@bot.command()
async def hire(ctx, *arg):
    await ctx.send(arg)


@slash.slash(
    name="count",
    description="Display fire count",
    options=[
        {
            "name": "employee_name",
            "description": "name of the employee",
            "type": 6,
            "required": True,
        }
    ],
    guild_ids=[SERVER_ID],
)
async def count(ctx: commands.Context, employee_name: discord.Member):
    employee: Person = Person(con, employee_name)

    message = "**{0}** was fired {1} time".format(
        employee.discordProfile.display_name, employee.hireCount - 1
    )

    # Plural for time(s)
    if employee.hireCount > 1:
        message = message + "s"

    await ctx.send(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("Can't find that person")
    else:
        print(error)


bot.run(TOKEN)
