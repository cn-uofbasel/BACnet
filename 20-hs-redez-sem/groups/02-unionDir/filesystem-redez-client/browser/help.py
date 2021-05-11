from util import color


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
		'reg'			: ['reg', 'rgstr', 'register'],
		'con'			: ['con', 'conn', 'connect'],
		'cd'			: ['cd','chdir'],
		'open'			: ['open', 'op'],
		'ls'			: ['ls', 'list', 'l', 'ls+', 'l+', "list+"],
		'srv'			: ['srv', 'srvls', 'serverlist'],
		'mk'			: ['mk','mkd ','mkdir ','makedir'],
		'add'			: ['add', 'put '],
		'rm'			: ['rm', 'delete', 'del', 'remove'],
		'mt'			: ['mt', 'mount', 'mnt'],
		'mv'			: ['mv', 'move'],
		'cp'			: ['cp', 'copy'],
		'rn'			: ['rn', 'rename'],
		'f'				: ['f', 'find', 'locate', 'search'],
		'--help' 		: ['--help', '-help', 'help', 'hlp', '-h', 'h'],
		'quit'			: ['quit','-quit ','exit ','-exit'],
		'clear'			: ['clear', 'clc', 'c', 'clean'],
		'y'		        : ['y ','yes'],
		'n'		        : ['n ','no'],

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
		'reg'	 : ['args: <IP> <server_name>'		,'Change the current working directory.'],
		'con'	 : ['args: <server_name>'		,'Change the current working directory.'],
		'cd'     : ['args: <directory_name>'			,'Change the current working directory.'],
		'open'	 : ['args: <file_name>'	 ,'Opens the specified file.'],
		'ls'     : ['args: [+]'		,'List files and directories. If a + is appended to the commmand, additional info gets displayed.'],
		'srv'	 : ['args: None'				,'Lists all remembered servers.'],
		'mk'     : ['args: <directory_name>','Creates a new folder in the current directory.'],
		'add'	 : ['args: <file_path> [<destination_path>]', 'Adds an existing file to the filesystem. If the second argument is empty, the file is copied to the root of the filesystem.'],
		'rm'     : ['args: <file_path>','Remove a file or directory.'],
		'mt'     : ['args: ???'					,'Mounts an external filesystem, making it accessible and attaching it to your existing directory structure.'],
		'mv'	 : ['args: <source_path> <destination_path>','Moves an file/folder (and all subfolders and files if there are any) into the new location.'],
		'cp'	 : ['args: <source_path> <destination_path>','Copies an file/folder (and all subfolders and files if there are any) into the new location.'],
		'rn'	 : ['args: <file_name> <new_name>','renames an file/folder.'],
		'f'	 	 : ['args: <file_name>','Finds a file/folder and returns its location. If -r argument is passed it searches all subfolders as well.'],
		'--help' : ['args: None' ,'Get list of all commands along with required or optional arguments.'],
		'quit'   : ['args: None'				,'Quits the program.'],
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
	commands = ['reg','con','cd','open','ls','srv','mk','add','rm','mt','mv','cp','rn','f','--help','quit','clear']
	help = color.green('this is the --help section:')
	for cmd in commands:
		help += css_1 + '» ' + color.bold(str(spfc_opr(cmd, True))) + color.cyan(css_2 + 'aliases: ' + str(spfc_opr(cmd))) + css_2 + '' + color.yellow(dct(cmd)[0]) + css_2 + '' + color.grey(dct(cmd)[1])
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


	
