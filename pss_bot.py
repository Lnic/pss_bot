from imp import reload
import time
import discord
from discord.ext import commands
import logging
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
import Levenshtein


search_threshold = 74

logger = logging.getLogger('discord')
logger.setLevel(logging.CRITICAL)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

time_start = time.clock()

import prestige_data

print('Data prep complete. Time Elapsed :'+str(time.clock()-time_start))

import character_data

print('Crew and equipment data prep complete. Time Elapsed :'+str(time.clock()-time_start))


def lined_string(text):
    return "```\n"+"%s\n"*len(text)%tuple(text)+"```\n"


source_check = "\nFeel free to check my prestige source. URL can be requested with ?spreadsheet. Alternatively, \
you can force a refresh operation with ```?refresh```"

#######

description = """A bot designed to relay known information regarding Pixel Starships."""

bot = commands.Bot(command_prefix=['?', '?\ '], description=description, help_attrs={'aliases' : ["CommandList", "Commandlist", "Command List", "command list", "commands", "Commands", "command", "Command", "commandlist"]})


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print('Full prep complete. Time Elapsed :'+str(time.clock()-time_start))
    await bot.change_presence(game=discord.Game(name='try ?help (prestige, recipe, stats, equipment, crew)'))


@bot.command(aliases=["Spreadsheet", "spread", "Spread"], category = 'Sources')
async def spreadsheet():
    """: Returns the URL for the prestige spreadsheet"""
    await bot.say(r"https://docs.google.com/spreadsheets/d/1Sn1yHJVqcN1bJGqhvEitgNSnT2NIS8hSRYqCLAqubKk/edit#gid=1068686197")


@bot.command(aliases=["recipes", "Recipe", "Recipes"])
async def recipe(*,request : str):
    """: 1 crew => Combinations which create that crew ; 1 result, 1 reagent => Combinations which use reagent for result"""
    if request.lower()=='help' or request.lower()=='names':
        await bot.say("Names for prestige results are: "+lined_string(prestige_data.all_prestige_results))
        # +"\*\* = confirmed since December update\n$ = confirmed since March update\n# = rumored\nunmarked = NOT confirmed since December update\nFor combinations which use the input crew, try ?prestige instead")
        return
    if ',' in request:
        names = request.lower().split(',')
        if names[1][0] == ' ':
            names[1] = names[1][1:]
    else:  # This will handle single name requests
        result=[]
        similarity_check = process.extract(request.lower(), request, scorer = fuzz.partial_ratio)#This will try to thin out the results so Demon Boy and Golden Boy don't show up together, etc.
        if similarity_check[0][1] == similarity_check[1][1]:
            sim_check_scorer = fuzz.token_sort_ratio
        else:
            sim_check_scorer = fuzz.partial_ratio
        for combo in prestige_data.prestiges: #Find all prestige combinations that generate the request
            if sim_check_scorer(request.lower(), prestige_data.prestiges[combo]) > prestige_data.search_threshold:
                result.append("%s = %s"%(([combo.title().split('_')][0]),prestige_data.prestiges[combo].title()))
        if result==[]:
            unique_check = process.extractOne(request, prestige_data.uniques, scorer = sim_check_scorer)
            if unique_check[1] > prestige_data.search_threshold:
                await bot.say("%s was parsed as %s which is a unique. Since uniques are obtainable through mineral draws, prestige recipes including elite crew are not recorded."%(request,unique_check[0])+"\nFor combinations which use the input crew, try ?prestige instead")
                return
            await bot.say("There are no recorded recipes for %s"%(request.title())+source_check+"\nFor combinations which use the input crew, try ?prestige instead")
            return
        else:
            phrase = "These combinations are listed as potentially making %s:"%request.title()+lined_string(result)
                     #+"\nConsider double checking your chosen recipe with ?prestige or the spreadsheet listed in ?spreadsheet"+"\n\*\* = confirmed since December update\n$ = confirmed since March update\n# = rumored\nunmarked = NOT confirmed since December update\nFor combinations which use the input crew, try ?prestige instead"
            while len(phrase) > 1950:
                await bot.say(phrase[:phrase.find('[',1600)]+"```")
                phrase = "```"+phrase[phrase.find('[',1600):]
            await bot.say(phrase)
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
            await bot.say("I see no relation between %s and %s"%(names[0].title(),names[1].title())+source_check+"\nFor combinations which use the input crew, try ?prestige instead")
            return
        else:
            phrase = "According to records, pertinent combinations between %s and %s are as follows:"%(names[0].title(),names[1].title())+lined_string(sorted(set([x.title() for x in result])))
            #+"Remember, only Legendary combinations are guaranteed by Savy"+"\n\*\* = confirmed since December update\n$ = confirmed since March update\n# = rumored\nunmarked = NOT confirmed since December update\nFor combinations which use the input crew, try ?prestige instead"
            while len(phrase) > 1950:
                await bot.say(phrase[:phrase.find('[',1600)]+"```")
                phrase = "```"+phrase[phrase.find('[',1600):]
            await bot.say(phrase)
            return
    else:
        phrase = "According to records, pertinent combinations between %s and %s are as follows:"%(names[0].title(),names[1].title())+lined_string(sorted(set([x.title() for x in result])))
        #+"Remember, only Legendary combinations are guaranteed by Savy"+"\n\*\* = confirmed since December update\n$ = confirmed since March update\n# = rumored\nunmarked = NOT confirmed since December update\nFor combinations which use the input crew, try ?prestige instead"
        while len(phrase) > 1950:
                await bot.say(phrase[:phrase.find('[',1600)]+"```")
                phrase = "```"+phrase[phrase.find('[',1600):]
        await bot.say(phrase)
        return


