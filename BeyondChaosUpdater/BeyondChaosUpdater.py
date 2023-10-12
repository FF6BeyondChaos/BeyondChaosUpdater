import platform
import time
import shutil
import os
import sys
import tempfile
import subprocess
import sprite_utils
from configparser import ConfigParser

# This is not part of the stdlib
try:
    import requests
except ImportError:
    sys.exit('Please install the `requests` python package '
             'before running updater. Try "pip install requests".')
try:
    import psutil
except ImportError:
    sys.exit('Please install the `psutil` python package '
             'before running updater. Try "pip install psutil".')
try:
    import jwt
except ImportError:
    sys.exit('Please install the `jwt` python package '
             'before running updater. Try "pip install jwt".')

__version__ = '3.0.0'

config = ConfigParser()
remaining_api_calls = 0
get_request_headers = {}

BASE_DIRECTORY = os.getcwd()
CONFIG_PATH = os.path.join(BASE_DIRECTORY, 'config.ini')
UPDATER_PATH = os.path.join(BASE_DIRECTORY, 'beyondchaosupdater.exe')
BACKUP_NAME = UPDATER_PATH + '.old'
_BASE_PROJ_URL = 'https://api.github.com/repos/FF6BeyondChaos/'

DEFAULT_CONFIG = {
    "Version": {
        'updater': __version__
    }
}

# Update: Does this asset require an update?
# Prompt: What should be displayed to the user to confirm the update?
# Location: Where should the asset be downloaded and extracted to?
# URL: What web address is the asset located at?
# Data: The data from the URL, so we don't need to hit the API multiple times.
_ASSETS = {
    "updater": {
        "prompt": "There is an update available for this updater.\n"
                  "Would you like to download the update from GitHub?\n",
        "location": BASE_DIRECTORY,
        "URL": os.path.join(_BASE_PROJ_URL, 'BeyondChaosUpdater/releases/latest'),
        "data": {}
    },
    "core": {
        "prompt": "There is an update available for the Beyond Chaos core files.\n"
                  "Would you like to download the update from GitHub?\n"
                  "This will replace the version of Beyond Chaos you are currently running.\n",
        "location": BASE_DIRECTORY,
        "URL": os.path.join(_BASE_PROJ_URL, 'BeyondChaosRandomizer/releases/latest'),
        "data": {}
    },
    "character_sprites": {
        "prompt": "There is an update available for Beyond Chaos' character sprites.\n"
                  "They are required to use the makeover code.\n"
                  "Would you like to download the new sprites from GitHub?\n",
        "location": os.path.join(BASE_DIRECTORY, "custom"),
        "URL": os.path.join(_BASE_PROJ_URL, 'BeyondChaosSprites/releases/latest'),
        "data": {}
    },
    "monster_sprites": {
        "prompt": "There is an update available for Beyond Chaos' monster sprites.\n"
                  "They are required to use the remonsterate code.\n"
                  "Would you like to download the new sprites from GitHub?\n",
        "location": os.path.join(BASE_DIRECTORY, "remonsterate"),
        "URL": os.path.join(_BASE_PROJ_URL, 'BeyondChaosMonsterSprites/releases/latest'),
        "data": {}
    }
}

# Load configuration data
# Read the config.ini file in the directory and then read in DEFAULT CONFIG to fill in any missing values
files_loaded = config.read(CONFIG_PATH)
config.read_dict(DEFAULT_CONFIG)
if files_loaded == 0:
    # config.ini did not exist. Create it.
    with open(CONFIG_PATH, 'w') as config_file:
        config.write(config_file)


