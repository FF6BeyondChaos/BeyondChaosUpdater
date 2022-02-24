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
        # wait 3 seconds
        print(Constants.wait)
        time.sleep(5)
        print(Constants.CheckINI)
        if Config.checkINI():
            print(Constants.INIFound)
        else:
            print(Constants.NoINI)
            Config.initConfig()
        update_sprites()
        update_remonsterate()
        update_beyond_chaos()
        Config.writeConfig()
        print(Constants.UpdaterCompleted)
        launch_beyond_chaos()
    except Exception:
        traceback.print_exc()


def launch_beyond_chaos():
    try:
        print(Constants.UpdaterClosing)
        os.startfile('BeyondChaos.exe')
        # wait 3 seconds
        time.sleep(3)
    except Exception:
        traceback.print_exc()


def update_remonsterate():

    try:
        # Create the remonsterate directory in the game directory
        base_directory = os.path.join(os.getcwd(), 'remonsterate')
        sprite_directory = os.path.join(base_directory, "sprites")
        image_file = os.path.join(base_directory, "images_and_tags.txt")
        monster_file = os.path.join(base_directory, "monsters_and_tags.txt")

        if not os.path.isdir(base_directory):
            os.mkdir(base_directory)
            print("Remonsterate directory created.")

        if not os.path.isdir(sprite_directory):
            # Create the remonsterate sprites directory in remonsterate
            os.mkdir(sprite_directory)
            print("Sprites directory created in remonsterate.")

        update_monster_sprites()

        #Generate images_and_tags.txt file for remonsterate based on the sprites in the sprites folder

        try:
            # Populate the file name lists. Iterates through directories starting in the
            #   remonsterate directory. Does not traverse directories past
            #   the depth specified by walk_distance.
            walk_distance = 6
            sprite_directory_level = sprite_directory.count(os.path.sep)
            spritelist = ""
            print("Looking for and analyzing png files in " + sprite_directory + " and " + str(walk_distance) +
                " levels of sub-directories.")
            for root, dirs, files in os.walk(sprite_directory):
                current_walking_directory = os.path.abspath(root)
                current_directory_level = current_walking_directory.count(os.path.sep)

                if current_directory_level > sprite_directory_level + walk_distance:
                    # del dirs[:] empties the list that os.walk uses to determine what
                    #   directories to walk through, meaning os.walk will move on to
                    #   the next directory. It does NOT delete or modify files on the
                    #   hard drive.
                    if len(dirs) > 0:
                        print("There were additional unexplored directories in " + current_walking_directory + ".")
                    del dirs[:]
                else:
                    for file_name in files:
                        if file_name.lower().endswith(".png"):
                            spritelist += str(os.path.join(root, file_name))[len(sprite_directory) + 1:] + "\n"
            with open(os.path.join(os.getcwd(), 'remonsterate\\images_and_tags.txt'), 'w') as text_file:
                text_file.write(spritelist)
            print("New images_and_tags file created in remonsterate.")

        except IOError as e:
            if not os.path.isfile(image_file):
                # Create the default images_and_tags.txt and monsters_and_tags.txt files
                with open(os.path.join(os.getcwd(), 'remonsterate\\images_and_tags.txt'), 'w') as text_file:
                    text_file.write(
'''# This is a sample image list file.
# This file contains the paths to every sprite that you wish to import randomly.
# The format is: path/to/file.png:tag1,tag2,tag3
# You can also omit the tags.
#
# Examples:
# sprites/dragon.png:reptile,flying,kickass,boss
# sprites/unicorn.png'''
                    )
                print("Template images_and_tags file created in remonsterate.")

        if not os.path.isfile(monster_file):
            with open(os.path.join(os.getcwd(), 'remonsterate\\monsters_and_tags.txt'), 'w') as text_file:
                text_file.write(
'''# This is a sample monster list file.
# This list is used to whitelist or blacklist specific tags for each monster.
# It is not necessary to list every monster in the game.
#
# The format is: monster_index:white_tag1,white_tag2,!black_tag1,!black_tag2
#   The monster index is in hexadecimal.
#   An exclamation point (!) denotes a blacklisted flag.
#
# If any tags are whitelisted, that monster can ONLY use sprites with
#   ALL of those tags.
# If a tag is blacklisted, that monster cannot use ANY sprites with that tag.
# These tags only work when using the default randomization functions.
#
# Examples:
# 0:humanoid,!female            # Narshe Guard
# 53:town,large,!boss           # HadesGigas
# 5d:desert                     # Areneid
# 128:humanoid,female,boss      # Goddess

# Guard_____
000:

# Soldier___
001:

# Templar___
002:

# Ninja_____
003:

# Samurai___
004:

# Orog______
005:

# Mag_Roader
006:

# Retainer__
007:

# Hazer_____
008:

# Dahling___
009:

# Rain_Man__
00A:

# Brawler___
00B:

# Apokryphos
00C:

# Dark_Force
00D:

# Whisper___
00E:

# Over_Mind_
00F:

# Osteosaur_
010:

# Commander_
011:

# Rhodox____
012:

# Were_Rat__
013:

# Ursus_____
014:

# Rhinotaur_
015:

# Steroidite
016:

# Leafer____
017:

# Stray_Cat_
018:

# Lobo______
019:

# Doberman__
01A:

# Vomammoth_
01B:

# Fidor_____
01C:

# Baskervor_
01D:

# Suriander_
01E:

# Chimera___
01F:

# Behemoth__
020:

# Mesosaur__
021:

# Pterodon__
022:

# FossilFang
023:

# White_Drgn
024:

# Doom_Drgn_
025:

# Brachosaur
026:

# Tyranosaur
027:

# Dark_Wind_
028:

# Beakor____
029:

# Vulture___
02A:

# Harpy_____
02B:

# HermitCrab
02C:

# Trapper___
02D:

# Hornet____
02E:

# CrassHoppr
02F:

# Delta_Bug_
030:

# Gilomantis
031:

# Trilium___
032:

# Nightshade
033:

# TumbleWeed
034:

# Bloompire_
035:

# Trilobiter
036:

# Siegfried_
037:

# Nautiloid_
038:

# Exocite___
039:

# Anguiform_
03A:

# Reach_Frog
03B:

# Lizard____
03C:

# ChickenLip
03D:

# Hoover____
03E:

# Rider_____
03F:

# Chupon____
040:

# Pipsqueak_
041:

# M_TekArmor
042:

# Sky_Armor_
043:

# Telstar___
044:

# Lethal_Wpn
045:

# Vaporite__
046:

# Flan______
047:

# Ing_______
048:

# Humpty____
049:

# Brainpan__
04A:

# Cruller___
04B:

# Cactrot___
04C:

# Repo_Man__
04D:

# Harvester_
04E:

# Bomb______
04F:

# Still_Life
050:

# Boxed_Set_
051:

# SlamDancer
052:

# HadesGigas
053:

# Pug_______
054:

# Magic_Urn_
055:

# Mover_____
056:

# Figaliz___
057:

# Buffalax__
058:

# Aspik_____
059:

# Ghost_____
05A:

# Crawler___
05B:

# Sand_Ray__
05C:

# Areneid___
05D:

# Actaneon__
05E:

# Sand_Horse
05F:

# Dark_Side_
060:

# Mad_Oscar_
061:

# Crawly____
062:

# Bleary____
063:

# Marshal___
064:

# Trooper___
065:

# General___
066:

# Covert____
067:

# Ogor______
068:

# Warlock___
069:

# Madam_____
06A:

# Joker_____
06B:

# Iron_Fist_
06C:

# Goblin____
06D:

# Apparite__
06E:

# PowerDemon
06F:

# Displayer_
070:

# Vector_Pup
071:

# Peepers___
072:

# Sewer_Rat_
073:

# Slatter___
074:

# Rhinox____
075:

# Rhobite___
076:

# Wild_Cat__
077:

# Red_Fang__
078:

# Bounty_Man
079:

# Tusker____
07A:

# Ralph_____
07B:

# Chitonid__
07C:

# Wart_Puck_
07D:

# Rhyos_____
07E:

# SrBehemoth
07F:

# Vectaur___
080:

# Wyvern____
081:

# Zombone___
082:

# Dragon____
083:

# Brontaur__
084:

# Allosaurus
085:

# Cirpius___
086:

# Sprinter__
087:

# Gobbler___
088:

# Harpiai___
089:

# GloomShell
08A:

# Drop______
08B:

# Mind_Candy
08C:

# WeedFeeder
08D:

# Luridan___
08E:

# Toe_Cutter
08F:

# Over_Grunk
090:

# Exoray____
091:

# Crusher___
092:

# Uroburos__
093:

# Primordite
094:

# Sky_Cap___
095:

# Cephaler__
096:

# Maliga____
097:

# Gigan_Toad
098:

# Geckorex__
099:

# Cluck_____
09A:

# Land_Worm_
09B:

# Test_Rider
09C:

# PlutoArmor
09D:

# Tomb_Thumb
09E:

# HeavyArmor
09F:

# Chaser____
0A0:

# Scullion__
0A1:

# Poplium___
0A2:

# Intangir__
0A3:

# Misfit____
0A4:

# Eland_____
0A5:

# Enuo______
0A6:

# Deep_Eye__
0A7:

# GreaseMonk
0A8:

# NeckHunter
0A9:

# Grenade___
0AA:

# Critic____
0AB:

# Pan_Dora__
0AC:

# SoulDancer
0AD:

# Gigantos__
0AE:

# Mag_Roader
0AF:

# Spek_Tor__
0B0:

# Parasite__
0B1:

# EarthGuard
0B2:

# Coelecite_
0B3:

# Anemone___
0B4:

# Hipocampus
0B5:

# Spectre___
0B6:

# Evil_Oscar
0B7:

# Slurm_____
0B8:

# Latimeria_
0B9:

# StillGoing
0BA:

# Allo_Ver__
0BB:

# Phase_____
0BC:

# Outsider__
0BD:

# Barb_e____
0BE:

# Parasoul__
0BF:

# Pm_Stalker
0C0:

# Hemophyte_
0C1:

# Sp_Forces_
0C2:

# Nohrabbit_
0C3:

# Wizard____
0C4:

# Scrapper__
0C5:

# Ceritops__
0C6:

# Commando__
0C7:

# Opinicus__
0C8:

# Poppers___
0C9:

# Lunaris___
0CA:

# Garm______
0CB:

# Vindr_____
0CC:

# Kiwok_____
0CD:

# Nastidon__
0CE:

# Rinn______
0CF:

# Insecare__
0D0:

# Vermin____
0D1:

# Mantodea__
0D2:

# Bogy______
0D3:

# Prussian__
0D4:

# Black_Drgn
0D5:

# Adamanchyt
0D6:

# Dante_____
0D7:

# Wirey_Drgn
0D8:

# Dueller___
0D9:

# Psychot___
0DA:

# Muus______
0DB:

# Karkass___
0DC:

# Punisher__
0DD:

# Balloon___
0DE:

# Gabbldegak
0DF:

# GtBehemoth
0E0:

# Scorpion__
0E1:

# Chaos_Drgn
0E2:

# Spit_Fire_
0E3:

# Vectagoyle
0E4:

# Lich______
0E5:

# Osprey____
0E6:

# Mag_Roader
0E7:

# Bug_______
0E8:

# Sea_Flower
0E9:

# Fortis____
0EA:

# Abolisher_
0EB:

# Aquila____
0EC:

# Junk______
0ED:

# Mandrake__
0EE:

# 1st_Class_
0EF:

# Tap_Dancer
0F0:

# Necromancr
0F1:

# Borras____
0F2:

# Mag_Roader
0F3:

# Wild_Rat__
0F4:

# Gold_Bear_
0F5:

# Innoc_____
0F6:

# Trixter___
0F7:

# Red_Wolf__
0F8:

# Didalos___
0F9:

# Woolly____
0FA:

# Veteran___
0FB:

# Sky_Base__
0FC:

# IronHitman
0FD:

# Io________
0FE:

# Pugs______
0FF:

# Whelk_____
100:

# Presenter_
101:

# Mega_Armor
102:

# Vargas____
103:

# TunnelArmr
104:

# Prometheus
105:

# GhostTrain
106:

# Dadaluma__
107:

# Shiva_____
108:

# Ifrit_____
109:

# Number_024
10A:

# Number_128
10B:

# Inferno___
10C:

# Crane_____
10D:

# Crane_____
10E:

# Umaro_____
10F:

# Umaro_____
110:

# Guardian__
111:

# Guardian__
112:

# Air_Force_
113:

# Tritoch___
114:

# Tritoch___
115:

# FlameEater
116:

# AtmaWeapon
117:

# Nerapa____
118:

# SrBehemoth
119:

# Kefka_____
11A:

# Tentacle__
11B:

# Dullahan__
11C:

# Doom_Gaze_
11D:

# Chadarnook
11E:

# Curley____
11F:

# Larry_____
120:

# Moe_______
121:

# Wrexsoul__
122:

# Hidon_____
123:

# KatanaSoul
124:

# L_30_Magic
125:

# Hidonite__
126:

# Doom______
127:

# Goddess___
128:

# Poltrgeist
129:

# Kefka_____
12A:false_kefka_do_not_replace

# L_40_Magic
12B:

# Ultros____
12C:

# Ultros____
12D:

# Ultros____
12E:

# Chupon____
12F:

# L_20_Magic
130:

# Siegfried_
131:

# L_10_Magic
132:

# L_50_Magic
133:

# Head______
134:

# Whelk_Head
135:

# Colossus__
136:

# CzarDragon
137:

# Master_Pug
138:

# L_60_Magic
139:

# Merchant__
13A:

# B_Day_Suit
13B:

# Tentacle__
13C:

# Tentacle__
13D:

# Tentacle__
13E:

# RightBlade
13F:

# Left_Blade
140:

# Rough_____
141:

# Striker___
142:

# L_70_Magic
143:

# Tritoch___
144:

# Laser_Gun_
145:

# Speck_____
146:

# MissileBay
147:

# Chadarnook
148:

# Ice_Dragon
149:

# Kefka_____
14A:

# Storm_Drgn
14B:

# Dirt_Drgn_
14C:

# Ipooh_____
14D:

# Leader____
14E:

# Grunt_____
14F:

# Gold_Drgn_
150:

# Skull_Drgn
151:

# Blue_Drgn_
152:

# Red_Dragon
153:

# Piranha___
154:

# Rizopas___
155:

# Specter___
156:

# Short_Arm_
157:

# Long_Arm__
158:

# Face______
159:

# Tiger_____
15A:

# Tools_____
15B:

# Magic_____
15C:

# Hit_______
15D:

# Girl______
15E:

# Sleep_____
15F:

# Hidonite__
160:

# Hidonite__
161:

# Hidonite__
162:

# L_80_Magic
163:

# L_90_Magic
164:

# ProtoArmor
165:

# MagiMaster
166:

# SoulSaver_
167:

# Ultros____
168:

# Naughty___
169:

# Phunbaba__
16A:

# Phunbaba__
16B:

# Phunbaba__
16C:

# Phunbaba__
16D:

# __________
16E:

# __________
16F:

# __________
170:

# Zone_Eater
171:

# __________
172:

# __________
173:

# __________
174:

# Officer___
175:

# Cadet_____
176:

# __________
177:

# __________
178:

# Soldier___
179:

# __________
17A:

# __________
17B:

# __________
17C:

# Atma______
17D:

# __________
17E:

# __________
17F:'''
                )
            print("Template monsters_and_tags file created in remonsterate.")
    except Exception:
        traceback.print_exc()

