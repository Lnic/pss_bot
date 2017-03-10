import time
import discord
from discord.ext import commands
import logging
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import Levenshtein

search_threshold = 74

logger = logging.getLogger('discord')
logger.setLevel(logging.CRITICAL)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

time_start=time.clock()

import prestige_data

print ('Data prep complete. Time Elapsed :'+str(time.clock()-time_start))

import character_data

print ('Crew and equipment data prep complete. Time Elapsed :'+str(time.clock()-time_start))

def lined_string(text):
    return "```\n"+"%s\n"*len(text)%tuple(text)+"```\n"

source_check = "\nFeel free to check my prestige source. URL can be requested with ?spreadsheet. Please report any errors with the bot to Phoenix's @DT-1236#0629 and direct updates to the prestige spreadsheet to Prestige Worldwide's @superjew#6070"

#######

description = """A bot designed to relay known information regarding Pixel Starships. Message Phoenix's @DT-1236#0629 if there are any problems with the bot. Updates to crew prestige information should be directed to Prestige Worldwide's @superjew#6070"""

bot = commands.Bot(command_prefix='?', description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print ('Full prep complete. Time Elapsed :'+str(time.clock()-time_start))
#    await bot.change_presence(game=discord.Game(name='Try ?commandlist'))
#change presence will have to wait until it's reconfigured for rewrite

@bot.command(aliases=["CommandList", "Commandlist", "Command List", "command list", "commands", "Commands", "command", "Command"])
async def commandlist(ctx,*, request : str=None):
    request = process.extractOne(request, ['prestige','names','recipe','stats'])[0]
    try:
        if request=="prestige":
            await ctx.send("Input: 1 crew name or 2 crew names separated by a comma. Gives result of crew prestige if known. Gives known possibilities for prestige if only 1 name is given")
        elif request=="names":
            await ctx.send("Gives acceptable spelling for Hero, Epic, or Unique crew")
        elif request=="recipe":
            await ctx.send("Gives known combinations which result in the given name. If 1 parent and 1 child are given, a list of other parents will be given which can produce the desired child.")
        elif request=="stats":
            await ctx.send("Gives requested stats for listed crew member. Use ?stats help for more information")
    except:
        await ctx.send("Try ?command with prestige, recipes, stats, or namelist")

@bot.command(aliases=["Spreadsheet", "spread", "Spread"])
async def spreadsheet(ctx,*,request : str=''):
    """Returns the URL for the prestige spreadsheet"""
    await ctx.send(r"https://docs.google.com/spreadsheets/d/11ZXN22CTmItPMVduRdpEwf6wR9KRMJR7Ro9HensEWSk/edit#gid=656420900")

@bot.command(aliases=["recipes", "Recipe", "Recipes"])
async def recipe(ctx,*,request : str):
    """Gives listed combinations to make single crew OR gives listed combinations including component crew member to make result crew member"""
    if request.lower()=='help' or request.lower()=='names':
        await ctx.send("Names for prestige results are: "+lined_string(prestige_data.all_prestige_results)+"\*\* = confirmed since December update\n# = rumored\nunmarked = NOT confirmed since December update")
        return
    if ',' in request:
        names = request.lower().split(',')
        if names[1][0] == ' ':
            names[1] = names[1][1:]
    else: #This will handle single name requests
        result=[]
        for combo in prestige_data.prestiges: #Find all prestige combinations that generate the request
            if fuzz.partial_ratio(request.lower(), prestige_data.prestiges[combo]) > prestige_data.search_threshold:
                result.append("%s = %s"%(([combo.title().split('_')][0]),prestige_data.prestiges[combo].title()))
        if result==[]:
            unique_check = process.extractOne(request, prestige_data.uniques, scorer = fuzz.partial_ratio)
            if unique_check[1] > prestige_data.search_threshold:
                await ctx.send("%s was parsed as %s which is a unique. Since uniques are obtainable through mineral draws, prestige recipes including elite crew are not recorded."%(request,unique_check[0]))
                return
            await ctx.send("There are no recorded recipes for %s"%(request.title())+source_check)
            return
        else:
            phrase = "These combinations are listed as potentially making %s:"%request.title()+lined_string(result)+"\nConsider double checking your chosen recipe with ?prestige or the spreadsheet"+"\n\*\* = confirmed since December update\n# = rumored\nunmarked = NOT confirmed since December update"
            while len(phrase) > 1950:
                await ctx.send(phrase[:phrase.find('[',1800)]+"```")
                phrase = "```"+phrase[phrase.find('[',1800):]
            await ctx.send(phrase)
            return
    result=[]
    for combo in prestige_data.prestiges:#This tree will handle prospective parent/child combinations
        if prestige_data.prestiges[combo] and fuzz.partial_ratio(names[0], prestige_data.prestiges[combo]) > prestige_data.search_threshold: #names[0] is the child/product here. This yields a list of all recipes making the child/product
            result.append("%s = %s"%(([combo.split('_')][0]),prestige_data.prestiges[combo])) #entries in result will be the full combination
    result = [x.title() for x in result if fuzz.partial_ratio(names[1],x) > prestige_data.search_threshold]#Take only entries which contain the parent/reagent, names[1]
    if not result:#If no entries contained the prevoius parent/reagent, names[1]...
        for combo in prestige_data.prestiges:#try it the other way around with names[1] as the child/product
            if prestige_data.prestiges[combo] and fuzz.partial_ratio(names[1], prestige_data.prestiges[combo]) > prestige_data.search_threshold: #names[1] is the child here
                result.append("%s = %s"%(([combo.split('_')][0]), prestige_data.prestiges[combo]))
        result = [x.title() for x in result if fuzz.partial_ratio(names[0],x) > prestige_data.search_threshold]#Take only entries which contain the parent/reagent, names[0]
        if not result:
            await ctx.send("I see no relation between %s and %s"%(names[0].title(),names[1].title())+source_check)
            return
        else:
            phrase = "According to records, pertinent combinations between %s and %s are as follows:"%(names[0].title(),names[1].title())+lined_string(sorted(set([x.title() for x in result])))+"Remember, only Legendary combinations are guaranteed by Savy"+"\n\*\* = confirmed since December update\n# = rumored\nunmarked = NOT confirmed since December update"
            while len(phrase) > 1950:
                await ctx.send(phrase[:phrase.find('[',1800)]+"```")
                phrase = "```"+phrase[phrase.find('[',1800):]
            await ctx.send(phrase)
            return
    else:
        phrase = "According to records, pertinent combinations between %s and %s are as follows:"%(names[0].title(),names[1].title())+lined_string(sorted(set([x.title() for x in result])))+"Remember, only Legendary combinations are guaranteed by Savy"+"\n\*\* = confirmed since December update\n# = rumored\nunmarked = NOT confirmed since December update"
        while len(phrase) > 1950:
                await ctx.send(phrase[:phrase.find('[',1800)]+"```")
                phrase = "```"+phrase[phrase.find('[',1800):]
        await ctx.send(phrase)
        return

@bot.command(aliases=["names"])
async def namelist(ctx,request : str=''):
    """returns a list of valid names"""
    if request.lower()=='legendary' or request.lower()=='legendaries' or request.lower()=='legend':
        await ctx.send('The following is a list of all known names of Legendary Crew. I will likely only understand names that are typed as follows:')
        await ctx.send(prestige_data.legendaries)
    elif request.lower()=='hero' or request.lower()=='heroes':
        await ctx.send('The following is a list of all known names of Hero Crew. I will likely only understand names that are typed as follows:')
        await ctx.send(prestige_data.heroes)
    elif request.lower()=='epic' or request.lower()=='epics':
        await ctx.send('The following is a list of all known names of Epic Crew. I will likely only understand names that are typed as follows:')
        await ctx.send(prestige_data.epics)
    elif request.lower()=='unique' or request.lower()=='uniques':
        await ctx.send('The following is a list of all known names of "Unique" Crew. I will likely only understand names that are typed as follows:')
        await ctx.send(prestige_data.uniques)
    else:
        await ctx.send('Valid inputs include hero, epic, or unique')

@bot.command(aliases=["Prestige"])
async def prestige(ctx,*,request : str):
    """Returns data on prestige results for the two crew members entered as input"""
    if ',' in request:
        names = request.lower().split(',')
    else: #If there's only one name, this tree will handle it. It will try to give all receipes for the one crew member
        result = []
        for combo in prestige_data.prestiges:
            if prestige_data.prestiges[combo] and process.extractOne(request.lower(),combo.lower().split('_'),scorer = fuzz.partial_ratio)[1] > prestige_data.search_threshold:
                result.append("%s = %s"%(([combo.title().split('_')][0]),prestige_data.prestiges[combo].title()))
        if not result: #This is for inputs with no recipes
            type_check = process.extractOne(request, character_data.crew.keys(), scorer = fuzz.partial_ratio)
            if type_check[1] > search_threshold:
                type_result = character_data.crew[type_check[0]].rarity
                if type_result in prestige_data.no_prestige_types:
                    if type_result == "Special":
                        phrase = "%s was parsed as **%s** which is %s type crew. Special crew cannot currently be made or used for prestige."%(request, type_check[0].title(), type_result)
                        await ctx.send(phrase)
                        return
                    if type_result == "Legendary":
                        phrase = "%s was parsed as **%s** which is %s type crew. Legendary is the highest tier of crew - therefore there are no combinations which use Legendary crew."%(request, type_check[0].title(), type_result)
                        await ctx.send(phrase)
                        return
                    if type_result == "Common" or type_result == "Elite":
                        phrase = "%s was parsed as **%s** which is %s type crew. Common and Elite crew combinations are not recorded."%(request, type_check[0].title(), type_result)
                        await ctx.send(phrase)
                        return                
                await ctx.send("%s was parsed as **%s**. There are no known recipes including %s"%(request, type_check[0], type_check[0].title())+source_check)
                return
            await ctx.send("Input not quite recognized. The closest entry is ```\n%s``` If this is correct, try again with this spelling."%type_check[0].title())
            return
        else: #This is for valid inputs
            short = sorted(set([x for x in prestige_data.hero+prestige_data.epic+prestige_data.unique if x[0] and fuzz.partial_ratio(request.lower(), x[0].lower()) > prestige_data.search_threshold][0][1:])) #will return the list which has the target in the 0th position, a column or row in the spreadsheet
            phrase = "%s is listed as being used in:"%(request)+lined_string(short)
            await ctx.send(phrase)
            phrase = ("Full recipes are as follows:\n"+lined_string(sorted(set([x.title() for x in result])))+"\*\* = confirmed since December update\n# = rumored\nunmarked = NOT confirmed since December update")
            while len(phrase) > 1950:
                await ctx.send(phrase[:phrase.find('[',1800)]+"```")
                phrase = "```"+phrase[phrase.find('[',1800):]
            await ctx.send(phrase)
            return
    key_1 = process.extractOne(request, prestige_data.prestiges.keys(),scorer = fuzz.partial_ratio)[0]
    if prestige_data.prestiges[key_1]:
        result_1 = prestige_data.prestiges[key_1].title()
    else:
        result_1 = "Unlisted"
    key_2 = process.extractOne(names[1]+names[0], prestige_data.prestiges.keys(),scorer = fuzz.partial_ratio)[0]
    if prestige_data.prestiges[key_2]:
        result_2 = prestige_data.prestiges[key_2].title()
    else:
        result_2 = "Unlisted"
    phrase = "%s was parsed as %s which yields:```\n%s```"%(request, key_1, result_1)
    await ctx.send(phrase)
    phrase = "%s yields:\n```\n%s```"%(key_2,result_2)+"\*\* = confirmed since December update\n# = rumored\nunmarked = NOT confirmed since December update"
    await ctx.send(phrase)

@bot.command(aliases=["Stats", 'stat', 'Stat'])
async def stats(ctx,*,request : str):
    """Provides stat readouts for requested crew"""
    initial_request = request
    if request.lower()=='help':
        await ctx.send("Give a crew name or a crew name and a stat separated by a comma. All stats will be given if no specific stat is provided. Valid names can be found with ?stat names. Valid stats are ```gender, race, hp, pilot, attack, fire_resistance, repair, weapon, shield, engine, research, walking_speed, running_speed, rarity, progression, xp, special_type, special, training, and equipment.```")
        return
    if request.lower()=='equip' or request.lower()=='equipment':
        await ctx.send("```%s```"%(character_data.equipment_loadouts))
        return
    if request.lower()=='names':
        await ctx.send("Valid names are: ```%s```"%(character_data.crew.keys()))
        return
    if ',' in request:
        request = request.lower().split(',')
    else: #This block handles single crew queries
        request = process.extractOne(request, character_data.crew.keys(), scorer = fuzz.partial_ratio)[0]
        name = character_data.crew[request].name.title()
        gender = character_data.crew[request].gender
        race = character_data.crew[request].race
        hp = character_data.crew[request].hp
        pilot = character_data.crew[request].pilot
        attack = character_data.crew[request].attack
        fire_resistance = character_data.crew[request].fire_resistance
        repair = character_data.crew[request].repair
        weapon = character_data.crew[request].weapon
        shield = character_data.crew[request].shield
        engine = character_data.crew[request].engine
        research = character_data.crew[request].research
        walking = character_data.crew[request].walking_speed
        running = character_data.crew[request].running_speed
        rarity = character_data.crew[request].rarity
        progression = character_data.crew[request].progression
        xp = character_data.crew[request].xp
        special_type = character_data.crew[request].special_type
        special = character_data.crew[request].special
        training = character_data.crew[request].training
        equipment =  character_data.crew[request].equipment
        phrase = "%s was parsed as **%s**\n"%(initial_request,request.title())+"```Name: %s \nGender: %s\nRace: %s \nHP: %s \nPilot: %s \nAttack: %s \nFire Resistance: %s \nRepair: %s \nWeapon: %s \nShield: %s \nEngine: %s \nResearch: %s \nWalking Speed: %s \nRunning Speed: %s\nRarity: %s \nProgression: %s \nXP: %s \nSpecial Type: %s \nSpecial: %s \nTraining: %s \nEquipment: %s - %s```"%(name, gender, race, hp, pilot, attack, fire_resistance, repair, weapon, shield, engine, research, walking, running, rarity, progression, xp, special_type, special, training, equipment, character_data.equipment_loadouts[int(character_data.crew[request].equipment)])
        await ctx.send(phrase)
        repair = character_data.crew[request].stats_equip['Repair']
        attack = character_data.crew[request].stats_equip['Attack']
        pilot = character_data.crew[request].stats_equip['Pilot']
        fire_resistance = character_data.crew[request].stats_equip['FireResistance']
        hp = character_data.crew[request].stats_equip['Hp']
        stamina = character_data.crew[request].stats_equip['Stamina']
        ability = character_data.crew[request].stats_equip['Ability']
        shield = character_data.crew[request].stats_equip['Shield']
        weapon = character_data.crew[request].stats_equip['Weapon']
        phrase = "With 50 training and the best available equipment, those stats could become:\n```\nName: %s\nHP: %s\nAttack: %s\nRepair: %s\nPilot: %s\nFire Resistance: %s\nStamina: %s\nSpecial Type: %s\nSpecial: %s\nShield: %s\nWeapon: %s```"%(name, hp, attack, repair, pilot, fire_resistance, stamina, special_type, ability, shield, weapon)
        await ctx.send(phrase)
        return
    if request[1][0] == ' ':
        request[1] = request[1][1:]
    crew0 = process.extractOne(request[0], character_data.crew.keys(), scorer = fuzz.partial_ratio)
    crew1 = process.extractOne(request[1], character_data.crew.keys(), scorer = fuzz.partial_ratio)
    if crew0[1] > prestige_data.search_threshold and crew1[1] > prestige_data.search_threshold:
        crew0 = crew0[0]
        crew1 = crew1[0]
        phrase = "%s and %s were parsed as %s and %s\nAs compared to %s, %s has\n"%(request[0],request[1],crew0,crew1,crew1,crew0)+"```%s - %s\nHP: %s \nPilot: %s \nAttack: %s \nFire Resistance: %s \nRepair: %s \nWeapon: %s \nShield: %s \nEngine: %s \nResearch: %s \nWalking Speed: %s \nRunning Speed: %s\nSpecial Type: %s \nSpecial: %s \nTraining : %s \nEquipment: %s```"%(crew0.title(),crew1.title(),character_data.crew[crew0].hp - character_data.crew[crew1].hp, character_data.crew[crew0].pilot - character_data.crew[crew1].pilot, round(character_data.crew[crew0].attack - character_data.crew[crew1].attack,4), round(character_data.crew[crew0].fire_resistance - character_data.crew[crew1].fire_resistance,5), round(character_data.crew[crew0].repair - character_data.crew[crew1].repair,4), character_data.crew[crew0].weapon - character_data.crew[crew1].weapon, character_data.crew[crew0].shield - character_data.crew[crew1].shield, character_data.crew[crew0].engine - character_data.crew[crew1].engine, character_data.crew[crew0].research - character_data.crew[crew1].research, character_data.crew[crew0].walking_speed - character_data.crew[crew1].walking_speed, character_data.crew[crew0].running_speed - character_data.crew[crew1].running_speed, str(character_data.crew[crew0].special_type)+" vs. "+str(character_data.crew[crew1].special_type), str(character_data.crew[crew0].special)+" vs. "+str(character_data.crew[crew1].special), character_data.crew[crew0].training - character_data.crew[crew1].training, character_data.equipment_loadouts[int(character_data.crew[crew0].equipment)] + " vs. " + character_data.equipment_loadouts[int(character_data.crew[crew1].equipment)])
        await ctx.send(phrase)
        repair0 = character_data.crew[crew0].stats_equip['Repair'][0]
        attack0 = character_data.crew[crew0].stats_equip['Attack'][0]
        pilot0 = character_data.crew[crew0].stats_equip['Pilot'][0]
        fire_resistance0 = character_data.crew[crew0].stats_equip['FireResistance'][0]
        hp0 = character_data.crew[crew0].stats_equip['Hp'][0]
        stamina0 = character_data.crew[crew0].stats_equip['Stamina'][0]
        ability0 = character_data.crew[crew0].stats_equip['Ability'][0]
        shield0 = character_data.crew[crew0].stats_equip['Shield'][0]
        weapon0 = character_data.crew[crew0].stats_equip['Weapon'][0]
        special_type0 = character_data.crew[crew0].special_type
        repair1 = character_data.crew[crew1].stats_equip['Repair'][0]
        attack1 = character_data.crew[crew1].stats_equip['Attack'][0]
        pilot1 = character_data.crew[crew1].stats_equip['Pilot'][0]
        fire_resistance1 = character_data.crew[crew1].stats_equip['FireResistance'][0]
        hp1 = character_data.crew[crew1].stats_equip['Hp'][0]
        stamina1 = character_data.crew[crew1].stats_equip['Stamina'][0]
        ability1 = character_data.crew[crew1].stats_equip['Ability'][0]
        shield1 = character_data.crew[crew1].stats_equip['Shield'][0]
        weapon1 = character_data.crew[crew1].stats_equip['Weapon'][0]
        special_type1 = character_data.crew[crew1].special_type
        phrase = "When equipment and training are involved, those values could potentially be:\n```\n%s - %s\nHP: %s\nAttack: %s\nRepair: %s\nPilot: %s\nFire Resistance: %s\nStamina: %s\nSpecial Type: %s vs. %s\nSpecial: %s vs. %s\nShield: %s\nWeapon: %s```"%(crew0.title(), crew1.title(), round(hp0-hp1, 2), round(attack0-attack1,4), round(repair0-repair1,4), round(pilot0-pilot1,4), round(fire_resistance0-fire_resistance1,4), round(stamina0-stamina1,3), special_type0, special_type1, ability0, ability1, round(shield0-shield1,4), round(weapon0-weapon1,4))
        await ctx.send(phrase)
        return

@bot.command(aliases=["Equip", 'Equipment', 'equip', 'Item', 'Items', 'item', 'items'])
async def equipment(ctx,*,request : str):
    """Returns information on equipment. Name, Stat, and Type are valid inputs."""
    #This block returns specific equipment entries
    if process.extractOne(request, character_data.equipment_data.Equipment.equipment.keys(), scorer = fuzz.partial_ratio)[1] > search_threshold:
        result = process.extractOne(request, character_data.equipment_data.Equipment.equipment.keys(), scorer = fuzz.token_sort_ratio)[0]
        phrase = ("%s was parsed as **%s**, which is **%s** with value ```%s: %s```"%(request, result, character_data.equipment_data.Equipment.equipment[result].type, character_data.equipment_data.Equipment.equipment[result].parameter_type, character_data.equipment_data.Equipment.equipment[result].value))
        await ctx.send(phrase)
    #This block returns a list of all equipment of one type
    if process.extractOne(request, character_data.equipment_data.Equipment.equipment_types.keys(), scorer = fuzz.partial_ratio)[1] > search_threshold:
        result = process.extractOne(request, character_data.equipment_data.Equipment.equipment_types.keys(), scorer = fuzz.token_sort_ratio)[0]
        phrase = ("%s was parsed as **%s**. All equipment of that type is as follows:"%(request, result) + lined_string(character_data.equipment_data.Equipment.equipment_types[result]))
        await ctx.send(phrase)
    #This block returns a list of all equipement which modifies one stat
    if process.extractOne(request, character_data.equipment_data.Equipment.stat_types.keys(), scorer = fuzz.partial_ratio)[1] > search_threshold:
        result = process.extractOne(request, character_data.equipment_data.Equipment.stat_types.keys(), scorer = fuzz.token_sort_ratio)[0]
        phrase = ("%s was parsed as **%s**. All equipment which modify that parameter are as follows:"%(request, result) + lined_string(character_data.equipment_data.Equipment.stat_types[result]))
        await ctx.send(phrase)
        return
    
@bot.command(aliases=["Crews", 'Crew', 'crews'])
async def crew(ctx,*,request : str):
    """Returns crew which satisfy all parameters"""
    if '=' in request:
        request = request.split(',')
        result = list(character_data.crew.keys())
        question = []
        for pair in request:
            pair = pair.split('=', 1)
            query = process.extractOne(pair[0], character_data.Crew.stratification.keys(), scorer = fuzz.partial_ratio)[0] #returns genders/races/rarities/progression/special_types
            parameter = process.extractOne(pair[1], character_data.Crew.stratification[query].keys(), scorer = fuzz.partial_ratio)[0]
            result = [x for x in character_data.Crew.stratification[query][parameter] if x in result]
            question.append(["%s = %s"%(query, parameter)])
        phrase = ("Crew which meet parameters:" + lined_string(question))
        await ctx.send(phrase)
        phrase = ("Are as follows:" + lined_string(result))
        await ctx.send(phrase)
        return
    if 'help' or 'Help' in request:
        if ',' in request:
            request = request.lower().split(',')
        else:
            await ctx.send("Try ?crew help, (parameter). Possible parameters include ```\n gender, race, rarity, progression, special type```")
        if fuzz.partial_ratio(request[1], 'genders') > search_threshold:
            await ctx.send("Try ?crew gender=(gender). Possible genders include: ```\n%s```"%list(character_data.Crew.stratification['genders'].keys()))
            return
        if fuzz.partial_ratio(request[1], 'races') > search_threshold:
            await ctx.send("Try ?crew race=(race). Possible races include: ```\n%s```"%list(character_data.Crew.stratification['races'].keys()))
            return
        if fuzz.partial_ratio(request[1], 'rarities') > search_threshold:
            await ctx.send("Try ?crew rarity=(rarity). Possible rarities include: ```\n%s```"%list(character_data.Crew.stratification['rarities'].keys()))
            return
        if fuzz.partial_ratio(request[1], 'progressions') > search_threshold:
            await ctx.send("Try ?crew progression=(progression). Possible progressions include: ```\n%s```"%list(character_data.Crew.stratification['progressions'].keys()))
            return
        if fuzz.partial_ratio(request[1], 'special types') > search_threshold:
            await ctx.send("Try ?crew special=(special type). Possible special types include: ```\n%s```"%list(character_data.Crew.stratification['special_types'].keys()))
            
bot.run('Mjc0NDU1NTg5NTY2ODA4MDc2.C2yWMw.uFEcuSxiZRJPp-UkloTvWV0z84Q')
