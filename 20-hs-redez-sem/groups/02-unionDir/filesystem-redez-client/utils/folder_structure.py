import os
from os import listdir
from os.path import isfile, isdir, join
import json
from browser import help_functions
		
def search(path, root, tree_dict, include=None):
	'''
	USE:
	*use via get function: "folder_structure.get(path)"
	
	Description:
	searches all sub folders and saves it to a dictionary (tree_dict) in this format:
		{
		  folder_path : [files (not folders) contained in this folder as array],
		  ...         : ...
		}
	
	Note:
	if include argument is given, the folders are included in the output as well (instead of just the files)
	'''
	folders = [f for f in listdir(path) if isdir (join(path, f))]
	files   = [f for f in listdir(path) if isfile(join(path, f))]
	
	if folders != [] and files != [] and path != root:  # so files that are in a folder containing other folders are also added
		tree_dict[path] = [f for f in listdir(path) if isfile(join(path, f))]
	if path == root: #in order to display the contents of the root folder as well (otherwise ignored)
		if include:
			tree_dict[path] = [f for f in listdir(path)]
		else:
			tree_dict[path] = [f for f in listdir(path) if isfile(join(path, f))]
		for f in folders:
			if include:
				search(join(path, f), root, tree_dict, True)
			else:
				search(join(path, f), root, tree_dict)
	elif folders != []:  # recursive search goes one level deeper
		for f in folders:
			if include:
				tree_dict[path] = [f for f in listdir(path)] #include directories
				search(join(path, f), root, tree_dict, True)
			else:
				search(join(path, f), root, tree_dict)
	else: # break condition: add it to the tree_dict structure
		tree_dict[path] = [f for f in listdir(path) if isfile(join(path, f))]



def get(path, include=None):
	'''
	USE:
	folder_structure.get(path) 
	
	Description:
	makes use of the recursive function "folder_structure.search()" which searches all sub folders and returns a dictionary in this format:
		{
		  folder_path : [files (not folders) contained in this folder as array],
		  ...         : ...
		}
	
	Note:
	if include argument is given, the folders are included in the output as well (instead of just the files)
	'''
	tree_dict = {} # dictionary with all directories and their files organized as a dictionary: {folder_path:[items_in_folder,listed,in,this,array]}
	if include:
		search(path, path, tree_dict, True)
	else:
		search(path, path, tree_dict)
	return tree_dict



	





