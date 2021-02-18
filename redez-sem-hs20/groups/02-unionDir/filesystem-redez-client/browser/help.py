from utils import color


def spfc_opr(operator, key=None):
	'''
	USE: help.opr(operator, [optional: key])
	
	Description:
	returns the speciffic operator needed for the '--help' text.
	
	Notes:
	- if the key argument is passed as True, the function will return the key instead of the entry associeated with it.
	- if you wish to expand the aliases, simply add them to the corresponding list
	- if you add extra operators, make sure to add them here ad well as in help.dct() and the error.get() dictionary and the help.help() dictionary.
	'''
	operator = operator.lower()
	dictionary = {
		#speciffic op.	|  aliases
		'cd'			: ['cd','chdir'],
		'reg'			: ['reg', 'rgstr', 'register'],
		'open'			: ['open', 'op'],
		'ls'			: ['ls', 'list', 'l', 'ls+', 'l+', "list+"],
		'srv'			: ['srv', 'srvls', 'serverlist'],
		'cat'			: ['cat', 'read', 'get'],
		'mk'			: ['mk','mkd','mkdir','makedir'],
		'add'			: ['add', 'put '],
		'rm'			: ['rm', 'delete', 'del', 'remove'],
		'mount'			: ['mt', 'mount', 'mnt'],
		'unmount'		: ['umt', 'unmount', 'umt'],
		'exp'			: ['exp', 'export'],
		'mkp'			: ['mkp','mockup'],
		'pwd'			: ['pwd','cwd','getcwd'],
		'img'			: ['img', 'image'],
		'txt'			: ['txt', 'text'],
		'mv'			: ['mv', 'move'],
		'cp'			: ['cp', 'copy'],
		'rn'			: ['rn', 'rename'],
		'f'				: ['f', 'find', 'locate', 'search'],
		'--help' 		: ['--help', '-help', 'help', 'hlp', '-h', 'h'],
		'q'				: ['q', '-q','quit'],
		'clear'			: ['clear', 'clc', 'c', 'clean'],
		'lines'			: ['lines','ln'],
		'y'		        : ['y','yes'],
		'n'		        : ['n','no'],

	}
	for k in dictionary:
		for e in dictionary[k]:
			if operator == e:
				if key: #key = True
					return k
				else: #key = False --> return entry
					return dictionary[k]
	return -1
	
	
	
def check_if_alias(operator, expected):
	'''
	USE:
	help.check_if_alias(some_operator, expected_operator)
	
	Description:
	Checks if the given (first arg) operator is a alias of the expected_operator.
	'''
	operator = operator.lower()
	check = spfc_opr(operator)
	if check == -1 or expected not in check:
		return False
	else:
		return True



def dct(operator):
	'''
	USE: help.dct(specific_operator)
	
	Description:
	returns the '--help' text from a speciffic operator
	
	Notes:
	-The speciffic operator can be obtained with:
		help.opr(operator)
	- if you add extra operators, make sure to add them here ad well as in help.spfc_opr() and the error.get() dictionary and the help.help() dictionary.
	'''
	dictionary = {
		#command   |arguments					|description
		'cd'     : ['args: folder_name'			,'Change the current working directory.'],
		'ls'     : ['args: [optional: ls+]'		,'List files and directories. If a + is appended to the commmand, additional info gets displayed.'],
		'open'	 : ['args: file_name'		,'Opens the specified file.'],
		'srv'	 : ['args: None'				,'Lists all remembered servers.'],
		'cat'    : ['args: file_name, [optional: lines_to_print_as_int]','Read text file (if file is image, it will open) or reads a range from a file when int is given.'],
		'mk'     : ['args: file_name, [optional: path]','Creates a new folder in the current directory.'],
		'add'	 : ['args: name, [optional: path]', 'Adds an existing file to the filesystem. If the second argument is empty, the file is copied to the root of the filesystem.'],
		'rm'     : ['args: name, [optional: path]','Remove a file and empty or non empty folders.'],
		'mt'     : ['args: ???'					,'Mounts an external filesystem, making it accessible and attaching it to your existing directory structure.'],
		'umt'    : ['args: ???'					,'Unmounts a previously mounted filesystem, removing it from your existing directory structure.'],
		'exp'    : ['args: None'				,'Prepares the mockup folder for export by renaming and encrypting all the files (except config.json) as a copy of root_mockup. Note: Make sure you are located in the folder containing the root_mockup (or in any of it\'s sub-folders.)'],
		'mkp'    : ['args: [optional: folder_depth(int)_OR_folder_name(string)]','Creates a mockup directory called "root_mockup" directory which is a random directory tree with randomply placed random files.'],
		'pwd'    : ['args: None'				,'Prints the full current working directory.'],
		'img'    : ['args: [optional: image_name]','Creates a random image file. If second argument is not given it is called "expl.png". if it is given, the file is created with the given name (or at desired location if ./location/file_name.png is passed).'],
		'txt'    : ['args: [optional: text_name]','Creates a random text file. If second argument is not given it is called "expl.txt". if it is given, the file is created with the given name (or at desired location if ./location/file_name.txt is passed).'],
		'mv'	 : ['args: object_to_be_moved, new_location','Moves an file/folder (and all subfolders and files if there are any) into the new location.'],
		'cp'	 : ['args: object_to_be_moved, new_location','Copies an file/folder (and all subfolders and files if there are any) into the new location.'],
		'rn'	 : ['args: object_to_be_renamed','renames an file/folder.'],
		'f'	 	 : ['args: object_to_be_found','Finds a file/folder and returns its location. If -r argument is passed it searches all subfolders as well.'],
		'q'      : ['args: None'				,'Quits the program.'],
		'--help' : ['[optional: operator]'		,'Get list of all commands. If speciffic operator is given as secon argument, it prints out only the help section for that operator.'],
		'clear'	 : ['args: None'				,'Clears the program terminal.'],
		'lines'	 : ['args: None'				,'Count all lines in all .py in current directory.']
	}
	return dictionary[operator]



