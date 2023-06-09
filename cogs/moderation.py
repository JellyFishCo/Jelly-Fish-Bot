import discord
from discord.ext import commands
from datetime import date
import time
today = date.today()
import datetime
from utils.util import Pag
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="ban", description="Bans the specified user for the specified reason.")
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.SlashCommandOptionType.user, reason : discord.Option(str, required=False)):
        await ctx.defer()
        if reason == None:
            reason = "No Reason Specified"
        embed = discord.Embed(title="Member Banned", description="I have successfully banned the specified member", color=discord.Color.green())
        embed.add_field(name="Member Name: ", value=f"{member.mention}", inline=False)
        embed.add_field(name="Reason: ", value=f"{reason}", inline=False)
        embed.set_footer(text=f"Requested By: {ctx.author.name}", icon_url=ctx.author.avatar)
        memberEmbed = discord.Embed(title="You have been banned", description=f"You have been banned from the server {ctx.guild.name}", color=discord.Color.red())
        memberEmbed.add_field(name="Responsible Moderator: ", value=f"{ctx.author.mention}", inline=False)
        memberEmbed.add_field(name="Reason: ", value=f"{reason}", inline=False)
        memberEmbed.add_field(name="Date: ", value=f"{today.day}-{today.month}-{today.year}", inline=False)
        ban_data = {"reason": reason, "timestamp": time.time(), "moderator": ctx.author.id, "guild_id": ctx.guild.id, "user_id": member.id}
        await self.bot.bans.insert(ban_data)
        await ctx.followup.send(embed=embed)
        try:
            await member.send(embed=memberEmbed)
            await member.ban(reason=reason)
        except discord.HTTPException:
            await member.ban(reason=reason)
            await ctx.send("Member has not been notified about their ban due to their DMs being disabled.")
        
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to run this command!\nYou are missing the `ban_members` permission.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I do not have the right permissions!\nI am missing the `ban_members` permission.")
        else:
            print(error)

    async def get_banned_users(ctx: discord.AutocompleteContext):
        banned_users = ctx.interaction.guild.bans()
        if banned_users == None:
            return
        choices = []
        async for ban_entry in banned_users:
            user = ban_entry.user
            choice = f"{user.name} ({user.id})"
            choices.append(choice)
        return choices
    
    @commands.slash_command(name="unban", description="Unbans the specified user.")
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_banned_users))):
        try:
            await ctx.defer()
            user_id = int(user.split("(")[-1].split(")")[0])
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            embed = discord.Embed(title="Successfully Unbanned User.", description=f"I have successfully unbanned {user.name} for you!", color=discord.Color.green())
            await ctx.followup.send(embed=embed)
        except Exception as e:
            await ctx.respond(f"Error unbanning user: ```\n{e}```")
            print(e)
    
    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to run this command!\nYou are missing the `ban_members` permission.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I do not have the right permissions!\nI am missing the `ban_members` permission.")
        else:
            print(error)

def setup(bot):
    bot.add_cog(Moderation(bot))