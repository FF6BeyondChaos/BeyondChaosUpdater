from zipfile import ZipFile
import subprocess
import Constants
import Config
import requests
import time
import shutil
import os
import time
import traceback
from pathlib import Path


def main():
    try:
        print(Constants.UpdaterLaunched)
        #wait 3 seconds
        print(Constants.wait)
        time.sleep(5)
        print(Constants.CheckINI)
        if Config.checkINI():
            print(Constants.INIFound)
            updateBC()
            updateSprites()
            Config.writeConfig()
            print(Constants.UpdaterCompleted)
            launchBC()
        else:
            print (Constants.NoINI)
            Config.initConfig()
            updateSprites()
            updateBC()
            print(Constants.UpdaterCompleted)
            launchBC()
    except Exception:
        traceback.print_exc()

def launchBC():
    try:
        print(Constants.UpdaterClosing)
        os.startfile('BeyondChaos.exe')
        #wait 3 seconds
        time.sleep(3)
    except Exception:
        traceback.print_exc()

def updateSprites():
    try:
        my_file = Path("Sprites.zip")
        if my_file.is_file() == False:
            #go get the sprites
            #ping github and get the new released version
            x = requests.get('https://api.github.com/repos/FF6BeyondChaos/BeyondChaosSprites/releases/latest').json() 
            # get the link to download the latest package
            downloadlink = x['assets'][0]['browser_download_url']
            #download the file and save it.
            local_filename = downloadlink.split('/')[-1]
            with requests.get(downloadlink, stream=True) as r:
                with open(local_filename, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            time.sleep(3)
        with ZipFile('Sprites.zip', 'r') as zipObj:
            print(Constants.UpdateSprites)
            # Extract all the contents of zip file in different directory
            zipObj.extractall(os.getcwd()+"/Custom/")
            #wait 3 seconds
            time.sleep(3)
            print(Constants.UpdateSpriteDone)
    except Exception:
        traceback.print_exc()

def updateBC():
    try:
        print (Constants.UpdateBC)
        my_file = Path("BeyondChaos.zip")
        if my_file.is_file() == False:
            #go get the sprites
            #ping github and get the new released version
            x = requests.get('https://api.github.com/repos/FF6BeyondChaos/BeyondChaosRandomizer/releases/latest').json() 
            # get the link to download the latest package
            downloadlink = x['assets'][0]['browser_download_url']
            #download the file and save it.
            local_filename = downloadlink.split('/')[-1]
            with requests.get(downloadlink, stream=True) as r:
                with open(local_filename, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            time.sleep(3)
        
        with ZipFile('BeyondChaos.zip', 'r') as zipObj:
            # Extract all the contents of zip file in different directory
            zipObj.extractall(os.getcwd())
            #wait 3 seconds
            time.sleep(3)
            print (Constants.UpdateBCDone)
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
   main()
   time.sleep(3)