@bot.command(aliases=["names"])
async def namelist(request : str=''):
    print(request)
    """returns a list of valid names"""
    if request.lower()=='legendary' or request.lower()=='legendaries' or request.lower()=='legend':
        await bot.say('The following is a list of all known names of Legendary Crew. I will likely only understand names that are typed as follows:')
        await bot.say(prestige_data.legendaries)
    elif request.lower()=='hero' or request.lower()=='heroes':
        await bot.say('The following is a list of all known names of Hero Crew. I will likely only understand names that are typed as follows:')
        await bot.say(prestige_data.heroes)
    elif request.lower()=='epic' or request.lower()=='epics':
        await bot.say('The following is a list of all known names of Epic Crew. I will likely only understand names that are typed as follows:')
        await bot.say(prestige_data.epics)
    elif request.lower()=='unique' or request.lower()=='uniques':
        await bot.say('The following is a list of all known names of "Unique" Crew. I will likely only understand names that are typed as follows:')
        await bot.say(prestige_data.uniques)
    else:
        await bot.say('Valid inputs include legendary, hero, epic, or unique')


@bot.command(aliases=["Prestige"])
async def prestige(*,request : str):
    """: 1 crew => Combinations which use crew as reagent ; crew, crew => Single combination using given crew"""
    if ',' in request:
        names = request.lower().split(',')
    else: #If there's only one name, this tree will handle it. It will try to give all receipes for the one crew member
        result = []
        similarity_check = process.extract(request.lower(), request, scorer = fuzz.partial_ratio)#This will try to thin out the results so Demon Boy and Golden Boy don't show up together, etc.
        if similarity_check[0][1] == similarity_check[1][1]:
            sim_check_scorer = fuzz.token_sort_ratio
        else:
            sim_check_scorer = fuzz.partial_ratio
        crew = process.extractOne(request.lower(), character_data.crew.keys(), scorer = sim_check_scorer)
        name = crew[0]
        pattern = re.compile("^" + name + "_")
        for combo in prestige_data.prestiges:
            if prestige_data.prestiges[combo] and process.extractOne(request.lower(),combo.lower().split('_'), scorer = sim_check_scorer)[1] > prestige_data.search_threshold and re.match(pattern, combo):
                    result.append("%s = %s"%(([combo.title().split('_')][0]),prestige_data.prestiges[combo].title()))
        if result.__len__() == 0 : #This is for inputs with no recipes
            rarity = character_data.crew[name].rarity
            if crew[1] > search_threshold:
                if rarity in prestige_data.no_prestige_types:
                    if rarity == "Special":
                        phrase = "%s was parsed as **%s** which is %s type crew. Special crew cannot currently be made or used for prestige."%(request, name.title(), rarity)+"\nFor combinations to create the input crew, try ?recipe instead"
                    if rarity == "Legendary":
                        phrase = "%s was parsed as **%s** which is %s type crew. Legendary is the highest tier of crew - therefore there are no combinations which use Legendary crew."%(request, name.title(), rarity  )+"\nFor combinations to create the input crew, try ?recipe instead"
                    if rarity == "Common" or rarity == "Elite":
                        phrase = "%s was parsed as **%s** which is %s type crew. Common and Elite crew combinations are not recorded."%(request, name[0].title(), rarity)+"\nFor combinations to create the input crew, try ?recipe instead"
                    await bot.say(phrase)
                    return
                await bot.say("%s was parsed as **%s**. There are no known recipes including %s"%(request, name, name.title()) + source_check+"\nFor combinations to create the input crew, try ?recipe instead")
                return
            await bot.say("Input not quite recognized. The closest entry is ```\n%s``` If this is correct, try again with this spelling."%name.title())
            return
        else:  # This is for valid inputs
            short = sorted(set([x for x in prestige_data.hero+prestige_data.epic+prestige_data.unique if x[0] and name == x[0].lower()][0][1:])) #will return the list which has the target in the 0th position, a column or row in the spreadsheet
            phrase = "%s is listed as being used in:"%(name)+lined_string(short)
            await bot.say(phrase)
            phrase = ("Full recipes are as follows:\n" + lined_string(sorted(set([x.title() for x in result]))))
            #+"\*\* = confirmed since December update\n$ = confirmed since March update\n# = rumored\nunmarked = NOT confirmed since December update"+"\nFor combinations to create the input crew, try ?recipe instead")
            while len(phrase) > 1950:
                await bot.say(phrase[:phrase.find('[',1750)]+"```")
                phrase = "```"+phrase[phrase.find('[',1750):]
            await bot.say(phrase)
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
    await bot.say(phrase)
    phrase = "%s yields:\n```\n%s```"%(key_2,result_2)+"\nFor combinations to create the input crew, try ?recipe instead"
    await bot.say(phrase)


