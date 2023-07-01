import discord
from discord.ext import commands
from discord_games.button_games import BetaRockPaperScissors
from discord_games.hangman import Hangman

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="rps", description="Starts up a game of Rock Paper Scissors.")
    async def rps(self, ctx: commands.Context[commands.Bot], player: discord.Option(discord.SlashCommandOptionType.user, required=False, description="f")):
        game = BetaRockPaperScissors(player)
        await game.start(ctx)

    @commands.slash_command(name="hangman", description="Starts up a game of Hangman")
    async def hangman(self, ctx: commands.Context[commands.Bot]):
        game = Hangman()
        await game.start(ctx, delete_after_guess=True)

def setup(bot):
    bot.add_cog(Games(bot))