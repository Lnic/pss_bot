from imp import reload
import time
import discord
from discord.ext import commands
import logging
import datetime

search_threshold = 74

# Colors used in embed
common_color = 0xffffff
unique_color = 0x09afff
epic_color = 0x6f00dd
hero_color = 0xfeb901
legendary_color = 0xfeb901
special_color = 0xffffff
alert_color = 0xff0000
ok_color = 0x008000


logger = logging.getLogger('discord')
logger.setLevel(logging.CRITICAL)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

sell_market = {}
buy_market = {}
swap_market = {}

time_start = time.clock()


def lined_string(text):
    return "```\n"+"%s\n"*len(text)%tuple(text)+"```\n"


source_check = "\n"


description = """A bot designed to help in Pixel french fleet Black market"""

bot = commands.Bot(command_prefix=['?', '?\ '],
                   description=description,
                   help_attrs={})


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print('Full prep complete. Time Elapsed :'+str(time.clock()-time_start))
    await bot.change_presence(game=discord.Game(name='try ?help (list, buy, sell, swap, clear)'))


@bot.command(aliases=["Sell"], pass_context=True)
async def sell(ctx):

    #id = str(ctx.message.author.id)
    id = str(ctx.message.author.name)
    item = str(ctx.message.content)
    item = item.replace('?sell ', '')

    sell_market[id] = dict(id=id, item=item, date=datetime.date.today())


    today = datetime.date.today()

    description = ''
    for list in sell_market:
        delta_day = today - sell_market[list]['date']
        description = description + "<@"+ sell_market[list]['id'] + "> sell: " + sell_market[list]['item'] + " since " + str(delta_day.days) + " days \n"
    embed = discord.Embed(title="SELL",
                          description=description,
                          color=ok_color)
    await bot.say(embed=embed)


@bot.command(aliases=["Buy"], pass_context=True)
async def buy(ctx):
    
    #id = str(ctx.message.author.id)
    id = str(ctx.message.author.name)
    item = str(ctx.message.content)
    item = item.replace('?buy ', '')

    buy_market[id] = dict(id=id, item=item, date=datetime.date.today())

    today = datetime.date.today()
    print(buy_market)
    description = ''
    for list in buy_market:

        delta_day = today - buy_market[list]['date']
        description = description + "<@"+ buy_market[list]['id'] + "> buy: " + buy_market[list]['item'] + " since " + str(delta_day.days) + " days \n"
    embed = discord.Embed(title="BUY",
                          description=description,
                          color=ok_color)
    await bot.say(embed=embed)


@bot.command(aliases=["Swap"], pass_context=True)
async def swap(ctx):
    #id = str(ctx.message.author.id)
    id = str(ctx.message.author.name)
    item = str(ctx.message.content)
    item = item.replace('?swap ', '')

    swap_market[id] = dict(id=id, item=item, date=datetime.date.today())

    today = datetime.date.today()
    
    description = ''
    for list in swap_market:
        delta_day = today - swap_market[list]['date']
        description = description + "<@" + swap_market[list]['id'] + "> swap: " + swap_market[list]['item'] + " since " + str(delta_day.days) + " days \n"
    embed = discord.Embed(title="SWAP",
                          description=description,
                          color=ok_color)
    await bot.say(embed=embed)


@bot.command(aliases=["List"], pass_context=True)
async def list(ctx):

    embed = discord.Embed(title="BLACK MARKET", description="Please remember to update your listings. "
                                                            "?list \n ?buy <buy list>\n ?sell <sell list>\n "
                                                            "?swap <swap list>\n ?clear <buy|sell|swap>",
                          color=ok_color)
    await bot.say(embed=embed)

    today = datetime.date.today()
    
    description = ''
    for list in sell_market:
        delta_day = today - sell_market[list]['date']
        description = description + "<@"+ sell_market[list]['id'] + "> sell: " + sell_market[list]['item'] + " since " + str(delta_day.days) + " days \n"
    embed = discord.Embed(title="SELL",
                          description=description,
                          color=ok_color)
    await bot.say(embed=embed)

    description = ''
    for list in buy_market:
        delta_day = today - buy_market[list]['date']
        description = description + "<@"+ buy_market[list]['id'] + "> buy: " + buy_market[list]['item'] + " since " + str(delta_day.days) + " days \n"
    embed = discord.Embed(title="BUY",
                          description=description,
                          color=ok_color)
    await bot.say(embed=embed)

    description = ''
    for list in swap_market:
        delta_day = today - swap_market[list]['date']
        description = description + "<@" + swap_market[list]['id'] + "> swap: " + swap_market[list]['item'] + " since " + str(delta_day.days) + " days \n"
    embed = discord.Embed(title="SWAP",
                          description=description,
                          color=ok_color)
    await bot.say(embed=embed)

@bot.command(aliases=["Clear"], pass_context=True)
async def clear(ctx, request : str):

    #id = str(ctx.message.author.id)
    id = str(ctx.message.author.name)

    today = datetime.date.today()
    
    if request == 'sell':
        try:
            del sell_market[str(id)]
        except KeyError:
            pass
    if request == 'buy':
        try:
            del buy_market[str(id)]
        except KeyError:
            pass
    if request == 'swap':
        try:
            del swap_market[str(id)]
        except KeyError:
            pass

    description = ''
    for list in sell_market:
        delta_day = today - sell_market[list]['date']
        description = description + "<@"+ sell_market[list]['id'] + "> sell: " + sell_market[list]['item'] + " since " + str(delta_day.days) + " days \n"
    embed = discord.Embed(title="SELL",
                          description=description,
                          color=ok_color)
    await bot.say(embed=embed)

    description = ''
    for list in buy_market:
        delta_day = today - buy_market[list]['date']
        description = description + "<@"+ buy_market[list]['id'] + "> buy: " + buy_market[list]['item'] + " since " + str(delta_day.days) + " days \n"
    embed = discord.Embed(title="BUY",
                          description=description,
                          color=ok_color)
    await bot.say(embed=embed)

    description = ''
    for list in swap_market:
        delta_day = today - swap_market[list]['date']
        description = description + "<@" + swap_market[list]['id'] + "> swap: " + swap_market[list]['item'] + " since " + str(delta_day.days) + " days \n"
    embed = discord.Embed(title="SWAP",
                          description=description,
                          color=ok_color)
    await bot.say(embed=embed)
    
bot.run('')
