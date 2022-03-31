import platform
from zipfile import ZipFile
from configparser import ConfigParser
import shutil
import os
import time
import sys
import tempfile
from pathlib import Path

# This is not part of the stdlib
try:
    import requests
except ImportError:
    sys.exit("Please install the `requests` python package "
             "before running updater. Try `pip install requests`.")

import remonstrate_utils

__version__ = "1.3.0"

DEFAULT_CONFIG = """
[Version]
Core=0.0.0
Sprite=0.0.0
Monster Sprite=0.0.0
"""

def write_default_config(fname="config.ini"):
    with open(fname, "w") as fout:
        print(DEFAULT_CONFIG, file=fout)

_BASE_PROJ_URL = 'https://api.github.com/repos/FF6BeyondChaos/'
_ASSET_URLS = {
    "updater": os.path.join(_BASE_PROJ_URL, 'BeyondChaosUpdater/releases/latest'),
    "core": os.path.join(_BASE_PROJ_URL, 'BeyondChaosRandomizer/releases/latest'),
    "sprite": os.path.join(_BASE_PROJ_URL, 'BeyondChaosSprites/releases/latest'),
    "monster_sprite": os.path.join(_BASE_PROJ_URL, 'BeyondChaosMonsterSprites/releases/latest')
}
def get_version(asset):
    resp = requests.get(_ASSET_URLS[asset])
    # check request result
    if not resp.ok:
        sys.exit(f"GitHub returned a bad response. Details:\n{resp.reason}")
    x = resp.json()
    return x['tag_name']

def update_version(asset, dst=None):
    x = requests.get(_ASSET_URLS[asset]).json()
    # get the link to download the latest package
    download_link = x['assets'][0]['browser_download_url']
    # download the file and save it.
    tmpdir = tempfile.mkdtemp()
    local_filename = os.path.join(tmpdir, download_link.split('/')[-1])
    with requests.get(download_link, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    dst = dst or os.getcwd()
    with ZipFile(local_filename, 'r') as zip_obj:
        # Extract all the contents of zip file in different directory
        if not os.path.exists(dst):
            os.makedirs(dst)
        zip_obj.extractall(dst)
        # wait 3 seconds
        time.sleep(3)
        print(f"Updater has updated the randomizer {asset}")

    return local_filename, x['tag_name']

def update_updater():
    print("Updater is updating the randomizer updater")
    update_version("updater", None)
    print("Updater has downloaded the newest version of the updater as a .zip file. Please unzip and use this newest file. Quitting updater.")

def update_monster_sprites(config):
    print("Updater is updating the randomizer monster sprites")
    _, tag = update_version("monster_sprite", "remonsterate")
    config.set('Version', 'Monster Sprite', tag)
    print("Updater has updated the randomizer monster sprites")

def update_sprites(config):
    print("Updater is updating the randomizer sprites")
    _, tag = update_version("sprite", "custom")
    config.set('Version', 'Sprite', tag)
    print("Updater has updated the randomizer sprites")

def update_beyond_chaos(config):
    print("\n\nWould you like to update the Beyond Chaos core files? "
          "This will download the latest stable release from "
          "GitHub, replacing the version of Beyond Chaos you are currently running.")
    choice = input("Y/N: ")
    if choice.lower() == "y":
        _, tag = update_version("core")
        config.set('Version', 'Core', tag)
        print("Updater has updated the randomizer core")
    else:
        print("Core update skipped.")

def launch_beyond_chaos():
    print("Launching Beyond Chaos")
    os.startfile('BeyondChaos.exe')
    # wait 3 seconds
    time.sleep(3)

def main(config_path=Path(os.path.join(os.getcwd(), "config.ini"))):
    config = ConfigParser(strict=False)
    running_os = platform.system()

    print("Welcome to the updater, we are starting things up, "
          "please do not close this window!")
    # wait 5 seconds
    print("Waiting 5 seconds for beyondchaos.exe to close")
    time.sleep(5)
    print("Checking to see if config file exists...")
    if os.path.exists(config_path):
        print("Config file was found, running updater.")
        config.read(config_path)
    else:
        print("No config file found, running first setup please wait.")
        write_default_config(config_path)
        config.read(config_path)

    print("Updater is checking for a new version of the randomizer updater")
    if __version__ != get_version("updater"):
        update_updater()
        time.sleep(10)
        sys.exit()
    else:
        print("No update required. You have the most current version!")

    print("Updater is checking for a new version of the randomizer core")
    if running_os != "Windows":
        print("Cannot update randomizer executable for non-Windows OS.")
    elif config.get('Version', 'Core') != get_version("core"):
        update_beyond_chaos(config)
    else:
        print("No update required. You have the most current version!")

    print("Updater is checking for a new version of the randomizer sprites")
    if config.get('Version', 'Sprite') != get_version("sprite"):
        update_sprites(config)
    else:
        print("No update required. You have the most current version!")

    print("Updater is checking for a new version of the randomizer monster sprites")
    if config.get('Version', 'Monster Sprite') != get_version("monster_sprite"):
        update_remonsterate(config)
    else:
        print("No update required. You have the most current version!")

    print("Rewriting updated version information to configuration.")
    with open(config_path, 'w') as fout:
        config.write(fout)

    print("Update completed all update tasks!")
    if running_os == "Windows":
        launch_beyond_chaos()
    else:
        print("Non-Windows OS detected, bypassing executable launch")

def update_remonsterate(config):
    # Create the remonsterate directory in the game directory
    base_directory = os.path.join(os.getcwd(), 'remonsterate')
    sprite_directory = os.path.join(base_directory, "sprites")
    image_file = os.path.join(base_directory, "images_and_tags.txt")
    monster_file = os.path.join(base_directory, "monsters_and_tags.txt")

    os.makedirs(base_directory)
    print("Remonsterate directory created.")

    os.makedirs(sprite_directory)
    print("Sprites directory created in remonsterate.")

    update_monster_sprites(config)

    # Generate images_and_tags.txt file for remonsterate based on the sprites in the sprites folder
    tag_file = os.path.join(os.getcwd(), 'remonsterate\\images_and_tags.txt')
    try:
        remonstrate_utils.construct_tag_file_from_dirs(sprite_directory, tag_file)
        print("New images_and_tags file created in remonsterate.")
    except IOError as e:
        remonstrate_utils.generate_tag_file(tag_file)
        if not os.path.isfile(image_file):
            print("Template images_and_tags file created in remonsterate.")

    tag_file = os.path.join(os.getcwd(), 'remonsterate\\monsters_and_tags.txt')
    if not os.path.isfile(monster_file):
        remonstrate_utils.generate_sample_monster_list(tag_file)
        print("Template monsters_and_tags file created in remonsterate.")

if __name__ == '__main__':
    main()
    time.sleep(3)
