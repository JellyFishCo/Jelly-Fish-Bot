import discord
from discord.ext import commands
import motor.motor_asyncio
from utils.mongo import Document
import os
import config
import sys
import asyncio
import string
import random

bot = commands.Bot(command_prefix="!", disableEveryone=False, intents=discord.Intents.all(), owner_id=config.owner_id)

class VerifyView(discord.ui.View):
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def button_callback(self, button, interaction: discord.Interaction):
        bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(config.mongo_url))
        bot.db = bot.mongo["development"]
        verify = Document(bot.db, "verify")
        for guild in bot.guilds:
            verify_filter = {"guild_id": guild.id}
            data = await verify.find_by_custom(verify_filter)
            if data:
                print("placeholder")
                role_id = data.get('role_id')
                role = discord.utils.get(guild.roles, id=role_id)
                try:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message("Verification Complete! :white_check_mark:", ephemeral=True)
                except discord.DiscordException as e:
                    await interaction.response.send_message(f"An error has occured! I appears my role is lower than the role that is trying to be given. Please send this error to the developer. ```{e}```")
            else:
                print("No data found.")

@bot.event
async def on_ready():
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----\n")

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="me getting developed"))

    print("Initilized Database\n-----")
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(config.mongo_url))
    bot.db = bot.mongo["development"]
    verify = Document(bot.db, "verify")
    for guild in bot.guilds:
        verify_filter = {"guild_id": guild.id}
        data = await verify.find_by_custom(verify_filter)
        if data:
            channel_id = data.get('channelid')
            channel = bot.get_channel(channel_id)
            message = data.get('message')
            embed = discord.Embed(title="Server Verification", description=message, color=discord.Color.blue())
            #await channel.purge(limit=1)
            #await channel.send(embed=embed, view=VerifyView(timeout=None))
        else:
            print("No data found.")


def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)

async def save_welcome_message(data, guild_id):
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(config.mongo_url))
    bot.db = bot.mongo["development"]
    welcome = Document(bot.db, "welcome")
    welcome_filter = {"guild_id": guild_id}
    doesExist = await welcome.find_by_custom(welcome_filter)
    print(doesExist)
    if doesExist:
        await welcome.delete_by_custom(welcome_filter)
        await welcome.insert(data)
    else:
        await welcome.insert(data)


async def save_verification(data, guild_id):
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(config.mongo_url))
    bot.db = bot.mongo["development"]
    verify = Document(bot.db, 'verify')
    verify_filter = {"guild_id": guild_id}
    doesExist = await verify.find_by_custom(verify_filter)
    print(doesExist)
    if doesExist:
        await verify.delete_by_custom(verify_filter)
        await verify.insert(data)
    else:
        await verify.insert(data)


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
    print(member.guild.id)
    data = await welcome.find_by_custom(welcome_filter)
    if data:
        channel_id = data.get('channelid')
        message = data.get('message')
        if '(member)' in message:
            newmessage = message.replace('(member)', member.mention)
        else:
            newmessage = message
        channel = bot.get_channel(channel_id)
        await channel.send(newmessage)

@bot.event
async def on_message_delete(message):
    if len(message.mentions) == 0:
        return
    else:
        ghostping = discord.Embed(title=f'GhostPing', color=discord.Color.blue(), timestamp=message.created_at)
        ghostping.add_field(name='**Name:**', value=f'{message.author.mention}')
        ghostping.add_field(name='**Message:**', value=f'{message.content}')
        ghostping.set_thumbnail(
            url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTXtzZMvleC8FG1ExS4PyhFUm9kS4BGVlsTYw&usqp=CAU')
        try:
            await message.channel.send(embed=ghostping)
        except discord.Forbidden:
            try:
                await message.author.send(embed=ghostping)
            except discord.Forbidden:
                return
if __name__ == "__main__":
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(config.mongo_url))
    bot.db = bot.mongo["development"]
    bot.punishments = Document(bot.db, "punishments")
    bot.suggest = Document(bot.db, "suggest")
    bot.verify = Document(bot.db, "verify")
    bot.welcome = Document(bot.db, "welcome")
    for file in os.listdir('./cogs'):
        if file.endswith(".py") and not file.startswith("_") :
            bot.load_extension(f"cogs.{file[:-3]}")
    bot.run(config.dev_token)