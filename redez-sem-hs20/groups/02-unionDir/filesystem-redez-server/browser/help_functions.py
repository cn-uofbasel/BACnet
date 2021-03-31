import os
from os import listdir
import getpass
from utils import color

def hashify_entire_dir(dir_path, unionpath):
	dirs = []
	files = []
	for (dirpath, dirnames, filenames) in os.walk(dir_path):
		for file in filenames:
			files.append(os.path.join(dirpath, file))
		for dir in dirnames:
			dirs.append(os.path.join(dirpath, dir))
	for dir in dirs:
		dir_name = dir.split(os.sep)[-1]
		path = dir.replace(os.sep + str(dir_name), "")
		dir_hashname = unionpath.create_hash(dir)
		os.rename(dir, dir.replace(dir_name, dir_hashname))
		fs_loc = unionpath.hashpath_to_fspath(path)
		unionpath.add_to_dictionary(dir_hashname, dir_name, "directory", path, fs_loc)
		for i in range(len(dirs)):
			dirs[i] = dirs[i].replace(os.path.join(path, dir_name), os.path.join(path, dir_hashname))
		for i in range(len(files)):
			files[i] = files[i].replace(os.path.join(path, dir_name), os.path.join(path, dir_hashname))
	for file in files:
		file_name = file.split(os.sep)[-1]
		path = file.replace(os.sep + str(file_name), "")
		fs_loc = unionpath.hashpath_to_fspath(path)
		extension = ""
		if "." in file_name:
			file_name, extension = file_name.split(".")
			extension = "." + extension
		file_hashname = unionpath.create_hash(file)
		os.rename(file, os.path.join(path, file_hashname))
		unionpath.add_to_dictionary(file_hashname, file_name, "file", path, fs_loc, extension)

def assign_new_hashes_dir(dir_path, unionpath):
	objects = []
	for (dirpath, dirnames, filenames) in os.walk(dir_path):
		for file in filenames:
			objects.append(os.path.join(dirpath, file))
		for dir in dirnames:
			objects.append(os.path.join(dirpath, dir))
	for object in objects:
		hash = object.split(os.sep)[-1]
		path = object.replace(os.sep + str(hash), "")
		info = unionpath.translate_from_hash(hash)
		name = info[0]
		type = info[2]
		extension = info[5]
		hash = unionpath.create_hash(os.path.join(path, name))
		new = os.path.join(path, hash)
		print(color.green("{} -> {}".format(object, new)))
		os.rename(object, new)
		for i in range(len(objects)):
			objects[i] = objects[i].replace(object, new)
		fs_loc = unionpath.hashpath_to_fspath(path)
		unionpath.add_to_dictionary(hash, name, type, path, fs_loc, extension=extension)

def get_files_from_current_dir(unionpath):
	files = []
	for file in listdir(unionpath.current_folder):
		match = unionpath.translate_from_hash(file)
		if match:
			files.append(match)
	files.sort()
	return files

def get_all_files_from_dir(dir):
	files = []
	for (dirpath, dirnames, filenames) in os.walk(dir):
		files.extend(filenames)
	return files

def home_path():
	path = os.getcwd()
	user = getpass.getuser()
	sep = os.sep
	path = os.path.normpath(path)
	path_folders = path.split(os.sep)
	root_idx = None
	user_idx = None
	if user_idx and not root_idx and len([i for i in path_folders if i != ''])>2:
		home_directory = len(path)-len(path[path.find(user):])
		path = path[home_directory+len(user):].replace("{}.uniondir/.root".format(sep),"")
		return path
	elif user_idx and not root_idx:
		path = sep.join(path_folders[root_idx:]).replace("{}.uniondir/.root".format(sep),"")
		return path
	else:
		path = sep + sep.join(path_folders[root_idx:]).replace("{}.uniondir/.root".format(sep),"")
		return path
