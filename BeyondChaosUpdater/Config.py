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
        config.read(Path(os.getcwd()+"/config.ini"))
        config.set('Version', 'Core', coreVersion)
        config.set('Version', 'Sprite', spriteVersion)
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
        CoreVersion = getCoreVersion()
        SpriteVersion = getSpriteVersion()
        writeConfig(CoreVersion, SpriteVersion)
    except Exception:
        traceback.print_exc()

def getSpriteVersion():
    try:
        x = requests.get('https://api.github.com/repos/FF6BeyondChaos/BeyondChaosSprites/releases/latest').json()   
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