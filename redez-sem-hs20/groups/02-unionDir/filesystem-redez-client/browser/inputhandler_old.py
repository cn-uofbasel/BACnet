from browser import help, operators_old
from utils import color
import os

class InputHandler:
    def __init__(self, client):
        self.client = client
        self.root_dir = client.root_dir
        self.user = client.user
        self.IP = client.IP
        os.chdir(self.root_dir)
        self.current_folder = os.getcwd()
        self.current_fs_folder = self.client.hashpath_to_fspath(self.current_folder)

    def get_input(self):
        self._update_folders()
        path_short_form = self.client.translate_path()

        cmds = input(color.bold(color.green('● ' + self.user + "@{}".format(self.IP))) + ":" + color.bold(
            color.blue(path_short_form) + '$ ')).split()
        result = self._handle(cmds, self.root_dir)
        if result == "quit":
                        return result
        if cmds:
            if help.check_if_alias(cmds[0], 'cd'):
                if result == "disconnect":
                    if self.client.disconnect_dialog():
                        return "quit"
            else:
                if result:
                    print(color.yellow(result))
            return True

    def _update_folders(self):
        self.current_folder = os.getcwd()
        self.current_fs_folder = self.client.hashpath_to_fspath(self.current_folder)
        self.client.current_folder = self.current_folder
        self.client.current_fs_folder = self.current_fs_folder

    def _handle(self, cmds, root):
        # prevent KeyError when enter is pressed
        if len(cmds) == 0:
            return

        elif cmds[0] == "debug":
            return self.client.print_properties()

        # [cd, chdir]
        elif help.check_if_alias(cmds[0], 'cd'):
            return operators_old.cd(cmds, root, self.client)

        # [open, op]
        elif help.check_if_alias(cmds[0], 'open'):
            operators_old.open(cmds, self.client)

        # [ls, readdir, list, l]
        elif help.check_if_alias(cmds[0], 'ls'):
            operators_old.ls(cmds, self.client)

        # [mk, mkd, mkdir, makedir]
        elif help.check_if_alias(cmds[0], 'mk'):
            operators_old.make_dir(cmds, self.client)

        # [mk, write, put, set, mkd, mkdir, makedir, makefile]
        elif help.check_if_alias(cmds[0], 'add'):
            operators_old.add(cmds, self.client, root)

        # [rm, unlink, delete, del, remove]
        elif help.check_if_alias(cmds[0], 'rm'):
            operators_old.rm(cmds, client=self.client)

        # [mt, mount]
        elif help.check_if_alias(cmds[0], 'mount'):
            operators_old.mt(cmds, self.client)

        # [mv, move]
        elif help.check_if_alias(cmds[0], 'mv'):
            operators_old.mv(cmds, self.client)

        # [cp, copy]
        elif help.check_if_alias(cmds[0], 'cp'):
            operators_old.cp(cmds, self.client)

        # [rn, rename]
        elif help.check_if_alias(cmds[0], 'rn'):
            operators_old.rn(cmds, self.client)

        # [f, find, locate, search]
        #elif help.check_if_alias(cmds[0], 'f'):
            #operators.f(cmds)


        # [q,-q,quit]
        elif help.check_if_alias(cmds[0], 'q'):
                return "quit"

        # [--help, -help, help, hlp, -h, h]
        elif help.check_if_alias(cmds[0], '--help'):
            operators_old.hlp(cmds)

        # [clear, clc, clean]
        elif help.check_if_alias(cmds[0], 'clear'):
            operators_old.clear(cmds)

        # [unknown]
        else:
            operators_old.unknown(cmds)

