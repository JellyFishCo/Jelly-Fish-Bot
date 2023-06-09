import discord
from discord.ext import commands
import motor.motor_asyncio
# TODO: write custom mongo helper.
# from utils.mongo import Document
import os
import config
import sys

bot = commands.Bot(command_prefix="!", disableEveryone=False, intents=discord.Intents.all(), owner_id=config.owner_id)

@bot.event
async def on_ready():
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----\n")

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="me getting developed"))

    # TODO: Add database.
    # print("Initilized Database\n-----")


def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.command()
async def restart(ctx):
    if ctx.author.id == config.owner_id:
        message = await ctx.send("Bot restarting.")
        restart_bot()
        await message.edit("Bot restarted")
    else:
        await ctx.channel.purge(limit=1)

if __name__ == "__main__":
    # TODO: Add all the documents here and init db connection.
    for file in os.listdir('./cogs'):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")
    bot.run(config.token)