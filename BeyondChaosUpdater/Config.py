from configparser import ConfigParser
from pathlib import Path
import os
import requests
import traceback
config = ConfigParser(strict=False)

#plans:
#the updater only will set the version...


def writeConfig():
    try:
        coreVersion = getCoreVersion()
        spriteVersion = getSpriteVersion()
        monsterSpriteVersion = getMonsterSpriteVersion()
        config.read(Path(os.getcwd()+"/config.ini"))
        try:
            config.add_section('Version')
        except Exception:
            #do nothing we know it broke because it doesn't exist
            #todo: turn this somehow into if not exists write it.
            print("Version Section already exists, skipping adding it")
        config.set('Version', 'Core', coreVersion)
        config.set('Version', 'Sprite', spriteVersion)
        config.set('Version', 'Monster Sprite', monsterSpriteVersion)
        #config.set('main', 'key3', 'value3')

        with open(Path(os.getcwd()+"/config.ini"), 'w') as f:
            config.write(f)
    except Exception:
        traceback.print_exc()


def checkINI():
    try:
        my_file = Path(os.getcwd()+"/config.ini")
        if my_file.is_file():
            # file exists
            return True
        else:
            return False
    except Exception:
        traceback.print_exc()

def initConfig():
    try:
        writeConfig()
    except Exception:
        traceback.print_exc()

def getSpriteVersion():
    try:
        x = requests.get('https://api.github.com/repos/FF6BeyondChaos/BeyondChaosSprites/releases/latest').json()   
        version = x['tag_name']
        return version
    except Exception:
        traceback.print_exc()

def getMonsterSpriteVersion():
    try:
        x = requests.get('https://api.github.com/repos/FF6BeyondChaos/BeyondChaosMonsterSprites/releases/latest').json()
        version = x['tag_name']
        return version
    except Exception:
        traceback.print_exc()

def getCoreVersion():
    try:
        x = requests.get('https://api.github.com/repos/FF6BeyondChaos/BeyondChaosRandomizer/releases/latest').json()   
        version = x['tag_name']
        return version
    except Exception:
        traceback.print_exc()