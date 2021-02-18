from utils import color
import os
from os import listdir
from os.path import isfile, join
from browser import help_functions


def has_valid_config(root_path):
	'''
	USE:
	permission.has_valid_config(root_path)
	
	Description:
	Returns True or False depending on wheather or not a valid config.json file is present in the given path folder.
	'''
	for f in listdir(root_path):
		if isfile(join(root_path, f)):
			if f == 'config.json': #TODO: just checks if there is a config file present, not if it is valid
				return True
	return False
	
		

def permission(cmd, loc):
	'''
	USE:
	permission.permission(str(operator), location) where location is in ['inside', 'outside'] meaning inside the root_folder or outside of it.
	
	Description:
	Returns True or False depending on wheather or not a given operator has permission to write. Check use in permission.has(),
	'''
	dictionary = {
		#TODO: currently the statements that are [True, True] also print out the 'You don't have write permissions' Error which is annoying since those commands dont need write permission (i.e.: sif user types ls the error shows up but ls still works since it only reads)
		'cd'			: [True, False],
		#'ls'			: [True, True],
		'cat'			: [True, False],
		#'mk'			: [True, True],
		#'add'			: [True, True],
		'rm'			: [True, False],
		#'mt'			: [True, True],
		#'umt'			: [True, True],
		#'exp'			: [True, True],
		#'mkp'			: [True, True],
		#'pwd'			: [True, True],
		'img'			: [True, False],
		'txt'			: [True, False],
		'mv'			: [True, False],
		'cp'			: [True, False],
		'rn'			: [True, False],
		#'--help' 		: [True, True],
		#'f'				: [True, True]
	}
	if loc=='inside':
		return dictionary[cmd][0]
	elif loc=='outside':
		return dictionary[cmd][1]

def inside_or_outside_root_folder(path):
	'''
	USE:
	permission.inside_or_outside_root_folder(path)
	
	Description:
	Returns 'inside' or 'outside' depending on weather or not the given path is inside the root_folder or not.
	'''
	path = os.path.normpath(path)
	path_folders = path.split(os.sep)
	if help_functions.get_root_name() in path_folders:
		return 'inside'
	else:
		print(color.red('You don\'t have write permissions in this folder'))
		return 'outside'
	
def has(path, cmd):
	'''
	USE:
	permission.has(path, str(operator))
	
	Description:
	Returns if the given operator has permission to function within the realm of the given path.
	'''
	loc = inside_or_outside_root_folder(path)
	return permission(cmd, loc)


