# This bot fires people
import string
from tokenize import String
import discord
from discord.ext import commands

import sqlite3 as sl
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("FIRE_BOT_TOKEN")
TEST_SERVER_ID = 933226891970764821
SERVER_ID_205 = 929888989765312512

# Bot setup
SERVER_ID = TEST_SERVER_ID
con = sl.connect("employment.db")
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix="!", intents=intents)

# Main driver code
@bot.command()
async def fire(ctx, *, employee: discord.Member, reason: str):
    await ctx.send("Fired {0}".format(employee.display_name))


@bot.command()
async def hire(ctx, *arg):
    await ctx.send(arg)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("Can't find that person")


bot.run(TOKEN)
