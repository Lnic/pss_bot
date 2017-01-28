import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import time

time_start=time.clock()

scope = [r'https://spreadsheets.google.com/feeds']

#os.chdir('discord_bots\\pss_bot')

credentials = ServiceAccountCredentials.from_json_keyfile_name('pss_bot.json', scope)

gc = gspread.authorize(credentials)

sheet = gc.open_by_key('1nJFO_nksOxlAW4VMgUjrqljOjKv8CKN665M72h3Jspw')

prestiges = {} #Dictionary containing all prestige information

legendary = sheet.worksheet("Legendary-PWW link").get_all_values() #singular indicates sheet name
hero = sheet.worksheet("Heroes-PWW link").get_all_values()
epic = sheet.worksheet("Epics-PWW link").get_all_values()

def all_names(sheet): #Assembles all names in the sheet
    return [x for x in sheet[0] if x!='']

def add_to_prestiges(name_list, source_sheet): #Adds all values in that sheet to the Prestige dictionary
    for name1 in range(1,len(name_list)+1):
        for name2 in range(1,len(name_list)+1):
            prestiges["%s_%s"%(name_list[name1-1],name_list[name2-1])]=source_sheet[name1][name2]

legendaries = all_names(legendary) #plural indicates name list
heroes = all_names(hero)
epics = all_names(epic)

add_to_prestiges(legendaries,legendary)
add_to_prestiges(heroes,hero)
add_to_prestiges(epics,epic)

print ('Data prep complete. Time Elapsed :'+str(time.clock()-time_start))

import discord
from discord.ext import commands
import random

description = """A bot designed to relay known information regarding Pixel Starships."""

bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def namelist(request : str):
    """returns a list of valid names"""
    if request.lower()=='legendary' or request.lower()=='legendaries':
        await bot.say('The following is a list of all known names of Legendary Crew. I will likely only understand names that are typed as follows:')
        await bot.say(legendaries)
    elif request.lower()=='hero' or request.lower()=='heroes':
        await bot.say('The following is a list of all known names of Hero Crew. I will likely only understand names that are typed as follows:')
        await bot.say(heroes)
    elif request.lower()=='epic' or request.lower()=='epics':
        await bot.say('The following is a list of all known names of Epic Crew. I will likely only understand names that are typed as follows:')
        await bot.say(epics)
    else:
        await bot.say('Valid inputs include legendary, hero, or epic')

@bot.command()
async def prestige(*,request : str):
    """Returns data on prestige results for the two crew members entered as input"""
    names = request.title().split(',')
    if names[1][0] == ' ':
        names[1] = names[1][1:]
    try:
        await bot.say(prestiges["%s_%s"%(names[0],names[1])])
    except:
        await bot.say("I didn't quite catch that. Make sure the two crew names are separated by a comma (,) and that they are spelled correctly. Reference ?namelist for names I recognize.")    
    finally:
        if prestiges["%s_%s"%(names[0],names[1])]=='':
            await bot.say("I don't appear to have any results for this combination.")

bot.run('Mjc0NDU1NTg5NTY2ODA4MDc2.C2yWMw.uFEcuSxiZRJPp-UkloTvWV0z84Q')
