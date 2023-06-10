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

async def save_welcome_message(data):
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(config.mongo_url))
    bot.db = bot.mongo["development"]
    welcome = Document(bot.db, "welcome")
    await welcome.insert(data)


@bot.command()
async def restart(ctx):
    if ctx.author.id == config.owner_id:
        await ctx.send("Bot restarting...")
        restart_bot()
        print(f"Bot restarted requested by: {ctx.author.name} : {ctx.author.id}")
    else:
        await ctx.channel.purge(limit=1)

@bot.event
async def on_member_join(member):
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(config.mongo_url))
    bot.db = bot.mongo["development"]
    welcome = Document(bot.db, "welcome")
    welcome_filter = {'guild_id': member.guild.id}
    data = await welcome.find_by_custom(welcome_filter)#
    if data:
        channel_id = data.get('channelid')
        message = data.get('message')
        if '(member)' in message:
            newmessage = message.replace('(member)', member.mention)
        else:
            newmessage = message
        channel = bot.get_channel(channel_id)
        await channel.send(newmessage)
    else:
        return

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