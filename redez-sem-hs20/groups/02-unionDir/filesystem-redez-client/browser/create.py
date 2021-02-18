'''
Project Imports
'''
from utils import color, folder_structure, hash_
from pathlib import Path
import random

'''
System Imports
'''
import os
import json

'''
Description:
Creates a welcoming message for the user upon starting up the program.
'''
def welcome():

    msg = color.cyan("############################################################################\n")
    msg += color.cyan("#                      ~ {}{}\n").format(
        color.purple("Redecentralised Filesystem"), color.cyan(" ~                      #"))
    msg += color.cyan("#                                                                          #\n")
    msg += color.cyan("#   - Establish connection with to file server with {}   {}\n").format(
        color.yellow("register <IP> <Name>"), color.cyan("#"))
    msg += color.cyan("#   - Enter {} {}\n").format(color.yellow("name"), color.cyan(
        "of known server                   	                   #"))
    msg += color.cyan("#   - List names of all known servers with {}           	   {}\n").format(
        color.yellow("serverlist"), color.cyan("#"))
    msg += color.cyan("#   - Exit program with {}                     	             	   {}\n").format(
        color.yellow("quit"), color.cyan("#"))
    msg += color.cyan("############################################################################\n")
    return msg

def thank():
    names = ['Ken Rotaris', 'Tunahan Erbay', 'Leonardo Salsi']
    random.shuffle(names)  # names in random order
    names[0] = color.bold(color.red(names[0]))
    names[1] = color.bold(color.greenDark(names[1]))
    names[2] = color.bold(color.yellow(names[2]))
    random.shuffle(names)
    msg = '\n   Thanks for using our Application!\n   Made with ' + color.bold(
            color.redLight('❤')) + ' by: {0}, {1}, {2}\n'.format(names[0], names[1], names[2])
    return msg

def config_folder():
    home = str(Path.home())
    dir = ".filesystem_config"
    path = os.path.join(home, dir)
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def serverlist_file(user, fsrootpath):
    filename = "servers.json"
    path = config_folder()
    file = os.path.join(path, filename)
    fspath = os.path.join(fsrootpath, "localhost")
    if not os.path.exists(fspath):
        os.mkdir(fspath)
    if not os.path.isfile(file):
        serverlist = {}
        hashk = hash_.get_hash_str("127.0.0.1{}".format(user))
        serverlist.update({"localhost": {"ip":"127.0.0.1", "hash":hashk, "path": fspath , "mounts": []}})
        config_file = open(file, "w+")
        json.dump(serverlist, config_file, indent=4)
        config_file.close()
    return file

def content_file(fsrootpath, hash):
    path = os.path.join(fsrootpath, "{}.json".format(hash))
    if not os.path.exists(path):
        content_file = open(path, "w+")
        json.dump({}, content_file, indent=4)
        content_file.close()
    return path

def filesystem():
    home = str(Path.home())
    dir = ".filesystem"
    path = os.path.join(home, dir)
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def serverlist(config_file):
    config_json = open(config_file, "r")
    return json.load(config_json)

def save_server_info(config_file, ip, name, hash, fsrootpath):
    config_json = open(config_file, "r")
    serverlist = json.load(config_json)
    fspath = os.path.join(fsrootpath, name)
    if not os.path.exists(fspath):
        os.mkdir(fspath)
    config_json.close()
    serverlist.update({name: {"ip": ip, "hash":hash, "path": fspath, "mounts": []}})
    config_json = open(config_file, "w")
    json.dump(serverlist, config_json, indent=4)
    config_json.close()

def logo():
    line = "                            `://///    ://///:                              \n"
    line += "                         `+dmmmmmms   `mmmmmmo   .`                         \n"
    line += "                        `dmmmmmmmm.   +mmmmmm-   od`                        \n"
    line += "                        smmmmmmmmy    dmmmmmm    hms                        \n"
    line += "                        hmmmmmmmm-   :mmmmmms   `mmh                        \n"
    line += "                        hmmmmmmm:   `mmmmmmm`   +mmh                        \n"
    line += "                        hmmmmmmm:   `mmmmmmm`   +mmh                        \n"
    line += "                        hmmmmmmh    +mmmmmmy    ymmh                        \n"
    line += "                        hmmmmmm+    ymmmmmm-   `mmmh                        \n"
    line += "                        hmmmmmm:    /mmmmd/    ommmh                        \n"
    line += "                        hmmmmmm/     .::-     :mmmmh                        \n"
    line += "                        smmmmmmd`            +mmmmms                        \n"
    line += "                        `hmmmmmmd/`       .+dmmmmmh`                        \n"
    line += "                          /hmmmmmmmhyssyhmmmmmmmh/                          \n"
    line += "                            `-://////////////:-`                            \n"
    line = color.purple(line)
    return line
