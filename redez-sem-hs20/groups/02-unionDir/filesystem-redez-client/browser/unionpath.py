from pathlib import Path
from utils import color
import os, json, math, hashlib, random, string
from datetime import datetime
from browser import help_functions

class Unionpath:

    def __init__(self):
        self._linux_home_path = Path.home()
        self.uniondir_dir = self._make_dir_in(self._linux_home_path, ".uniondir")
        self.filesystem_root_dir = self._make_dir_in(self.uniondir_dir, ".root")
        self.configuration_dir = self._make_dir_in(self.uniondir_dir, ".config")
        self.dictionary_file = self._make_file_in(self.configuration_dir, "dictionary", "json")
        self.serverlist_file = self._make_file_in(self.configuration_dir, "servers", "json")
        self.namespace_logger_file = self._make_file_in(self.configuration_dir, "operations", "log")
        self.NAME, self.TIME, self.TYPE, self.LOCATION, self.HASH, self.EXTENSION, self.FS_PATH = 0, 1, 2, 3, 4, 5, 6

    def _make_dir_in(self, path, dir):
        path = os.path.join(path, dir)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def _make_file_in(self, path, file, extension=None):
        if extension:
            file += ".{}".format(extension)
        path = os.path.join(path, file)
        if not os.path.exists(path):
            file_item = open(path, "w+")
            if extension == "json":
                json.dump({}, file_item, indent=4)
            file_item.close()
        return path

    def add_to_dictionary(self, hash, name, type, location, extension="", fs_path = "", timestamp=None):
        content_json = open(self.dictionary_file, "r")
        content = json.load(content_json)
        content_json.close()
        if not timestamp:
            timestamp = math.trunc(datetime.timestamp(datetime.now()))
        info = {"name": name, "time": timestamp, "type": type, "location":location, "extension":extension, "fs_path":fs_path}
        item = {hash:info}
        content.update(item)
        content_json = open(self.dictionary_file, "w")
        json.dump(content, content_json, indent=4)
        content_json.close()

    def edit_dictionary(self, hash, op, name=None, repl=None, hashdir=None):
        with open(self.dictionary_file, 'r') as data_file:
            data = json.load(data_file)
            data_file.close()

        for element in data:
            if op == 'del' and hash in element:
                del data[hash]
                break
            elif op == 'ren-name' and hash in element:
                data[hash]['name'] = name
                break
            elif op == 'ren-fs_path' and hash in element:
                tmp_fs_path = str(data[hash]['fs_path'])
                if tmp_fs_path:
                    if os.sep in tmp_fs_path:
                        dirs = tmp_fs_path.split(os.sep)
                        for i in range(len(dirs)):
                            if dirs[i] == name:
                                dirs[i] = repl
                        tmp_fs_path = ""
                        for i in range(len(dirs) - 1):
                            tmp_fs_path += dirs[i] + os.sep
                        tmp_fs_path += dirs[len(dirs) - 1]
                        data[hash]['fs_path'] = tmp_fs_path
                    else:
                        data[hash]['fs_path'] = repl
                break
            elif op == 'ren-fs_path_full' and hash in element:
                tmp_fs_path = str(data[hash]['fs_path'])
                dirs = tmp_fs_path.split(os.sep)
                for dir in dirs:
                    if hashdir.get(dir):
                        tmp_fs_path = tmp_fs_path.replace(dir, hashdir.get(dir))
                data[hash]['fs_path'] = tmp_fs_path

        with open(self.dictionary_file, 'w') as data_file:
            json.dump(data, data_file, indent=4)
            data_file.close()

    def create_hash(self, string):
            hash_object = hashlib.sha1((str(datetime.now()) + string + self._create_random_string(5)).encode())
            return hash_object.hexdigest()

    def _create_random_string(self, size):
        return ''.join(random.choice(string.ascii_letters) for i in range(size))

    def translate_path(self, tilde=True):
        path_short_form = help_functions.home_path()
        dirs = path_short_form.split(os.sep)
        path = ""
        for dir in dirs:
            info = self.translate_from_hash(dir)
            if info:
                path += info[0] + os.sep
            else:
                path += dir + os.sep
        if tilde:
            return "~" + path[:-1]
        else:
            return path[:-1]

    def hashpath_to_fspath(self, path):
        path_tmp = path.replace(self.filesystem_root_dir, "")
        if os.sep in path_tmp:
            path = path.replace(self.filesystem_root_dir + os.sep, "")
            dirs = path.split(os.sep)
            for dir in dirs:
                name = self.translate_from_hash(dir)[0]
                path = path.replace(dir, name)
            return path
        else:
            return ""

    def fspath_to_hashpath(self, name, fs_path):
        content_json = open(self.dictionary_file, "r")
        content = json.load(content_json)
        content_json.close()
        matches = []
        paths = []
        hashes = []
        extensions = []
        for obj in content:
            info = self.translate_from_hash(obj)
            if info[self.NAME] == name and info[self.FS_PATH] == fs_path:
                matches.append(info)
                paths.append(info[self.LOCATION])
                hashes.append(info[self.HASH])
                extensions.append(info[self.EXTENSION])
        if len(matches) == 0:
            return None
        elif len(matches) == 1:
            return os.path.join(paths[0], hashes[0] + extensions[0])
        else:
            choice = self.handle_duplicates(matches, fs_path)
            return os.path.join(paths[choice], hashes[choice] + extensions[choice])

    def translate_from_hash(self, hash):
        try:
            hash = os.path.splitext(hash)[0]
            content_json = open(self.dictionary_file, "r")
            content = json.load(content_json)
            content_json.close()
            name = content.get(hash)['name']
            time = content.get(hash)['time']
            type = content.get(hash)['type']
            location = content.get(hash)['location']
            extension = content.get(hash)['extension']
            fs_path = content.get(hash)['fs_path']
            content_json.close()
            return [name, time, type, location, hash, extension, fs_path]
        except:
            return None

    def translate_to_hash(self, name, path, suppress=False):
        content_json = open(self.dictionary_file, "r")
        content = json.load(content_json)
        content_json.close()
        matches = []
        hashes = []
        for obj in content:
            info = self.translate_from_hash(obj)
            if info[0] == name and info[3] == path:
                matches.append(info)
                hashes.append(obj)
        if suppress:
            if len(matches) == 0:
                return None
            elif len(matches) == 1:
                return hashes[0]
            else:
                return hashes[-1]
        else:
            if len(matches) == 0:
                return None
            elif len(matches) == 1:
                return hashes[0]
            else:
                return hashes[self.handle_duplicates(matches, name)]

    def handle_duplicates(self, matches, name):
        msg = "{} duplicates of {} have been found. Select one by entering the corresponding number:".format(len(matches), name)
        str = ""
        cnt = 0
        for info in matches:
            str += "\r\n[{}] {}: Fingerprint -> {}".format(cnt+1, info[0], info[1])
            cnt += 1
        msg += str
        print(color.yellow(msg))
        while True:
            try:
                choice = input(color.bold(color.purple("{} -> ".format(name))))
                choice = int(choice)
                if choice >= 1 and choice <= len(matches):
                    choice -= 1
                    return choice
                else:
                    print(color.red("Please enter a number between {} and {}.".format(1, len(matches))))
            except:
                print(color.red("Please enter a number between {} and {}.".format(1, len(matches))))

    def create_short_cwd(self, tilde=False):
        current_path = os.getcwd().replace(self.filesystem_root_dir, "")

        if current_path == "":
            current_path = os.sep

        if tilde:
            current_path = "~" + current_path

        return current_path