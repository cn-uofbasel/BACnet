import os
from os import listdir
import re
import getpass
import shutil
from utils import color, folder_structure, error
from net import protocol
import subprocess as subprocess
from subprocess import DEVNULL, PIPE
import hashlib
import math, datetime

def ls_help(arg=None, client=None):
	'''
	USE:
	operators.ls(path, [optional: -r])
	
	Description: 
	List files and directories. If -r is given as last argument, it recursively lists all files in the subdirectories of the current directory.
	'''
	files = []
	path = client.current_folder
	if arg:
		dictionary = folder_structure.get(path)
		for path in dictionary:
			files.append(path)
			for f in dictionary[path]:
				files.append("   "+f)
		return files
	else:
		for file in listdir(path):
			match = client.translate_from_hash(file)
			if match:
				files.append(match)
		files.sort()
		return files

def open_help(file):
	if os.sep in file:
		print("maybeoutside")
	try:
		DEVNULL = open(os.devnull, 'wb')
		p = subprocess.Popen(['xdg-open /WAIT', file], stdout=PIPE, stderr=DEVNULL)
		print("closed")
		return True
	except:
		return False


def make_dir_tree_help(client, dir_name, dir_path="root", dst=None):
	'''
	USE:
	operators.make_dir(cmds) where cmds = [name_of_dir]

	Description:
	Creates an empty folder in the current directory.

	Note:
	name_of_dir is the name the folder takes on upon creation.
	'''
	flag = False
	dirs = None
	tmp_path = ""
	if dst:
		tmp_path = client.current_folder
		client.current_folder = dst
		os.chdir(client.current_folder)
	path = client.current_folder
	if os.sep in dir_path and dir_path != client.root_dir:
		flag = True
		dirs = dir_path.split(os.sep)
		for i in range(len(dirs) - 1):
			dirs[i] = client.translate_to_hash(dirs[i], path, True)
			path = os.path.join(path, dirs[i])
			if not dirs[i]:
				return
			dir_name = _list_to_path(dirs)
	bool, hashname, timestamp = protocol.add_dir(client, dir_name)
	if bool:
		curr = client.current_folder
		if flag:
			for i in range(len(dirs) - 1):
				os.chdir(dirs[i])
			client.current_folder = os.getcwd()
		location = client.current_folder
		fs_loc = client.hashpath_to_fspath(location)
		dir_path = os.path.join(client.current_folder, hashname)
		os.mkdir(dir_path)
		os.chdir(curr)
		client.current_folder = os.getcwd()
		client.add_to_dict(hashname, dir_name.split(os.sep)[-1], "directory", location, fs_path=fs_loc, timestamp=timestamp)
		if dst:
			client.current_folder = tmp_path
			os.chdir(client.current_folder)
		return hashname, location

def make_dir_help(client, dir_name):
	'''
	USE:
	operators.make_dir(cmds) where cmds = [name_of_dir]

	Description:
	Creates an empty folder in the current directory.

	Note:
	name_of_dir is the name the folder takes on upon creation.
	'''
	flag = False
	path = client.current_folder
	dirs = None
	if os.sep in dir_name:
		flag = True
		dirs = dir_name.split(os.sep)
		for i in range(len(dirs) - 1):
			dirs[i] = client.translate_to_hash(dirs[i], path, False)
			path = os.path.join(path, dirs[i])
			if not dirs[i]:
				return
			dir_name = _list_to_path(dirs)
	bool, hashname, timestamp = protocol.add_dir(client, dir_name)
	if bool:
		curr = client.current_folder
		if flag:
			curr = client.current_folder
			for i in range(len(dirs) - 1):
				os.chdir(dirs[i])
			client.current_folder = os.getcwd()
		location = client.current_folder
		fs_loc = client.hashpath_to_fspath(location)
		dir_path = os.path.join(client.current_folder, hashname)
		os.mkdir(dir_path)
		os.chdir(curr)
		client.current_folder = os.getcwd()
		if os.sep in dir_name:
			client.add_to_dict(hashname, dir_name.split(os.sep)[-1], "directory", location, fs_path=fs_loc, timestamp=timestamp)
		else:
			client.add_to_dict(hashname, dir_name.split(os.sep)[-1], "directory", location, fs_path=fs_loc, timestamp=timestamp)
		return hashname

