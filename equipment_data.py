import urllib.request

source = urllib.request.urlopen(r'http://api.pixelstarships.com/ItemService/ListItemDesigns2?languageKey=en').read()
source = source.decode("utf-8")

item_id_map = {}

class Equipment:

    equipment = {}
    equipment_types = {"EquipmentHead":[], "EquipmentBody":[], "EquipmentLeg":[], "EquipmentWeapon":[], "EquipmentAccessory":[]}
    stat_types = {"Repair":[], "Attack":[], "Pilot":[], "FireResistance":[], "Hp":[], "Stamina":[], "Ability":[], "Shield":[], "Weapon":[], "Engine":[]}


    def __init__(self, source):
        name_start = source.find("ItemDesignName") + len("ItemDesignName") + 2
        self.name = source[name_start:source.find('"', name_start)]
        description_start = source.find("ItemDesignDescription") + len("ItemDesignDescription") + 2
        self.description = source[description_start:source.find('"', description_start)]
        type_start = source.find("ItemSubType") + len("ItemSubType") + 2
        self.type = source[type_start:source.find('"', type_start)] 
        Equipment.equipment_types[self.type].append(self.name)  # Add name to list of like equipment types
        parameter_start = type_start = source.find("EnhancementType") + len("EnhancementType") + 2
        self.parameter_type = source[parameter_start:source.find('"', parameter_start)]
        Equipment.stat_types[self.parameter_type].append(self.name)  # Add name to list of equipment which improve the same stat
        value_start = source.find("EnhancementValue") + len("EnhancementValue") + 2
        self.value = source[value_start:source.find('"', value_start)]
        stats = {"Repair":0, "Attack":0, "Pilot":0, "FireResistance":0, "Hp":0, "Stamina":0, "Ability":0, "Shield":0, "Weapon":0, "Engine":0}
        stats[self.parameter_type] = self.value  # update the stat dictionary with the proper value

        # Add-on for equipments recipes   - Lnic
        ingredients_start = source.find("Ingredients") + len("Ingredients") + 2
        self.ingredients = source[ingredients_start:source.find('"', ingredients_start)]
        ingredients = {}
        ingredients[self.name] = self.ingredients

        itemid_start = source.find("ItemDesignId") + len("ItemDesignId") + 2
        self.itemid = source[itemid_start:source.find('"', itemid_start)]
        itemid = {}
        itemid[self.name] = self.itemid

        rarity_start = source.find("Rarity") + len("Rarity") + 2
        self.rarity = source[rarity_start:source.find('"', rarity_start)]

while source.find("ItemDesign ", 1) > 0:  # This block will create all crew equipment entries
    source = source[source.find("ItemDesign ", 1):]
    type_start = source.find("ItemType")
    item_type = source[type_start + 10:source.find('"', type_start + 10)]
    name_start = source.find("ItemDesignName") + len("ItemDesignName") + 2
    sub_start = source.find("ItemSubType") + len("ItemSubType") + 2
    sub_type = source[sub_start:source.find('"', sub_start)]

    itemid_start = source.find("ItemDesignId") + len("ItemDesignId") + 2
    item_id_map[source[itemid_start:source.find('"', itemid_start)]] = source[name_start:source.find('"', name_start)]
    if item_type != "Equipment" or sub_type not in Equipment.equipment_types:
        continue
    else:
        Equipment.equipment[source[name_start:source.find('"', name_start)]] = Equipment(source)



#for equip in Equipment.equipment:
#     print(equip)
#     print(Equipment.equipment[equip].itemid)
#print(item_id_map)


        # Make an entry in the equipment dictionary for self

max_augment = {"EquipmentHead":{"Repair":[], "Attack":[], "Pilot":[], "FireResistance":[], "Hp":[], "Stamina":[], "Ability":[], "Shield":[], "Weapon":[], "Engine":[]}, "EquipmentBody":{"Repair":[], "Attack":[], "Pilot":[], "FireResistance":[], "Hp":[], "Stamina":[], "Ability":[], "Shield":[], "Weapon":[], "Engine":[]}, "EquipmentLeg":{"Repair":[], "Attack":[], "Pilot":[], "FireResistance":[], "Hp":[], "Stamina":[], "Ability":[], "Shield":[], "Weapon":[], "Engine":[]}, "EquipmentWeapon":{"Repair":[], "Attack":[], "Pilot":[], "FireResistance":[], "Hp":[], "Stamina":[], "Ability":[], "Shield":[], "Weapon":[], "Engine":[]}, "EquipmentAccessory":{"Repair":[], "Attack":[], "Pilot":[], "FireResistance":[], "Hp":[], "Stamina":[], "Ability":[], "Shield":[], "Weapon":[], "Engine":[]}}
# The above dictionary has entries for each equipment slot in the top level
# Each of those then has another slot for each parameter augment type
# The goal will be to have one entry for each, the max level entry

for slot in max_augment:
    for stat in max_augment[slot]:  # List comprehension below will give equipment of a slot and stat type
        entry = [x for x in Equipment.equipment if x in Equipment.equipment_types[slot] and x in Equipment.stat_types[stat]]
        if not entry:
            continue  # next line will give value associated with the equipment
        values = [Equipment.equipment[x].value for x in entry]
        zipped = zip(values, entry)
        max_augment[slot][stat] = sorted(zipped, key=lambda x:float(x[0]))[-1]
