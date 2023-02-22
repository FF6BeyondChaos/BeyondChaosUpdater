import configparser
import platform
import time
import shutil
import os
import sys
import tempfile
import remonstrate_utils
import subprocess
from configparser import ConfigParser
from pathlib import Path

# This is not part of the stdlib
try:
    import requests
except ImportError:
    sys.exit("Please install the `requests` python package "
             "before running updater. Try `pip install requests`.")
try:
    import psutil
except ImportError:
    sys.exit("Please install the `psutil` python package "
             "before running updater. Try `pip install psutil`.")

__version__ = "2.1.4"

config = ConfigParser(strict=False)
parent_process_id = [arg[len("-pid "):] for arg in sys.argv if arg.startswith("-pid ")] or None

UPDATER_FILE = os.path.join(os.getcwd(), "beyondchaosupdater.exe")
BACKUP_NAME = UPDATER_FILE + ".old"
_BASE_PROJ_URL = 'https://api.github.com/repos/FF6BeyondChaos/'

# Update: Does this asset require an update?
# Prompt: What should be displayed to the user to confirm the update?
# Location: Where should the asset be downloaded and extracted to?
# URL: What web address is the asset located at?
# Data: The data from the URL, so we don't need to hit the API multiple times.
_ASSETS = {
    "updater": {
        "update": False,
        "prompt": "There is an update available for this updater.\n"
                  "Would you like to download the update from GitHub?\n",
        "location": os.getcwd(),
        "URL": os.path.join(_BASE_PROJ_URL, 'BeyondChaosUpdater/releases/latest'),
        "data": {}
    }
    ,
    "core": {
        "update": False,
        "prompt": "There is an update available for the Beyond Chaos core files.\n"
                  "Would you like to download the update from GitHub?\n"
                  "This will replace the version of Beyond Chaos you are currently running.\n",
        "location": os.getcwd(),
        "URL": os.path.join(_BASE_PROJ_URL, 'BeyondChaosRandomizer/releases/latest'),
        "data": {}
    }
    ,
    "character_sprites": {
        "update": False,
        "prompt": "There is an update available for Beyond Chaos' character sprites.\n"
                  "They are required to use the makeover code.\n"
                  "Would you like to download the new sprites from GitHub?\n",
        "location": os.path.join(os.getcwd(), "custom"),
        "URL": os.path.join(_BASE_PROJ_URL, 'BeyondChaosSprites/releases/latest'),
        "data": {}
    }
    ,
    "monster_sprites": {
        "update": False,
        "prompt": "There is an update available for Beyond Chaos' monster sprites.\n"
                  "They are required to use the remonsterate code.\n"
                  "Would you like to download the new sprites from GitHub?\n",
        "location": os.path.join(os.getcwd(), "remonsterate"),
        "URL": os.path.join(_BASE_PROJ_URL, 'BeyondChaosMonsterSprites/releases/latest'),
        "data": {}
    }
}


def get_version(asset):
    resp = requests.get(_ASSETS[asset]["URL"])
    # check request result
    if not resp.ok:
        print(f"GitHub returned a bad response.\nDetails:{resp.reason}")
        input("Press enter to exit...")
        sys.exit()
    x = resp.json()
    return x['tag_name']