def get_web_token():
    global get_request_headers
    # Application has read-only access to the BeyondChaosRandomizer repository
    # Web token lasts 9 minutes
    payload = {
        'iat': int(time.time()) - 30,
        'exp': int(time.time()) + 570,
        'iss': '304388'
    }
    signing_key = jwt.jwk_from_pem(pem_content=bytes('''-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAraBSKgFWY8cMaPC8JaluID7YlNm/vOhPIzQVqKczBKP3YDyT
VmCupXLXkIL7TtclhIruclm80NsAqx4IkyCxrauicLVeXlqFINPCWl7sbdQBgnkk
aw5VK44BWZIFKemf4qKtIJRnMA78IFmHJwQVKfPQqs4xByk5vXLsvGH7OCjZJ/Eh
9VP2htNCac5x2H/LaLzuTFbJJPhYTO1QwguSDnu1FJGwAGtqEag4HkfIbVUrZI4V
8oLLglFxlHHPGWH4RLqxE4F2V104c7I+E+fVaRTGV1S26zQ+TLFQGJQgNwPD/61J
BLxIIdr1lw1X18RW1z82Kv5QERzjtN2mV1jllQIDAQABAoIBAAN3G6yy8iJzqo+9
nkOyKfyCxJfT8Lu4dzvgoj4HeEEzdJB7JQWoUFQFAsBjnNhp+tm2XCP0HoycklrX
8pvdHy60Kj3NoOCJNfb9wvdCxb07afxMpqlsU87Wurgq7ed0PjirvoDT9WtEIUwT
/VqN/k4kC5odG2VlMT3SuV7ZJcZtId3K6lRZgmn8T4ODbcqcjIVe6ZvDX4i/WthX
QUKPv7PticuaP1aOZ6zV4ardtBu45WKg9ZTl4O65sUFfxeu/i0KGiX+LzEVqcI3e
8j1OUixVvd3D/ePuBlm1H3b7bSHRz6T33oCWNBts3S+pKHHgW22oOOtYyEsZ3+BP
086YG9ECgYEA1cycMVnhOup0ZxA59gOylj8NASwFisQlaMP007VcjiojH5vLCAPp
a1k6Z2z/koDJiQxOqiyDvUv1bpVo5gOc2OB9BCVnwKKR/+A4l9UiddUXNAYgG1vY
ZP+xcUliXn50j/9mo2isiRRRWkDpLIciO545jcRRroR8difrpEhNE5sCgYEAz+W/
Ywz/HADT/p0dOzx3QuD9oXJTutToJy2/BnrfHDlvu5v/OwJt/IU8yYAVhkfx+VY5
HefD+04dYrCLyd0dyBZid0lxbXG4C+Q1hIhAYvj/fUaqGy8U8Z9N7anVWuunL4rw
omOOb6nsIRr3hlFCVxwfxXOmcEBDd0zOwWOc9o8CgYEAjAUR8jxEBtrP20PEQfuP
9Vhbwv26r3PgcCmN6S0o7a5pDGVy5c/yCi0I0/2Nr7wKwWe/CTJYIRxjI8ZUSffp
vBvhpFp/Baky5xpI1h9vDy68oIS2eFSBdzwCUQhXlT1KR5hj9vcxsCEPWoWScGgc
ImFwngkJ2brI7HUenZwAZqsCgYBKT/NjcofV+K3Oe1axj+GJdGb0yKsJQ4VgS8fW
hyEtM5Ku2woWi73I389kr3YCM8FYwOtVtzyknb1/Q2AUXgeBOA8mWIhE+Lsy9PX0
U8fAGQUqQJIZeXDhFXKDm4t6HnX6Vo3BXhjR7UlMZBlKV82A2bq5l6dMxIvZHwlg
szyuHQKBgBvj2eOo5QzJZp2KCUpHaVfsMtxtLXf8mfmPBkzWEp7yaALEE6opKOeu
+XDiG2cABNW0zHi8It0e81LUB7d1czv0vr3nspLZbbe2rV7p5LeAYKRPPtC34I+Y
IUDMfyYGvvrC9Ajz+gQkT5Lp6flc1aPL5pqtiT/eBi3Tu8xMCH8d
-----END RSA PRIVATE KEY-----''', 'utf-8'))
    jwt_instance = jwt.JWT()
    encoded_jwt = jwt_instance.encode(payload, key=signing_key, alg='RS256')
    response = requests.post(
        headers={
            'Accept': 'application/vnd.github+json',
            'Authorization': 'Bearer ' + encoded_jwt,
            'X-GitHub-Api-Version': '2022-11-28'
        },
        url='https://api.github.com/app/installations/35180196/access_tokens')

    access_token = response.json()['token']
    get_request_headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + access_token,
        'X-GitHub-Api-Version': '2022-11-28'
    }


def send_get_request(url: str, stream=False):
    resp = requests.get(
        url,
        headers=get_request_headers,
        stream=stream
    )
    # check request result
    if not resp.ok:
        # Try refreshing the web token
        get_web_token()
        resp = requests.get(
            url,
            headers=get_request_headers,
            stream=stream
        )
        if not resp.ok:
            print(f'GitHub returned a bad response.\nDetails:{resp.reason}')
            input('Press enter to exit...')
            sys.exit()
    if stream is True:
        return resp
    else:
        return resp.json()


