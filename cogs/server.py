import discord
from discord.ext import commands


class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="setupverify", description="Sets up the verification command.")
    @commands.has_guild_permissions(manage_guild=True)
    async def setupverify(self, ctx, channel: discord.SlashCommandOptionType.channel, role: discord.SlashCommandOptionType.role, message: discord.Option(str, required=True, description="The message you want to be sent into the channel")):
        await ctx.defer()
        verify_filter = {"guild_id": ctx.guild.id}
        data = {"channelid": channel.id, "role_id": role.id, "guild_id": ctx.guild.id, "message": message}
        doesExist = await self.bot.verify.find_by_custom(verify_filter)
        if doesExist:
            await self.bot.verify.delete_by_custom(verify_filter)
            await self.bot.verify.insert(data)
        else:
            await self.bot.verify.insert(data)
        await ctx.followup.send("Verification has been setup! :heavy_check_mark:")

    @commands.slash_command(name="setupwelcome", description="Sets up welcome messages.")
    @commands.has_guild_permissions(manage_guild=True)
    async def setupwelcome(self, ctx, channel: discord.SlashCommandOptionType.channel, message: discord.Option(str, required=True, description="The message you want to be sent into the channel. Put (member) anywhere for it to ping the member.")):
        await ctx.defer()
        welcome_filter = {"guild_id": ctx.guild.id}
        data = {"channelid": channel.id, "message": message}
        doesExist = await self.bot.welcome.find_by_custom(welcome_filter)
        if doesExist:
            await self.bot.welcome.delete_by_custom(welcome_filter)
            await self.bot.welcome.insert(data)
        else:
            await self.bot.welcome.insert(data)
        await ctx.followup.send("Welcome messages has been setup! :heavy_check_mark:")

def setup(bot):
    bot.add_cog(Server(bot))