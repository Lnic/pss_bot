import urllib.request
import equipment_data

def finder(target, source):
    return source[source.find(target)+len(target)+1:source.find('"',source.find(target)+len(target)+2)]

class Crew:

    stratification = {'genders':{}, 'races': {}, 'rarities':{}, 'progressions':{}, 'special_types':{}}

    def __init__(self, source, name):
        '''Crew from Pixel Starships'''
        #self.name = finder("CharacterDesignName=",source)
        self.name = name
        self.gender = finder("GenderType=",source)
        self.race = finder("RaceType=",source)
        self.hp = float(finder("FinalHp=",source))
        self.pilot = float(finder("FinalPilot=",source))
        self.attack = float(finder("FinalAttack=",source))
        self.fire_resistance = float(finder("FireResistance=",source))
        self.repair = float(finder("FinalRepair=",source))
        self.weapon = float(finder("FinalWeapon=",source))
        self.shield = float(finder("FinalShield=",source))
        self.engine = float(finder("FinalEngine=",source))
        self.research = float(finder("FinalResearch=",source))
        self.walking_speed = float(finder("WalkingSpeed=",source))
        self.running_speed = float(finder("RunSpeed=",source))
        self.rarity = finder("Rarity=",source)
        self.progression = finder("ProgressionType=",source)
        self.xp = finder("XpRequirementScale=",source)
        self.special_type = finder("SpecialAbilityType=",source)
        self.special = float(finder("SpecialAbilityFinalArgument=",source))
        self.training = float(finder("TrainingCapacity=",source))
        self.equipment = finder("EquipmentMask=",source)
        if self.equipment == "8":
            self.slots = ["EquipmentWeapon"]
        else:
            self.slots = equipment_loadouts[int(self.equipment)].split(' and ')
            for entry in range(len(self.slots)):
                self.slots[entry] = 'Equipment'+self.slots[entry]
        self.stats_equip = {"Repair":[self.repair, ''], "Attack":[self.attack*1.5, '+ 50% Training'], "Pilot":[self.pilot, ''], "FireResistance":[self.fire_resistance , ''], "Hp":[self.hp*1.5, '+ 50% Training'], "Stamina":[50, '+ 50 Training'], "Ability":[50, '+ 50% Training'], "Shield":[self.shield, ''], "Weapon":[self.weapon, '']}
        for slot in self.slots: #Training values are assumed to be 50. Ability will need to be divided by 100 and then multiplied by self.special
            for stat in equipment_data.max_augment[slot]: #Individual stats
                if equipment_data.max_augment[slot][stat]: #If something's there, add it
                    self.stats_equip[stat][0] += float(equipment_data.max_augment[slot][stat][0])
                    self.stats_equip[stat][1] += " + " + equipment_data.max_augment[slot][stat][1]
                    self.stats_equip[stat][0] = round(self.stats_equip[stat][0], 5)
        self.stats_equip["Ability"][0] = round((1+(self.stats_equip["Ability"][0]*.01))*self.special, 5)
        if self.race not in Crew.stratification['races']:
            Crew.stratification['races'][self.race] = [self.name]
        else:
            Crew.stratification['races'][self.race].append(self.name)
        if self.gender not in Crew.stratification['genders']:
            Crew.stratification['genders'][self.gender] = [self.name]
        else:
            Crew.stratification['genders'][self.gender].append(self.name)
        if self.rarity not in Crew.stratification['rarities']:
            Crew.stratification['rarities'][self.rarity] = [self.name]
        else:
            Crew.stratification['rarities'][self.rarity].append(self.name)
        if self.special_type not in Crew.stratification['special_types']:
            Crew.stratification['special_types'][self.special_type] = [self.name]
        else:
            Crew.stratification['special_types'][self.special_type].append(self.name)
        if self.progression not in Crew.stratification['progressions']:
            Crew.stratification['progressions'][self.progression] = [self.name]
        else:
            Crew.stratification['progressions'][self.progression].append(self.name)

crew={}
metrics=['name','gender','race','hp','pilot','attack','fire_resistance','repair','weapon','shield','engine','research','walking_speed','running_speed','rarity','progression','xp','special_type','special','training','equipment']
equipment_loadouts={6:'Body and Leg', 24:'Accessory and Weapon', 5:'Head and Leg', 8:'Weapon', 9:'Head and Weapon', 10:'Body and Weapon', 12:'Weapon and Leg', 3:'Head and Body'}
crew_names = [x.name for x in crew]

def all_crew_values(source):
    text=source[:]
    while len(text)>0:
        if text.find(r"/CharacterDesign>")>0:
            name=(str(finder("CharacterDesignName=",text)).lower())
            crew[name]=Crew(text,str(name))
            text=text[text.find(r"/CharacterDesign>")+len(r"/CharacterDesign>")+1:]
        else:
            break

#pss_api=open("ListAllCharacterDesigns2.txt","r+").read() #If ever I need to switch to offline character data
with urllib.request.urlopen(r'http://api2.pixelstarships.com/CharacterService/ListAllCharacterDesigns2?languageKey=en') as response: #I needed to switch back to the 'older' one
#with urllib.request.urlopen(r'https://api.pixelstarships.com/CharacterService/ListAllCharacterDesigns2?languageKey=en') as response: #This is the newer url, apparently
    pss_api = response.read()
pss_api = pss_api.decode("utf-8")
all_crew_values(pss_api)