def _list_to_path(dirs):
	path = ""
	for i in range(len(dirs) - 1):
		path += dirs[i] + os.sep
	path += dirs[len(dirs) - 1]
	return path

def add_help(src, client, dst):
	if os.path.isdir(src):
		return _add_dir(src, client, dst)
	elif os.path.isfile(src):
		return _add_file(src, client, dst)

def _add_file(src, client, dst):
	bool, hashname, timestamp = protocol.add_file(src, dst, client)
	filename = _get_filename(src)
	got_filename = ""
	flag = False
	if bool:
		shutil.copy2(src, dst)
		extension = os.path.splitext(src)[1]
		fs_path = client.hashpath_to_fspath(dst)
		filepath = os.path.join(dst, filename)
		if client.root_dir in src:
			got_filename = client.translate_from_hash(src.split(os.sep)[-1])[0]
			if got_filename:
				flag = True
		new_filepath = filepath.replace(filename, "{}{}".format(hashname, extension))
		if flag:
			client.add_to_dict(hashname, got_filename, "file", dst, extension, fs_path=fs_path, timestamp=timestamp)
		else:
			client.add_to_dict(hashname, filename, "file", dst, extension, fs_path=fs_path, timestamp=timestamp)
		os.rename(filepath, new_filepath)
		return "{}{}".format(hashname, extension)

def _add_dir(src, client, dst):
	folders, folders_long = folder_structure.get_short(src)
	folders_rename = []
	folders_dict = {}
	folders_hashed = []
	first = True
	upmost_hashname=""
	for i in range(len(folders)):
		if os.sep in folders[i]:
			name = folders[i].split(os.sep)[-1]
		else:
			name = folders[i]
		hashname, location = make_dir_tree_help(client, name, folders[i], dst=dst)
		if first:
			upmost_hashname = hashname
			first = False
		if client.root_dir in folders_long[i]:
			folders_rename.append([client.translate_from_hash(folders_long[i].split(os.sep)[-1])[0], os.path.join(location, hashname)])
		folders_dict.update({name: hashname})
	for folder in folders:
		folders_hashed.append(hashify(folder, folders_dict))
	for renames in folders_rename:
		rn_help(renames[1], renames[0], client)
	for i in range(len(folders_hashed)):
		current_dir = dst + os.sep + folders_hashed[i]
		files = _get_all_path_of_files(folders_long[i])
		for file in files:
			_add_file(file, client, current_dir)
	return upmost_hashname

def hashify(path, name_dict):
	ret = ""
	if os.sep in path:
		dirs = path.split(os.sep)
		for i in range(len(dirs)):
			dirs[i] = name_dict.get(dirs[i])
		for i in range(len(dirs) - 1):
			ret += dirs[i] + os.sep
		return ret + dirs[len(dirs) - 1]
	else:
		return name_dict.get(path)

def _get_all_path_of_files(path):
	files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
	for i in range(len(files)):
		files[i] = path + os.sep + files[i]
	return files

def _get_filename(src):
	src_spl = src.split(os.sep)
	return src_spl[-1]

def rm_help(name, client=None, start_path=None, suppress=False): #TODO: Make this happen
	'''
	USE:
	operators.rm(name_of_file)
	
	Description: 
	Remove a file and empty or non empty folders.
	
	Note:
	name_of_file can have an extension (if you wish to delete a file) or no extension (if you want to delete a folder)
	'''
	hash = client.translate_to_hash(name, client.current_folder)
	extension = client.translate_from_hash(hash)[5]
	if hash:
		if start_path:
			curr = start_path
		else:
			curr = client.current_folder
		path = os.path.join(curr, hash) + extension
		if os.path.isfile(path):
			extension = client.translate_from_hash(hash)[5]
			resp = protocol.remove(client, hash, str(extension))
			if resp:
				os.remove(path)
				client.edit_content_file(hash, 'del')
				return True
		elif os.path.isdir(path):
			content = []
			content.append(path.split(os.sep)[-1])
			for (dirpath, dirnames, filenames) in os.walk(path):
				content += dirnames
				content += [re.sub('[.][^.]+$','',x) for x in filenames]
			count = len(content)
			if count > 1 and not suppress:
				while True:
					inp = input(color.yellow("This directory contains files. Are you sure you want to delete it and all "
											 "of its content? [y/n/show] -> "))
					if inp.lower() == "y" or inp.lower() == "yes":
						break
					elif inp.lower() == "n" or inp.lower() == "no":
						return False
					elif inp.lower() == "show":
						dir_icon = "📁"
						file_icon = "📄"
						for c in content:
							info = client.translate_from_hash(c)
							name = info[0]
							type = info[2]
							if type == 'file':
								print("{}  ".format(file_icon) + color.purple(name))
							elif type == 'directory':
								print("{}  ".format(dir_icon) + color.blue(name))
			for chash in content:
				resp = protocol.delete(client, chash)
				if resp:
					client.edit_content_file(chash, 'del')
				else:
					return False
			resp = protocol.remove(client, hash, "None")
			if resp:
				shutil.rmtree(path)
			return True
		print(color.purple(str(path)))
	else:
		print(color.red("The file/folder {} does not exist.".format(name)))

