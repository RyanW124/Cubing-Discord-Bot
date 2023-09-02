from nextcord import Interaction
from nextcord.ext import commands
import nextcord
from data import *
from util import testID, make_error
from Views import Show
from typing import Literal


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
    @nextcord.slash_command(guild_ids=[testID], name="list", description='Show list of 12 most recent solves')
    async def getList(self, interaction: Interaction):
        user = User.get_user(interaction.user.id)
        if user.timing:
            embed = make_error("End your current solve before using other commands. End solve by pressing stop time")
            await interaction.response.send_message(embed=embed)
            return
        embed = Time.get_embed(user, '0', interaction)
        view = Show(interaction.user.id)
        msg = await interaction.response.send_message(embed=embed, view=view)
        await user.change_msg(msg)

    @nextcord.slash_command(guild_ids=[testID], name="stats", description='Show stats of past solves')
    async def getStats(self, interaction: Interaction):
        user = User.get_user(interaction.user.id)
        if user.timing:
            embed = make_error("End your current solve before using other commands. End solve by pressing stop time")
            await interaction.response.send_message(embed=embed)
            return
        embed = Time.get_embed(user, '0', interaction, True)
        view = Show(interaction.user.id, True)
        msg = await interaction.response.send_message(embed=embed, view=view)
        await user.change_msg(msg)

    @nextcord.slash_command(guild_ids=[testID], name="details", description='Show details of a solve')
    async def details(self, interaction: Interaction, solve_n: int):
        user = User.get_user(interaction.user.id)
        if user.timing:
            embed = make_error("End your current solve before using other commands. End solve by pressing stop time")
            await interaction.response.send_message(embed=embed)
            return
        if solve_n < 1 or solve_n > len(user.times):
            await interaction.response.send_message(embed=make_error(f"{solve_n} is not a valid solve #"))
            return
        embed = nextcord.Embed(color=nextcord.Color.green())
        t = user.times[solve_n-1]
        text = str(t)
        embed.set_author(name=f"{interaction.user.name}'s solve #{solve_n}", icon_url=interaction.user.display_avatar.url)
        embed.add_field(name=f"{t.stype}: {t.scramble}", value="Time: " + text, inline=False)
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(guild_ids=[testID], name="clear", description='Clears all solves of a given type')
    async def clear(self, interaction: Interaction, scramble_type: Literal["All", "2x2", "3x3", "4x4", "5x5", "6x6", "7x7", "Other"]="All"):
        user = User.get_user(interaction.user.id)
        if user.timing:
            embed = make_error("End your current solve before using other commands. End solve by pressing stop time")
            await interaction.response.send_message(embed=embed)
            return
        og = len(user.times)
        if scramble_type == "All":
            user.times = []
        else:
            user.times = [i for i in User.get_user(interaction.user.id).times if i.stype != scramble_type]
        embed = nextcord.Embed(color=nextcord.Color.green())
        embed.add_field(name=f"Successfully cleared", value=f"{scramble_type} solves ({og-len(user.times)} total)", inline=False)
        await interaction.response.send_message(embed=embed)


    @nextcord.slash_command(guild_ids=[testID], name="delete", description='Delete a solve')
    async def delete(self, interaction: Interaction, solve_n: int):
        user = User.get_user(interaction.user.id)
        if user.timing:
            embed = make_error("End your current solve before using other commands. End solve by pressing stop time")
            await interaction.response.send_message(embed=embed)
            return
        if solve_n < 1 or solve_n > len(user.times):
            await interaction.response.send_message(embed=make_error(f"{solve_n} is not a valid solve #"))
            return
        embed = nextcord.Embed(color=nextcord.Color.green())
        user.times.pop(solve_n-1)
        embed.add_field(name=f"Successfully deleted", value=f"Solve #{solve_n}", inline=False)
        await interaction.response.send_message(embed=embed)
    async def getStat(self, interaction, scramble_type, n, name, function, mini):
        user = User.get_user(interaction.user.id)
        if user.timing:
            embed = make_error("End your current solve before using other commands. End solve by pressing stop time")
            await interaction.response.send_message(embed=embed)
            return
        if n < mini:
            embed = make_error(f"n has to be greater or equal to {mini}")
        else:
            embed = nextcord.Embed(colour=nextcord.Color.green())
            l = [i for i in User.get_user(interaction.user.id).times if scramble_type == "All" or i.stype == scramble_type]
            t, l = function(l[::-1], n)
            text = str(t)
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
            embed.add_field(name=f"{name}{n}", value=text, inline=False)
            text = ""
            for i in l:
                text+=str(i) + ", "
            if not text:
                text = "N/A"
            embed.add_field(name=f"Solves", value=text.removesuffix(", "), inline=False)
        await interaction.response.send_message(embed=embed)
    @nextcord.slash_command(guild_ids=[testID], name="ao", description='Show the current average of n')
    async def ao(self, interaction: Interaction, scramble_type: Literal["All", "2x2", "3x3", "4x4", "5x5", "6x6", "7x7", "Other"]="All", n:int = 5):
        await self.getStat(interaction, scramble_type, n, "ao", Time.ao, 3)

    @nextcord.slash_command(guild_ids=[testID], name="mo", description='Show the current mean of n')
    async def mo(self, interaction: Interaction, scramble_type: Literal["All", "2x2", "3x3", "4x4", "5x5", "6x6", "7x7", "Other"]="All", n: int = 3):
        await self.getStat(interaction, scramble_type, n, "mo", Time.mo, 1)

    @nextcord.slash_command(guild_ids=[testID], name="bestmo", description='Show the best mean of n')
    async def best_mo(self, interaction: Interaction, scramble_type: Literal["All", "2x2", "3x3", "4x4", "5x5", "6x6", "7x7", "Other"]="All", n: int = 3):
        await self.getStat(interaction, scramble_type, n, "Best mo", Time.best_mo, 1)

    @nextcord.slash_command(guild_ids=[testID], name="bestao", description='Show the best average of n')
    async def best_ao(self, interaction: Interaction, scramble_type: Literal["All", "2x2", "3x3", "4x4", "5x5", "6x6", "7x7", "Other"]="All", n: int = 5):
        await self.getStat(interaction, scramble_type, n, "Best ao", Time.best_ao, 3)

def setup(bot):
    bot.add_cog(Stats(bot))