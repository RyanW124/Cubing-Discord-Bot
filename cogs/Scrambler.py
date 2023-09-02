import nextcord, asyncio
from cube import Cube
from nextcord import Interaction
from nextcord.ext import commands
import os
from Views import *
from util import *
from typing import Literal
from match import Match


class Scrambler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False

#     Events
#     @commands.Cog.listener()
#     async def on_ready(self):
#         await self.bot.change_presence(activity=discord.Game(name='!help'), status=discord.Status.do_not_disturb)
    #[10, 20, 45, 60, 80, 100]
    @nextcord.slash_command(guild_ids=[testID], name="endmatch", description='Ends current match')
    async def endmatch(self, interaction: Interaction):
        user = User.get_user(interaction.user.id)
        if user.match is None:
            await interaction.response.send_message(embed=make_error("You don't have an ongoing match"))
            return
        if user.match.virtual:
            await interaction.response.send_message(embed=make_error(f"{interaction.user.name} ended match, no one wins"))
        else:
            await user.match.msg.edit(embed=make_error(f"{interaction.user.name} ended match, no one wins"), view=None, content="")
            await interaction.response.defer()

        user.match.end()

    @nextcord.slash_command(guild_ids=[testID], name="endvirtual", description='Ends current virtual solve')
    async def endvirtual(self, interaction: Interaction):
        user = User.get_user(interaction.user.id)
        if not user.virtualing:
            await interaction.response.send_message(embed=make_error("You don't have an ongoing virtual solve"))
            return
        user.current.endtime(perf_counter())
        user.current.dnf()
        embed = nextcord.Embed()
        text = str(user.current)
        embed.colour = nextcord.Color.green()
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name=f"{user.current.stype}: {user.current.scramble}", value="Time: " + text, inline=False)
        user.times.append(user.current)
        user.timing = False
        user.virtual = None
        user.virtualing = False
        await interaction.response.send_message(embed=embed)
    @nextcord.slash_command(guild_ids=[testID], name="virtual", description='starts a virtual solve')
    async def virtual(self, interaction: Interaction, scramble_type: Literal["2x2", "3x3", "4x4", "5x5", "6x6", "7x7"]="3x3"):
        user = User.get_user(interaction.user.id)
        if user.virtualing:
            await interaction.response.send_message(embed=make_error("End your current virtual solve before starting a new solve"))
            return
        await self.nxn(int(scramble_type[0]), interaction, True)

    def convert(self, n):
        n = n % 360
        if n > 180:
            n -= 360
        return n
    @nextcord.slash_command(guild_ids=[testID], name="angle", description='changes angle of camera to x°, y°, z°')
    async def angle(self, interaction: Interaction, x:float, y:float, z:float):
        x = self.convert(x)
        y = self.convert(y)
        z = self.convert(z)
        user = User.get_user(interaction.user.id)
        user.rotation = (x, y, z)
        embed = nextcord.Embed()
        embed.colour = nextcord.Color.green()
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name=f"Successfully set camera angle to", value=f"{x}°, {y}°, {z}°", inline=False)
        await interaction.response.send_message(embed=embed)
    @nextcord.slash_command(guild_ids=[testID], name="movelist", description='show a list of possible moves')
    async def movelist(self, interaction: Interaction):
        embed = nextcord.Embed()
        embed.colour = nextcord.Color.blue()
        embed.add_field(name=f"Basic turns", value=f"Up (U), Down(D), Right(R), Left (L), Front (F), Back (B)", inline=False)
        embed.add_field(name=f"Turn direction", value=f"Adding nothing is clockwise (F), adding an apostrophe is counter-clockwise (F'), adding the number 2 is a double turn (F2)", inline=False)
        embed.add_field(name=f"Wide moves", value=f"Add a w behind basic turn or use lowercase to turn 2 layers (Rw/r)", inline=False)
        embed.add_field(name=f"N wide moves", value=f"Add a number n before wide move to turn n layers (3Rw)", inline=False)
        embed.add_field(name=f"Slice turns", value=f"Add a number n before basic turn to turn nth layers (3R)", inline=False)
        embed.add_field(name=f"Cube Rotations", value=f"x, y, z rotates cube in R, U, F direction, respectively", inline=False)
        embed.set_image("https://jperm.net/images/notation.png")
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(guild_ids=[testID], name="match", description='1v1 another user')
    async def match(self, interaction: Interaction, user: nextcord.User, scramble_type: Literal["2x2", "3x3", "4x4", "5x5", "6x6", "7x7", "2x2 Virtual", "3x3 Virtual", "4x4 Virtual", "5x5 Virtual", "6x6 Virtual", "7x7 Virtual"]="3x3"):
        if user is interaction.user:
            await interaction.response.send_message(embed=make_error("Can't play against yourself"))
        if user.bot:
            await interaction.response.send_message(embed=make_error("Can't play against bots"))
        match = Match(interaction.user, user, int(scramble_type[0]), scramble_type.endswith("Virtual"))
        users = [User.get_user(interaction.user.id), User.get_user(user.id)]
        match.msg = await interaction.response.send_message(file=nextcord.File(match.url), embed=match.embed, view=Ready(match))
        os.remove(match.url)
        for _ in range(30):
            await asyncio.sleep(0.5)
            if match.yes:
                for i in users:
                    i.match = match
                break
        else:
            await match.msg.edit(embed=make_error("Match aborted"), view=None)
    @nextcord.slash_command(guild_ids=[testID], name="move", description='makes a move in a virtual solve')
    async def move(self, interaction: Interaction, moves):
        user = User.get_user(interaction.user.id)
        if user.match is not None:
            cube = user.match.c1 if user.id == user.match.p1.id else user.match.c2
            await self.makemove(user, interaction, cube, moves, user.match, interaction.user.name)
            return
        if not moves:
            await interaction.response.send_message(embed=make_error("Moves cannot be blank"))
            return

        if user.virtual is None:
            await interaction.response.send_message(embed=make_error("You don't have an ongoing virtual solve"))
            return
        if not user.virtualing:
            await interaction.response.send_message(embed=make_error("Start time before moving"))
            return

        await self.makemove(user, interaction, user.virtual, moves)
    async def makemove(self, user, interaction, cube, moves, match=None, name=None):
        try:
            cube.do(moves)
        except ValueError:
            await interaction.response.send_message(embed=make_error("Invalid moves, use **/movelist** to see possible moves"))
            return
        img, _ = cube.to_3d(*user.rotation)
        url = f"{interaction.user.id}.png"
        img.save(url)
        embed = nextcord.Embed()
        embed.add_field(name=f"Successfully made the moves ", value=moves, inline=False)
        embed.colour = nextcord.Color.green()
        embed.set_image("attachment://" + url)
        await interaction.response.send_message(file=nextcord.File(url), embed=embed)
        if cube.solved():
            if match:
                t = perf_counter() - match.started
                embed = nextcord.Embed()
                text = str(Time.num(t))
                embed.colour = nextcord.Color.green()
                embed.set_author(name=f"🏆 Winner: {name} 🏆", icon_url=interaction.user.display_avatar.url)
                s = match.size
                embed.add_field(name=f"{s}x{s}: {user.match.scramble}", value="Time: " + text, inline=False)
                await interaction.channel.send(embed=embed, view=None)
                match.end()
            else:
                user.current.endtime(perf_counter())
                embed = nextcord.Embed()
                text = str(user.current)
                embed.colour = nextcord.Color.green()
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
                embed.add_field(name=f"{user.current.stype}: {user.current.scramble}", value="Time: " + text, inline=False)
                user.times.append(user.current)
                user.timing = False
                user.virtualing = False
                user.virtual = None
                await interaction.channel.send(embed=embed)
        os.remove(url)

    async def nxn(self, size, interaction, v=False):
        user = User.get_user(interaction.user.id)
        user.virtual = None
        user.virtualing = False
        if user.timing:
            embed = make_error("End your current solve before using other commands. End solve by pressing stop time")
            await interaction.response.send_message(embed=embed)
            return
        scramble = Cube.scramble(size)
        cube = Cube(size)
        cube.do(scramble)
        img, _ = cube.to_3d(*user.rotation)
        url = f"{interaction.user.id}.png"
        img.save(url)
        embed = nextcord.Embed()
        embed.add_field(name=f"{size}x{size} Scramble", value=scramble, inline=False)
        embed.colour = nextcord.Color.green()
        embed.set_image("attachment://" + url)
        if v:
            user.virtual = cube
            embed.description = "Use **/move** to make a move, **/movelist** to see possible moves, and **/angle** to change angle of camera"
        view = VStart if v else Start
        view = view(f"{size}x{size}", scramble, interaction.user.id)
        msg = await interaction.response.send_message(file=nextcord.File(url), embed=embed, view=view)
        await user.change_msg(msg)
        os.remove(url)

    @nextcord.slash_command(guild_ids=[testID], name="addtime", description='Add a time')
    async def addtime(self, interaction: Interaction):
        user = User.get_user(interaction.user.id)
        if user.timing:
            embed = make_error("End your current solve before using other commands. End solve by pressing stop time")
            await interaction.response.send_message(embed=embed)
            return
        modal = Addtime()
        await interaction.response.send_modal(modal)



    @nextcord.slash_command(guild_ids=[testID], name="close", description='Turns off bot')
    @commands.is_owner()
    async def close(self, interaction: Interaction):
        await interaction.response.send_message('bye')
        await self.bot.close()
    #commands
    @nextcord.slash_command(guild_ids=[testID], name="3x3", description='Generates a 3x3 scramble')
    async def three(self, interaction: Interaction):
        await self.nxn(3, interaction)

    @nextcord.slash_command(guild_ids=[testID], name="2x2", description='Generates a 2x2 scramble')
    async def two(self, interaction: Interaction):
        await self.nxn(2, interaction)

    @nextcord.slash_command(guild_ids=[testID], name="4x4", description='Generates a 4x4 scramble')
    async def four(self, interaction: Interaction):
        await self.nxn(4, interaction)

    @nextcord.slash_command(guild_ids=[testID], name="5x5", description='Generates a 5x5 scramble')
    async def five(self, interaction: Interaction):
        await self.nxn(5, interaction)

    @nextcord.slash_command(guild_ids=[testID], name="6x6", description='Generates a 6x6 scramble')
    async def six(self, interaction: Interaction):
        await self.nxn(6, interaction)

    @nextcord.slash_command(guild_ids=[testID], name="7x7", description='Generates a 7x7 scramble')
    async def seven(self, interaction: Interaction):
        await self.nxn(7, interaction)




def setup(bot):
    bot.add_cog(Scrambler(bot))