import discord
from discord.ext import commands


class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='verify', description="Run this command to verify yourself.")
    async def verify(self, ctx):
        verify_filter = {'guild_id': ctx.guild.id}
        verify_data = await self.bot.verify.find_by_custom(verify_filter)
        if verify_data:
            role_id = verify_data.get('role_id')
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            await ctx.author.add_roles(role)
            await ctx.author.send(f"You have been verified in {ctx.guild.name}.")
            await ctx.respond("Task completed.", delete_after=3)


def setup(bot):
    bot.add_cog(Server(bot))