@bot.command(aliases=["Stats", 'stat', 'Stat'])
async def stats(*,request : str):
    """: 1 crew = > Full stats including equipment interactions for requested crew ; crew, crew => Stat comparison between the two crew members"""
    initial_request = request
    if request.lower()=='help':
        await bot.say("Give a crew name or a crew name and a stat separated by a comma. All stats will be given if no specific stat is provided. Valid names can be found with ?stat names. Valid stats are ```gender, race, hp, pilot, attack, fire_resistance, repair, weapon, shield, engine, research, walking_speed, running_speed, rarity, progression, xp, special_type, special, training, and equipment.```")
        return
    if request.lower()=='equip' or request.lower()=='equipment':
        await bot.say("```%s```"%(character_data.equipment_loadouts))
        return
    if request.lower()=='names':
        await bot.say("Valid names are: ```%s```"%(character_data.crew.keys()))
        return
    if ',' in request:
        request = request.lower().split(',')
    else:  # This block handles single crew queries
        similarity_check = process.extract(request, character_data.crew.keys(), scorer = fuzz.partial_ratio)
        if similarity_check[0][1] == similarity_check[1][1]:
            request = process.extractOne(request, character_data.crew.keys(), scorer = fuzz.token_sort_ratio)[0]
        else:            
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
        await bot.say(phrase)
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
        await bot.say(phrase)
        return
    if request[1][0] == ' ':
        request[1] = request[1][1:]
    similarity_check = process.extract(request[0], character_data.crew.keys(), scorer = fuzz.partial_ratio) #Moving forward, this will handle crew comparisons
    if similarity_check[0][1] == similarity_check[1][1]:
        crew0 = process.extractOne(request[0], character_data.crew.keys(), scorer = fuzz.token_sort_ratio)
    else:            
        crew0 = process.extractOne(request[0], character_data.crew.keys(), scorer = fuzz.partial_ratio)
    similarity_check = process.extract(request[1], character_data.crew.keys(), scorer = fuzz.partial_ratio)
    if similarity_check[0][1] == similarity_check[1][1]:
        crew1 = process.extractOne(request[1], character_data.crew.keys(), scorer = fuzz.token_sort_ratio)
    else:            
        crew1 = process.extractOne(request[1], character_data.crew.keys(), scorer = fuzz.partial_ratio)
    if crew0[1] > prestige_data.search_threshold and crew1[1] > prestige_data.search_threshold:
        crew0 = crew0[0]
        crew1 = crew1[0]
        phrase = "%s and %s were parsed as %s and %s\nAs compared to %s, %s has\n"%(request[0],request[1],crew0,crew1,crew1,crew0)+"```%s - %s\nHP: %s \nPilot: %s \nAttack: %s \nFire Resistance: %s \nRepair: %s \nWeapon: %s \nShield: %s \nEngine: %s \nResearch: %s \nWalking Speed: %s \nRunning Speed: %s\nSpecial Type: %s \nSpecial: %s \nTraining : %s \nEquipment: %s```"%(crew0.title(),crew1.title(),character_data.crew[crew0].hp - character_data.crew[crew1].hp, character_data.crew[crew0].pilot - character_data.crew[crew1].pilot, round(character_data.crew[crew0].attack - character_data.crew[crew1].attack,4), round(character_data.crew[crew0].fire_resistance - character_data.crew[crew1].fire_resistance,5), round(character_data.crew[crew0].repair - character_data.crew[crew1].repair,4), character_data.crew[crew0].weapon - character_data.crew[crew1].weapon, character_data.crew[crew0].shield - character_data.crew[crew1].shield, character_data.crew[crew0].engine - character_data.crew[crew1].engine, character_data.crew[crew0].research - character_data.crew[crew1].research, character_data.crew[crew0].walking_speed - character_data.crew[crew1].walking_speed, character_data.crew[crew0].running_speed - character_data.crew[crew1].running_speed, str(character_data.crew[crew0].special_type)+" vs. "+str(character_data.crew[crew1].special_type), str(character_data.crew[crew0].special)+" vs. "+str(character_data.crew[crew1].special), character_data.crew[crew0].training - character_data.crew[crew1].training, character_data.equipment_loadouts[int(character_data.crew[crew0].equipment)] + " vs. " + character_data.equipment_loadouts[int(character_data.crew[crew1].equipment)])
        await bot.say(phrase)
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
        await bot.say(phrase)
        return


