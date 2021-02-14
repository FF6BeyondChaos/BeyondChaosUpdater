from zipfile import ZipFile
import subprocess
import Constants
import Config
import requests
import shutil
from pathlib import Path


def main():
    print(Constants.UpdaterLaunched)
    print(Constants.CheckINI)
    if Config.checkINI:
        print(Constants.INIFound)
        updateBC()
        updateSprites()
        print(Constants.UpdaterCompleted)
        launchBC()
    else:
        print (Constants.NoINI)
        Config.initConfig()
        updateSprites()
        updateBC()
        print(Constants.UpdaterCompleted)
        launchBC()

def launchBC():
     print(Constants.UpdaterClosing)
     subprocess.run("BeyondChaos.exe", shell=True)
     #wait 3 seconds
     time.sleep(3)

def updateSprites():
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
        print(Constants.UpdaterUnzipping)
        # Extract all the contents of zip file in different directory
        zipObj.extractall("/Custom/")
        #wait 3 seconds
        time.sleep(3)
        print(Constants.UpdateSpriteDone)

def updateBC():
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
        print(Constants.UpdaterUnzipping)
        # Extract all the contents of zip file in different directory
        zipObj.extractall()
        #wait 3 seconds
        time.sleep(3)
        print (Constants.UpdateBCDone)



if __name__ == '__main__':
   main()