from time import perf_counter

import nextcord
from nextcord import Interaction
from util import make_error
from data import *

class Start(nextcord.ui.View):
    def __init__(self, stype, scramble, user):
        super().__init__()
        self.stype = stype
        self.scramble = scramble
        self.state = 0
        self.user = user

    async def end(self, user):
        await user.change_msg(None)

    @nextcord.ui.button(label="Start Time", style=nextcord.ButtonStyle.green)
    async def start(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user:
            return
        user = User.get_user(interaction.user.id)
        user.current = Time(perf_counter(), self.stype, self.scramble)
        user.timing = True
        view = Stop(self.stype, self.scramble, interaction.user.id)
        msg = await interaction.response.send_message("Stop time", view=view)
        await user.change_msg(msg)
        self.state = 1
        self.stop()

    @nextcord.ui.button(label="Don't Time", style=nextcord.ButtonStyle.red)
    async def dont(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user:
            return
        self.state = 2
        await self.end(User.get_user(interaction.user.id))
        self.stop()

class Stop(nextcord.ui.View):
    def __init__(self, stype, scramble, user):
        super().__init__()
        self.stopped = False
        self.stype = stype
        self.scramble = scramble
        self.user = user
    @nextcord.ui.button(label="Stop Time", style=nextcord.ButtonStyle.red)
    async def stopp(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user:
            return
        user = User.get_user(interaction.user.id)
        user.current.endtime(perf_counter())
        embed = nextcord.Embed()
        text = str(user.current)
        embed.colour = nextcord.Color.green()
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name=f"{self.stype}: {self.scramble}", value="Time: "+text, inline=False)
        user.times.append(user.current)
        user.timing = False
        view = Penalty(self.user, self.stype, self.scramble)
        msg = await user.msg.edit(embed=embed, view=view, content="")
        # await user.change_msg(msg)
        self.stop()
class Show(nextcord.ui.View):
    def __init__(self, user, stats=False):
        super().__init__()
        self.stats = stats
        self.user = user

    @nextcord.ui.select(placeholder="Add Filter", options=[nextcord.SelectOption(label=f"No filter", value='0')]+
                                                          [nextcord.SelectOption(label=f"{i}x{i} only", value=str(i))
                                                           for i in range(2, 8)]+
                                                          [nextcord.SelectOption(label=f"Other only", value='1')])
    async def filter(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
        if interaction.user.id != self.user:
            return
        user = User.get_user(interaction.user.id)
        embed = Time.get_embed(user, select.values[0], interaction, self.stats)
        await user.msg.edit(embed=embed)

class Penalty(nextcord.ui.View):
    def __init__(self, user, stype, scramble):
        super().__init__()
        self.user = user
        self.stype = stype
        self.scramble = scramble
    async def end(self, interaction):
        embed = nextcord.Embed()
        user = User.get_user(interaction.user.id)
        text = str(user.current)
        embed.colour = nextcord.Color.green()
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name=f"{self.stype}: {self.scramble}", value="Time: " + text, inline=False)

        await user.msg.edit(view=None, embed=embed)
        user.msg = None
    @nextcord.ui.button(label="OK", style=nextcord.ButtonStyle.green)
    async def ok(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user:
            return
        user = User.get_user(interaction.user.id)
        user.current.ok()
        await self.end(interaction)

    @nextcord.ui.button(label="+2", style=nextcord.ButtonStyle.blurple)
    async def plus(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user:
            return
        user = User.get_user(interaction.user.id)
        user.current.plustwo()
        await self.end(interaction)

    @nextcord.ui.button(label="DNF", style=nextcord.ButtonStyle.blurple)
    async def dnf(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user:
            return
        user = User.get_user(interaction.user.id)
        user.current.dnf()
        await self.end(interaction)

class Addtime(nextcord.ui.Modal):
    convert = {"": 0, "OK": 0, "+2": 1, "DNF": 2}
    def __init__(self):
        super().__init__("Add a time")
        self.time = nextcord.ui.TextInput("Time (hours ad minutes are optional)", required=True, placeholder="hours:minutes:seconds")
        self.add_item(self.time)
        self.pen = nextcord.ui.TextInput("Penalty (OK, +2, DNF)", default_value="OK", required=False)
        self.add_item(self.pen)
        self.stype = nextcord.ui.TextInput("Scramble Type", default_value="3x3", required=False)
        self.add_item(self.stype)
        self.scramble = nextcord.ui.TextInput("Scramble", placeholder="Example: B2 D F B2 U' F' R B' F2 R2 L' B2 U2 B2 D2 L2 B2 U2 L' D'",required=False)
        self.add_item(self.scramble)
    def isfloat(self, s):
        try:
            float(s)
        except ValueError:
            return False
        return True
    async def callback(self, interaction: Interaction) -> None:
        error = 1
        errorem = nextcord.Embed(colour=nextcord.Color.red())
        t = self.time.value.split(":")
        h, m, s = "", "", t[-1]
        if len(t) >= 2:
            m = t[-2]
        if len(t) >= 3:
            h = t[-3]
        if len(t) >= 4:
            errorem.add_field(name=f"Error {error}", value="Time has too many colons", inline=False)
            error += 1
        if not h:
            h = "0"
        if not m:
            m = "0"
        if not s:
            s = "0"
        if not h.isnumeric():
            errorem.add_field(name=f"Error {error}", value="Hours has to be a non-negative integer", inline=False)
            error += 1
        if not m.isnumeric() or int(m) >= 60:
            errorem.add_field(name=f"Error {error}", value="Minutes has to be an integer between [0, 60)", inline=False)
            error += 1
        if not self.isfloat(s) or float(s) < 0 or float(s) >= 60:
            errorem.add_field(name=f"Error {error}", value="Seconds has to be a number between [0, 60)", inline=False)
            error += 1
        if self.pen.value.upper() not in self.convert:
            errorem.add_field(name=f"Error {error}", value="Penalty must either be OK, +2, or DNF", inline=False)
            error += 1
        if error != 1:
            await interaction.response.send_message(embed=errorem)
            return
        time = int(h)*3600+int(m)*60 + float(s)
        stype = self.stype.value if self.stype.value in set(f"{i}x{i}" for i in range(2, 8)) else "Other"
        time = Time(time, stype, self.scramble.value, False)
        p = self.convert[self.pen.value]
        if p == 0:
            time.ok()
        elif p == 1:
            time.plustwo()
        elif p == 2:
            time.dnf()
        User.get_user(interaction.user.id).times.append(time)
        embed = nextcord.Embed(description="Successfully added time")
        text = str(time)
        embed.colour = nextcord.Color.green()
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name=f"{stype}: {self.scramble.value}", value="Time: " + text, inline=False)
        await interaction.response.send_message(embed=embed)
class VStart(nextcord.ui.View):
    def __init__(self, stype, scramble, user):
        super().__init__()
        self.stype = stype
        self.scramble = scramble
        self.state = 0
        self.user = user

    async def end(self, user):
        await user.change_msg(None)

    @nextcord.ui.button(label="Start Time", style=nextcord.ButtonStyle.green)
    async def start(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user:
            return
        user = User.get_user(interaction.user.id)
        user.current = Time(perf_counter(), self.stype, self.scramble)
        user.timing = True
        self.state = 1
        user.virtualing = True
        await user.change_msg(None)
        self.stop()

class MStop(nextcord.ui.View):
    def __init__(self, match):
        super().__init__()
        self.match = match
    @nextcord.ui.button(label="Stop Time", style=nextcord.ButtonStyle.red)
    async def stopp(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id == self.match.p1.id:
            name = self.match.p1.name
        elif interaction.user.id == self.match.p2.id:
            name = self.match.p2.name
        else:
            return
        t = perf_counter() - self.match.started
        embed = nextcord.Embed()
        text = str(Time.num(t))
        embed.colour = nextcord.Color.green()
        embed.set_author(name=f"🏆 Winner: {name} 🏆", icon_url=interaction.user.display_avatar.url)
        s = self.match.size
        embed.add_field(name=f"{s}x{s}: {self.match.scramble}", value="Time: "+text, inline=False)
        await self.match.msg.edit(embed=embed, view=None)
        self.match.end()
class Ready(nextcord.ui.View):
    def __init__(self, match):
        super().__init__()
        self.match = match

    @nextcord.ui.button(label="Ready", style=nextcord.ButtonStyle.green)
    async def ready(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id == self.match.p1.id:
            await self.match.ready(1, interaction)
        elif interaction.user.id == self.match.p2.id:
            await self.match.ready(2, interaction)
        else:
            return
        user = User.get_user(interaction.user.id)
        if user.match or user.timing:
            await interaction.response.send_message(embed=make_error(f"{interaction.user.mention} end your match before readying"))


    @nextcord.ui.button(label="Unready", style=nextcord.ButtonStyle.red)
    async def unready(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id == self.match.p1.id:
            await self.match.ready(1, interaction, False)
        elif interaction.user.id == self.match.p2.id:
            await self.match.ready(2, interaction, False)
        else:
            return
        await interaction.response.defer()
