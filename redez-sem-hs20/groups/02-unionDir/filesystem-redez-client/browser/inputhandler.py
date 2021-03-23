from browser import help, operators, unionpath
from utils import color
from net import protocol
import os

class InputHandler:
    def __init__(self):
        self.unionpath = unionpath.Unionpath()
        self.operator = operators.Operators(self.unionpath)
        self.protocol = protocol.Protocol(self.unionpath)

    def get_input(self):
        path_short_form = self.unionpath.create_short_cwd(True)

        if self.unionpath.connected:
            message = color.bold(color.green('● ' + self.unionpath.user_name + "@{}".format(self.unionpath.client.IP))) + ":" + color.bold(
                color.blue(path_short_form) + '$ ')
        else:
            message = color.bold(color.grey('● ') + color.green(self.unionpath.user_name)) + ":" + color.bold(
            color.blue(path_short_form) + '$ ')

        cmds = input(message).split()
        result_input = self._handle(cmds)
        result_server = self.protocol.handle(cmds)
        if result_input == "END":
            return result_input

    def _handle(self, cmds):
        # prevent KeyError when enter is pressed
        if len(cmds) == 0:
            return

        elif cmds[0] == 'debug':
            print(os.getcwd())

        # [reg, register]
        elif help.check_if_alias(cmds[0], 'reg'):
            return self.operator.reg(cmds)

        # [con, conn, connect]
        elif help.check_if_alias(cmds[0], 'con'):#TODO
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

        # [srv, srvls, serverlist]
        elif help.check_if_alias(cmds[0], 'srv'): #TODO
            self.operator.srv(cmds)

        # [mk, mkd, mkdir, makedir]
        elif help.check_if_alias(cmds[0], 'mk'):
            self.operator.mk(cmds)

        # [mk, write, put, set, mkd, mkdir, makedir, makefile]
        elif help.check_if_alias(cmds[0], 'add'):
            self.operator.add(cmds)

        # [rm, unlink, delete, del, remove]
        elif help.check_if_alias(cmds[0], 'rm'):
            self.operator.rm(cmds)

        # [mt, mount]
        elif help.check_if_alias(cmds[0], 'mt'): #TODO
            self.operator.mount(cmds)

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
        elif help.check_if_alias(cmds[0], 'f'): #TODO
            self.operator.rn(cmds)

        # [--help, -help, help, hlp, -h, h]
        elif help.check_if_alias(cmds[0], '--help'):
            self.operator.hlp(cmds)

        # [q,-q,quit]
        elif help.check_if_alias(cmds[0], 'quit'):
            return self.operator.quit(cmds)

        # [clear, clc, clean]
        elif help.check_if_alias(cmds[0], 'clear'):
            self.operator.clear(cmds)

        # [unknown]
        else:
            self.operator.unknown(cmds)

