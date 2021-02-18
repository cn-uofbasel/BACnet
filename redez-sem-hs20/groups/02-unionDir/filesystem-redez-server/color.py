#--- ANSI Escape sequences - VT100 / VT52 ---
'''
USE:
color.[some_color](some_string)

Description:
these functions suround a given string in ANSI Escape sequences for them to be printed out in the given color (=method name)
'''
def green(string):
	return ('\033[92m' + string + '\033[0m')
def greenDark(string):
	return ('\033[32m' + string + '\033[0m')
def blue(string):
	return ('\033[94m' + string + '\033[0m')
def blueDark(string):
	return ('\033[34m' + string + '\033[0m')
def cyan(string):
	return ('\033[36m' + string + '\033[0m')
def yellow(string):
	return ('\033[93m' + string + '\033[0m')
def yellowDark(string):
	return ('\033[33m' + string + '\033[0m')	
def red(string):
	return ('\033[31m' + string + '\033[0m')
def redLight(string):
	return ('\033[91m' + string + '\033[0m')
def purple(string):
	return ('\033[35m' + string + '\033[0m')
def purpleLight(string):
	return ('\033[95m' + string + '\033[0m')
def grey(string):
	return ('\033[2m' + string + '\033[0m')
def underline(string):
	return ('\033[4m' + string + '\033[0m')
def bold(string):
	return ('\033[1m' + string + '\033[0m')
def inverted(string):
	return ('\033[7m' + string + '\033[0m')
def blink(string):
	return ('\033[5m' + string + '\033[0m')
def hidden (string): #TODO: Use for password entry
	return ('\033[8m' + string + '\033[0m')
#--------------------------------------------
	
	
	
def print_it(files, arg=None):
	'''
	USE:
	color.print_it(files_to_be_printed_as_array, [Optional: arg]) where arg determines if there are lines ('-------') printed around the block
	
	Description:
	prints out a given array containing elements in a folder in a color coded way.
	'''
	print(grey('there are ({}) files in this folder'.format(len(files))))
	if arg:
		print('\n-------------------')
	for f in files:
		typ = f.split('.')[-1]
		if typ in ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'tif', 'tiff', 'eps']:
			print("  " + purple(f))
		elif typ in ['txt', 'md']:
			print("  " + f)
		elif typ in ['py', 'json']:
			print("  " + yellow(f))
		elif len(f.split('.')) == 1:
			print("  " + blue(f))
		else:
			print("  " + f)
	if arg:
		print('\n-------------------')
		
		
		
