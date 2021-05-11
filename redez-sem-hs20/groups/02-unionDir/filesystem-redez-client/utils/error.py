from util import color
from browser import help
import random

def get(cmds, typ, add_attr=None):
	'''
	USE:
	error.get(cmds, type, [optional:add_attr]) where add_attr must be < 3
	
	Description:
	Returns a correctly colored message according to declared "typ"
	'''
	#---------------------------------------------------------------
	if not add_attr:
		add_attr = [None,None,None]
	elif len(add_attr)<3:
		for i in range(3-len(add_attr)):
			add_attr.append(None)
	if len(cmds) < 2:
		cmds.append(None)
	
	operator = help.spfc_opr(cmds[0],True)
	names=[None,None,None]
	if operator == 'q':
		names = ['Ken Rotaris', 'Tunahan Erbay', 'Leonardo Salsi']
		random.shuffle(names) #names in random order
		names[0] = color.bold(color.red(names[0]))
		names[1] = color.bold(color.greenDark(names[1]))
		names[2] = color.bold(color.yellow(names[2]))
		random.shuffle(names)
		
	dictionary = {
		#command   | messages #TODO: blank messages are not being used yet/ have not ben set yet.
		'cd'     : {'success': color.greenDark(''),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('The directory does not exist')
					},
		'open': 		{'success': color.greenDark(''),
				   	'warning': color.yellow('wrong argument format'),
				   	'error': color.red('unable to open file')
				   	},
		'ls'     : {'success': color.greenDark(''),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('given directory doesn\'t exist'),
					'unknown': color.red('Unknown option \'{}\''.format(cmds[1]))
					},
		'cat'    : {'success': color.greenDark(''),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('file doesn\'t exist at \'{1}\''.format(cmds[0], add_attr)),
					'nt_supp': color.red('file type currently not supported by \'{}\' command'.format(cmds[0])),
					'hint'	 : color.grey('tip: use \'{}\' followed by an integer to display a range.'.format(cmds[0]))
					},
		'mk'    : {'success': color.greenDark('folder {0} created'.format(add_attr[0])),  #add_attr = [name, path]
					'warning': color.yellow('wrong argument format'),
					'file_error'  : color.red('name cannot contain a dot'),  #add_attr = [name, typ, path]
					'format_error' : color.red('please use command as follows: mk <dir_name>'),
				   	'path_error': color.red('the path the folder is to be created in does not exist'.format(add_attr))
				   },
		'add'	 : {'success': color.greenDark('File added to the filesystem.'),
					# add_attr = [name, path]
					'warning': color.yellow('wrong argument format'),
					'error': color.red('{0} "{1}" already exists at {2}'.format(add_attr[1], add_attr[0], add_attr[2])),
					# add_attr = [name, typ, path]
					'path_error': color.red('The source does not exist'.format(add_attr)),
					'format_error': color.red('\'{}\' either outside of the filesystem or not an existing directory'.format(add_attr[2])),
					'nodstdir': color.red('Destination folder does not exist.'),
					'fs_error': color.red('Cannot add files from within the filesystem.')
					 },
		'rm'     : {'success': color.greenDark('deleted {0} from {1}'.format(add_attr[0], add_attr[1])),  #add_attr = [name, path]
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('{0} "{1}" does not exists at {2}'.format(add_attr[1], add_attr[0], add_attr[2])),  #add_attr = [name, typ, path]
					'path_error' : color.red('\'{}\' doesn\'t exist'.format(add_attr))
                    },
		'mount'     : {'success': color.greenDark('Filesystem mounted successfully.'),
					'warning': color.yellow('Mount a filesystem of an other user with mnt <user> <filesystem_name> [<path>]'),
					'error'  : color.red('Unable to mount filesystem.'),
					'nodst': color.red('Destination path does not exist.')
					},
		'umt'    : {'success': color.greenDark(''),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('')
					},
		'exp'    : {'success': color.greenDark('Filesystem has been successfully exported!'),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('No root_mockup folder found at current location or its super folders \'{}\'.'.format(add_attr[0]))
					},
		'mkp'    : {'success': color.greenDark(''),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('folder \'{0}\' already exists at \'{1}\''.format(add_attr[0], add_attr[1]))
					},
		'pwd'    : {'success': color.greenDark(''),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('')
					},
		'img'    : {'success': color.greenDark('sucessfully created image \'{0}\' at \'{1}\''.format(add_attr[0], add_attr[1])),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('')
					},
		'txt'    : {'success': color.greenDark('sucessfully created text \'{0}\' at \'{1}\''.format(add_attr[0], add_attr[1])),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('')
					},
		'mv'     : {'success': color.greenDark('sucessfully moved file \'{0}\' to \'{1}\''.format(add_attr[0], add_attr[1])),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('the {0} path \'{1}\' doen\'s exist'.format(add_attr[0], add_attr[1])),
					'sameDir': color.grey('Information: you moving a file/folder within the same directory.'),
					'nodstdir': color.red('The destination directory does not exist.'),
					'nosrcdir': color.red('The source file or directory does not exist.')
					},
		'cp'     : {'success': color.greenDark('sucessfully copied file \'{0}\' to \'{1}\''.format(add_attr[0], add_attr[1])),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('the {0} path \'{1}\' doen\'s exist'.format(add_attr[0], add_attr[1]))
					},
		'rn'     : {'success' : color.greenDark('sucessfully renamed file \'{0}\' to \'{1}\''.format(add_attr[0], add_attr[1])),
					'warning' : color.yellow('wrong argument format'),
					'error'   : color.red('the given path \'{0}\' doen\'s exist'.format(add_attr[0])),
					'nosrcdir': color.red('The source file or directory does not exist.')
					},
		'f'    	 : {'success': color.greenDark('\'{0}\' found at {1}'.format(add_attr[0], add_attr[1])),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('\'{0}\' not found in \'{1}\''.format(add_attr[0], add_attr[1]))
					},
		'--help' : {'success': color.greenDark(''),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('')
					},
		'quit'      : {'success': '\n   Thanks for using our Application!\n   Made with ' + color.bold(
            color.redLight('<3')) + ' by: {0}, {1}, {2}\n'.format(names[0], names[1], names[2]),
					'warning': color.yellow('If you want to terminate program, enter q without further arguments.'),
					'error'  : color.red('If you want to terminate the program, enter q without further arguments.')
					},
		'clear'  : {'success': color.greenDark(''),
					'warning': color.yellow('wrong argument format'),
					'error'  : color.red('')
					}
					
	}
	
	return dictionary[operator][typ]
	
	
	
