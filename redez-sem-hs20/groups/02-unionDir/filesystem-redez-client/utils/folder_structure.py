import os
from os import listdir
from os.path import isfile, isdir, join
import json
import ntpath
import pathlib

from browser import help_functions
from utils.hash_ import get_hash


#TODO: Namensräume sind nicht einfach eine Tabelle. Aktive definitionsfrage. Wenn es um ein Directory geht steht drin wo man ein mount machen soll.
def save_to_json(name, data, path=None): #TODO: not used currently
	'''
	USE:
	folder_structure.save_to_json(file_name_without_extension, data, [OPTIONAL: path (else cwd)]) 
	
	Description:
	the first command can be used in combination with this one to save the dictionary to a .json file
	'''
	#name+='.json'
	if path:
		name = os.path.join(path,name)
	else:
		name = os.path.join(os.getcwd(),name)
	#data_as_json_string = json.dumps(data, sort_keys=True,indent=4, separators=(',', ': ')) #makes json file human readable
	with open(name, 'w') as f:
		json.dump(data, f, ensure_ascii=False, indent=4)
	f.close()



def read_json(name, folder_path=None): #TODO: not used currently
	'''
	USE:
	folder_structure.read_json(json_name, [OPTIONAL: path (else cwd)])
	
	Description:
	Returns the data contained in the json file.
	'''
	if not folder_path:
		folder_path = os.getcwd()
	path = os.path.join(folder_path,name)
	#path = folder_path
	with open(path, 'r') as f:
		data = json.load(f)
	f.close()
	return data
	
	
		
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


def get_short(path, include=None):
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
	exc = help_functions.get_upper_dir(path) + os.sep
	tree_dict = []
	tree_dict_tmp = [x[0] for x in os.walk(path)]
	print(exc)
	for dir in tree_dict_tmp:
		tree_dict.append(dir.replace(exc, ""))

	return [sorted(tree_dict), sorted(tree_dict_tmp)]

	
def save_current_folder_structure(path): #TODO: doesnt take a path
	'''
	USE:
	folder_structure.save_current_folder_structure([Optional: folder_name])
	
	Description:
	Saves the currently folder structure into a dictionary and saves it as .json file.
	'''
	#TODO: New JSON-structure
	data = file_to_json(path)
	#path = os.path.join(path, help_functions.get_root_name())
	name = help_functions.get_json_names()[0]
		
	save_to_json(name, data, path)

def file_to_json(syspath):
    systemname = str(ntpath.basename(syspath))
    print(systemname)
    data = []
    jsondata = {}
    pathlist = pathlib.Path(syspath).glob('**/*.*')
    for path in pathlist:
        dict = {}
        dict['name'] = str(ntpath.basename(path))
        dict['fullpath'] = systemname+str(path).replace(syspath,"").replace(str(ntpath.basename(path)),"")
        dict['hash'] = get_hash(path)
        data.append(dict)
    jsondata["{}".format(syspath)] = data
    return jsondata

def load_last_saved_folder_structure(folder_path, name):
	'''
	USE:
	folder_structure.load_last_saved_folder_structure(path)
	
	Description:
	Loads the currently folder structure into a dictionary which is returned by the function.
	It loads the saved folder_structure.json file.
	
	Note:
	Given path is the folder where the folder_structure.json resides but without the 'folder_structure.json' part at the end
	'''
	
	folder_structure_dictionary = read_json(name, folder_path)
	return folder_structure_dictionary
	
	
	
	
#To test this:
'''
d = get('/home/kentar/Desktop/Re-Dez_priv/filesystem-redez/code/test',True)
for path in d:
	print(path)
	for f in d[path]:
		print('\t'+f)
sys.exit()
'''



