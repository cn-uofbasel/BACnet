import os
from browser import  help, help_functions
from utils import color, error, line_counter
from net import client
from browser import executions

class Operators:

	def __init__(self, unionpath, client):
		self.unionpath = unionpath
		self.client = client
		self.executions = executions.Executions(self.unionpath)

	'''
	Connects the client to a known server
	'''
	def con(self, cmds):
		if len(cmds) == 1:
			self.client = client.Client()
		elif len(cmds) == 2:
			self.client = client.Client(cmds[1])
		else:
			print(error.get(cmds, 'error'))

	'''
	Change the current working directory
	'''
	def cd(self, cmds):
		if len(cmds) == 2:
			curr = os.getcwd()
			if cmds[1] == "..":
				if os.getcwd().__eq__(self.unionpath.filesystem_root_dir):
					return
				else:
					os.chdir('..')
					return
			try:
				dir = self.unionpath.translate_to_hash(cmds[1], curr)
				os.chdir(dir)
				new = os.getcwd()
				if not new.__contains__(self.unionpath.filesystem_root_dir):
					os.chdir(curr)
					print(color.red("Accessing outside the filesystem."))
					return "disconnect"
			except:
				path = os.path.join(os.getcwd(), cmds[1])
				print(error.get(cmds, 'error'))
		else:
			print(error.get(cmds, 'warning'))

	'''
	Opens the specified file with the standard application
	'''
	def open(self, cmds):

		if len(cmds) == 2:
			file = cmds[1]
			if os.sep in file:
				print(color.red(file))
			if os.path.isfile(file):
				if help_functions.open_help(file):
					print("opening")
				else:
					print(error.get(cmds, 'error'))
			else:
				print(error.get(cmds, 'error'))
		else:
			print(error.get(cmds, 'warning'))

	'''
	List files and directories. If a + is appended to the command, additional info gets displayed.
	'''
	def ls(self, cmds):
		files = None
		if len(cmds) == 1:
			if "+" in cmds[0]:
				additional = True
			else:
				additional = False
			files = help_functions.ls_help(self.unionpath)  # "ls"
		else:  # error: too many arguments given
			print(error.get(cmds, 'warning'))
			print(help.helping(cmds))
			return
		if files: #if files has ben set, it went trough sucessfully and can be printed
			if len(files) > 20: #if there are more than 20 files to display: ask
				i = input("would you like to display all ({}) entries? [y/n]: ".format(len(files))).lower()
				if i == 'y':
					help_functions.print_file(files, True, additional=additional, client=self.client)
			else:
				help_functions.print_file(files, additional=additional, client=self.client)

	'''
	Copies file or folder (depending on weather an extension is given or not) to the filesystem. If a second path
	is given, the file or folder will be copied there, provided it is within the current filesystem. Else the file
	or folder will be copied into the root directory of the file system.
	'''
	def add(self, cmds, unmuted=None):
		if len(cmds) < 2 or len(cmds) > 3:
			if not unmuted:
				print(error.get(cmds, 'warning'))
				print(help.helping(cmds))
			return
		if self.unionpath.filesystem_root_dir in cmds[1]:
			print(error.get(cmds, 'fs_error'))
			return

		if len(cmds) == 2:
			source = cmds[1]
			destination = None
		else:
			source = cmds[1]
			destination = cmds[2]

		if os.path.isdir(source):
			self.executions.add_directory_to_filesystem(source, destination)
		elif os.path.isfile(source):
			self.executions.add_file_to_filesystem(source, destination)
		else:
			print(error.get(cmds, 'path_error'))
			return


	def make_dir(self, cmds):
		if len(cmds) == 2:
			if "." not in cmds[1]:
				if not help_functions.make_dir_help(self.client, cmds[1]):
					print(error.get(cmds, 'path_error'))
			else:
				print(error.get(cmds, 'file_error'))
		else:
			print(error.get(cmds, 'format_error'))


	def rm(self, cmds, unmuted=None): #TODO: only delete when user has secret key
		'''
		USE:
		operators.rm(cmds) where cmds = [rm, name_of_file, [OPTIONAL: path_(else_cwd)]] where name_of_file can also be /path/to/file.extension (instead of giving it as a seperate optional argument).

		Description:
		Remove a file and empty or non empty folders. name_of_file can be a path.

		Note:
		name_of_file can have an extension (if you wish to delete a file) or no extension (if you want to delete a folder)
		'''
		if len(cmds) == 2: #no path is given (path = cwd)
			help_functions.rm_help(cmds[1], client=self.client)
		else:
			if not unmuted:
				print(error.get(cmds, 'warning'))
				print(help.helping(cmds))


	def mt(self, cmds):
		'''
		USE:
		operators.mt(cmds) where cmds = [umt, path]

		Description:
		Mounts a storage filesystem, making it accessible and attaching it to an existing directory structure
		'''
		if len(cmds) == 3 or len(cmds) == 4:
			user = cmds[1]
			fs_name = cmds[2]
			if len(cmds) == 3:
				dst = self.client.current_folder
			else:
				dst = help_functions.mv_help(dst=cmds[3], client=self.client)
				if dst == 2:
					print(error.get(cmds, 'nodst'))
					return
				else:
					dst = dst[1]
			if help_functions.mnt_help(user, fs_name, dst, self.client):
				print(error.get(cmds, 'success'))
			else:
				print(error.get(cmds, 'error'))
				help_functions.rm_help(fs_name, self.client, dst, suppress=True)
		else:
			print(error.get(cmds, 'warning'))
			print(help.helping(cmds))


	def umt(self, cmds):
		'''
		USE:
		operators.umt(cmds) where cmds = [umt, path]

		Description:
		Unmounts a mounted filesystem (informing the system to complete any pending read or write operations, and safely detaching it.)
		'''
		print("Unmount filesystem") #TODO
		print(error.get(cmds, 'warning'))
		print(help.helping(cmds))


	def pwd(self, cmds):
		'''
		USE:
		operators.pwd(cmds) where cmds = [pwd]

		Description:
		Prints the full current working directory.
		'''
		if len(cmds) == 1:
			print(os.getcwd())
		else:
			print(error.get(cmds, 'warning'))
			print(help.helping(cmds))


	def mv(self, cmds, delete=True):
		'''
		USE:
		operators.mv(cmds) where cmds = [mv, object_to_be_moved, new_location]

		Description:
		Moves a file/folder (and all subfolders and files if there are any) into the new location.

		Note:
		The while loop can be used for name collisions in the import and mount as well.
		'''
		if len(cmds) == 3:
			if "." in cmds[1]:
				name = cmds[1].split(os.sep)[-1]
			else:
				name = cmds[1]
			paths = help_functions.mv_help(src=cmds[1], dst=cmds[2], client=self.client)
			if paths == 1:
				print(error.get(cmds, 'nosrcdir'))
			elif paths == 2:
				print(error.get(cmds, 'nodstdir'))
			elif len(paths) == 2:
				src, dst = paths
				if src == dst:
					return
				if os.path.isfile(src):
					object = help_functions.add_help(src, self.client, dst)
					help_functions.rn_help(os.path.join(dst, object), name, client=self.client)
				elif os.path.isdir(src):
					object = help_functions.add_help(src, self.client, dst)
					help_functions.rn_help(os.path.join(dst, object), name, client=self.client)
			if delete:
				start_path = help_functions.get_upper_dir(paths[0])
				help_functions.rm_help(name, client=self.client, start_path=start_path, suppress=True)
			else:
				print(error.get(cmds, 'warning'))
		else:
			print(error.get(cmds, 'warning'))
			print(help.helping(cmds))


	def cp(self, cmds):
		'''
		USE:
		operators.cp(cmds) where cmds = [cp, object_to_be_copied, new_location]

		Description:
		Copies a file/folder (and all subfolders and files if there are any) into the new location.

		Note:
		The while loop can be used for name collisions in the import and mount as well.
		'''
		self.mv(cmds, self.client, delete=False)


	def rn(self, cmds):
		'''
		USE:
		operators.rn(cmds) where cmds = [rn, object_to_be_renamed, new_name]

		Description:
		Renames a file/folder.

		Note:
		The new_name argument must not be a path! (if it is required to be a path for some reason in the future, this can easily be changed tough.)
		'''
		if len(cmds) == 3:
			name = cmds[2]
			paths = help_functions.mv_help(src=cmds[1], client=self.client)
			if paths == 1:
				print(error.get(cmds, 'nosrcdir'))
				return
			else:
				src = paths[0]
				help_functions.rn_help(src, name, client=self.client)
		else:
			print(error.get(cmds, 'warning'))
			print(help.helping(cmds))



	def f(self, cmds): #TODO
		return

	def quit(self, cmds):
		'''
		USE:
		operators.quit(cmds) where cmds = [quit]

		Description:
		Quits the program
		'''
		if len(cmds) == 1:
			if self.client.disconnect_dialog():
				if help_functions.quit_help(self.client):
					return True
			else:
				return False
		else:
			print(error.get(cmds, 'warning'))
			print(help.helping(cmds))


	def hlp(self, cmds):
		'''
		USE:
		operators.hlp(cmds) where cmds = [help, speciffic_operator]

		Description:
		Get list of all commands. If speciffic operator is given as secon argument, it prints out only the help section for that operator.
		'''
		if len(cmds) == 1:
			print(help.help())
		elif len(cmds) == 2: # show help for a speciffic command
			print(help.helping([cmds[1]]))
		else:
			print(error.get(cmds, 'warning'))
			print(help.helping(cmds))



	def clear(self, cmds):
		'''
		USE:
		operators.clear(cmds) where cmds = [clear]

		Description:
		Clears the program terminal
		'''
		if len(cmds) == 1:
			help_functions.clear()
		else:
			print(error.get(cmds, 'warning'))
			print(help.helping(cmds))



	def lines(self, cmds=None):
		'''
		USE:
		operators.lines([optional: cmds_from_terminal])

		Description:
		"count all lines of code in a python package and print an informative output. It will count all lines in all .py"

		Note:
		The code snipped (30 lines) used to output the result is an exact copy from StackOverflow answer 46329364 (Made by: Bryce93). The source can be found here: https://stackoverflow.com/questions/38543709/count-lines-of-code-in-directory-using-python#answer-46329364. This is clarified here and in the output as well to prevent misconseptions of plagiarism.
		'''
		print()
		print(line_counter.countlines(os.getcwd()))
		text = "from StackOverflow Answer 46329364 (Made by: Bryce93)"
		source = "https://stackoverflow.com/questions/38543709/count-lines-of-code-in-directory-using-python#answer-46329364'"
		print('\n' + color.grey(f"\u001b]8;;{source}\u001b\\{text}\u001b]8;;\u001b\\") + '\n')



	def unknown(self, cmds=None):
		'''
		USE:
		operators.unknown([optional: cmds_from_terminal])

		Description:
		when entered command is not known, this should be printed
		'''
		print(color.red("Unknown command"))
		print(color.grey("type --help to view the help section."))

	def inside_filesystem(self, path):
		return path.__contains__(self.unionpath.filesystem_root_dir)
