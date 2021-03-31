import hashlib

def get_hash_from_string(str):
	'''
	USE:
	hash.get_hash(str)
	
	Description:
	Generates a hash key with a given string
	'''
	hash_object = hashlib.sha1(str.encode())
	return hash_object.hexdigest()


def get_hash_from_file(path):
	'''
	USE:
	hash.get_hash_from_file(path)

	Description:
	Returns hash value of the file (at given path). Probably doesnt work when there are multiple files at the given path
	so it should be a specific file path not a dictionary path.
	'''
	file = path
	BLOCK_SIZE = 65536  # in 64 kb Blocks
	file_hash = hashlib.sha256()
	with open(file, 'rb') as f:
		f_block = f.read(BLOCK_SIZE)
		while len(f_block) > 0:
			file_hash.update(f_block)
			f_block = f.read(BLOCK_SIZE)

	return file_hash.hexdigest()