def quit_help(client=None):
	return protocol.quit(client)

def rn_help(src, name, client=None):
	old_name = client.translate_from_hash(src.split(os.sep)[-1])[0]
	client.edit_content_file(re.sub('[.][^.]+$', '',src.split(os.sep)[-1]), 'ren-name', name=name)
	if os.path.isdir(src):
		content = []
		for (dirpath, dirnames, filenames) in os.walk(src):
			content += dirnames
			content += [re.sub('[.][^.]+$', '', x) for x in filenames]
		for c in content:
			client.edit_content_file(c, 'ren-fs_path', name=old_name, repl=name)

def mv_help(src=None, dst=None, client=None):
	src_ret, dst_ret = None, None
	if src:
		src = os.path.join(client.current_fs_folder, src)
		src_path = ""
		if os.sep in src:
			src_dirs = src.split(os.sep)
			for i in range(len(src_dirs) - 1):
				if i == 0:
					src_path += src_dirs[i]
				else:
					src_path += os.sep + src_dirs[i]
			src_name = src_dirs[len(src_dirs) - 1]
		else:
			src_path = ""
			src_name = src
		src_ret = client.fspath_to_hashpath(src_name, src_path)
		if not src_ret:
			return 1

	if dst:
		dst = os.path.join(client.current_fs_folder, dst)
		dst_path = ""
		if os.sep in dst:
			dst_dirs = dst.split(os.sep)
			for i in range(len(dst_dirs) - 1):
				if i == 0:
					dst_path += dst_dirs[i]
				else:
					dst_path += os.sep + dst_dirs[i]
			dst_name = dst_dirs[len(dst_dirs) - 1]
		else:
			dst_path = ""
			dst_name = dst
		dst_ret = client.fspath_to_hashpath(dst_name, dst_path)
		if not dst_ret:
			return 2

	return [src_ret, dst_ret]

def mnt_help(user, fs_name, dst, client):
	res = protocol.mount(client, user, fs_name, dst)
	if res == False:
		return False
	else:
		bool, hashdir, filehashes, root_dir_hash = res
		for filehash in filehashes:
			client.edit_content_file(filehash, 'ren-fs_path_full', hashdir=hashdir)
		client.update_serverlist('add-mount', root_dir_hash)
		return True

def print_file(paths, arg=None, additional=False, client=None):
	dir_icon = "📁"
	file_icon = "📄"
	mount_icon = "📦"
	img_icon = "🖼"
	music_icon = "🎵"
	movie_icon = "🎥"
	name, time, type, location, hash, extension, fs_path = 0, 1, 2, 3, 4, 5, 6
	f_list = []
	d_list = []
	for p in paths:
		if p[type] == 'file':
			f_list.append(p)
		elif p[type] == 'directory':
			d_list.append(p)
	paths = f_list + d_list
	if arg:
		print('\n-------------------')
	if not additional:
		for p in paths:
			if p[type] == 'file':
				icon = file_icon
				if p[extension] in [".png",".jpg",".jpeg",".bmp",".gif", ".eps"]:
					icon = img_icon
				elif p[extension] in [".mp3", ".wav", ".flac", ".aac"]:
					icon = music_icon
				elif p[extension] in [".mp4", ".mov", ".avi", ".wmv"]:
					icon = movie_icon
				print("{}  ".format(icon) + color.purple(p[name]))
			elif p[type] == 'directory':
				icon = dir_icon
				if p[hash] in client.get_mounts():
					icon = mount_icon
				print("{}  ".format(icon) + color.blue(p[name]))
	else:
		for p in paths:
			date = datetime.datetime.fromtimestamp(int(p[time])).strftime('%m/%d/%Y %H:%M:%S')
			if p[type] == 'file':
				if p[type] == 'file':
					icon = file_icon
					if p[extension] in [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".eps"]:
						icon = img_icon
					elif p[extension] in [".mp3", ".wav", ".flac", ".aac"]:
						icon = music_icon
					elif p[extension] in [".mp4", ".mov", ".avi", ".wmv"]:
						icon = movie_icon
				if not str(p[extension]):
					add_info = color.cyan(" \tDate: {}  \tFingerprint: {}".format(date, p[time]))
				else:
					add_info = color.cyan(" \tType: {}  \tDate: {}  \tFingerprint: {}".format(p[extension], date, p[time]))
				print("{}  ".format(icon) + color.purple(p[name]) + add_info)
			elif p[type] == 'directory':
				icon = dir_icon
				if p[hash] in client.get_mounts():
					icon = mount_icon
				add_info = color.cyan(" \tDate: {}  \tFingerprint: {}".format(date, p[time]))
				print("{}  ".format(icon) + color.blue(p[name]) + add_info)
	if arg:
		print('\n-------------------')