def update_asset_from_web(asset):
    global config

    data = _ASSETS[asset]["data"]
    # get the link to download the latest package
    download_link = data['assets'][0]['browser_download_url']
    # download the file and save it.
    temp_dir = tempfile.mkdtemp()
    local_filename = os.path.join(temp_dir, download_link.split('/')[-1])
    with send_get_request(url=download_link, stream=True) as file_binary:
        with open(local_filename, 'wb') as file_name:
            shutil.copyfileobj(file_binary.raw, file_name)

    if asset == "updater":
        # The currently-running executable cannot be deleted, so we rename it instead
        # Then, we download the latest version from GitHub
        # Finally, we run the newly downloaded exe and exit this older version
        if os.path.exists(BACKUP_NAME):
            os.remove(BACKUP_NAME)
        os.rename(os.path.join(os.getcwd(), "beyondchaosupdater.exe"), BACKUP_NAME)

        # Extract the new update
        sprite_utils.extract_archive(local_filename, _ASSETS[asset]["location"] or os.getcwd())

        config.set('Version', asset, data['tag_name'])

        print("The updater has been updated. Restarting...\n")
        subprocess.Popen(args=sys.argv, executable=UPDATER_PATH)
        sys.exit()

    elif asset == "core":
        # Extract the new update
        sprite_utils.extract_archive(local_filename, _ASSETS[asset]["location"] or os.getcwd())

        config.set('Version', asset, data['tag_name'])

    if asset == "character_sprites" or asset == "monster_sprites":
        update_sprites = True
        back_up_sprites = False

        # Compare the stored hash value with the hash of the existing spritereplacements file
        sprite_hash = config.get(section="Hashes", option=asset, fallback='Unknown')
        if sprite_hash == 'Unknown':
            # If the hash for the asset does not exist, we can just back up the files to be safe
            back_up_sprites = True
        else:
            current_hash = ''
            if asset == "character_sprites":
                current_hash = sprite_utils.get_directory_hash(_ASSETS[asset]["location"] + "/sprites")
                current_hash = sprite_utils.md5_update_from_file(_ASSETS[asset]["location"] +
                                                                 "/spritereplacements.txt", current_hash)
            elif asset == "monster_sprites":
                current_hash = sprite_utils.get_directory_hash(_ASSETS[asset]["location"])

            if not sprite_hash == current_hash.hexdigest():
                # The asset has been customized
                while True:
                    print(f'It appears your {str.replace(asset, "_", " ")} have been customized.')
                    print(f'Would you like to back up the current {str.replace(asset, "_", " ")}'
                          ' folder before updating?')
                    choice = input('"Y" to create backup, '
                                   '"N" to overwrite, or '
                                   f'"S" to skip updating the {str.replace(asset, "_", " ")}: ')
                    if choice.lower() == 'y' or choice.lower() == 'yes':
                        back_up_sprites = True
                        break
                    elif choice.lower() == 'n' or choice.lower() == 'no':
                        break
                    elif choice.lower() == 's':
                        update_sprites = False
                        break
                    else:
                        print('Please answer "Y" for yes, "N" for no, or "S" to skip.')

        if update_sprites:
            if back_up_sprites and os.path.exists(_ASSETS[asset]["location"]):
                timestamp = str(time.time())
                shutil.copytree(_ASSETS[asset]["location"], _ASSETS[asset]["location"] + "_backup_" + timestamp)
                # os.rename(_ASSETS[asset]["location"], _ASSETS[asset]["location"] + "_backup_" + timestamp)
                print("Your custom directory has been backed up to " + _ASSETS[asset]["location"] +
                      "_backup_" + timestamp + ".")

            # Extract the new update
            sprite_utils.extract_archive(local_filename, _ASSETS[asset]["location"] or os.getcwd())
            print(f'{str.replace(asset.title(), "_", " ")} have been updated.')
            # Set the hash of the new character sprites update
            if config:
                if not config.has_section("Hashes"):
                    config.add_section("Hashes")
                if asset == "character_sprites":
                    current_hash = sprite_utils.get_directory_hash(_ASSETS[asset]["location"] + "/sprites")
                    config.set("Hashes", asset, sprite_utils.md5_update_from_file(_ASSETS[asset]["location"] +
                                                                                  "/spritereplacements.txt",
                                                                                  current_hash).hexdigest())
                elif asset == "monster_sprites":
                    config.set("Hashes", asset,
                               sprite_utils.get_directory_hash(_ASSETS[asset]["location"]).hexdigest())

            if asset == "monster_sprites":
                print(f'Updating remonsterate files.')
                update_remonsterate()
                print(f'Remonsterate files updated.')

            config.set('Version', asset, data['tag_name'])
        else:
            print(f'{str.replace(asset.title(), "_", " ")} update skipped.')


