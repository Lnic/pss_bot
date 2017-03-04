"""import xml.dom.minidom
import urllib.request

with urllib.request.urlopen(r'http://api2.pixelstarships.com/CharacterService/ListAllCharacterDesigns2?languageKey=en') as response:
    pss_api = response.read()

def xml_list(data, tagName):
    data = data.decode(pyxb._InputEncoding) 
    xmlDoc = xml.dom.minidom.parseString(data)
    itemList = []
    itemList = xmlDoc.getElementsByTagName(tagName)
    return itemList

def xml_value(data, attribute):
    value = data.attributes[attribute].value
    value = value.replace(r"'", "&#39;")
    #value = value.encode('utf-8')
    return value

#tags = ps.xml_list(response_from_server, 'Message')
#UserName = ps.xml_value(tags[i], 'UserName')
#Message = ps.xml_value(tags[i], 'Message')
"""
