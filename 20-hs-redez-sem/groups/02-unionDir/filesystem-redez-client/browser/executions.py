import shutil, os, datetime
from browser import help_functions, create
from utils import color
from net import protocol
import subprocess

class Executions:

    def __init__(self, unionpath):
        self.unionpath = unionpath

    '''
    Command reg
    '''
    def register_to_server(self, IP, name):
        self.unionpath.connected = self.unionpath.client.connect(IP)
        if self.unionpath.connected:
            server = self.unionpath.edit_mount_list("get",property="servers").get(IP)
            if server:
                if server == name:
                    self.unionpath.edit_mount_list("add_server", IP=IP, servername=name)
                else:
                    while True:
                        anwser = input(color.yellow("Server at IP: {} already registered. Rename {} -> {}? [y/n] -> ".format(IP, server, name))).lower()
                        if anwser.__eq__("y") or anwser.__eq__("yes"):
                            self.unionpath.edit_mount_list("add_server",IP=IP, servername=name)
                            break
                        elif anwser.__eq__("n") or anwser.__eq__("no"):
                            break
            else:
                self.unionpath.edit_mount_list("add_server", IP=IP, servername=name)
        else:
            print(color.red("Connection to {} no established".format(IP)))
            return

    '''
    Command con
    '''
    def connect_to_server(self, name):
        servers  = self.unionpath.edit_mount_list("get",property="servers")
        candidates = []
        IP = None
        for server in servers:
            if name == servers.get(server):
                candidates.append(server)
        if len(candidates) == 0:
            print(color.red("No server under the name {} registered".format(name)))
            return
        elif len(candidates) == 1:
            IP =  candidates[0]
        else:
            print(color.yellow("Multiple servers under the name {} registered: ".format(name)))
            for i in range(len(candidates)):
                print("[{}] -> {}".format(i+1, candidates[i]))
            while True:
                try:
                    choice = input(color.bold(color.purple("{} -> ".format(name))))
                    choice = int(choice)
                    if choice >= 1 and choice <= len(candidates):
                        choice -= 1
                        break
                    else:
                        print(color.red("Please enter a number between {} and {}.".format(1, len(candidates))))
                except:
                    print(color.red("Please enter a number between {} and {}.".format(1, len(candidates))))
            IP = candidates[choice]
        self.unionpath.connected = self.unionpath.client.connect(IP)
        if not self.unionpath.connected:
            print(color.red("Unable to connect to {}({}).".format(name, IP)))

    '''
    Command srv
    '''
    def show_registered_servers(self):
        servers = self.unionpath.edit_mount_list("get", property="servers")
        conn_IP = self.unionpath.client.IP
        for server in servers:
            if conn_IP == server:
                print(color.cyan(" (*) " + server + " -> " + servers.get(server)))
            else:
                print(color.cyan("     " + server + " -> " + servers.get(server)))
    '''
    Command cd
    '''
    def change_directory(self, name):
        curr = os.getcwd()
        if name == "..":
            if os.getcwd().__eq__(self.unionpath.filesystem_root_dir):
                return
            else:
                os.chdir('..')
                self.unionpath.current_folder = os.getcwd()
                return
        elif name == "root" or name == "home":
            os.chdir(self.unionpath.filesystem_root_dir)
            self.unionpath.current_folder = os.getcwd()
            return
        dir = self.unionpath.translate_to_hash(name, curr)
        os.chdir(dir)
        self.unionpath.current_folder = os.getcwd()

    '''
    Command open
    '''
    def open_file(self, file):
        if "." in file:
            file = file.split(".")[0]
        filehash = self.unionpath.translate_to_hash(file, self.unionpath.current_folder)
        if not filehash:
            print(color.red("The file {} does not exist".format(file)))
            return
        path = os.path.join(self.unionpath.current_folder, filehash)
        if os.path.isfile(path):
            self.unionpath.edit_dictionary(filehash, "timestamp")
            FNULL = open(os.devnull, 'w')
            subprocess.call(["xdg-open", path], stdout=FNULL, stderr=FNULL)
        else:
            self.change_directory(file)

    '''
    Command add if file
    '''
    def add_file_to_filesystem(self, source, destination=None):
        if ".uniondir" in source:
            print(color.red("Cannot add object from within the filesystem."))
            return
        if not destination:
            destination = self.unionpath.current_folder
        else:
            curr = self.unionpath.current_folder
            dirs = destination.split(os.sep)
            for dir in dirs:
                dir_hash = self.unionpath.translate_to_hash(dir, curr)
                if not dir_hash:
                    print("{} does not exist".format(destination))
                    return
                curr = os.path.join(curr, dir_hash)
            destination = curr
        filename, extension = self.unionpath.get_filename(source)
        hashname = self.unionpath.create_hash(source)
        path = shutil.copy2(source, destination)
        os.rename(path, path.replace(filename + extension, hashname))
        fs_loc = self.unionpath.hashpath_to_fspath(destination)
        self.unionpath.add_to_dictionary(hashname, filename, "file", destination, fs_loc, extension)
        return

    '''
    Command add if dir
    '''
    def add_directory_to_filesystem(self, source, destination=None):
        tmp = self.unionpath.current_folder
        if ".uniondir" in source:
            print(color.red("Cannot add object from within the filesystem."))
            return
        if not destination:
            destination = self.unionpath.current_folder
        else:
            curr = self.unionpath.current_folder
            dirs = destination.split(os.sep)
            for dir in dirs:
                curr = os.path.join(curr, self.unionpath.translate_to_hash(dir, curr))
            destination = curr
        os.chdir(destination)
        fs_loc = self.unionpath.hashpath_to_fspath(os.getcwd())
        os.chdir(self.unionpath.current_folder)
        dir_name = source.split(os.sep)[-1]
        dir_hashname = self.unionpath.create_hash(source)
        destination = os.path.join(destination, dir_hashname)
        dst_dir = shutil.copytree(source, destination)
        self.unionpath.add_to_dictionary(dir_hashname, dir_name, "directory", os.getcwd(), fs_loc)
        help_functions.hashify_entire_dir(dst_dir, self.unionpath)
        os.chdir(tmp)
        self.unionpath.current_folder = tmp
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
                print(dirs[i])
                dirs[i] = self.unionpath.translate_to_hash(dirs[i], path, False)
                if not dirs[i]:
                    return
                path = os.path.join(path, dirs[i])
            new_directory = new_directory.split(os.sep)[-1]
        if flag:
            print(color.green(new_directory))
            for i in range(len(dirs) - 1):
                os.chdir(dirs[i])
        fs_loc = self.unionpath.hashpath_to_fspath(os.getcwd())
        hashname = self.unionpath.create_hash(os.path.join(os.getcwd(), new_directory))
        dir_path = os.path.join(os.getcwd(), hashname)
        os.mkdir(dir_path)
        self.unionpath.add_to_dictionary(hashname, new_directory, "directory", os.getcwd(), fs_loc)
        os.chdir(self.unionpath.current_folder)
        return hashname

    '''
    Command ls
    '''
    def list_folder_content(self, paths, arg=None, additional=False):
        dir_icon = "📁"
        file_icon = "📄"
        mount_icon = "📦"
        img_icon = "🖼"
        music_icon = "🎵"
        movie_icon = "🎥"
        name, time, type, location, hash, extension, fs_path = 0, 1, 2, 3, 4, 5, 6
        f_list = []
        d_list = []
        for p in paths:
            if p[type] == 'file':
                f_list.append(p)
            elif p[type] == 'directory':
                d_list.append(p)
        paths = f_list + d_list
        if arg:
            print('\n-------------------')
        if not additional:
            for p in paths:
                if p[type] == 'file':
                    icon = file_icon
                    if p[extension] in [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".eps"]:
                        icon = img_icon
                    elif p[extension] in [".mp3", ".wav", ".flac", ".aac"]:
                        icon = music_icon
                    elif p[extension] in [".mp4", ".mov", ".avi", ".wmv"]:
                        icon = movie_icon
                    if extension != "":
                        print("{}  ".format(icon) + color.purple(p[name] + p[extension]))
                    else:
                        print("{}  ".format(icon) + color.purple(p[name]))
                elif p[type] == 'directory':
                    icon = dir_icon
                    if p[hash] in self.unionpath.get_server_info('mount'):
                        icon = mount_icon
                    print("{}  ".format(icon) + color.blue(p[name]))
        else:
            for p in paths:
                date = datetime.datetime.fromtimestamp(int(p[time])).strftime('%m/%d/%Y %H:%M:%S')
                if p[type] == 'file':
                    if p[type] == 'file':
                        icon = file_icon
                        if p[extension] in [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".eps"]:
                            icon = img_icon
                        elif p[extension] in [".mp3", ".wav", ".flac", ".aac"]:
                            icon = music_icon
                        elif p[extension] in [".mp4", ".mov", ".avi", ".wmv"]:
                            icon = movie_icon
                    if not str(p[extension]):
                        add_info = color.cyan(" \tDate: {}  \tFingerprint: {}".format(date, p[time]))
                    else:
                        add_info = color.cyan(
                            " \tType: {}  \tDate: {}  \tFingerprint: {}".format(p[extension], date, p[time]))
                    if extension != "":
                        print("{}  ".format(icon) + color.purple(p[name] + p[extension]) + add_info)
                    else:
                        print("{}  ".format(icon) + color.purple(p[name]) + add_info)
                elif p[type] == 'directory':
                    icon = dir_icon
                    if p[hash] in self.unionpath.get_server_info('mount'):
                        icon = mount_icon
                    add_info = color.cyan(" \tDate: {}  \tFingerprint: {}".format(date, p[time]))
                    print("{}  ".format(icon) + color.blue(p[name]) + add_info)
        if arg:
            print('\n-------------------')

    '''
    Command rm
    '''
    def remove_object(self, name, suppress = False):
        obj_hash, os_obj_path = self.unionpath.get_full_path(name)
        hashes = [obj_hash]
        if os.path.isfile(os_obj_path):
            os.remove(os_obj_path)
        elif os.path.isdir(os_obj_path):
            if len(os.listdir(os_obj_path)) == 0:
                empty = True
            else:
                empty = False
            if not empty:
                tmp = self.unionpath.current_folder
                os.chdir(os_obj_path)
                self.unionpath.current_folder = os.getcwd()
                files = help_functions.get_files_from_current_dir(self.unionpath)
                os.chdir(tmp)
                self.unionpath.current_folder = tmp
                if not suppress:
                    while True:
                        show_content = input(color.yellow("Folder {} is not empty. Display content? [y/n/stop]".format(name)))
                        if show_content.lower() == "y" or show_content.lower() == "yes":
                            self.list_folder_content(files)
                            break
                        elif show_content.lower() == "n" or show_content.lower() == "no":
                            break
                        elif show_content.lower() == "stop":
                            return
                        else:
                            print(color.red("Please enter [y/n], if you want to stop the deletion enter [stop]."))
                    while True:
                        show_content = input(color.yellow("Delete all content of {}? [y/n]".format(name)))
                        if show_content.lower() == "y" or show_content.lower() == "yes":
                            for (dirpath, dirnames, filenames) in os.walk(os_obj_path):
                                hashes.extend(filenames)
                                hashes.extend(dirnames)
                            shutil.rmtree(os_obj_path)
                            return hashes
                        elif show_content.lower() == "n" or show_content.lower() == "no":
                            return
                else:
                    for (dirpath, dirnames, filenames) in os.walk(os_obj_path):
                        hashes.extend(filenames)
                        hashes.extend(dirnames)
                    shutil.rmtree(os_obj_path)
                    return hashes
            else:
                shutil.rmtree(os_obj_path)
                return hashes

    '''
    Command rn
    '''
    def rename_object(self, path, name):
        if os.sep in name:
            print(color.red("The name cannot contain the character {}.".format(os.sep)))
            return
        if "." in name:
            name = name.split(".")[0]
        if os.sep in path:
            if "." in path.split(os.sep)[1]:
                dirs = path.split(os.sep)
                dirs[-1] = dirs[-1].split(".")[0]
                path = ""
                for i in range(len(dirs) - 1):
                    path = os.path.join(path, dirs[i])
        else:
            if "." in path:
                path = path.split(".")[0]
        curr = self.unionpath.current_folder
        if os.sep in path:
            dirs = path.split(os.sep)
            for i in range(len(dirs)):
                dirs[i] = self.unionpath.translate_to_hash(dirs[i], curr, False)
                if not dirs[i]:
                    print(color.red("Location does not exist."))
                    return
                curr = os.path.join(curr, dirs[i])
        else:
            hash_name = self.unionpath.translate_to_hash(path, curr, False)
            curr = os.path.join(curr, hash_name)
        self.unionpath.edit_dictionary(hash=curr.split(os.sep)[-1], op='ren-name', name=name)

    '''
    Command cp
    '''
    def copy_within_filesystem(self, source, destination, keep=False):
        curr = self.unionpath.current_folder
        if os.sep in source:
            dirs = source.split(os.sep)
            source = curr
            for i in range(len(dirs)):
                dirs[i] = self.unionpath.translate_to_hash(dirs[i], source, False)
                if not dirs[i]:
                    print(color.red("Location does not exist."))
                    return
                source = os.path.join(source, dirs[i])
        else:
            source = os.path.join(curr, self.unionpath.translate_to_hash(source, curr, False))
        if os.sep in destination:
            dirs = destination.split(os.sep)
            destination = curr
            for i in range(len(dirs)):
                dirs[i] = self.unionpath.translate_to_hash(dirs[i], destination, False)
                if not dirs[i]:
                    print(color.red("Location does not exist."))
                    return
                destination = os.path.join(destination, dirs[i])
        else:
            destination = os.path.join(curr, self.unionpath.translate_to_hash(destination, curr, False))
        if os.path.isdir(source):
            src_info = self.unionpath.translate_from_hash(source.split(os.sep)[-1])
            src_name, src_type = src_info[0], src_info[2]
            self.unionpath.current_folder = destination
            root_cpy_hash = self.unionpath.create_hash(os.path.join(curr, src_name))
            dst_path = shutil.copytree(source, os.path.join(destination, root_cpy_hash))
            fs_loc = self.unionpath.hashpath_to_fspath(destination)
            self.unionpath.add_to_dictionary(root_cpy_hash, src_name, "directory", destination, fs_loc)
            help_functions.assign_new_hashes_dir(dst_path, self.unionpath)
            if not keep:
                hashes = [source.split(os.sep)[-1]]
                for (dirpath, dirnames, filenames) in os.walk(source):
                    hashes.extend(filenames)
                    hashes.extend(dirnames)
                shutil.rmtree(source)
                if hashes:
                    for file in hashes:
                        self.unionpath.edit_dictionary(file, 'del')
        elif os.path.isfile(source):
            src_info = self.unionpath.translate_from_hash(source.split(os.sep)[-1])
            src_hash, src_name, src_type, src_extension = src_info[4], src_info[0], src_info[2], src_info[5]
            self.unionpath.current_folder = destination
            file_path = shutil.copy2(source, destination)
            hashname = self.unionpath.create_hash(file_path)
            fs_loc = self.unionpath.hashpath_to_fspath(destination)
            os.rename(file_path, file_path.replace(src_hash, hashname))
            self.unionpath.add_to_dictionary(hashname, src_name, "file", destination, fs_loc, src_extension)
            if not keep:
                self.unionpath.edit_dictionary(src_hash, 'del')
                os.remove(source)
        self.unionpath.current_folder = curr
        os.chdir(self.unionpath.current_folder)

    '''
    Clears terminal
    '''
    def clear_terminal(self):
        try:
            if os.name == 'nt':
                _ = os.system('cls')
            else:
                _ = os.system('clear')
        except:
            pass

    def terminate_program(self):
        while True:
            terminate = input(color.yellow("Terminate Uniondir? [y/n] -> ")).lower()
            if terminate.__eq__("y") or terminate.__eq__("yes"):
                terminate = True
                break
            elif terminate.__eq__("n") or terminate.__eq__("no"):
                terminate = False
                break
        if not terminate:
            return
        if self.unionpath.connected:
            self.unionpath.client.disconnect()
        print(create.thank())
        return "END"