def home_path():
	'''
	USE:
	help.home_path(system_user_name)
	
	Description:
	Returns the shortened form of the home directory if path becomes too long. if user is in a directory called help_functions.get_root_name() then it returns for example "~root_mockup"
	'''
	path = os.getcwd()
	user = getpass.getuser()
	root = get_root_name()
	sep  = os.sep
		
	path = os.path.normpath(path)
	path_folders = path.split(os.sep)

	root_idx = None
	user_idx = None

	try:
		root_idx = path_folders.index(root)
	except: #substring not found
		try:
		    user_idx = path_folders.index(user)
		except: #substring not found
		    return path.replace("{}.filesystem".format(sep),"")
		    
	if user_idx and not root_idx and len([i for i in path_folders if i != ''])>2: #root not found in path but user found
		home_directory = len(path)-len(path[path.find(user):])
		path = path[home_directory+len(user):].replace("{}.filesystem".format(sep),"")
		#path = "~" + sep +sep.join(path_folders[user_idx:])
		return path
	elif user_idx and not root_idx:
		path = sep.join(path_folders[root_idx:]).replace("{}.filesystem".format(sep),"")
		return path
	else: #root found in path - WORKS
		path = sep + sep.join(path_folders[root_idx:]).replace("{}.filesystem".format(sep),"")
		return path



def get_root_name():
	'''
	USE:
	help_functions.get_root_name()
	
	Description:
	Returns the root folder name.
	'''
	return 'root_mockup'
	
	
	
def get_json_names():
	'''
	USE:
	help_functions.get_json_names()
	
	Description:
	Returns the .json file names.
	'''
	return ['folder_structure.json', 'hash_data.json']



def get_last_item_name_of_path(path):
	'''
	USE:
	help_functions.get_last_item_name_of_path(path)
	
	Description:
	Returns the last part of a path string. For example: 'a/b/c/d' --> 'd'
	'''
	return os.path.basename(os.path.normpath(path))
	

def get_upper_dir(path):
	dirs = path.split(os.sep)
	ret = ""
	for i in range(len(dirs) - 2):
		ret += dirs[i] + os.sep
	ret += dirs[len(dirs) - 2]
	return ret

def cd_Up_one_directory(path):
	'''
	USE:
	help_functions.cd_Up_one_directory(path)
	
	Description:
	Does the same to the path string as what 'cd ..' does to the path.
	'''
	name = get_last_item_name_of_path(path)
	path = path.replace(name,'') #Maybe this can cause problems? because it doesnt remove the last / after the path --> 'this/is/a/path' becomes 'this/is/a/' instead of 'this/is/a' works on linux when tested
	return path
	
	
	
def findnth(string, substring, n):
	'''
	USE:
	help_functions.findnth(string, substring, n)
	
	Description:
	Returns the index of the nth occurance of the substring character in string
	'''
	parts = string.split(substring, n+1)
	if len(parts) <= n+1:
		return -1
	return (len(string)-len(parts[-1])-len(substring))




def clear():
    try:
        if os.name == 'nt':
            _ = os.system('cls')
        else:
            _ = os.system('clear')
    except:
        None

def create_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)
		
