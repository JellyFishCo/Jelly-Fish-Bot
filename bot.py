import discord
from discord.ext import commands
import motor.motor_asyncio
from utils.mongo import Document
import os
import config
import sys
import asyncio

bot = commands.Bot(command_prefix="!", disableEveryone=False, intents=discord.Intents.all(), owner_id=config.owner_id)

@bot.event
async def on_ready():
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----\n")

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="me getting developed"))

    print("Initilized Database\n-----")


def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.command()
async def restart(ctx):
    if ctx.author.id == config.owner_id:
        await ctx.send("Bot restarting...")
        restart_bot()
        print(f"Bot restarted requested by: {ctx.author.name} : {ctx.author.id}")
    else:
        await ctx.channel.purge(limit=1)

if __name__ == "__main__":
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(config.mongo_url))
    # TODO: This text field should change from "development" to "production" when released.
    bot.db = bot.mongo["development"]
    bot.bans = Document(bot.db, "bans")
    bot.kicks = Document(bot.db, "kicks")
    bot.warns = Document(bot.db, "warns")
    bot.suggest = Document(bot.db, "suggest")
    for file in os.listdir('./cogs'):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")
    bot.run(config.token)