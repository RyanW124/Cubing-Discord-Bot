import nextcord
from nextcord import Interaction
from nextcord.ext import commands
import os

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)


for filename in os.listdir('cogs'):
    if filename.endswith('.py'):

        bot.load_extension(f'cogs.{filename[:-3]}')


@bot.event
async def on_ready():
    print('ready')
    channel = bot.get_channel(876792128154525730)


bot.run(input("Code: "))
