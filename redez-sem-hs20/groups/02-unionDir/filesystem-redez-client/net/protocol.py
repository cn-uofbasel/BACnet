from utils import color
import ast
import os

BUFFER_SIZE = 8 * 1024

'''
Sends information about file added to the filesystem in the following format:
 ADD <source_path> <destination_path>
'''


def add_file(src, dst, client):
    msg = "ADD {} {}".format(src, dst)
    client.send(msg)
    send_file(src, client)
    msg = client.server_socket.recv(2048)
    if msg:
        return handle_message(msg.decode("utf-8"))
    else:
        return False


'''
Sends information about file added to the filesystem in the following format:
 ADD <source_path> <destination_path>
'''


def add_dir(client, dir_name):
    fs_path = client.current_folder.replace(client.root_dir, "")
    if not fs_path:
        fs_path = "root"
    msg = "DIR {} {}".format(fs_path, dir_name)
    client.send(msg)
    msg = client.server_socket.recv(2048)
    if msg:
        return handle_message(msg.decode("utf-8"))
    else:
        return False


def remove(client, name, extension=None):
    fs_path = client.current_folder.replace(client.root_dir, "")
    if not fs_path:
        fs_path = "root"
    msg = "REM {} {} {}".format(fs_path, name, str(extension))
    client.send(msg)
    msg = client.server_socket.recv(2048)
    if msg:
        return handle_message(msg.decode("utf-8"))
    else:
        return False


def delete(client, hash):
    msg = "DEL {}".format(hash)
    client.send(msg)
    msg = client.server_socket.recv(2048)
    if msg:
        return handle_message(msg.decode("utf-8"))
    else:
        return False


