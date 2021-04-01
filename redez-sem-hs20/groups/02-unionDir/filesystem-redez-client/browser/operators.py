import os, re
from browser import  help, help_functions
from utils import color, error
from browser import executions

class Operators:

	def __init__(self, unionpath):
		self.unionpath = unionpath
		self.executions = executions.Executions(self.unionpath)

	'''
	Allows registration to a server.
	'''
	def reg(self, cmds):
		if len(cmds) == 3:
			if re.match("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", cmds[1]):
				self.executions.register_to_server(cmds[1], cmds[2])
				return "reg"
			else:
				print(color.yellow("{} is not a valid IP-address.".format(cmds[1])))
		else:
			print(help.helping(cmds))

	'''
	Connects the client to a known server
	'''
	def con(self, cmds):
		if len(cmds) == 2:
			self.executions.connect_to_server(cmds[1])
			return "reg"
		else:
			print(help.helping(cmds))

	'''
	Displays list of known connections
	'''
	def srv(self, cmds):
		if len(cmds) == 1:
			self.executions.show_registered_servers()
		else:
			print(help.helping(cmds))

	'''
	Change the current working directory
	'''
	def cd(self, cmds):
		if len(cmds) == 2:
			try:
				self.executions.change_directory(cmds[1])
			except:
				print(error.get(cmds, 'error'))
		else:
			print(help.helping(cmds))

	'''
	Opens the specified file with the standard application
	'''
	def open(self, cmds):
		if len(cmds) == 2:
			return self.executions.open_file(cmds[1])
		else:
			print(help.helping(cmds))

	'''
	List files and directories. If a + is appended to the command, additional info gets displayed.
	'''
	def ls(self, cmds):
		if len(cmds) == 1:
			if "+" in cmds[0]:
				additional = True
			else:
				additional = False
			files = help_functions.get_files_from_current_dir(self.unionpath)
		else:
			print(help.helping(cmds))
			return
		if files:
			if len(files) > 20:
				i = input("would you like to display all ({}) entries? [y/n]: ".format(len(files))).lower()
				if i == 'y':
					self.executions.list_folder_content(files, True, additional=additional)
			else:
				self.executions.list_folder_content(files, additional=additional)

	'''
	Creates a directory in either the current or in a specified directory depending on the parameters.
	'''
	def mk(self, cmds):
		if len(cmds) == 2:
			if "." not in cmds[1]:
				self.executions.make_directory(cmds[1])
			else:
				print(error.get(cmds, 'file_error'))
		else:
			print(help.helping(cmds))

	'''
	Copies file or folder (depending on weather an extension is given or not) to the filesystem. If a second path
	is given, the file or folder will be copied there, provided it is within the current filesystem. Else the file
	or folder will be copied into the root directory of the file system.
	'''
	def add(self, cmds, unmuted=None):
		if len(cmds) < 2 or len(cmds) > 3:
			if not unmuted:
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
			return self.executions.add_directory_to_filesystem(source, destination)
		elif os.path.isfile(source):
			return self.executions.add_file_to_filesystem(source, destination)
		else:
			print(error.get(cmds, 'path_error'))
			return

	"""
	Removes file or folder.
	"""
	def rm(self, cmds):
		if len(cmds) == 2:
			files, filehashes = self.executions.remove_object(cmds[1])
			if files:
				for file in files:
					self.unionpath.edit_dictionary(file, 'del')
			print("result length: {}".format(len(["rm", filehashes])))
			return "rm", filehashes
		else:
			print(help.helping(cmds))

	'''
	Mounts a Filesystem from or to a server.
	'''
	def mount(self, cmds):
		if len(cmds) == 2:
			while True:
				response = input(color.yellow("Do you want to upload or download a partition? [u/d/stop] -> ")).lower()
				if response == "d" or response == "download":
					return self.executions.download_mount_partition(cmds[1])
				elif response == "u" or response == "upload":
					return self.executions.upload_mount_partition(cmds[1])
				elif response == "stop":
					return
		elif len(cmds) == 3:
			response = cmds[2]
			if response == "d" or response == "download":
				return self.executions.download_mount_partition(cmds[1])
			elif response == "u" or response == "upload":
				return self.executions.upload_mount_partition(cmds[1])
			else:
				print(help.helping(cmds))
		else:
			print(help.helping(cmds))


	'''
	Moves a file or folder to the specified destination.
	'''
	def mv(self, cmds):
		if len(cmds) == 3:
			return self.executions.copy_within_filesystem(cmds[1], cmds[2], keep=False)
		else:
			print(help.helping(cmds))

	'''
	Copies a file or directory to the specified destination.
	'''
	def cp(self, cmds):
		if len(cmds) == 3:
			return self.executions.copy_within_filesystem(cmds[1], cmds[2], keep=True)
		else:
			print(help.helping(cmds))

	'''
	Allows to rename a file or directory.
	'''
	def rn(self, cmds):
		if len(cmds) == 3:
			self.executions.rename_object(cmds[1], cmds[2])
		else:
			print(help.helping(cmds))

	'''
	Closes the program.
	'''
	def quit(self, cmds):
		if len(cmds) == 1:
			return self.executions.terminate_program()
		else:
			print(error.get(cmds, 'error'))

	'''
	Displays all available commands.
	'''
	def hlp(self, cmds):
		if len(cmds) == 1:
			print(help.help())
		elif len(cmds) == 2:
			print(help.helping([cmds[1]]))
		else:
			print(error.get(cmds, 'warning'))
			print(help.helping(cmds))

	'''
	Clears the terminal.
	'''
	def clear(self, cmds):
		if len(cmds) == 1:
			self.executions.clear_terminal()
		else:
			print(help.helping(cmds))


	'''
	Exports the log file
	'''
	def exp(self):
		self.executions.export_log_file()

	'''
	Handles unknown commands.
	'''
	def unknown(self, cmds=None):
		'''
		USE:
		operators.unknown([optional: cmds_from_terminal])

		Description:
		when entered command is not known, this should be printed
		'''
		print(color.red("Unknown command"))
		print(color.grey("type --help to view the help section."))