def main():
    global remaining_api_calls

    running_os = platform.system()

    # Reorder the assets so updater is first, in case somebody reorders _ASSETS
    #   It's better to update the updater first in case it affects the rest of the process.
    ordered_assets = {'updater': _ASSETS.get('updater'), **_ASSETS}

    for asset in ordered_assets:
        remaining_api_calls = \
            send_get_request(url="https://api.github.com/rate_limit")['resources']['core']['remaining']
        if remaining_api_calls < 2:
            # Updating an asset requires two API calls: To get the release info, then to download the update
            print('Unable to update remaining assets: GitHub API calls have been exhausted. '
                  'Please try again at the top of the next hour.')
            break
        if asset == "updater":
            if __version__ == send_get_request(_ASSETS[asset]['URL'])['tag_name']:
                continue
        else:
            if asset == "core" and running_os != "Windows":
                print("Cannot update randomizer executable for non-Windows OS.")
                continue
            if (config.get(section='Version', option=asset, fallback='Unknown') ==
                    send_get_request(_ASSETS[asset]['URL'])['tag_name']):
                continue

        # Retrieve the updated asset data from GitHub
        _ASSETS[asset]["data"] = send_get_request(url=_ASSETS[asset]["URL"])
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
            print(f"Skipping {asset.replace('_', ' ')} update.\n")
            continue
        elif choice.lower() == "y":
            print(f"Updating the Beyond Chaos {asset.replace('_', ' ')}...")
            update_asset_from_web(asset)
            print(f"The Beyond Chaos {asset.replace('_', ' ')} " +
                  ("have" if asset.endswith("s") else "has") + " been updated.\n")

    print("Recording version information in config.ini.")
    with open(CONFIG_PATH, 'w') as new_config_file:
        config.write(new_config_file)

    print("Completed all update tasks!")
    if running_os == "Windows" and os.path.isfile(os.path.join(BASE_DIRECTORY, "BeyondChaos.exe")):
        input('Press enter to launch Beyond Chaos.')
        subprocess.Popen(
            args=(),
            executable='BeyondChaos.exe'
        )
        os.system('cls' if os.name == 'nt' else 'clear')
        sys.exit()
    else:
        input('Press enter to exit.')


def update_remonsterate():
    # Create the remonsterate directory in the game directory
    base_directory = os.path.join(os.getcwd(), 'remonsterate')
    sprite_directory = os.path.join(base_directory, "sprites")
    image_file = os.path.join(base_directory, "images_and_tags.txt")
    monster_file = os.path.join(base_directory, "monsters_and_tags.txt")

    if not os.path.exists(base_directory):
        os.makedirs(base_directory)
        print("Created the remonsterate folder.")

    if not os.path.exists(sprite_directory):
        os.makedirs(sprite_directory)
        print("Created the sprites subfolder in the remonsterate folder.")

    # Generate images_and_tags.txt file for remonsterate based on the sprites in the sprites folder
    tag_file = os.path.join(os.getcwd(), 'remonsterate\\images_and_tags.txt')
    try:
        sprite_utils.construct_tag_file_from_dirs(sprite_directory, tag_file)
        print('New images_and_tags.txt file generated in the remonsterate folder.')
    except IOError:
        sprite_utils.generate_tag_file(tag_file)
        if not os.path.isfile(image_file):
            print("Error: Failed to automatically generate an image_and_tags.txt file using the contents of your "
                  "remonsterate sprites subfolder. Also failed to generate a blank template image_and_tags.txt file.")
        else:
            print("Error: Failed to automatically generate an image_and_tags.txt file using the contents of your "
                  "remonsterate sprites subfolder. A blank template image_and_tags.txt file has been created instead.")

    if not os.path.isfile(monster_file):
        sprite_utils.generate_sample_monster_list(monster_file)
        print("Generated a template monsters_and_tags.txt file in the remonsterate folder.")


if __name__ == '__main__':
    args = sys.argv
    for arg in args:
        if isinstance(arg, str) and arg.startswith('-pid '):
            parent_process_id = arg[len('-pid '):]
    try:
        # Test internet connectivity by using the simplest possible request to a reliable source
        requests.head(url='http://www.google.com')
        get_web_token()
        main()
    except requests.exceptions.ConnectionError:
        print('ERROR: No internet connection is available. '
              'Please connect to the internet and try running the updater again.')
        input('Press any key to exit...')