def help():
	'''
	USE: help.help()
	
	Description:
	returns the '--help' text
	
	Notes:
	if you add extra operators, make sure to add them here ad well as in help.spfc_opr() and the error.get() dictionary and the help.dct() dictionary.
	'''
	css_1='\n\n   '
	css_2='\n      '
	help = color.green('this is the --help section:') + \
		   css_1 +'» ' + color.bold(str(spfc_opr('cd', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('cd'))) + css_2 + '' + color.yellow(dct('cd')[0]) + css_2 + '' + color.grey(dct('cd')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('ls', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('ls'))) + css_2 + '' + color.yellow(dct('ls')[0]) + css_2 + '' + color.grey(dct('ls')[1]) + \
		   css_1 + '» ' + color.bold(str(spfc_opr('open', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('open'))) + css_2 + '' + color.yellow(dct('open')[0]) + css_2 + '' + color.grey(dct('open')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('srv', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('srv'))) + css_2 + '' + color.yellow(dct('srv')[0]) + css_2 + '' + color.grey(dct('srv')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('cat', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('cat'))) + css_2 + '' + color.yellow(dct('cat')[0]) + css_2 + '' + color.grey(dct('cat')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('mk', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('mk'))) + css_2 + '' + color.yellow(dct('mk')[0]) + css_2 + '' + color.grey(dct('mk')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('add', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('add'))) + css_2 + '' + color.yellow(dct('add')[0]) + css_2 + '' + color.grey(dct('add')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('rm', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('rm'))) + css_2 + '' + color.yellow(dct('rm')[0]) + css_2 + '' + color.grey(dct('rm')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('mt', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('mt'))) + css_2 + '' + color.yellow(dct('mt')[0]) + css_2 + '' + color.grey(dct('mt')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('umt', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('umt'))) + css_2 + '' + color.yellow(dct('umt')[0]) + css_2 + '' + color.grey(dct('umt')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('exp', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('exp'))) + css_2 + '' + color.yellow(dct('exp')[0]) + css_2 + '' + color.grey(dct('exp')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('mkp', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('mkp'))) + css_2 + '' + color.yellow(dct('mkp')[0]) + css_2 + '' + color.grey(dct('mkp')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('img', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('img'))) + css_2 + '' + color.yellow(dct('img')[0]) + css_2 + '' + color.grey(dct('img')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('txt', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('txt'))) + css_2 + '' + color.yellow(dct('txt')[0]) + css_2 + '' + color.grey(dct('txt')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('mv', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('mv'))) + css_2 + '' + color.yellow(dct('mv')[0]) + css_2 + '' + color.grey(dct('mv')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('cp', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('cp'))) + css_2 + '' + color.yellow(dct('cp')[0]) + css_2 + '' + color.grey(dct('cp')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('rn', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('rn'))) + css_2 + '' + color.yellow(dct('rn')[0]) + css_2 + '' + color.grey(dct('rn')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('f', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('f'))) + css_2 + '' + color.yellow(dct('f')[0]) + css_2 + '' + color.grey(dct('f')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('lines', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('lines'))) + css_2 + '' + color.yellow(dct('lines')[0]) + css_2 + '' + color.grey(dct('lines')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('clear', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('clear'))) + css_2 + '' + color.yellow(dct('clear')[0]) + css_2 + '' + color.grey(dct('clear')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('--help', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('--help'))) + css_2 + '' + color.yellow(dct('--help')[0]) + css_2 + '' + color.grey(dct('--help')[1]) + \
		   css_1 +'» ' + color.bold(str(spfc_opr('q', True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr('q'))) + css_2 + '' + color.yellow(dct('q')[0]) + css_2 + '' + color.grey(dct('q')[1])
	return help
	
	
	
def helper(operator):
	'''
	USE:
	help.helper(operator)
	
	Description:
	returns operator inormation as array:
		['arguments', 'description']
	'''
	return dct(operator)



def helping(cmds):
	'''
	USE:
	help.helping(cmds)
	
	Description:
	Returns the description of a speciffic operator
	'''
	return (color.grey('  please use "{0}" as follows:\n\t{1}\n  Description:\n\t{2}'.format(cmds[0], helper(spfc_opr(cmds[0], True))[0], helper(spfc_opr(cmds[0], True))[1])))


	
