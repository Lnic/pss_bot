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
            prestiges["%s_%s"%(name_list[name1-1],name_list[name2-1])]=source_sheet[name1][name2].lower()

heroes = all_names(hero) #plural indicates name list
epics = all_names(epic)
uniques = all_names(unique)

add_to_prestiges(heroes,hero)
legendaries=list(set(prestiges.values()))
add_to_prestiges(epics,epic)
add_to_prestiges(uniques,unique)

print ('Prestige data prep complete. Time Elapsed :'+str(time.clock()-time_start))

def finder(target, source):
    return source[source.find(target)+len(target)+1:source.find('"',source.find(target)+len(target)+2)]

class Crew:
    def __init__(self, source, name):
        '''Crew from Pixel Starships'''
        #self.name = finder("CharacterDesignName=",source)
        self.name = name
        self.gender = finder("GenderType=",source)
        self.race = finder("RaceType=",source)
        self.hp = finder("FinalHp=",source)
        self.pilot = finder("FinalPilot=",source)
        self.attack = finder("FinalAttack=",source)
        self.fire_resistance = finder("FireResistance=",source)
        self.repair = finder("FinalRepair=",source)
        self.weapon = finder("FinalWeapon=",source)
        self.shield = finder("FinalShield=",source)
        self.engine = finder("FinalEngine=",source)
        self.research = finder("FinalResearch=",source)
        self.walking_speed = finder("WalkingSpeed=",source)
        self.rarity = finder("Rarity=",source)
        self.progression = finder("ProgressionType=",source)
        self.xp = finder("XpRequirementScale=",source)
        self.special_type = finder("SpecialAbilityType=",source)
        self.special = finder("SpecialAbilityFinalArgument=",source)
        self.training = finder("TrainingCapacity=",source)
        self.equipment = finder("EquipmentMask=",source)

crew={}

def all_crew_values(source):
    text=source[:]
    while len(text)>0:
        name=(str(finder("CharacterDesignName=",text)).lower())
        crew[name]=Crew(text,str(name))
        if text.find("/CharacterDesign")>0:
            text=text[text.find("/CharacterDesign")+len("/CharacterDesign")+1:]
        else:
            break
        
pss_api=open("ListAllCharacterDesigns2.txt","r+").read()
all_crew_values(pss_api)

print ('Crew data prep complete. Time Elapsed :'+str(time.clock()-time_start))

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
        if request.lower()=="prestige" or request.lower()=="prestiges":
            await bot.say("Input: 1 crew name or 2 crew names separated by a comma. Gives result of crew prestige if known. Gives known possibilities for prestige if only 1 name is given")
        elif request.lower()=="namelist" or request.lower()=="names":
            await bot.say("Gives acceptable spelling for Hero, Epic, or Unique crew")
        elif request.lower()=="recipe" or request.lower()=="recipes":
            await bot.say("Gives known combinations which result in the given name. If 1 parent and 1 child are given, a list of other parents will be given which can produce the desired child.")
        elif request.lower()=="stats" or request.lower()=="stat":
            await bot.say("Gives requested stats for listed crew member. Use ?stats help for more information")
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
                if request.lower() in prestiges[combo]:
                    result.append([combo.lower().split('_')][0])
            if result==[]:
                await bot.say("There are no recorded recipes for %s"%(request.title()))
                return
            else:
                await bot.say("These combinations are listed as potentially making %s: ```%s```"%(request.title(), result))
                return
        except:
            await bot.say("There are no recorded recipes for %s"%(request.title()))
            return
    try:
        result=[]
        for combo in prestiges:
            if names[0].lower() in prestiges[combo]: #names[0] is the child here
                result.append([combo.lower().split('_')][0])
        if not [x for x in result if names[1].lower() in x]:
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
                await bot.say("According to records, combining %s with the following: \n\n ```%s``` \n\nwill yield %s"%(names[0].title(),set([x[0] for x in result]),names[1].title()))
                return
        else:
            result=[combo for combo in result if names[1].title() in combo]#looking for another parent
            if result==[]:
                await bot.say("I see no relation between %s and %s"%(names[0].title(),names[1].title()))
                return
            else:
                for combo in result:
                    combo.remove(names[1].title())
                await bot.say("According to records, combining %s with the following: \n\n ```%s``` \n\nwill yield %s"%(names[1].title(),set([x[0] for x in result]),names[0].title()))
                return
    except:
        await bot.say("Not sure. Check spelling. I will also only calculate for 2 crew (1 generation). I will also probably have trouble with Visiri Capt'n")
    
@bot.command(aliases=["names"])
async def namelist(request : str):
    """returns a list of valid names"""
    if request.lower()=='legendary' or request.lower()=='legendaries' or request.lower()=='legend':
        await bot.say('The following is a list of all known names of Legendary Crew. I will likely only understand names that are typed as follows:')
        await bot.say(legendaries)
    elif request.lower()=='hero' or request.lower()=='heroes':
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
        await bot.say("%s is recorded as being used in ```%s```"%("Visiri Capt'n", result))
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
            await bot.say("Unrecognized or the crew is not hero, epic, or unique. Please check spelling with ?namelist")
            return
        if result==set():
            await bot.say("No known recipes including %s"%(request.title()))
            return
        else:
            await bot.say("%s is recorded as being used in ```%s```"%(request.title(), result))
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

@bot.command(aliases=["Stats", 'stat', 'Stat'])
async def stats(*,request : str):
    if request.lower()=='help':
        await bot.say("Give a crew name and a stat separated by a comma. Valid names can be found with ?stat names. Valid stats are ```gender, race, hp, pilot, attack, fire_resistance, repair, weapon, shield, engine, research, walking_speed, rarity, progression, xp, special_type, special, training, and equipment.```")
        return
    if request.lower()=='names':
        await bot.say("Valid names are: ```%s```"%(crew.keys()))
    if ',' in request:
        request = request.lower().split(',')
    if request[1][0] == ' ':
        request[1] = request[1][1:]
    try:
        await bot.say("%s's %s is: %s"%(request[0].title(), request[1], getattr(crew[request[0]],request[1])))
    except:
        await bot.say("I don't understand something. Try ?help to correct spelling")
  
bot.run('Mjc0NDU1NTg5NTY2ODA4MDc2.C2yWMw.uFEcuSxiZRJPp-UkloTvWV0z84Q')
