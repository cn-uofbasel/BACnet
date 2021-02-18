import hashlib
import os

from utils import folder_structure



#TODO: Wenn ein Dateiverzeichnis geändert wird, erzeugt man einen neuen hash wert. D.H. die alten Directories bleiben bestehen und jedes veränderte Directory fliesst zu einem neuen File mit einem neuen Hash wert. Wir verlieren keine Informationen sondern erzeugen immer wieder neue (append only log).
#--> At the moment we just support the export command which creates a dublicate filesystem and renames the files. The idea (I believe) is to do this in real time: whenever a file is changed: the folder structure is saved and that change appended to the Log (should be easy to implement by justupdating folder_structure.json after every relevant "write" operator command is done). That way we can undo changes like mounting a file system or go back in time to the old state of the file system (5 logs ago for example).

def get_hash(path):
	'''
	USE:
	hash.get_hash(path)
	
	Description:
	Returns hash value of the file (at given path). Probably doesnt work when there are multiple files at the given path so it should be a specific file path not a dictionary path.
	'''
	file = path
	BLOCK_SIZE = 65536 #in 64 kb Blocks
	file_hash = hashlib.sha256()
	with open(file, 'rb') as f:
		f_block = f.read(BLOCK_SIZE)
		while len(f_block) > 0:
		    file_hash.update(f_block)
		    f_block = f.read(BLOCK_SIZE)
		    
	return file_hash.hexdigest()


def get_hash_str(str):
	'''
	USE:
	hash.get_hash(str)

	Description:
	Generates a hash key with a given string
	'''
	hash_object = hashlib.sha1(str.encode())
	return hash_object.hexdigest()
	
def folder_structure_to_hash(folder_path, hash_json_name, dict_json_name):
	'''
	USE:
	hash.folder_structure_to_hash()
	
	Description:
	Saves current folder structure to json and then creates a new json with the hash values of the correspoding files
	'''
	
	hash_path = os.path.join(folder_path, hash_json_name)
	dict_path = os.path.join(folder_path, dict_json_name)
	
	folder_structure.save_current_folder_structure(folder_path)
	dictionary = folder_structure.load_last_saved_folder_structure(folder_path, dict_json_name)
	hash_data = {}
	for path in dictionary:
		hash_data[path] = []
		
	for path in dictionary:
		for f in dictionary[path]:
			file_path = os.path.join(path,f)
			hash_value = get_hash(file_path)
			#TODO: SOLL: Hashwert + Zufallszahl --> hould work when uncommented but not tested
			#random_hex = secrets.token_hex(15)
			#hash_value+=random_hex
			hash_data[path].append(hash_value)
	
	folder_structure.save_to_json(hash_path, hash_data)


