import os
from pathlib import Path
import json

server_path = dir_path = os.path.dirname(os.path.realpath(__file__))

def folder(name):
	home = str(Path.home())
	dir = ".filesystem_server"
	path = os.path.join(home, dir)
	path = os.path.join(path, name)
	if not os.path.exists(path):
		os.mkdir(path)
	return path

def file_path_in_filesystem(name):
	home = str(Path.home())
	dir = ".filesystem_server"
	path = os.path.join(home, dir)
	path = os.path.join(path, name)
	return path

def file(name):
	home = str(Path.home())
	dir = ".filesystem_server"
	path = os.path.join(home, dir)
	path = os.path.join(path, name)
	return open(path, "wb")

def json_file(name):
	home = str(Path.home())
	dir = ".filesystem_server"
	path = os.path.join(home, dir)
	path = os.path.join(path, name)
	file = open(path, "w")
	print(file)
	json.dump({}, file, indent=4)
	file.close()
	return

def config_folder():
	dir = "../.server_config"
	path = os.path.join(server_path, dir)
	flag = False
	if not os.path.exists(path):
		os.mkdir(path)
		flag = True
	return path, flag

def config_client_files():
	filename1 = "server_config.json"
	filename2 = "client_list.json"
	path, flag = config_folder()
	file1 = os.path.join(path, filename1)
	file2 = os.path.join(path, filename2)
	if not os.path.isfile(file1):
		config_file = open(file1, "w+")
		json.dump({}, config_file , indent=4)
		config_file.close()
	if not os.path.isfile(file2):
		config_file2 = open(file2, "w+")
		json.dump({}, config_file2 , indent=4)
		config_file2.close()
	return file1, file2, flag

def filesystem_path():
	home = str(Path.home())
	dir = ".filesystem_server"
	path = os.path.join(home, dir)
	return path

def filesystem():
	home = str(Path.home())
	dir = ".filesystem_server"
	path = os.path.join(home, dir)
	flag = False
	if not os.path.exists(path):
		os.mkdir(path)
		flag = True
	return path, flag

def get_json_content(clients_file):
	clients_json = open(clients_file, "r")
	return json.load(clients_json)

def update_server_list(config_file, ip, name):
	config_json = open(config_file, "r")
	serverlist = json.load(config_json)
	config_json.close()
	serverlist.update({name:ip})
	config_json = open(config_file, "w")
	json.dump(serverlist, config_json, indent=4)
	config_json.close()
