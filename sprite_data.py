import urllib.request

source = urllib.request.urlopen(r'http://api.pixelstarships.com/FileService/ListSprites?languageKey=en').read()
source = source.decode("utf-8")

sprite_id_map = {}

while source.find("Sprite ", 1) > 0:  # This block will create all crew equipment entries

    source = source[source.find("Sprite ", 1):]
    spriteid_start = source.find("SpriteId") + len("SpriteId") + 2
    imagefileid_start = source.find("ImageFileId") + len("ImageFileId") + 2

    sprite_id_map[source[spriteid_start:source.find('"', spriteid_start)]] = source[imagefileid_start:source.find('"', imagefileid_start)]

#print(sprite_id_map['4'])

