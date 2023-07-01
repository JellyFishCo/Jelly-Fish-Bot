import discord
from discord.ext import commands
import config

class BotCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="botstatus", description="Sets the bots status.")
    async def botstatus(self, ctx, status: str):
        if ctx.author.id == config.owner_id:
            embed = discord.Embed(title="Bot Status", description="The current status of the bot.", color=discord.Color.blue())
            embed.add_field(name="Current Status: ", value=f"{status}", inline=True)
            channel = self.bot.get_channel(1110624933052162109)
            await channel.purge(limit=1)
            await channel.send(embed=embed)
            await ctx.respond("Task Completed", delete_after=2)
        else:
            await ctx.respond("You are not the owner of the bot!")

    @commands.slash_command(name="botupdate", description="Adds a bot update to the bot update channel.")
    async def botupdate(self, ctx, title: str, description: str):
        if ctx.author.id == config.owner_id:
            embed = discord.Embed(title=title, description=description, color=discord.Color.green())
            channel = self.bot.get_channel(1110624933052162108)
            await channel.send(embed=embed)
            await ctx.respond("Task Completed", delete_after=2)
        else:
            await ctx.respond("You are not the owner of the bot!")

def setup(bot: commands.Bot):
    bot.add_cog(BotCommands(bot))