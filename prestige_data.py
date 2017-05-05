import gspread
from oauth2client.service_account import ServiceAccountCredentials

search_threshold = 74

scope = [r'https://spreadsheets.google.com/feeds']

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
sub_hero = [x[0].lower() for x in hero if x[0]]
sub_epic = [x[0].lower() for x in epic if x[0]]
sub_unique = [x[0].lower() for x in unique if x[0]]

add_to_prestiges(heroes,hero)
legendaries=list(set([x.lower() for x in prestiges.values()]))
add_to_prestiges(epics,epic)
add_to_prestiges(uniques,unique)
all_prestige_results = sorted(set([prestiges[combo] for combo in prestiges]))
all_names = sub_hero+sub_epic+sub_unique+legendaries
no_prestige_types = ["Common", "Elite", "Special", "Legendary"]

def lined_string(text):
    return "```\n"+"%s\n"*len(text)%tuple(text)+"```"

