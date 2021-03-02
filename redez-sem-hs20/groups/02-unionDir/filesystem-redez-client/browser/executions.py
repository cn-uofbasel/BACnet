import shutil, os
from browser import help_functions

class Executions:

    def __init__(self, unionpath):
        self.unionpath = unionpath


    '''
    Command con
    '''
    def connect_to_server(self, cmds):
        return

    '''
    Command cd
    '''
    def change_directory(self, cmds):
        return

    '''
    Command open
    '''
    def open_file(self, cmds):
        return

    '''
    Command ls
    '''
    def list_directory(self, cmds):
        return

    '''
    Command add
    '''
    def add_file_to_filesystem(self, source, destination=None):
        if not destination:
            destination = self.unionpath.current_folder
        filename, extension = self.unionpath.get_filename(source)
        hashname = self.unionpath.create_hash(source)
        path = shutil.copy2(source, destination)
        os.rename(path, path.replace(filename, hashname))
        fs_loc = self.unionpath.hashpath_to_fspath(destination)
        self.unionpath.add_to_dictionary(hashname, filename, "file", destination, extension, fs_loc)
        return

    def add_directory_to_filesystem(self, source, destination=None):
        if not destination:
            destination = self.unionpath.current_folder

        return

    '''
    Command mkdir
    '''
    def make_directory(self, new_directory):
        path = self.unionpath.current_folder
        dirs = None
        flag = False
        if os.sep in new_directory:
            flag = True
            dirs = new_directory.split(os.sep)
            for i in range(len(dirs) - 1):
                dirs[i] = self.unionpath.translate_to_hash(dirs[i], path, False)
                path = os.path.join(path, dirs[i])
                if not dirs[i]:
                    return
                new_directory = help_functions.list_to_path(dirs)
        if flag:
            for i in range(len(dirs) - 1):
                os.chdir(dirs[i])
        fs_loc = self.unionpath.hashpath_to_fspath(os.getcwd())
        hashname = self.unionpath.create_hash(os.path.join(os.getcwd(), new_directory))
        dir_path = os.path.join(os.getcwd(), hashname)
        os.mkdir(dir_path)
        os.chdir(self.unionpath.current_folder)
        self.unionpath.add_to_dictionary()
        return
