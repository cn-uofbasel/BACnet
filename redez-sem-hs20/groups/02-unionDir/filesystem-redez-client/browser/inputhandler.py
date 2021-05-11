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

        message = input(message)
        cmds = message.split()
        result = self._handle(cmds)
        if result:
            if (isinstance(result, tuple)):
                if len(result) == 2:
                    self.protocol.handle(result[0], additional=result[1])
            else:
                if len([result]) == 1:
                    result = self.protocol.handle(result)
                    if result == "END":
                        return result
                elif len([result]) == 2:
                    self.protocol.handle(result[0], additional=result[1])


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
        elif help.check_if_alias(cmds[0], 'con'):
            return self.operator.con(cmds)

        # [cd, chdir]
        elif help.check_if_alias(cmds[0], 'cd'):
            self.operator.cd(cmds)

        # [open, op]
        elif help.check_if_alias(cmds[0], 'open'):
            return self.operator.open(cmds)

        # [ls, readdir, list, l]
        elif help.check_if_alias(cmds[0], 'ls'):
            self.operator.ls(cmds)

        # [srv, srvls, serverlist]
        elif help.check_if_alias(cmds[0], 'srv'):
            self.operator.srv(cmds)

        # [mk, mkd, mkdir, makedir]
        elif help.check_if_alias(cmds[0], 'mk'):
            self.operator.mk(cmds)

        # [mk, write, put, set, mkd, mkdir, makedir, makefile]
        elif help.check_if_alias(cmds[0], 'add'):
            return self.operator.add(cmds)

        # [rm, unlink, delete, del, remove]
        elif help.check_if_alias(cmds[0], 'rm'):
            return self.operator.rm(cmds)

        # [mt, mount]
        elif help.check_if_alias(cmds[0], 'mt'): #TODO
            return self.operator.mount(cmds)

        # [mv, move]
        elif help.check_if_alias(cmds[0], 'mv'):
            return self.operator.mv(cmds)

        # [cp, copy]
        elif help.check_if_alias(cmds[0], 'cp'):
            return self.operator.cp(cmds)

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

        elif help.check_if_alias(cmds[0], 'exp'):
             self.operator.exp()

        # [unknown]
        else:
            self.operator.unknown(cmds)