def update_asset_from_web(asset):
    global config
    global parent_process_id
    if not asset == 'updater' and parent_process_id:
        for proc in psutil.process_iter():
            if proc.pid == int(parent_process_id[0]) and proc.name().startswith("BeyondChaos"):
                print("Killing process.")
                proc.kill()
                time.sleep(3)
        if psutil.pid_exists(int(parent_process_id[0])):
            input("Failed to automatically stop BeyondChaos.exe. "
                  "Please exit the program and then press any key. ")
        else:
            parent_process_id = None

    data = _ASSETS[asset]["data"]
    # get the link to download the latest package
    download_link = data['assets'][0]['browser_download_url']
    # download the file and save it.
    temp_dir = tempfile.mkdtemp()
    local_filename = os.path.join(temp_dir, download_link.split('/')[-1])
    with requests.get(download_link, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    if asset == "updater":
        # The currently-running executable cannot be deleted, so we rename it instead
        # Then, we download the latest version from GitHub
        # Finally, we run the newly downloaded exe and exit this older version
        if os.path.exists(BACKUP_NAME):
            os.remove(BACKUP_NAME)
        os.rename(os.path.join(os.getcwd(), "beyondchaosupdater.exe"), BACKUP_NAME)

        # Extract the new update
        remonstrate_utils.extract_archive(local_filename, _ASSETS[asset]["location"] or os.getcwd())

        if config:
            if not config.has_section("Version"):
                config.add_section("Version")
            config.set('Version', asset, data['tag_name'])

        print("The updater has been updated. Restarting...\n")
        subprocess.Popen(args=sys.argv, executable=UPDATER_FILE)
        sys.exit()

    elif asset == "core":
        # Extract the new update
        remonstrate_utils.extract_archive(local_filename, _ASSETS[asset]["location"] or os.getcwd())

        if config:
            if not config.has_section("Version"):
                config.add_section("Version")
            config.set('Version', asset, data['tag_name'])

    if asset == "character_sprites" or asset == "monster_sprites":
        update_sprites = True
        back_up_sprites = False
        if config:
            if config.has_section("Hashes"):
                if config.has_option("Hashes", asset):
                    # Compare the stored hash value with the hash of the existing spritereplacements file
                    if asset == "character_sprites":
                        current_hash = remonstrate_utils.get_directory_hash(_ASSETS[asset]["location"] + "/sprites")
                        current_hash = remonstrate_utils.md5_update_from_file(_ASSETS[asset]["location"] +
                                                                              "/spritereplacements.txt", current_hash)
                    elif asset == "monster_sprites":
                        current_hash = remonstrate_utils.get_directory_hash(_ASSETS[asset]["location"])

                    if not config.get("Hashes", asset) == current_hash.hexdigest():
                        # The asset has been customized
                        prompting = True

                        while prompting:
                            prompting = False
                            print("It appears your " + str.replace(asset, "_", " ") + " have been customized.")
                            print("Would you like to back up the current " + str.replace(asset, "_", " ") +
                                  " folder before updating?")
                            choice = input("'Y' to create backup, "
                                           "'N' to overwrite, or "
                                           "'S' to skip updating the " + str.replace(asset, "_", " ") + ": ")
                            if choice.lower() == "y" or choice.lower() == "yes":
                                back_up_sprites = True
                            elif choice.lower() == "n" or choice.lower() == "no":
                                pass
                            elif choice.lower() == "s":
                                update_sprites = False
                            else:
                                prompting = True
                                print("Please answer Y for yes or N for no.")
                else:
                    # If the hash for the asset does not exist, we can just back up the files to be safe
                    back_up_sprites = True

        if update_sprites:
            if back_up_sprites:
                timestamp = str(time.time())
                shutil.copytree(_ASSETS[asset]["location"], _ASSETS[asset]["location"] + "_backup_" + timestamp)
                # os.rename(_ASSETS[asset]["location"], _ASSETS[asset]["location"] + "_backup_" + timestamp)
                print("Your custom directory has been backed up to " + _ASSETS[asset]["location"] +
                      "_backup_" + timestamp + ".")

            # Extract the new update
            remonstrate_utils.extract_archive(local_filename, _ASSETS[asset]["location"] or os.getcwd())

            # Set the hash of the new character sprites update
            if config:
                if not config.has_section("Hashes"):
                    config.add_section("Hashes")
                if asset == "character_sprites":
                    current_hash = remonstrate_utils.get_directory_hash(_ASSETS[asset]["location"] + "/sprites")
                    config.set("Hashes", asset, remonstrate_utils.md5_update_from_file(_ASSETS[asset]["location"] +
                               "/spritereplacements.txt", current_hash).hexdigest())
                elif asset == "monster_sprites":
                    config.set("Hashes", asset,
                               remonstrate_utils.get_directory_hash(_ASSETS[asset]["location"]).hexdigest())

            if asset == "monster_sprites":
                update_remonsterate()

            if config:
                if not config.has_section("Version"):
                    config.add_section("Version")
                config.set('Version', asset, data['tag_name'])
        else:
            print(asset + " update skipped.")


def launch_beyond_chaos():
    if os.path.isfile("BeyondChaos.exe"):
        print("Launching Beyond Chaos")
        subprocess.Popen(args=[], executable='BeyondChaos.exe')
        # wait 3 seconds
        time.sleep(3)
        os.system('cls' if os.name == 'nt' else 'clear')
        sys.exit()


def main(config_path=Path(os.path.join(os.getcwd(), "config.ini"))):
    # rates = requests.get("https://api.github.com/rate_limit").json()
    # print(str(rates))
    # return
    global config
    if os.path.exists(config_path):
        config.read(config_path)

    running_os = platform.system()

    for asset in _ASSETS:
        try:
            if asset == "updater":
                if __version__ != get_version(asset):
                    # Version mismatch - there is an update available
                    _ASSETS["updater"]["update"] = True
            else:
                if asset == "core" and running_os != "Windows":
                    print("Cannot update randomizer executable for non-Windows OS.")
                    continue

                if config.get('Version', asset) != get_version(asset):
                    # Version mismatch - there is an update available
                    _ASSETS[asset]["update"] = True
        except (configparser.NoSectionError, configparser.NoOptionError):
            # Config has no information about the section or option. Probably first time setup, so update.
            _ASSETS[asset]["update"] = True

        if _ASSETS[asset]["update"]:
            # Retrieve the updated asset data from GitHub
            _ASSETS[asset]["data"] = requests.get(_ASSETS[asset]["URL"]).json()
            # In the asset, get the ['data']. From the data, get the ['assets'] (releases) returned from GitHub. We want
            # index [0], presumably the newest release, and then we get the download ['size'] attribute from that
            download_size = int(_ASSETS[asset]["data"]['assets'][0]['size'])
            if download_size < 1000:
                size_suffix = "Bytes"
            elif download_size < 1000000:
                size_suffix = "KB"
                download_size = round(download_size / 1000, 2)
            elif download_size < 1000000000:
                size_suffix = "MB"
                download_size = round(download_size / 1000000, 2)
            else:
                size_suffix = "GB"
                download_size = round(download_size / 1000000000, 2)
            print(_ASSETS[asset]["prompt"] +
                  "The download size is " + str(download_size) + " " + size_suffix + ".")
            choice = input("Y/N: ")
            if choice.lower() == "n":
                _ASSETS[asset]["update"] = False
                print(f"Skipping {asset.replace('_', ' ')} update.")
            elif choice.lower() == "y":
                if asset == "updater":
                    # If we're updating the updater, we can skip the rest of the questions until the updater updates
                    break

            print("")

    for asset in _ASSETS:
        if _ASSETS[asset]["update"]:
            print(f"Updating the Beyond Chaos {asset.replace('_', ' ')}...")
            update_asset_from_web(asset)
            print(f"The Beyond Chaos {asset.replace('_', ' ')} " +
                  ("have" if asset.endswith("s") else "has") + " been updated.\n")

    print("Rewriting updated version information to configuration.")
    with open(config_path, 'w') as fout:
        config.write(fout)

    print("Completed all update tasks!")
    if running_os == "Windows":
        if not parent_process_id:
            # If Beyond Chaos isn't already running, start it
            launch_beyond_chaos()
        else:
            print("")
    else:
        print("Non-Windows OS detected, bypassing executable launch")


def update_remonsterate():
    # Create the remonsterate directory in the game directory
    base_directory = os.path.join(os.getcwd(), 'remonsterate')
    sprite_directory = os.path.join(base_directory, "sprites")
    image_file = os.path.join(base_directory, "images_and_tags.txt")
    monster_file = os.path.join(base_directory, "monsters_and_tags.txt")

    if not os.path.exists(base_directory):
        os.makedirs(base_directory)
        print("Remonsterate directory created.")

    if not os.path.exists(sprite_directory):
        os.makedirs(sprite_directory)
        print("Sprites directory created in remonsterate.")

    # Generate images_and_tags.txt file for remonsterate based on the sprites in the sprites folder
    tag_file = os.path.join(os.getcwd(), 'remonsterate\\images_and_tags.txt')
    try:
        remonstrate_utils.construct_tag_file_from_dirs(sprite_directory, tag_file)
        print("New images_and_tags file created in remonsterate.")
    except IOError:
        remonstrate_utils.generate_tag_file(tag_file)
        if not os.path.isfile(image_file):
            print("Template images_and_tags file created in remonsterate.")

    tag_file = os.path.join(os.getcwd(), 'remonsterate\\monsters_and_tags.txt')
    if not os.path.isfile(monster_file):
        remonstrate_utils.generate_sample_monster_list(tag_file)
        print("Template monsters_and_tags file created in remonsterate.")


if __name__ == '__main__':
    try:
        requests.head(url='http://www.google.com')
        main()
        time.sleep(3)
    except requests.exceptions.ConnectionError:
        print("ERROR: No internet connection is available. Please connect to the internet and try running the updater "
              "again.")
        input("Press any key to exit...")
