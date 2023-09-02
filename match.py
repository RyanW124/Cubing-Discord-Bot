from cube import *
from data import *
from Views import *
from time import perf_counter
import asyncio

class Match:
    def __init__(self, p1, p2, size, virtual=False):
        self.p1 = p1
        self.p2 = p2
        self.ready1 = False
        self.ready2 = False
        self.started = None
        self.scramble = Cube.scramble(size)
        self.cube = Cube(size)
        self.size = size
        self.cube.do(self.scramble)
        self.c1 = self.c2 = None
        img, _ = self.cube.to_3d(-10, 10, 0)
        self.url = f"{p1.id}{p2.id}.png"
        img.save(self.url)
        self.virtual = virtual
        self.embed = nextcord.Embed()
        self.embed.set_footer(text="Times in matches are not counted to individual times")
        self.embed.set_author(name="You have 15 seconds to accept")
        self.embed.add_field(name=f"{size}x{size} Scramble", value=self.scramble, inline=False)
        self.embed.add_field(name=p1.name, value="Not ready", inline=False)
        self.embed.add_field(name=p2.name, value="Not ready", inline=False)
        self.embed.colour = nextcord.Color.green()
        self.embed.set_image("attachment://" + self.url)
        self.msg = None
    @property
    def yes(self):
        return self.ready1 and self.ready2
    async def ready(self, n, interaction, r=True):
        if n == 1:
            self.ready1 = r
        else:
            self.ready2 = r
        self.embed.set_field_at(n, name=(self.p1 if n == 1 else self.p2).name,
                                value="Ready" if r else "Not ready", inline=False)
        await self.msg.edit(embed=self.embed)
        if self.yes:
            await self.msg.edit(view=None)
            # asyncio.run(self.countdown(interaction))
            for i in range(4):
                await interaction.channel.send("Start!" if i == 3 else str(3 - i))
                await asyncio.sleep(1)
            self.started = perf_counter()
            if self.virtual:
                self.c1 = Cube(self.size)
                self.c2 = Cube(self.size)
                self.c1.do(self.scramble)
                self.c2.do(self.scramble)
            else:
                self.msg = await interaction.channel.send("Press to stop time", view=MStop(self))
    def end(self):
        p1 = User.get_user(self.p1.id)
        p2 = User.get_user(self.p2.id)
        p1.match = p2.match =None