@bot.command(aliases=["Equip", 'Equipment', 'equip', 'Item', 'Items', 'item', 'items'])
async def equipment(*,request : str):
    """: request => Returns all entries which match the request
        types = Accessory, Head, Body, Leg, Weapon
        stats = Attack, Repair, HP, Weapon, Pilot, Shield, Stamina, Fire Resistance, Ability
        name = specific names of equipment (e.g. Assault Armor, Combat Pants, etc.)"""
    # This block returns specific equipment entries
    if process.extractOne(request, character_data.equipment_data.Equipment.equipment.keys(), scorer = fuzz.partial_ratio)[1] > search_threshold:
        result = process.extractOne(request, character_data.equipment_data.Equipment.equipment.keys(), scorer = fuzz.token_sort_ratio)[0]

        # Get the recipe and format it as text
        full_recipe = character_data.equipment_data.Equipment.equipment[result].ingredients
        ingredients = full_recipe.split("|")
        recipe = 'Created from: ```'

        first = True
        for ingredient in ingredients:
            artifact = character_data.equipment_data.item_id_map[ingredient.split("x")[0]]
            quantity = ingredient.split("x")[1]
            if first:
              recipe = recipe + "\n\t" + quantity + " x " + artifact
              first = False
            else:
              recipe = recipe + "\n  & " + quantity + " x " + artifact


        recipe = recipe + "```"
        phrase = ("%s was parsed as **%s**, which is **%s** with value ```%s: %s``` \n %s "%(request, result, character_data.equipment_data.Equipment.equipment[result].type, character_data.equipment_data.Equipment.equipment[result].parameter_type, character_data.equipment_data.Equipment.equipment[result].value, recipe))
        await bot.say(phrase)
    # This block returns a list of all equipment of one type
    if process.extractOne(request, character_data.equipment_data.Equipment.equipment_types.keys(), scorer = fuzz.partial_ratio)[1] > search_threshold:
        result = process.extractOne(request, character_data.equipment_data.Equipment.equipment_types.keys(), scorer = fuzz.token_sort_ratio)[0]
        phrase = ("%s was parsed as **%s**. All equipment of that type is as follows:"%(request, result) + lined_string(character_data.equipment_data.Equipment.equipment_types[result]))
        await bot.say(phrase)
    # This block returns a list of all equipment which modifies one stat
    if process.extractOne(request, character_data.equipment_data.Equipment.stat_types.keys(), scorer = fuzz.partial_ratio)[1] > search_threshold:
        result = process.extractOne(request, character_data.equipment_data.Equipment.stat_types.keys(), scorer = fuzz.token_sort_ratio)[0]
        phrase = ("%s was parsed as **%s**. All equipment which modify that parameter are as follows:"%(request, result) + lined_string(character_data.equipment_data.Equipment.stat_types[result]))
        await bot.say(phrase)
        return


