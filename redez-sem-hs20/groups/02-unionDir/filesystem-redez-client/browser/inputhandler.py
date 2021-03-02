from browser import help, operators, unionpath
from utils import color
from net import client
import os, getpass

class InputHandler:
    def __init__(self):
        self.unionpath = unionpath.Unionpath()
        self.user = getpass.getuser()
        self.client = client.Client()
        self.operator = operators.Operators(self.unionpath, self.client)

    def get_input(self):
        path_short_form = self.unionpath.create_short_cwd(True)

        if self.client.connect_status:
            message = color.bold(color.green('● ' + self.user + "@{}".format(self.client.IP))) + ":" + color.bold(
                color.blue(path_short_form) + '$ ')
        else:
            message = color.bold(color.grey('● ') + color.green(self.user)) + ":" + color.bold(
            color.blue(path_short_form) + '$ ')

        cmds = input(message).split()
        result = self._handle(cmds)
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

    def _handle(self, cmds):
        # prevent KeyError when enter is pressed
        if len(cmds) == 0:
            return

        # [reg, register]
        elif help.check_if_alias(cmds[0], 'reg'):
            return self.operator.reg(cmds)

        # [con, conn, connect]
        elif help.check_if_alias(cmds[0], 'con'):
            return self.operator.con(cmds)

        # [cd, chdir]
        elif help.check_if_alias(cmds[0], 'cd'):
            return self.operator.cd(cmds)

        # [open, op]
        elif help.check_if_alias(cmds[0], 'open'):
            self.operator.open(cmds)

        # [ls, readdir, list, l]
        elif help.check_if_alias(cmds[0], 'ls'):
            self.operator.ls(cmds)

        # [mk, mkd, mkdir, makedir]
        elif help.check_if_alias(cmds[0], 'mk'):
            self.operator.make_dir(cmds)

        # [mk, write, put, set, mkd, mkdir, makedir, makefile]
        elif help.check_if_alias(cmds[0], 'add'):
            self.operator.add(cmds)

        # [rm, unlink, delete, del, remove]
        elif help.check_if_alias(cmds[0], 'rm'):
            self.operator.rm(cmds)

        # [mt, mount]
        elif help.check_if_alias(cmds[0], 'mount'):
            self.operator.mt(cmds)

        # [mv, move]
        elif help.check_if_alias(cmds[0], 'mv'):
            self.operator.mv(cmds)

        # [cp, copy]
        elif help.check_if_alias(cmds[0], 'cp'):
            self.operator.cp(cmds)

        # [rn, rename]
        elif help.check_if_alias(cmds[0], 'rn'):
            self.operator.rn(cmds)

        # [f, find, locate, search]
        #elif help.check_if_alias(cmds[0], 'f'):
            #operators.f(cmds)

        # [q,-q,quit]
        elif help.check_if_alias(cmds[0], 'q'):
                return "quit"

        # [--help, -help, help, hlp, -h, h]
        elif help.check_if_alias(cmds[0], '--help'):
            self.operator.hlp(cmds)

        # [clear, clc, clean]
        elif help.check_if_alias(cmds[0], 'clear'):
            self.operator.clear(cmds)

        # [unknown]
        else:
            self.operator.unknown(cmds)