def mount(client, user, fs_name, dst):
    try:
        msg = "MNT_USER {} {} {}".format(user, client.filesystem_hash, fs_name)
        client.send(msg)
        user_matches = client.server_socket.recv(2048)
        user_matches = ast.literal_eval(user_matches.decode("utf-8"))
        #print(user_matches)
        if user_matches == "DMNT":
            return False
        if len(user_matches) == 0:
            user_choice = "None"
        elif len(user_matches) == 1:
            user_choice = user_matches[0][0]
        else:
            msg = ""
            #print(color.yellow("Multiple possibilities found:"))
            for i in range(len(user_matches) - 1):
                msg += color.yellow("[{}] {}@{} -> {} [{}]\n".format(i+1, user_matches[i][1], user_matches[i][2], user_matches[i][0], fs_name))
            msg += color.yellow("[{}] {}@{} -> {} [{}]".format(len(user_matches) - 1+1, user_matches[len(user_matches) - 1][1], user_matches[len(user_matches) - 1][2], user_matches[len(user_matches) - 1][0], fs_name))
            while True:
                print(msg)
                try:
                    choice = input(color.bold(color.green('● ' + client.user + "@{}".format(client.IP))) + color.purple(
                        ":{} -> ".format(user)))
                    choice = int(choice)
                    if choice >= 1 and choice <= len(user_matches):
                        choice -= 1
                        break
                    else:
                        print(color.red("Please enter a number between {} and {}.".format(1, len(user_matches))))
                except:
                    print(color.red("Please enter a number between {} and {}.".format(1, len(user_matches))))
            user_choice = user_matches[choice][0]
        if user_choice in client.get_mounts():
            print(color.yellow("This filesystem is already mounted"))
            return False
        client.send(user_choice)
        root_mount = client.server_socket.recv(2048)
        root_mount = root_mount.decode("utf-8").split()
        if not root_mount[0] == "DIR":
            return False
        root_dir_hash, time = root_mount[1], root_mount[2]
        client.add_to_dict(root_dir_hash, fs_name, "directory", dst, timestamp=time)
        path = client.make_dir(dst, root_dir_hash)
        client.send("DIR_DONE")
        dir_batch = []
        fs_path_root = fs_name
        while True:
            dir_info = client.server_socket.recv(2048)
            dir_info = dir_info.decode("utf-8").split()
            if dir_info[0] == "DIR":
                dir_batch.append([dir_info[1][1:], dir_info[2], dir_info[3], dir_info[4], dir_info[5]])
                client.send("DONE")
            elif dir_info[0] == "DIR_DONE":
                #print(color.green("GOT ALL"))
                break
        hashdict = {}
        for i in range(len(dir_batch)):
            dir_path, dir_hash, name, time, type = dir_batch[i]
            #print("DIR {} {} {} {} {} ".format(dir_path, dir_hash, name, time, type))
            hashdict.update({dir_hash: name})
            client.make_dir(path, dir_path)
            if os.sep not in dir_path:
                dir_path = dir_path.replace(dir_hash, "")
            else:
                dir_path = dir_path.replace(dir_hash + os.sep, "")
            if not dir_path:  # hash, name, type, location, extension="", fs_path = "", timestamp=None
                client.add_to_dict(dir_hash, name, type, path, fs_path=fs_path_root, timestamp=time)
            else:
                fs_path = dir_path
                dirs = dir_path.split(os.sep)
                #print(color.purple(fs_path))
                #print(hashdict)
                for dir in dirs:
                    fs_path = fs_path.replace(dir, hashdict.get(dir))
                fs_path = fs_path.replace(os.sep + name, "")
                client.add_to_dict(dir_hash, name, type, os.path.join(path, dir_path.replace(os.sep + dir_hash, "")),
                                   fs_path=os.path.join(fs_path_root, fs_path), timestamp=time)
        client.send("DIRS_DONE")
        #print(color.green("DIRS_DONE SENT"))
        filehashes = []
        while True:
            file_info = client.server_socket.recv(2048)
            file_info = file_info.decode("utf-8").split()
            if file_info[0] == "CMNT":
                return True, hashdict, filehashes, root_dir_hash
            elif len(file_info) != 7:
                continue
            #print(file_info)
            file_fs_path, file_hash, name, time, type, extension = file_info[1], file_info[2], file_info[3], file_info[4], file_info[5], file_info[6]
            if file_info[0] == "FILE":
                #print(color.green("SEND CFILE"))
                client.send("CFILE")
            filepath = os.path.join(path, file_fs_path)
            with open(filepath, "wb") as file:
                while True:
                    bytes = client.server_socket.recv(BUFFER_SIZE)
                    file.write(bytes)
                    if bytes.strip()[-3:] == b'EOF':
                        break
                    elif bytes.strip()[-3:] == b'INT':
                        return False
                file.close()
            if extension == "None":
                extension = ""
            abs_path = os.path.join(path, file_fs_path.replace(root_dir_hash, "")).replace(
                os.sep + file_hash + extension,
                "")
            file_fs_path = os.path.join(fs_path_root, file_fs_path).replace(os.sep + file_hash + extension, "")
            client.add_to_dict(file_hash, name, type, abs_path, fs_path=file_fs_path, timestamp=time, extension=extension)
            #print(color.green("SEND CCFILE"))
            filehashes.append(file_hash)
            client.send("CCFILE")
    except:
        return False



def hashify(path, name_dict):
    ret = ""
    if os.sep in path:
        dirs = path.split(os.sep)
        for i in range(len(dirs)):
            dirs[i] = name_dict.get(dirs[i])
        for i in range(len(dirs) - 1):
            ret += dirs[i] + os.sep
        return ret + dirs[len(dirs) - 1]
    else:
        return name_dict.get(path)


def send_file(src, client):
    try:
        with open(src, 'rb') as file:
            while True:
                bytes = file.read()
                if not bytes:
                    break
                client.send_bytes(bytes)
            client.send_bytes(b'\EOF')
        return
    except:
        client.send_bytes(b'\INT')
        print(color.red("{} was not found.".format(src)))
        return


def quit(client):
    msg = "QUIT"
    client.send(msg)
    msg = client.server_socket.recv(2048)
    if msg:
        return handle_message(msg.decode("utf-8"))
    else:
        return False


def handle_message(msg):
    msg_spl = msg.split()
    cmd = msg_spl[0]
    if cmd == "CADD":
        return True, msg_spl[1], msg_spl[2]
    elif cmd == "NCADD":
        return False, None
    elif cmd == "CDIR":
        return True, msg_spl[1], msg_spl[2]
    elif cmd == "CNEW":
        return msg_spl[1]
    elif cmd == "CREM":
        return True
    elif cmd == "DREM":
        return False
    elif cmd == "CDEL":
        return True
    elif cmd == "DDEL":
        return False
    elif cmd == "CQUIT":
        return True
    elif cmd == "CMNT":
        return True
    elif cmd == "DMNT":
        return True