@bot.command(aliases=["Crews", 'Crew', 'crews'])
async def crew(*,request : str):
    """: try ?crew help
       example: ```?crew race = white, rarity = hero```"""
    if '=' in request:
        request = request.split(',') # splits parameter=value entries by ','
        roster = list(character_data.crew.keys())
        result = list(character_data.crew.keys())
        question = []
        for pair in request:
            pair = pair.split('=', 1) # parses parameter=value entries with '='
            parameter = process.extractOne(pair[0], character_data.Crew.stratification.keys(), scorer = fuzz.token_set_ratio)[0] # returns genders/races/rarities/progression/special_types/equipment
            interim = process.extract(pair[1], character_data.Crew.stratification[parameter].keys(), scorer = fuzz.token_set_ratio)
            value = [x[0] for x in interim if x[1] == interim[0][1]] # likely just one thing, but may have multiple equipment types
            passed = []
            for entry in value:
                [passed.append(x) for x in character_data.Crew.stratification[parameter][entry] if x not in passed]
                print(passed)
            [result.remove(x) for x in roster if x in result and x not in passed]
            print(len(result))
            question.append(["%s = %s"%(parameter, value)])
        print(len(result))
        phrase = ("Crew with values:" + lined_string(question))
        await bot.say(phrase)
        phrase = ("Are as follows:" + lined_string(result))
        await bot.say(phrase)
        return
    if 'help' or 'Help' in request:
        if ',' in request:
            request = request.lower().split(',')
        else:
            await bot.say("Try ?crew help, (parameter). Possible parameters include ```\n gender, race, rarity, progression, special type```")
        if fuzz.partial_ratio(request[1], 'genders') > search_threshold:
            await bot.say("Try ?crew gender=(gender). Possible genders include: ```\n%s```"%list(character_data.Crew.stratification['genders'].keys()))
            return
        if fuzz.partial_ratio(request[1], 'races') > search_threshold:
            await bot.say("Try ?crew race=(race). Possible races include: ```\n%s```"%list(character_data.Crew.stratification['races'].keys()))
            return
        if fuzz.partial_ratio(request[1], 'rarities') > search_threshold:
            await bot.say("Try ?crew rarity=(rarity). Possible rarities include: ```\n%s```"%list(character_data.Crew.stratification['rarities'].keys()))
            return
        if fuzz.partial_ratio(request[1], 'progressions') > search_threshold:
            await bot.say("Try ?crew progression=(progression). Possible progressions include: ```\n%s```"%list(character_data.Crew.stratification['progressions'].keys()))
            return
        if fuzz.partial_ratio(request[1], 'special types') > search_threshold:
            await bot.say("Try ?crew special=(special type). Possible special types include: ```\n%s```"%list(character_data.Crew.stratification['special_types'].keys()))
        if fuzz.partial_ratio(request[1], 'equipment') > search_threshold:
            await bot.say("Try ?Crew equipment=(slots). Possible equipment loadouts include: ```\n%s```"%list(character_data.Crew.stratification['equipment'].keys()))


@bot.command(aliases=["Refresh", 'Reload', 'reload'])
async def refresh(*,request : str=''):
    """Refreshes prestige information"""
    await bot.say("Refresh operation attempted. PSS Bot functions will be unavailable for 1-10 minutes.")
    reload(prestige_data)
    await bot.say("Prestige data refreshed")
    return

bot.run('')
