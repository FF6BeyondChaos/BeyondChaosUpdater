from configparser import ConfigParser
from pathlib import Path
import os
config = ConfigParser()

#plans:
#the updater only will set the version...
CoreVersion = ""
SpriteVersion = ""

def writeConfig():
    config.read(os.getcwd()+'config.ini')
    config.add_section('Version')
    config.set('Version', 'Core', CoreVersion)
    config.set('Version', 'Sprite', SpriteVersion)
    #config.set('main', 'key3', 'value3')

    with open('config.ini', 'w') as f:
        config.write(f)

def readConfig():
    config.read(os.getcwd()+'config.ini')
    CoreVersion = config.get('Version', 'Core') # -> "value1"
    SpriteVersion= config.get('Version', 'Sprite') # -> "value2"
    #print config.get('main', 'key3') # -> "value3"


def checkINI():
    my_file = Path("config.ini")
    if my_file.is_file():
        # file exists
        return True
    else:
        return False

def initConfig():
    getCoreVersion()
    getSpriteVersion()
    writeConfig()

def getSpriteVersion():
    x = requests.get('https://api.github.com/repos/FF6BeyondChaos/BeyondChaosSprites/releases/latest').json()   
    SpriteVersion = x['tag_name']

def getCoreVersion():
    x = requests.get('https://api.github.com/repos/BeyondChaos/BeyondChaosRandomizer/releases/latest').json()   
    CoreVersion = x['tag_name']