def update_sprites():
    try:
        my_file = Path('Sprites.zip')
        if not my_file.is_file():
            # go get the sprites
            # ping github and get the new released version
            x = requests.get('https://api.github.com/repos/FF6BeyondChaos/BeyondChaosSprites/releases/latest').json()
            # get the link to download the latest package
            download_link = x['assets'][0]['browser_download_url']
            # download the file and save it.
            local_filename = download_link.split('/')[-1]
            with requests.get(download_link, stream=True) as r:
                with open(local_filename, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            time.sleep(3)
        with ZipFile('Sprites.zip', 'r') as zipObj:
            print(Constants.UpdateSprites)
            # Extract all the contents of zip file in different directory
            zipObj.extractall(os.path.join(os.getcwd(), 'custom'))
            # wait 3 seconds
            time.sleep(3)
            print(Constants.UpdateSpriteDone)
    except Exception:
        traceback.print_exc()

def update_monster_sprites():
    try:
        my_file = Path('MonsterSprites.zip')
        if not my_file.is_file():
            # go get the sprites
            # ping github and get the new released version
            x = requests.get('https://api.github.com/repos/FF6BeyondChaos/BeyondChaosMonsterSprites/releases/latest').json()
            # get the link to download the latest package
            download_link = x['assets'][0]['browser_download_url']
            # download the file and save it.
            local_filename = download_link.split('/')[-1]
            with requests.get(download_link, stream=True) as r:
                with open(local_filename, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            time.sleep(3)
        with ZipFile('MonsterSprites.zip', 'r') as zipObj:
            print(Constants.UpdateMonsterSprites)
            # Extract all the contents of zip file in different directory
            zipObj.extractall(os.path.join(os.getcwd(), 'Remonsterate'))
            # wait 3 seconds
            time.sleep(3)
            print(Constants.UpdateMonsterSpriteDone)
    except Exception:
        traceback.print_exc()

def update_beyond_chaos():
    try:
        print()
        print()
        print("Would you like to update the Beyond Chaos core files? This will download the latest stable release from "
              "GitHub, replacing the version of Beyond Chaos you are currently running.")
        choice = input("Y/N: ")
        if choice.lower() == "y":
            print(Constants.UpdateBC)
            my_file = Path('BeyondChaos.zip')
            if not my_file.is_file():
                # go get the sprites
                # ping github and get the new released version
                x = requests.get('https://api.github.com/repos/FF6BeyondChaos/BeyondChaosRandomizer/releases/latest').json()
                # get the link to download the latest package
                download_link = x['assets'][0]['browser_download_url']
                # download the file and save it.
                local_filename = download_link.split('/')[-1]
                with requests.get(download_link, stream=True) as r:
                    with open(local_filename, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                time.sleep(3)

            with ZipFile('BeyondChaos.zip', 'r') as zipObj:
                # Extract all the contents of zip file in different directory
                zipObj.extractall(os.getcwd())
                # wait 3 seconds
                time.sleep(3)
                print(Constants.UpdateBCDone)
        else:
            print("Core update skipped.")
    except Exception:
        traceback.print_exc()


if __name__ == '__main__':
    main()
    time.sleep(3)
