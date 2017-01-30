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

hero = sheet.worksheet("Legendary-PWW link").get_all_values() #singular indicates sheet name
epic = sheet.worksheet("Heroes-PWW link").get_all_values()
unique = sheet.worksheet("Epics-PWW link").get_all_values()

def all_names(sheet): #Assembles all names in the sheet
    return [x.lower() for x in sheet[0] if x!='']

def add_to_prestiges(name_list, source_sheet): #Adds all values in that sheet to the Prestige dictionary
    for name1 in range(1,len(name_list)+1):
        for name2 in range(1,len(name_list)+1):
            prestiges["%s_%s"%(name_list[name1-1],name_list[name2-1])]=source_sheet[name1][name2]

heroes = all_names(hero) #plural indicates name list
epics = all_names(epic)
uniques = all_names(unique)

add_to_prestiges(heroes,hero)
add_to_prestiges(epics,epic)
add_to_prestiges(uniques,unique)

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
    await bot.change_presence(game=discord.Game(name='Try ?commandlist'))

@bot.command(aliases=["CommandList", "Commandlist", "Command List", "command list", "commands", "Commands", "command", "Command"])
async def commandlist(*, request : str):
    try:
        if request=="prestige" or request=="prestiges":
            await bot.say("Input: 1 crew name or 2 crew names separated by a comma. Gives result of crew prestige if known. Gives known possibilities for prestige if only 1 name is given")
        elif request=="namelist" or request=="names":
            await bot.say("Gives acceptable spelling for Hero, Epic, or Unique crew")
        elif request=="recipe" or request=="recipes":
            await bot.say("Gives known combinations which result in the given name. If 1 parent and 1 child are given, a list of other parents will be given which can produce the desired child.")
    except:
        await bot.say("I don't know what that is")

@bot.command(aliases=["recipes", "Recipe", "Recipes"])
async def recipe(*,request : str):
    if ',' in request:
        names = request.lower().split(',')
        if names[1][0] == ' ':
            names[1] = names[1][1:]
    else:
        try:
            result=[]
            for combo in prestiges:
                if request.title() in prestiges[combo]:
                    result.append([combo.title().split('_')][0])
            if result==[]:
                await bot.say("There are no recorded recipes for %s"%(request.title()))
                return
            else:
                await bot.say("These combinations are listed as potentially making %s: %s"%(request.title(), result))
                return
        except:
            await bot.say("There are no recorded recipes for %s"%(request.title()))
            return
    try:
        result=[]
        for combo in prestiges:
            if names[0].title() in prestiges[combo]: #names[0] is the child here
                result.append([combo.title().split('_')][0])
        if not [x for x in result if names[1].title() in x]:
            for combo in prestiges:
                if names[1].title() in prestiges[combo]: #names[1] is the child here
                    result.append([combo.title().split('_')][0])
            result=[combo for combo in result if names[0].title() in combo]#looking for another parent
            if result==[]:
                await bot.say("I see no relation between %s and %s"%(names[0].title(),names[1].title()))
                return
            else:
                for combo in result:
                    combo.remove(names[0].title())
                await bot.say("According to records, combining %s with the following: \n\n %s \n\nwill yield %s"%(names[0].title(),set([x[0] for x in result]),names[1].title()))
                return
        else:
            result=[combo for combo in result if names[1].title() in combo]#looking for another parent
            if result==[]:
                await bot.say("I see no relation between %s and %s"%(names[0].title(),names[1].title()))
                return
            else:
                for combo in result:
                    combo.remove(names[1].title())
                await bot.say("According to records, combining %s with the following: \n\n %s \n\nwill yield %s"%(names[1].title(),set([x[0] for x in result]),names[0].title()))
                return
    except:
        await bot.say("Not sure. Check spelling. I will also only calculate for 2 crew (1 generation). I will also probably have trouble with Visiri Capt'n")
    
@bot.command(aliases=["names"])
async def namelist(request : str):
    """returns a list of valid names"""
    if request.lower()=='hero' or request.lower()=='heroes':
        await bot.say('The following is a list of all known names of Hero Crew. I will likely only understand names that are typed as follows:')
        await bot.say(heroes)
    elif request.lower()=='epic' or request.lower()=='epics':
        await bot.say('The following is a list of all known names of Epic Crew. I will likely only understand names that are typed as follows:')
        await bot.say(epics)
    elif request.lower()=='unique' or request.lower()=='uniqes':
        await bot.say('The following is a list of all known names of "Unique" Crew. I will likely only understand names that are typed as follows:')
        await bot.say(uniques)
    else:
        await bot.say('Valid inputs include hero, epic, or unique')

@bot.command(aliases=["Prestige"])
async def prestige(*,request : str):
    """Returns data on prestige results for the two crew members entered as input"""
    if request.lower()=="visiri capt'n": #Visiri Captain is weird, okay?
        result=(set([x for x in unique if x[0]=="Visiri Capt'n"][0][1:]))
        await bot.say("%s is recorded as being used in %s"%("Visiri Capt'n", result))
        return
    if ',' in request:
        names = request.lower().split(',')
    else: #If there's only one name, this tree will handle it. It will try to give all receipes for the one crew member
        if request.lower() in heroes:
            result=(set([x for x in hero if x[0]==request.title()][0][1:]))            
        elif request.lower() in epics:
            result=(set([x for x in epic if x[0]==request.title()][0][1:]))          
        elif request.lower() in uniques:
            result=(set([x for x in unique if x[0]==request.title()][0][1:]))
        else:
            await bot.say("Unrecognized. Please check spelling with ?namelist")
            return
        if result==set():
            await bot.say("No known recipes including %s"%(request.title()))
            return
        else:
            await bot.say("%s is recprded as being used in %s"%(request.title(), result))
            return
    if names[1][0] == ' ':
        names[1] = names[1][1:]
    try: #Returns plain prestige results
        if prestiges[r"%s_%s"%(names[0],names[1])]=='':
            if prestiges[r"%s_%s"%(names[1],names[0])]=='':
                await bot.say("I don't appear to have any results for this combination.")
                return
            else:
                await bot.say("%s + %s = %s"%(names[0].title(),names[1].title(),prestiges[r"%s_%s"%(names[1],names[0])]))
                return
        else:
            await bot.say("%s + %s = %s"%(names[0].title(),names[1].title(),prestiges[r"%s_%s"%(names[1],names[0])]))
            return
    except:
        await bot.say("Please separate names by a comma (,) and reference ?namelist for spelling. Don't mix rarities.")

bot.run('Mjc0NDU1NTg5NTY2ODA4MDc2.C2yWMw.uFEcuSxiZRJPp-UkloTvWV0z84Q')
