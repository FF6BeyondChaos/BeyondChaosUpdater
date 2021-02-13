from zipfile import ZipFile
import subprocess
import Constants
from pathlib import Path


def main():
    print(Constants.UpdaterLaunched)
    updateBC()
    updateSprites()
    launchBC()

def launchBC():
     print(Constants.UpdaterClosing)
     subprocess.run("BeyondChaos.exe", shell=True)
     #wait 3 seconds
     time.sleep(3)

def updateSprites():
    my_file = Path("Sprites.zip")
    if my_file.is_file():
        with ZipFile('Sprites.zip', 'r') as zipObj:
           print(Constants.UpdaterUnzipping)
           # Extract all the contents of zip file in different directory
           zipObj.extractall("/Custom/")
           #wait 3 seconds
           time.sleep(3)
           print(Constants.UpdaterCompleted)
          
    
    else:
        print(Constants.UpdaterSpriteError)
        time.sleep(3)

def updateBC():
    my_file = Path("BeyondChaos.zip")
    if my_file.is_file():
        with ZipFile('BeyondChaos.zip', 'r') as zipObj:
           print(Constants.UpdaterUnzipping)
           # Extract all the contents of zip file in different directory
           zipObj.extractall()
           #wait 3 seconds
           time.sleep(3)
           print(Constants.UpdaterCompleted)
    
    else:
        print(Constants.UpdaterBCError)
        time.sleep(3)

if __name__ == '__main__':
   main()